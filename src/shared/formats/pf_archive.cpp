// TH04 PAR directory and streamed DOS file view. The resident interrupt entry
// is in pf_int21.asm; this unit owns only the archive and virtual handle state.
// There is one active archive and at most one intercepted member handle.
// Its DOS handle actually belongs to the backing archive: pf_busy in the
// ASM hook forwards this unit's own DOS reads instead of intercepting them.
#pragma option -zCSHARED -3

#include <dos.h>
#include <io.h>
#include <string.h>

#include "src/shared/runtime/api.hpp"

static const unsigned PF_RECORD_BYTES = 32u;
static const unsigned PF_RECORD_NAME = 3u;
static const unsigned PF_RECORD_PACKED_SIZE = 16u;
static const unsigned PF_RECORD_LOGICAL_SIZE = 18u;
static const unsigned PF_RECORD_PAYLOAD_OFFSET = 20u;
static const unsigned PF_ENCODING_REPEAT = 0x9595u;
static const unsigned PF_CARRY_FLAG = 1u;

enum PfDosFunction {
	PF_DOS_OPEN = 0x3D,
	PF_DOS_CLOSE = 0x3E,
	PF_DOS_READ = 0x3F,
	PF_DOS_WRITE = 0x40,
	PF_DOS_SEEK = 0x42,
	PF_DOS_IOCTL = 0x44,
	PF_DOS_DUPLICATE = 0x45,
	PF_DOS_FORCE_DUPLICATE = 0x46,
};

// Exact stack order built by pf_int21.asm. These are saved 16-bit registers
// and the original interrupt return frame, not ordinary C++ call arguments.
struct PfFrame {
	unsigned es, ds, bp, di, si, dx, cx, bx, ax, ip, cs, flags;
};
typedef char PfFrameSize[(sizeof(PfFrame) == 24) ? 1 : -1];

extern "C" int TH04_PASCAL pf_hook_install(void);
extern "C" void TH04_PASCAL pf_hook_remove(void);
extern "C" unsigned bbufsiz;
extern "C" unsigned pferrno;
extern "C" unsigned char pfkey;

static char archive_path[128];
static unsigned char __seg *directory_records;
static unsigned member_count;
static unsigned archive_active;

struct ArchiveMemberStream {
	unsigned active;
	unsigned handle;
	unsigned char __seg *buffer;
	unsigned buffer_capacity, buffer_size, buffer_cursor;
	unsigned packed_size, packed_fetched; // Bytes fetched, including unread buffer data.
	unsigned logical_size, encoding; // Declared size is the SEEK_END origin only.
	unsigned char payload_xor_key;
	unsigned long payload_file_offset;
	unsigned long decoded_offset; // Decompressed bytes already delivered/discarded.
	int previous_byte; // -1 before the first byte; otherwise an 8-bit value.
	unsigned repeat_remaining; // Additional copies after the two equal literals.
};
static ArchiveMemberStream member_stream;

static unsigned pf_read_le16(const unsigned char far *p)
{
	return (unsigned)p[0] | ((unsigned)p[1] << 8);
}

static unsigned long pf_read_le32(const unsigned char far *p)
{
	return (unsigned long)pf_read_le16(p) |
		((unsigned long)pf_read_le16(p + 2) << 16);
}

static unsigned char uppercase_ascii(unsigned char c)
{
	return ((c >= 'a') && (c <= 'z')) ? (unsigned char)(c - 32) : c;
}

static int member_name_matches(const char far *path, const unsigned char far *name)
{
	// Match just the basename. Case folding acts bytewise and does not parse
	// CP932 lead/trail pairs; retain that limitation during semantic cleanup.
	const char far *basename = path;
	unsigned name_index;
	for (const char far *p = path; *p; p++) {
		if ((*p == '\\') || (*p == '/') || (*p == ':')) {
			basename = p + 1;
		}
	}
	for (name_index = 0; name_index < 13; name_index++) {
		if (uppercase_ascii((unsigned char)basename[name_index]) !=
			uppercase_ascii(name[name_index])) {
			return 0;
		}
		if (name[name_index] == 0) {
			return 1;
		}
	}
	return basename[13] == 0;
}

static void close_member(void)
{
	// Close the backing DOS handle and release its refill buffer separately.
	if (member_stream.active) {
		_dos_close(member_stream.handle);
		member_stream.active = 0;
	}
	if (member_stream.buffer) {
		hmem_free(member_stream.buffer);
		member_stream.buffer = 0;
	}
}

static int rewind_member(void)
{
	// Seeking backwards in a compressed member restarts at its payload.
	// Discard buffered encoded bytes and all repeated-byte decoder history.
	if (lseek(member_stream.handle, (long)member_stream.payload_file_offset, SEEK_SET) < 0) {
		return 0;
	}
	member_stream.buffer_size = member_stream.buffer_cursor =
		member_stream.packed_fetched = member_stream.repeat_remaining = 0;
	member_stream.decoded_offset = 0;
	member_stream.previous_byte = -1;
	return 1;
}

