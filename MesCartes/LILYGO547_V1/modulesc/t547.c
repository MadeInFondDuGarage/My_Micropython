//
// Based on https://github.com/russhughes/lilygo_t547
// Patched for ESP32-S3 + LilyGo-EPD47 driver (https://github.com/Xinyuan-LilyGO/LilyGo-EPD47/tree/esp32s3)
// - Removed epd_highlevel / epd_internals dependencies
// - Removed rotation support (fixed landscape)
// - Removed back_fb / difference_fb / dirty_lines / waveform / lut
// - Fixed mp_obj_type_t API for MicroPython >= 1.20
// - Fixed mp_raise_ValueError API for MicroPython >= 1.20
// - EpdRect -> Rect_t
// - epd_draw_rect / epd_fill_rect signature updated
// - epd_fullclear -> epd_clear
// - epd_hl_update_area -> epd_draw_grayscale_image
//

#include <string.h>
#include <math.h>
#include "py/runtime.h"
#include "py/objstr.h"

#include "definition.h"
#include "epd_driver.h"
#include "t547.h"

//
// Method Implementations
//
extern const mp_obj_type_t t547_type;


Background_t screen_background= WHITE;

Rotation_t screen_rotation = 0;

// init()
static mp_obj_t t547_init(size_t n_args, const mp_obj_t *args) {
    epd_screen_init();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(t547_init_obj, 1, 2, t547_init);

// deinit()
static mp_obj_t t547_deinit(mp_obj_t self_in) {
    t547_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if (self->owns_fb && self->front_fb != NULL) {
        heap_caps_free(self->front_fb);  // libère seulement si on l'a alloué
        self->front_fb = NULL;
    }
    epd_screen_poweroff_all();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(t547_deinit_obj, t547_deinit);

// power(state)
static mp_obj_t t547_power(mp_obj_t self_in, mp_obj_t state) {
    if (mp_obj_is_true(state)) {
        epd_screen_poweron();
    } else {
        epd_screen_poweroff();
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_2(t547_power_obj, t547_power);

// width() - fixed landscape
static mp_obj_t t547_width(mp_obj_t self_in) {
    return mp_obj_new_int(EPD_WIDTH);
}
static MP_DEFINE_CONST_FUN_OBJ_1(t547_width_obj, t547_width);

// height() - fixed landscape
static mp_obj_t t547_height(mp_obj_t self_in) {
    return mp_obj_new_int(EPD_HEIGHT);
}
static MP_DEFINE_CONST_FUN_OBJ_1(t547_height_obj, t547_height);

// push(time, color)
static mp_obj_t t547_push(size_t n_args, const mp_obj_t *args) {
    int time  = mp_obj_get_int(args[1]);
    int color = mp_obj_get_int(args[2]);
    epd_screen_push_pixels(epd_full_screen(), time, color);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(t547_push_obj, 1, 3, t547_push);

// copy_bitmap(x, y, width, height,bitmap,)
static mp_obj_t t547_copy_bitmap(size_t n_args, const mp_obj_t *args) {
    t547_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    mp_buffer_info_t bitmap_info;
    mp_get_buffer_raise(args[5], &bitmap_info, MP_BUFFER_READ);

    Rect_t area = {
        .x      = mp_obj_get_int(args[1]),
        .y      = mp_obj_get_int(args[2]),
        .width  = mp_obj_get_int(args[3]),
        .height = mp_obj_get_int(args[4]),
    };

    epd_copy_to_screenbuffer(area, bitmap_info.buf, self->front_fb);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(t547_copy_bitmap_obj, 6, 6, t547_copy_bitmap);


// clean, nettoie en blanc ou en noir une zone au choix, on peut aussi mettre le buffer sur la même zone
static mp_obj_t t547_clean(size_t n_args, const mp_obj_t *args) {
    t547_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    Rect_t area = {0, 0, EPD_WIDTH, EPD_HEIGHT};

    if (n_args == 7 ) { //sinon il y a la couleur en plus
        area.x      = mp_obj_get_int(args[1]);
        area.y      = mp_obj_get_int(args[2]);
        area.width  = mp_obj_get_int(args[3]);
        area.height = mp_obj_get_int(args[4]);
        uint8_t color= mp_obj_get_int(args[5]);

        if ( mp_obj_get_int(args[6])==0 || mp_obj_get_int(args[6])==2) //0 j'ai que l'écran, 2 les 2
            {
                epd_screen_poweron(); //ici je clean l'écran'
                for(int32_t y =0;y<5;y++)
                {
                        {epd_screen_push_pixels(area,200,1);} //je ne fait que du blanc sur l écran car un buffer ne peut pas faire le blanc si c est en noir.
                }
                epd_screen_poweroff();
            }

        if ( mp_obj_get_int(args[6])==1 || mp_obj_get_int(args[6])==2) //ici je nettoie la même zone sur le buffer, si j'ai 1 le buffer, 2 les deux
            {
                epd_buf_clean(area,color,self->front_fb);
            }

    }

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(t547_clean_obj, 1, 7, t547_clean);

// clear()
static mp_obj_t t547_clear(size_t n_args, const mp_obj_t *args) {
    //j'efface l'écran. uniquement pour rafraichir au besoin
    Rect_t area = {0, 0, EPD_WIDTH, EPD_HEIGHT};
    Rect_t full_screen = {0, 0, EPD_WIDTH, EPD_HEIGHT};
    if (n_args == 5) {
        area.x      = mp_obj_get_int(args[1]);
        area.y      = mp_obj_get_int(args[2]);
        area.width  = mp_obj_get_int(args[3]);
        area.height = mp_obj_get_int(args[4]);
    }

    if (area.x == full_screen.x && area.y == full_screen.y &&
        area.width == full_screen.width && area.height == full_screen.height)
        {
        Rotation_t deg = screen_rotation;
        screen_rotation=0;
        epd_screen_poweron();
        epd_screen_clear_area(area);
        epd_screen_poweroff();
        screen_rotation=deg;
        }
    else
        {
        epd_screen_poweron();
        epd_screen_clear_area(area);
        epd_screen_poweroff();
        }

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(t547_clear_obj, 1, 6, t547_clear);

// show([x, y, w, h])
// draw_mode parameter kept for API compatibility but ignored
// epd_draw_grayscale_image does not support partial modes
static mp_obj_t t547_show(size_t n_args, const mp_obj_t *args) {
    t547_obj_t *self = MP_OBJ_TO_PTR(args[0]);

    if (n_args > 1 && !mp_obj_is_integer(args[1])) {
        mp_raise_ValueError(MP_ERROR_TEXT("Invalid mode"));
    }

    Rect_t area = {0, 0, EPD_WIDTH, EPD_HEIGHT};
    if (n_args == 5) {
        area.x      = mp_obj_get_int(args[1]);
        area.y      = mp_obj_get_int(args[2]);
        area.width  = mp_obj_get_int(args[3]);
        area.height = mp_obj_get_int(args[4]);
    }
    epd_screen_poweron();
    epd_screen_print(area, self->front_fb, BLACK_ON_WHITE);
    epd_screen_poweroff();

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(t547_show_obj, 1, 6, t547_show);


static mp_obj_t t547_get_buffer(mp_obj_t self_in) { //Ce memoryview pointe directement sur front_fb sans que le GC le scanne, car items ne lui appartient pas. sinon cela entraine trop de lenteur sur le rpl entr autre
    t547_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_obj_array_t *ar = m_new_obj(mp_obj_array_t);
    ar->base.type = &mp_type_memoryview;
    ar->typecode = 'B' | MP_OBJ_ARRAY_TYPECODE_FLAG_RW;
    ar->free = 0;
    ar->len = EPD_WIDTH / 2 * EPD_HEIGHT;
    ar->items = self->front_fb;
    return MP_OBJ_FROM_PTR(ar);
}
static MP_DEFINE_CONST_FUN_OBJ_1(t547_get_buffer_obj, t547_get_buffer);


static mp_obj_t t547_orientation(mp_obj_t self_in,mp_obj_t rotation) {
    screen_rotation = mp_obj_get_int(rotation);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_2(t547_orientation_obj, t547_orientation);

static mp_obj_t t547_get_orientation(mp_obj_t self_in) {
    return mp_obj_new_int(screen_rotation);
}
static MP_DEFINE_CONST_FUN_OBJ_1(t547_get_orientation_obj, t547_get_orientation);

//
// Module
//

static const mp_rom_map_elem_t t547_locals_dict_table[] = {
    {MP_ROM_QSTR(MP_QSTR_init),          MP_ROM_PTR(&t547_init_obj)},
    {MP_ROM_QSTR(MP_QSTR_deinit),        MP_ROM_PTR(&t547_deinit_obj)},
    {MP_ROM_QSTR(MP_QSTR_power),         MP_ROM_PTR(&t547_power_obj)},
    {MP_ROM_QSTR(MP_QSTR_width),         MP_ROM_PTR(&t547_width_obj)},
    {MP_ROM_QSTR(MP_QSTR_height),        MP_ROM_PTR(&t547_height_obj)},
    {MP_ROM_QSTR(MP_QSTR_push),          MP_ROM_PTR(&t547_push_obj)},
    {MP_ROM_QSTR(MP_QSTR_copy_bitmap),   MP_ROM_PTR(&t547_copy_bitmap_obj)},
    {MP_ROM_QSTR(MP_QSTR_clean),         MP_ROM_PTR(&t547_clean_obj)},
    {MP_ROM_QSTR(MP_QSTR_clear),         MP_ROM_PTR(&t547_clear_obj)},
    {MP_ROM_QSTR(MP_QSTR_show),          MP_ROM_PTR(&t547_show_obj)},
    {MP_ROM_QSTR(MP_QSTR_get_buffer),    MP_ROM_PTR(&t547_get_buffer_obj)},
    {MP_ROM_QSTR(MP_QSTR_orientation),    MP_ROM_PTR(&t547_orientation_obj)},
    {MP_ROM_QSTR(MP_QSTR_get_orientation),    MP_ROM_PTR(&t547_get_orientation_obj)},

    {MP_ROM_QSTR(MP_QSTR_BLACK),          MP_ROM_INT(BLACK)},
    {MP_ROM_QSTR(MP_QSTR_WHITE),         MP_ROM_INT(WHITE)},

    {MP_ROM_QSTR(MP_QSTR_SCREEN_BUFFER), MP_ROM_INT(2)},

};
static MP_DEFINE_CONST_DICT(t547_locals_dict, t547_locals_dict_table);

static void t547_print(const mp_print_t *print, mp_obj_t self_in, mp_print_kind_t kind) {
    (void) kind;
    mp_printf(print, "<t547>");
}

mp_obj_t t547_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    mp_arg_check_num(n_args, n_kw, 0, 1, false);
    //version acceptant un buffer externe plus simple pour du débug notament. permet aussi si besoin d'init via un buffer interne si rien n'st passer.
    //on peut aussi récupérr le buffer interne via get_buffer.

    const int fb_size = EPD_WIDTH / 2 * EPD_HEIGHT;
    t547_obj_t *self  = m_new_obj(t547_obj_t);
    self->base.type   = &t547_type;
    self->owns_fb     = false;

    if (n_args == 1) {
        mp_buffer_info_t bufinfo;
        mp_get_buffer_raise(all_args[0], &bufinfo, MP_BUFFER_RW);
        if (bufinfo.len < fb_size)
            mp_raise_ValueError(MP_ERROR_TEXT("buffer too small"));
        self->front_fb = bufinfo.buf;
    } else {
        self->front_fb = heap_caps_malloc(fb_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (self->front_fb == NULL)
            mp_raise_msg(&mp_type_MemoryError, MP_ERROR_TEXT("out of memory"));
        self->owns_fb = true;
        memset(self->front_fb, 0xFF, fb_size);
    }

    return MP_OBJ_FROM_PTR(self);
}

MP_DEFINE_CONST_OBJ_TYPE(
    t547_type,
    MP_QSTR_t547,
    MP_TYPE_FLAG_NONE,
    print, t547_print,
    make_new, t547_make_new,
    locals_dict, &t547_locals_dict
);

static const mp_rom_map_elem_t t547_module_globals_table[] = {
    {MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_t547)},
    {MP_ROM_QSTR(MP_QSTR_T547),     (mp_obj_t) &t547_type},
};
static MP_DEFINE_CONST_DICT(t547_module_globals, t547_module_globals_table);

const mp_obj_module_t t547_user_cmodule = {
    .base    = {&mp_type_module},
    .globals = (mp_obj_dict_t *) &t547_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_t547, t547_user_cmodule);
