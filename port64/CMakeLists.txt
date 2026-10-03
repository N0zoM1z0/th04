cmake_minimum_required(VERSION 3.16)
project(th04_port64 LANGUAGES CXX)

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
  message(FATAL_ERROR "TH04 port64 requires a 64-bit compiler")
endif()

add_library(
  th04-portable-core STATIC
  application_state.cpp
  bullet_geometry.cpp
  item_system.cpp
  menu_state.cpp
  random_lcg.cpp
  random_ring.cpp
)
target_compile_features(th04-portable-core PUBLIC cxx_std_17)
target_compile_definitions(th04-portable-core PUBLIC GAME=4)
target_include_directories(th04-portable-core PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/..")

add_executable(th04-port64 main.cpp view.cpp)
target_compile_features(th04-port64 PRIVATE cxx_std_17)
target_link_libraries(th04-port64 PRIVATE th04-portable-core)

add_executable(th04-port64-contracts contracts.cpp)
target_link_libraries(th04-port64-contracts PRIVATE th04-portable-core)

foreach(target th04-portable-core th04-port64 th04-port64-contracts)
  if(MSVC)
    target_compile_options(${target} PRIVATE /W4)
  else()
    target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
  endif()
endforeach()
if(MINGW)
  foreach(target th04-port64 th04-port64-contracts)
    target_link_options(${target} PRIVATE -static -static-libgcc -static-libstdc++)
  endforeach()
endif()
if(WIN32)
  target_link_libraries(th04-port64 PRIVATE user32 gdi32)
else()
  find_package(PkgConfig REQUIRED)
  pkg_check_modules(SDL2 REQUIRED IMPORTED_TARGET sdl2)
  target_link_libraries(th04-port64 PRIVATE PkgConfig::SDL2)
endif()

enable_testing()
add_test(NAME portable-contracts COMMAND th04-port64-contracts)
