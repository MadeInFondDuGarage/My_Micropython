#ifndef HERSHEY_FONT_H
#define HERSHEY_FONT_H

#include <stdint.h>
#include "py/obj.h"

/*
 * Module MicroPython : hershey_font
 *
 * API exposée côté Python :
 *
 *   hershey_font.draw_text_bin(
 *       font_bin,        # bytes / bytearray du .bin
 *       x, y,            # position baseline
 *       text,            # str
 *       color,           # 0..255
 *       framebuffer,     # bytearray (4bpp, 2 pixels / byte)
 *       width, height,   # dimensions écran
 *       font_height_px   # hauteur en pixels
 *   )
 */

mp_obj_t mp_draw_text_bin(size_t n_args, const mp_obj_t *args);

#endif /* HERSHEY_FONT_H */