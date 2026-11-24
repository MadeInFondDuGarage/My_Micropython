#include "hershey_font.h"

#include <stdlib.h>
#include <string.h>

#include "py/runtime.h"
#include "py/buffer.h"

/* ============================================================
 * Pixel (4 bpp, 2 pixels par octet)
 * ============================================================ */

static inline void draw_pixel(
    uint8_t *buf,
    int width,
    int height,
    int x,
    int y,
    uint8_t color
) {
    if (x < 0 || x >= width || y < 0 || y >= height) return;

    color = 255 - color;

    int pos = (y * width >> 1) + (x >> 1);
    uint8_t p = buf[pos];

    if (x & 1) {
        p = (p & 0x0F) | (color & 0xF0);
    } else {
        p = (p & 0xF0) | (color >> 4);
    }

    buf[pos] = p;
}

/* ============================================================
 * Ligne (Bresenham entier)
 * ============================================================ */

static void draw_line(
    uint8_t *buf,
    int width,
    int height,
    int x1,
    int y1,
    int x2,
    int y2,
    uint8_t color
) {
    int dx = abs(x2 - x1);
    int dy = -abs(y2 - y1);
    int sx = (x1 < x2) ? 1 : -1;
    int sy = (y1 < y2) ? 1 : -1;
    int err = dx + dy;

    while (1) {
        draw_pixel(buf, width, height, x1, y1, color);
        if (x1 == x2 && y1 == y2) break;
        int e2 = err << 1;
        if (e2 >= dy) { err += dy; x1 += sx; }
        if (e2 <= dx) { err += dx; y1 += sy; }
    }
}

/* ============================================================
 * API MicroPython : draw_text_bin
 * ============================================================ */

mp_obj_t mp_draw_text_bin(size_t n_args, const mp_obj_t *args) {

    /* ---------- Arguments ---------- */
    // 0: font_bin (bytes)
    // 1: x
    // 2: y
    // 3: text (str)
    // 4: color
    // 5: framebuffer (bytearray)
    // 6: width
    // 7: height
    // 8: font_height_px

    mp_buffer_info_t font;
    mp_get_buffer_raise(args[0], &font, MP_BUFFER_READ);

    int x = mp_obj_get_int(args[1]);
    int y = mp_obj_get_int(args[2]);

    GET_STR_DATA_LEN(args[3], text, text_len);

    int color = mp_obj_get_int(args[4]);

    mp_buffer_info_t fb;
    mp_get_buffer_raise(args[5], &fb, MP_BUFFER_RW);

    int width  = mp_obj_get_int(args[6]);
    int height = mp_obj_get_int(args[7]);
    int font_height_px = mp_obj_get_int(args[8]);

    /* ---------- Font header ---------- */
    const uint8_t *p = font.buf;

    uint16_t glyph_count = p[0] | (p[1] << 8);
    const uint8_t *index = p + 6;

    /* ---------- Scaling (Q8.8) ---------- */
    const int FONT_UNITS_HEIGHT = 120;
    int scale = (font_height_px << 8) / FONT_UNITS_HEIGHT;

    int cx = x;

    /* ---------- Loop characters ---------- */
    for (size_t i = 0; i < text_len; i++) {
        uint16_t code = text[i];
        const uint8_t *gi = index;
        const uint8_t *glyph = NULL;

        /* lookup unicode */
        for (int g = 0; g < glyph_count; g++) {
            uint16_t u = gi[0] | (gi[1] << 8);
            if (u == code) {
                uint32_t off =
                    gi[2]
                  | (gi[3] << 8)
                  | (gi[4] << 16)
                  | (gi[5] << 24);
                glyph = font.buf + off;
                break;
            }
            gi += 6;
        }

        if (!glyph) {
            cx += font_height_px / 3;
            continue;
        }

        uint8_t advance   = glyph[0];
        uint8_t seg_count = glyph[1];
        const uint8_t *seg = glyph + 2;

        /* ---------- Loop segments ---------- */
        for (int s = 0; s < seg_count; s++) {
            int x1 = (int8_t)seg[0];
            int y1 = (int8_t)seg[1];
            int x2 = (int8_t)seg[2];
            int y2 = (int8_t)seg[3];
            seg += 4;

            int xx1 = cx + ((x1 * scale) >> 8);
            int yy1 = y  - ((y1 * scale) >> 8);
            int xx2 = cx + ((x2 * scale) >> 8);
            int yy2 = y  - ((y2 * scale) >> 8);

            draw_line(
                fb.buf,
                width,
                height,
                xx1, yy1,
                xx2, yy2,
                (uint8_t)color
            );
        }

        cx += (advance * scale) >> 8;
    }

    return mp_const_none;
}

/* ============================================================
 * Module registration
 * ============================================================ */

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(
    mp_draw_text_bin_obj,
    9,
    mp_draw_text_bin
);

STATIC const mp_rom_map_elem_t hershey_font_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_hershey_font) },
    { MP_ROM_QSTR(MP_QSTR_draw_text_bin), MP_ROM_PTR(&mp_draw_text_bin_obj) },
};

STATIC MP_DEFINE_CONST_DICT(
    hershey_font_module_globals,
    hershey_font_module_globals_table
);

const mp_obj_module_t hershey_font_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&hershey_font_module_globals,
};

MP_REGISTER_MODULE(
    MP_QSTR_hershey_font,
    hershey_font_user_cmodule
);