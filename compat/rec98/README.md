# ReC98 compatibility boundary

This directory quarantines compile-time dependencies that currently exist only
in the pinned ReC98 source tree. Product source includes a forwarding header as
`compat/rec98/<upstream-path>`; only files below this directory may directly
include `libs/`, `platform/`, `th01/`, `th02/`, `th03/`, or `th05/` paths.

Each forwarding header deliberately contains one include and no copied
declaration. This keeps upstream provenance visible, avoids vendoring the
129-file recursive header closure, and prevents compatibility material from
being counted as reconstructed TH04 source. The exact replay copies this whole
directory into each clean pinned-ReC98 materialization and records every file's
path, size, and SHA-256 in its private receipt.

The directory is reusable by other PC-98 reconstruction repositories:

1. Keep the same `compat/rec98/<upstream-path>` naming contract.
2. Add one forwarding header for each directly required upstream header.
3. Reject direct cross-game/ReC98 includes in product source.
4. Materialize and attest the compatibility directory as a build input.
5. Replace forwarders incrementally with target-attested common ABI/platform
   headers; place genuinely shared maintained code in that repository's
   `src/shared/` tree.

This is a migration boundary, not the final shared library. It still requires
the pinned ReC98 checkout behind the forwarding headers and therefore does not
make TH04 independently buildable by itself. A clean standalone build is only
reached when the required declarations have been reconstructed locally and the
last forwarding header is removed.
