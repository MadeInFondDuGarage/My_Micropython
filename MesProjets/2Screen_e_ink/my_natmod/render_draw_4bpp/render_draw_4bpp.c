// render_draw_4bpp.c - natmod MicroPython dynamique (.mpy)
// ESP32S3 - MicroPython 1.28
// Primitives graphiques pour framebuffer 4bpp
// 2 pixels par octet, nibble haut = pixel pair, nibble bas = pixel impair

#include "py/dynruntime.h"
#include <stdint.h>

// ---------- help ----------
static const char HELP_TEXT[] =
"render_draw_4bpp\n"
"\n"
"Fonctions:\n"
"  set_context(buf,width,height,orientation) : mise en place des lien vers le buffer d'écran, avec les dimensions de ce dernier'\n"
"  set_orientation(int) : passe une orientation (0,90,180,270) les valeurs doivent être exacte \n"
"  get_orientation() : renvoie l'angle en cours, la largueur et hauteur logique \n"
"  draw_pixel(x,y,couleur) : dessine un pixel avec une couleur sur 16 niveaux de gris. 0=noir 15=blanc \n"
"  draw_line(x,y,x,y,couleur) : dessine une ligne \n"
"  draw_rect(x,y,w,h,couleur, plein) : dessine un rectangle et peut le remplir en couleur (0,1) \n"
"  draw_circle(x,y,r,couleur,plein) : dessine une cercle x,y est le centre, r le rayon, la couleur et le remplissage comme le reste \n"
"  draw_triangle(x1, y1, x2, y2, x3, y3, couleur, plein) : dessine une triangle \n";


// ---------- contexte écran ----------
static uint8_t  *BUF;
static int32_t   HwWIDTH;
static int32_t   HwHEIGHT;
static int32_t   WIDTH ; // largeur logique (selon orientation)
static int32_t   HEIGHT; //  hauteur logique (selon orientation)
static int32_t   ORIENTATION;

