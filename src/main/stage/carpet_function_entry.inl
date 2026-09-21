void pascal near carpet_lighting_put_new(int cel, unsigned int target_level)
{
	#define _SI               	reinterpret_cast<uint8_t near *>(_SI)
	#define tile_image_vos    	reinterpret_cast<vram_offset_t __ds *>(_BX)
	#define tile_ring_bytewise	reinterpret_cast<uint8_t __ds*>(tile_ring)
