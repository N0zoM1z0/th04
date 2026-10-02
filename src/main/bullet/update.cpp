// TH04 MAIN's historical bullet_u.cpp object is one physical producer.
// Keep the exact recovered motion prefix and bullets_update body together so
// native-link routing preserves the original BULLET_U_TEXT ownership surface.
#ifdef TH04P
// Far entries use MAIN_03 CS. Give the compiler that same frame for its
// CS-relative switch tables, rather than adding the group only at link time.
#pragma option -zCBULLET_U_TEXT -zPmain_03
#endif
#include "src/main/bullet/update_prefix.inl"
#include "src/main/bullet/update_body.inl"