static int read_payload_byte(void)
{
	// packed_fetched counts DOS bytes brought into the refill buffer. The
	// buffer cursor counts their consumption; decoded_offset is independent.
	unsigned bytes_read;
	if (member_stream.buffer_cursor == member_stream.buffer_size) {
		unsigned refill_bytes;
		if (member_stream.packed_fetched == member_stream.packed_size) {
			return -1;
		}
		refill_bytes = member_stream.packed_size - member_stream.packed_fetched;
		if (refill_bytes > member_stream.buffer_capacity) {
			refill_bytes = member_stream.buffer_capacity;
		}
		if (_dos_read(member_stream.handle, (void far *)member_stream.buffer,
			refill_bytes, &bytes_read) || !bytes_read) {
			return -1;
		}
		member_stream.packed_fetched += bytes_read;
		member_stream.buffer_size = bytes_read;
		member_stream.buffer_cursor = 0;
	}
	return member_stream.buffer[member_stream.buffer_cursor++] ^ member_stream.payload_xor_key;
}

static int decode_member_byte(void)
{
	int value;
	if (member_stream.repeat_remaining) {
		member_stream.repeat_remaining--;
		return member_stream.previous_byte;
	}
	value = read_payload_byte();
	if (value < 0) {
		return -1;
	}
	// Stored 0xF388 members fall through unchanged after payload XOR. For
	// 0x9595, two equal literals consume a count of additional copies. The
	// second literal itself is returned by this call, including when count=0.
	if ((member_stream.encoding == PF_ENCODING_REPEAT) &&
		(value == member_stream.previous_byte)) {
		int count = read_payload_byte();
		if (count < 0) {
			return -1;
		}
		member_stream.repeat_remaining = (unsigned)count;
	}
	member_stream.previous_byte = value;
	return value;
}

static unsigned read_member(unsigned char far *out, unsigned count)
{
	// Stop at the encoded stream's end, not the declared logical size. Five
	// pinned resources expand one byte beyond that size; callers can read it.
	// An underlying error also yields a short read through this service.
	unsigned bytes_written = 0;
	while (bytes_written < count) {
		int value = decode_member_byte();
		if (value < 0) {
			break;
		}
		out[bytes_written++] = (unsigned char)value;
		member_stream.decoded_offset++;
	}
	return bytes_written;
}

static void dos_frame_success(PfFrame far *frame, unsigned ax)
{
	frame->ax = ax;
	frame->flags &= ~PF_CARRY_FLAG;
}

static void dos_frame_failure(PfFrame far *frame, unsigned dos_error)
{
	frame->ax = dos_error;
	frame->flags |= PF_CARRY_FLAG;
}

extern "C" int TH04_PASCAL pf_dispatch(PfFrame far *frame)
{
	// Return 0 to chain to DOS, 1 to return the edited frame with IRET.
	// Success/error is encoded in saved AX and FLAGS, not in this return value.
	unsigned dos_function = frame->ax >> 8;
	if (!archive_active) {
		return 0;
	}
	if (dos_function == PF_DOS_OPEN) {
		const char far *path = (const char far *)MK_FP(frame->ds, frame->dx);
		unsigned member_index;
		int handle;
		// Intercept read-only opens only. A second simultaneous member open
		// is forwarded to DOS; it does not replace the active stream.
		if ((frame->ax & 3u) != 0 || member_stream.active) {
			return 0;
		}
		for (member_index = 0; member_index < member_count; member_index++) {
			const unsigned char far *entry =
				(const unsigned char far *)directory_records +
				member_index * PF_RECORD_BYTES;
			if (!member_name_matches(path, entry + PF_RECORD_NAME)) {
				continue;
			}
			if (_dos_open(archive_path, 0, &handle)) {
				dos_frame_failure(frame, 2);
				return 1;
			}
			member_stream.handle = handle;
			member_stream.active = 1;
			member_stream.encoding = pf_read_le16(entry);
			member_stream.payload_xor_key = entry[2];
			member_stream.packed_size = pf_read_le16(entry + PF_RECORD_PACKED_SIZE);
			member_stream.logical_size = pf_read_le16(entry + PF_RECORD_LOGICAL_SIZE);
			member_stream.payload_file_offset = pf_read_le32(entry + PF_RECORD_PAYLOAD_OFFSET);
			member_stream.buffer_capacity = bbufsiz ? bbufsiz : 512;
			member_stream.buffer = (unsigned char __seg *)hmem_allocbyte(member_stream.buffer_capacity);
			if (!member_stream.buffer || !rewind_member()) {
				close_member();
				dos_frame_failure(frame, 8);
				return 1;
			}
			dos_frame_success(frame, handle);
			return 1;
		}
		return 0;
	}
	if (!member_stream.active || (frame->bx != member_stream.handle)) {
		return 0;
	}
	if (dos_function == PF_DOS_READ) {
		unsigned bytes_written = read_member((unsigned char far *)MK_FP(frame->ds, frame->dx), frame->cx);
		dos_frame_success(frame, bytes_written);
		return 1;
	}
	if (dos_function == PF_DOS_CLOSE) {
		close_member();
		dos_frame_success(frame, 0);
		return 1;
	}
	if (dos_function == PF_DOS_SEEK) {
		long seek_delta = (long)(((unsigned long)frame->cx << 16) | frame->dx);
		long seek_origin;
		long target_offset;
		unsigned char discard[64];
		unsigned count;
		switch (frame->ax & 0xffu) {
		case 0: seek_origin = 0; break;
		case 1: seek_origin = (long)member_stream.decoded_offset; break;
		case 2: seek_origin = (long)member_stream.logical_size; break;
		default: dos_frame_failure(frame, 1); return 1;
		}
		target_offset = seek_origin + seek_delta;
		if ((target_offset < 0) || ((unsigned long)target_offset > 65536UL)) {
			dos_frame_failure(frame, 1);
			return 1;
		}
		if (((unsigned long)target_offset < member_stream.decoded_offset) && !rewind_member()) {
			dos_frame_failure(frame, 1);
			return 1;
		}
		while (member_stream.decoded_offset < (unsigned long)target_offset) {
			// Retain narrowing to 16 bits before the 64-byte clamp. The
			// accepted upper offset is 65536; wider arithmetic in a port
			// needs a separate boundary probe before changing this order.
			count = (unsigned)((unsigned long)target_offset - member_stream.decoded_offset);
			if (count > sizeof(discard)) {
				count = sizeof(discard);
			}
			if (read_member(discard, count) != count) {
				dos_frame_failure(frame, 1);
				return 1;
			}
		}
		dos_frame_success(frame, (unsigned)member_stream.decoded_offset);
		frame->dx = (unsigned)(member_stream.decoded_offset >> 16);
		return 1;
	}
	// Reject writes, IOCTL and duplication on the intercepted backing handle.
	// Other functions still chain to DOS through the final return below.
	if ((dos_function == PF_DOS_WRITE) || (dos_function == PF_DOS_IOCTL) ||
		(dos_function == PF_DOS_DUPLICATE) ||
		(dos_function == PF_DOS_FORCE_DUPLICATE)) {
		dos_frame_failure(frame, 1);
		return 1;
	}
	return 0;
}

