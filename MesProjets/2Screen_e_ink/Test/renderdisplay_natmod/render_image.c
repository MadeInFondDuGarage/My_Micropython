// render_image.c - natmod MicroPython pour chargement et rendu BMP
// ESP32S3 - MicroPython 1.28
// Buffer écran : 4bpp, 2 pixels par octet, nibble haut = pixel pair

#include "py/runtime.h"
#include "py/obj.h"
#include "py/mphal.h"
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// ---------- état interne du natmod ----------
static uint8_t  *bmp_buf    = NULL;
static int32_t   bmp_width  = 0;
static int32_t   bmp_height = 0;
static int32_t   bmp_bpp    = 0;

// ---------- helpers internes ----------

static inline uint32_t read_u16_le(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8);
}

static inline uint32_t read_u32_le(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

// conversion vers 4bpp selon le format source
static inline uint8_t pixel_1bpp(const uint8_t *buf, int32_t base, int32_t px) {
    return ((buf[base + (px >> 3)] >> (7 - (px & 7))) & 1) * 15;
}

static inline uint8_t pixel_4bpp(const uint8_t *buf, int32_t base, int32_t px) {
    uint8_t b = buf[base + (px >> 1)];
    return (px & 1) ? (b & 0x0F) : (b >> 4);
}

static inline uint8_t pixel_8bpp(const uint8_t *buf, int32_t base, int32_t px) {
    return buf[base + px] >> 4;
}

static inline uint8_t pixel_24bpp(const uint8_t *buf, int32_t base, int32_t px) {
    int32_t p = base + px * 3;
    // BMP BGR → luminance → 4bpp
    uint32_t gray = ((uint32_t)buf[p+2] * 299 +
                     (uint32_t)buf[p+1] * 587 +
                     (uint32_t)buf[p]   * 114) / 1000;
    return (uint8_t)(gray >> 4);
}

// écriture pixel dans le framebuffer 4bpp avec rotation
static void write_pixel(uint8_t *fb, int32_t hw_w, int32_t hw_h,
                        int32_t orientation, int32_t x, int32_t y, uint8_t color) {
    int32_t px, py;

    switch (orientation) {
        case 90:
            px = y;
            py = hw_h - 1 - x;
            break;
        case 180:
            px = hw_w - 1 - x;
            py = hw_h - 1 - y;
            break;
        case 270:
            px = hw_w - 1 - y;
            py = x;
            break;
        default: // 0
            px = x;
            py = y;
            break;
    }

    if (px < 0 || px >= hw_w || py < 0 || py >= hw_h)
        return;

    int32_t pos = (py * hw_w / 2) + (px / 2);
    if (px & 1)
        fb[pos] = (fb[pos] & 0xF0) | (color & 0x0F);
    else
        fb[pos] = (fb[pos] & 0x0F) | (color << 4);
}

// ---------- bmp_load(filepath) ----------
// charge le fichier BMP en mémoire C
// retourne un tuple (width, height, bpp)
STATIC mp_obj_t render_image_bmp_load(mp_obj_t filepath_obj) {
    const char *path = mp_obj_str_get_str(filepath_obj);

    // ouverture
    mp_obj_t open_args[2] = {
        filepath_obj,
        MP_OBJ_NEW_QSTR(MP_QSTR_rb)
    };
    mp_obj_t file = mp_call_function_n_kw(
        mp_load_global(MP_QSTR_open), 2, 0, open_args);

    // lecture complète
    mp_obj_t read_ret = mp_call_method_n_kw(0, 0,
        (mp_obj_t[]){file, MP_OBJ_NEW_QSTR(MP_QSTR_read)});
    mp_call_method_n_kw(0, 0,
        (mp_obj_t[]){file, MP_OBJ_NEW_QSTR(MP_QSTR_close)});

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(read_ret, &bufinfo, MP_BUFFER_READ);
    const uint8_t *data = (const uint8_t *)bufinfo.buf;
    size_t data_len = bufinfo.len;

    // vérifications
    if (data_len < 54 || data[0] != 'B' || data[1] != 'M')
        mp_raise_ValueError(MP_ERROR_TEXT("Not a BMP file"));

    uint32_t bpp = read_u16_le(data + 28);
    if (bpp != 1 && bpp != 2 && bpp != 4 && bpp != 8 && bpp != 24)
        mp_raise_ValueError(MP_ERROR_TEXT("Unsupported BMP bpp"));

    uint32_t compression = read_u32_le(data + 30);
    if (compression != 0)
        mp_raise_ValueError(MP_ERROR_TEXT("Compressed BMP not supported"));

    uint32_t width   = read_u32_le(data + 18);
    uint32_t height  = read_u32_le(data + 22);
    uint32_t offset  = read_u32_le(data + 10);

    uint32_t pixel_data_len = data_len - offset;

    // libère l'ancien buffer si présent
    if (bmp_buf != NULL) {
        free(bmp_buf);
        bmp_buf = NULL;
    }

    bmp_buf = (uint8_t *)malloc(pixel_data_len);
    if (bmp_buf == NULL)
        mp_raise_msg(&mp_type_MemoryError, MP_ERROR_TEXT("bmp_load: malloc failed"));

    memcpy(bmp_buf, data + offset, pixel_data_len);
    bmp_width  = (int32_t)width;
    bmp_height = (int32_t)height;
    bmp_bpp    = (int32_t)bpp;

    mp_obj_t tuple[3] = {
        mp_obj_new_int(bmp_width),
        mp_obj_new_int(bmp_height),
        mp_obj_new_int(bmp_bpp)
    };
    return mp_obj_new_tuple(3, tuple);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(render_image_bmp_load_obj, render_image_bmp_load);

// ---------- bmp_draw(fb, hw_w, hw_h, orientation, x, y, decallage) ----------
// dessine le BMP chargé dans le framebuffer Python
STATIC mp_obj_t render_image_bmp_draw(size_t n_args, const mp_obj_t *args) {
    if (bmp_buf == NULL)
        mp_raise_ValueError(MP_ERROR_TEXT("No BMP loaded, call bmp_load first"));

    // récupération du framebuffer Python (bytearray)
    mp_buffer_info_t fbinfo;
    mp_get_buffer_raise(args[0], &fbinfo, MP_BUFFER_WRITE);
    uint8_t *fb = (uint8_t *)fbinfo.buf;

    int32_t hw_w        = mp_obj_get_int(args[1]);
    int32_t hw_h        = mp_obj_get_int(args[2]);
    int32_t orientation = mp_obj_get_int(args[3]);
    int32_t x           = mp_obj_get_int(args[4]);
    int32_t y           = mp_obj_get_int(args[5]);
    int32_t decallage   = mp_obj_get_int(args[6]);

    // alignement ligne BMP : multiple de 4 octets
    int32_t row_bytes = (bmp_width * bmp_bpp + 31) / 32 * 4;

    for (int32_t py = 0; py < bmp_height; py++) {
        // BMP stocké de bas en haut → on inverse
        int32_t base = (bmp_height - 1) * row_bytes - py * row_bytes;

        for (int32_t px = 0; px < bmp_width; px++) {
            uint8_t c;
            switch (bmp_bpp) {
                case 1:  c = pixel_1bpp (bmp_buf, base, px); break;
                case 4:  c = pixel_4bpp (bmp_buf, base, px); break;
                case 8:  c = pixel_8bpp (bmp_buf, base, px); break;
                default: c = pixel_24bpp(bmp_buf, base, px); break;
            }
            write_pixel(fb, hw_w, hw_h, orientation,
                        x + px, y - decallage + py, c);
        }
    }

    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(render_image_bmp_draw_obj, 7, 7, render_image_bmp_draw);

// ---------- bmp_free() ----------
// libère le buffer interne (optionnel)
STATIC mp_obj_t render_image_bmp_free(void) {
    if (bmp_buf != NULL) {
        free(bmp_buf);
        bmp_buf = NULL;
    }
    bmp_width = bmp_height = bmp_bpp = 0;
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(render_image_bmp_free_obj, render_image_bmp_free);

// ---------- table des fonctions exportées ----------
STATIC const mp_rom_map_elem_t render_image_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_render_image) },
    { MP_ROM_QSTR(MP_QSTR_bmp_load), MP_ROM_PTR(&render_image_bmp_load_obj) },
    { MP_ROM_QSTR(MP_QSTR_bmp_draw), MP_ROM_PTR(&render_image_bmp_draw_obj) },
    { MP_ROM_QSTR(MP_QSTR_bmp_free), MP_ROM_PTR(&render_image_bmp_free_obj) },
};
STATIC MP_DEFINE_CONST_DICT(render_image_module_globals, render_image_module_globals_table);

const mp_obj_module_t render_image_module = {
    .base    = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&render_image_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_render_image, render_image_module);