// ---------- set_context(BUF, HwWIDTH, HwHEIGHT) ----------
static mp_obj_t py_set_context(size_t n_args, const mp_obj_t *args) {
    mp_buffer_info_t fbinfo;
    mp_get_buffer_raise(args[0], &fbinfo, MP_BUFFER_WRITE);
    BUF      = (uint8_t *)fbinfo.buf;
    HwWIDTH  = mp_obj_get_int(args[1]);
    HwHEIGHT = mp_obj_get_int(args[2]);
    ORIENTATION = mp_obj_get_int(args[3]);
    HEIGHT = HwHEIGHT;
    WIDTH    = HwWIDTH; // mis à jour par set_orientation si besoin

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(set_context_obj, 4, 4, py_set_context);

// ---------- set_orientation(ORIENTATION) ----------
static mp_obj_t py_set_orientation(mp_obj_t ori_obj) {
    ORIENTATION = mp_obj_get_int(ori_obj);
    // WIDTH et HEIGHT = valeur logique après rotation, surtout utile en récupération pour calcul externe avec les référence de la rotation
    if(ORIENTATION > -1 && ORIENTATION < 90)
    {   ORIENTATION=0;
        WIDTH=HwWIDTH;
        HEIGHT=HwHEIGHT; }
        else if (ORIENTATION > 89 && ORIENTATION <180 )
        {   ORIENTATION= 90;
            WIDTH=HwHEIGHT;
            HEIGHT=HwWIDTH; }
            else if  (ORIENTATION > 179 && ORIENTATION < 269)
            {
                ORIENTATION=180;
                WIDTH=HwWIDTH;
                HEIGHT=HwHEIGHT; }
                else if (ORIENTATION > 269 && ORIENTATION < 360)
                {
                    ORIENTATION = 270;
                    WIDTH=HwHEIGHT;
                    HEIGHT=HwWIDTH; }
                    else {  ORIENTATION=0;
                        WIDTH=HwWIDTH;
                        HEIGHT=HwHEIGHT; }

                        // WIDTH = (ORIENTATION == 90 || ORIENTATION == 270) ? HwHEIGHT : HwWIDTH;
                        return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(set_orientation_obj, py_set_orientation);

// ---------- get_orientation() → (deg, w, h) ----------
static mp_obj_t py_get_orientation(void) {

    mp_obj_t tuple[3] = {
        mp_obj_new_int(ORIENTATION), mp_obj_new_int(WIDTH),
        mp_obj_new_int(HEIGHT)
    };
    return mp_obj_new_tuple(3, tuple);
}
static MP_DEFINE_CONST_FUN_OBJ_0(get_orientation_obj, py_get_orientation);

// ---------- draw_pixel : seul accès au framebuffer ----------
static void draw_pixel(int32_t x, int32_t y, uint8_t color) {
    int32_t px, py;
    switch (ORIENTATION) {
        case 90:  px = y;              py = HwHEIGHT - 1 - x; break;
        case 180: px = HwWIDTH - 1 - x; py = HwHEIGHT - 1 - y; break;
        case 270: px = HwWIDTH - 1 - y; py = x;                 break;
        default:  px = x;              py = y;                 break;
    }
    if (px < 0 || px >= HwWIDTH || py < 0 || py >= HwHEIGHT) return;
    int32_t pos = (py * HwWIDTH / 2) + (px / 2);
    if (px & 1)
        BUF[pos] = (BUF[pos] & 0xF0) | (color & 0x0F);
    else
        BUF[pos] = (BUF[pos] & 0x0F) | (color << 4);
}

// ---------- draw_pixel exposé Python ----------
// draw_pixel(x, y, color)
static mp_obj_t py_draw_pixel(size_t n_args, const mp_obj_t *args) {
    draw_pixel(mp_obj_get_int(args[0]),
               mp_obj_get_int(args[1]),
               (uint8_t)mp_obj_get_int(args[2]));
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(draw_pixel_obj, 3, 3, py_draw_pixel);

// ---------- Bresenham interne ----------
static void draw_line_internal(int32_t x1, int32_t y1, int32_t x2, int32_t y2, uint8_t color) {
    int32_t dx =  (x2 > x1 ? x2 - x1 : x1 - x2);
    int32_t dy = -(y2 > y1 ? y2 - y1 : y1 - y2);
    int32_t sx = x1 < x2 ? 1 : -1;
    int32_t sy = y1 < y2 ? 1 : -1;
    int32_t err = dx + dy;
    while (1) {
        draw_pixel(x1, y1, color);
        if (x1 == x2 && y1 == y2) break;
        int32_t e2 = 2 * err;
        if (e2 >= dy) { err += dy; x1 += sx; }
        if (e2 <= dx) { err += dx; y1 += sy; }
    }
}

// ---------- draw_line(x1, y1, x2, y2, color) ----------
static mp_obj_t py_draw_line(size_t n_args, const mp_obj_t *args) {
    draw_line_internal(mp_obj_get_int(args[0]), mp_obj_get_int(args[1]),
                       mp_obj_get_int(args[2]), mp_obj_get_int(args[3]),
                       (uint8_t)mp_obj_get_int(args[4]));
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(draw_line_obj, 5, 5, py_draw_line);

// ---------- draw_rect(x, y, w, h, color, fill) ----------
static mp_obj_t py_draw_rect(size_t n_args, const mp_obj_t *args) {
    int32_t x     = mp_obj_get_int(args[0]);
    int32_t y     = mp_obj_get_int(args[1]);
    int32_t w     = mp_obj_get_int(args[2]);
    int32_t h     = mp_obj_get_int(args[3]);
    uint8_t color = (uint8_t)mp_obj_get_int(args[4]);
    int32_t fill  = mp_obj_get_int(args[5]);

    if (fill) {
        for (int32_t row = y; row < y + h; row++)
            for (int32_t col = x; col < x + w; col++)
                draw_pixel(col, row, color);
    } else {
        for (int32_t col = x; col < x + w; col++) {
            draw_pixel(col, y,         color);
            draw_pixel(col, y + h - 1, color);
        }
        for (int32_t row = y + 1; row < y + h - 1; row++) {
            draw_pixel(x,         row, color);
            draw_pixel(x + w - 1, row, color);
        }
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(draw_rect_obj, 6, 6, py_draw_rect);

// ---------- draw_circle(cx, cy, r, color, fill) ----------
static mp_obj_t py_draw_circle(size_t n_args, const mp_obj_t *args) {
    int32_t cx    = mp_obj_get_int(args[0]);
    int32_t cy    = mp_obj_get_int(args[1]);
    int32_t r     = mp_obj_get_int(args[2]);
    uint8_t color = (uint8_t)mp_obj_get_int(args[3]);
    int32_t fill  = mp_obj_get_int(args[4]);

    int32_t px = r, py = 0, err = 1 - r;

    while (px >= py) {
        if (fill) {
            for (int32_t i = cx - px; i <= cx + px; i++) {
                draw_pixel(i, cy + py, color);
                draw_pixel(i, cy - py, color);
            }
            for (int32_t i = cx - py; i <= cx + py; i++) {
                draw_pixel(i, cy + px, color);
                draw_pixel(i, cy - px, color);
            }
        } else {
            draw_pixel(cx + px, cy + py, color);
            draw_pixel(cx - px, cy + py, color);
            draw_pixel(cx + px, cy - py, color);
            draw_pixel(cx - px, cy - py, color);
            draw_pixel(cx + py, cy + px, color);
            draw_pixel(cx - py, cy + px, color);
            draw_pixel(cx + py, cy - px, color);
            draw_pixel(cx - py, cy - px, color);
        }
        py++;
        if (err < 0) {
            err += 2 * py + 1;
        } else {
            px--;
            err += 2 * (py - px) + 1;
        }
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(draw_circle_obj, 5, 5, py_draw_circle);

// ---------- draw_triangle(x1,y1, x2,y2, x3,y3, color, fill) ----------
static mp_obj_t py_draw_triangle(size_t n_args, const mp_obj_t *args) {
    int32_t x1    = mp_obj_get_int(args[0]);
    int32_t y1    = mp_obj_get_int(args[1]);
    int32_t x2    = mp_obj_get_int(args[2]);
    int32_t y2    = mp_obj_get_int(args[3]);
    int32_t x3    = mp_obj_get_int(args[4]);
    int32_t y3    = mp_obj_get_int(args[5]);
    uint8_t color = (uint8_t)mp_obj_get_int(args[6]);
    int32_t fill  = mp_obj_get_int(args[7]);

    if (!fill) {
        draw_line_internal(x1, y1, x2, y2, color);
        draw_line_internal(x2, y2, x3, y3, color);
        draw_line_internal(x3, y3, x1, y1, color);
    } else {
        // tri des sommets par y croissant
        int32_t t;
        if (y1 > y2) { t=x1;x1=x2;x2=t; t=y1;y1=y2;y2=t; }
        if (y1 > y3) { t=x1;x1=x3;x3=t; t=y1;y1=y3;y3=t; }
        if (y2 > y3) { t=x2;x2=x3;x3=t; t=y2;y2=y3;y3=t; }

        int32_t total_h = y3 - y1;
        if (total_h == 0) return mp_const_none;

        for (int32_t row = y1; row <= y3; row++) {
            int32_t upper = (row < y2);
            int32_t seg_h = upper ? (y2 - y1) : (y3 - y2);
            if (seg_h == 0) continue;
            int32_t xa = x1 + (x3 - x1) * (row - y1) / total_h;
            int32_t xb = upper
                ? x1 + (x2 - x1) * (row - y1) / (y2 - y1)
                : x2 + (x3 - x2) * (row - y2) / (y3 - y2);
            if (xa > xb) { t = xa; xa = xb; xb = t; }
            for (int32_t col = xa; col <= xb; col++)
                draw_pixel(col, row, color);
        }
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(draw_triangle_obj, 8, 8, py_draw_triangle);

// ---------- help ----------
static mp_obj_t py_help(void) {
    return mp_obj_new_str(HELP_TEXT, strlen(HELP_TEXT));
}
static MP_DEFINE_CONST_FUN_OBJ_0(help_obj, py_help);

// ---------- point d'entrée natmod ----------
mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args) {
    MP_DYNRUNTIME_INIT_ENTRY
    mp_store_global(MP_QSTR_set_context,    MP_OBJ_FROM_PTR(&set_context_obj));
    mp_store_global(MP_QSTR_set_orientation,MP_OBJ_FROM_PTR(&set_orientation_obj));
    mp_store_global(MP_QSTR_get_orientation, MP_OBJ_FROM_PTR(&get_orientation_obj));
    mp_store_global(MP_QSTR_draw_pixel,     MP_OBJ_FROM_PTR(&draw_pixel_obj));
    mp_store_global(MP_QSTR_draw_line,      MP_OBJ_FROM_PTR(&draw_line_obj));
    mp_store_global(MP_QSTR_draw_rect,      MP_OBJ_FROM_PTR(&draw_rect_obj));
    mp_store_global(MP_QSTR_draw_circle,    MP_OBJ_FROM_PTR(&draw_circle_obj));
    mp_store_global(MP_QSTR_draw_triangle,  MP_OBJ_FROM_PTR(&draw_triangle_obj));
    mp_store_global(MP_QSTR_help,           MP_OBJ_FROM_PTR(&help_obj));
    MP_DYNRUNTIME_INIT_EXIT
}