extern "C" void TH04_PASCAL pfend(void)
{
	// Unhook before releasing directory/buffer state that the callback reads.
	if (archive_active) {
		pf_hook_remove();
		archive_active = 0;
	}
	close_member();
	if (directory_records) {
		hmem_free(directory_records);
		directory_records = 0;
	}
	member_count = 0;
}

extern "C" void TH04_PASCAL pfstart(const unsigned char far *path)
{
	int handle;
	unsigned bytes_read, directory_entries, directory_bytes, directory_key, byte_index;
	unsigned char header[16];
	unsigned char far *entries;
	pfend();
	pferrno = 0;
	for (byte_index = 0; byte_index + 1 < sizeof(archive_path) && path[byte_index]; byte_index++) {
		archive_path[byte_index] = path[byte_index];
	}
	archive_path[byte_index] = 0;
	if (path[byte_index]) {
		pferrno = 1;
		return;
	}
	if (_dos_open(archive_path, 0, &handle)) {
		pferrno = 2;
		return;
	}
	if (_dos_read(handle, header, sizeof(header), &bytes_read) || bytes_read != sizeof(header)) {
		pferrno = 3;
		_dos_close(handle);
		return;
	}
	directory_bytes = pf_read_le16(header);
	directory_entries = pf_read_le16(header + 4);
	directory_key = pf_read_le16(header + 6);
	// The directory has one terminal record after the real member records.
	if ((directory_entries > 1023) ||
		(directory_bytes != (directory_entries + 1u) * PF_RECORD_BYTES) ||
		(directory_key > 255)) {
		pferrno = 3;
		_dos_close(handle);
		return;
	}
	pfkey = (unsigned char)directory_key;
	directory_records = (unsigned char __seg *)hmem_allocbyte(directory_bytes);
	if (!directory_records) {
		pferrno = 8;
		_dos_close(handle);
		return;
	}
	if (_dos_read(handle, (void far *)directory_records, directory_bytes,
		&bytes_read) || bytes_read != directory_bytes) {
		pferrno = 3;
		_dos_close(handle);
		pfend();
		return;
	}
	_dos_close(handle);
	entries = (unsigned char far *)directory_records;
	for (byte_index = 0; byte_index < directory_bytes; byte_index++) {
		// Update the key with the decoded byte, wrapping modulo 256.
		unsigned char value = entries[byte_index] ^ (unsigned char)directory_key;
		entries[byte_index] = value;
		directory_key = (unsigned char)(directory_key - value);
	}
	for (byte_index = directory_entries * PF_RECORD_BYTES;
		byte_index < directory_bytes; byte_index++) {
		if (entries[byte_index]) {
			pferrno = 3;
			pfend();
			return;
		}
	}
	member_count = directory_entries;
	// The hook becomes active only after the complete directory is available.
	archive_active = (unsigned)pf_hook_install();
}
