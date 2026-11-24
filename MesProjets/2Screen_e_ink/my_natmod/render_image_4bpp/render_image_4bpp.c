// render_image.c - natmod MicroPython dynamique (.mpy)
// ESP32S3 - MicroPython 1.28
// Buffer écran : 4bpp, 2 pixels par octet, nibble haut = pixel pair
// construction dune version en c natmod pour charger une image bmp vers une vers 4bpp d'un ecran.

#include "py/dynruntime.h"
#include <stdint.h>

// ---------- help ----------
static const char HELP_TEXT[] =
"render_glyph_4bpp\n"
"\n"
"Fonctions:\n"
"  set_context(buf,width,height,orientation) : mise en place des lien vers le buffer d'écran, avec les dimensions de ce dernier'\n"
"  set_orientation(int) : passe une orientation (0,90,180,270) les valeurs doivent être exacte \n"
"  get_orientation() : renvoie l'angle en cours, la largueur et hauteur logique \n"
"  get_size() : renvoie les bpp, largeur et hauteur de l'image \n"
"  load_bmp(chemin) : charge le fichier en mémoire pour le préparer au dessin \n"
"  draw_bmp(x,y,decallage en y) : dessine le bmp, le décallage permet de le centrer et agit uniquement sur y"
;

// ---------- contexte écran ----------
static uint8_t  *BUF;
static int32_t   HwWIDTH;
static int32_t   HwHEIGHT;
static int32_t   WIDTH ; // largeur logique (selon orientation)
static int32_t   HEIGHT; //  hauteur logique (selon orientation)
static int32_t   ORIENTATION;


// ---------- état interne ----------
static const uint8_t   *bmp_buf    = NULL;
static int32_t   bmp_width  = 0;
static int32_t   bmp_height = 0;
static int32_t   bmp_bpp    = 0;
static mp_obj_t  bmp_data_ref=MP_OBJ_NULL;

// ---------- helpers lecture little-endian ----------
static inline uint32_t ru16(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8);
}
static inline uint32_t ru32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
    ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

// ---------- conversion pixel vers 4bpp ----------
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
    uint32_t gray = ((uint32_t)buf[p+2] * 299 +
    (uint32_t)buf[p+1] * 587 +
    (uint32_t)buf[p]   * 114) / 1000;
    return (uint8_t)(gray >> 4);
}

// ---------- draw_pixel interne ----------
static void draw_pixel(int32_t x, int32_t y, uint8_t color) {
    int32_t px, py;
    switch (ORIENTATION) {
        case 90:
            px = y;
            py = HwHEIGHT - 1 - x;
            break;
        case 180:
            px = HwWIDTH - 1 - x;
            py = HwHEIGHT - 1 - y;
            break;
        case 270:
            px = HwWIDTH - 1 - y;
            py = x;
            break;
        default:
            px = x;
            py = y;
            break;
    }
    if (px < 0 || px >= HwWIDTH || py < 0 || py >= HwHEIGHT) return;
    int32_t pos = (py * HwWIDTH / 2) + (px / 2);
    if (px & 1)
        BUF[pos] = (BUF[pos] & 0xF0) | (color & 0x0F);
    else
        BUF[pos] = (BUF[pos] & 0x0F) | (color << 4);
}

// ========== fonctions exposées ==========

// ---------- set_context(BUF, HwWIDTH, HwHEIGHT) ----------
static mp_obj_t py_set_context(size_t n_args, const mp_obj_t *args) {
    mp_buffer_info_t fbinfo;
    mp_get_buffer_raise(args[0], &fbinfo, MP_BUFFER_WRITE);
    BUF      = (uint8_t *)fbinfo.buf;
    HwWIDTH  = mp_obj_get_int(args[1]);
    HwHEIGHT = mp_obj_get_int(args[2]);
    ORIENTATION= mp_obj_get_int(args[3]);
    WIDTH    = HwWIDTH; // mis à jour par set_orientation si besoin
    HEIGHT   =HwHEIGHT;

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

// ---------- get_size() → (bpp, w, h) ----------
static mp_obj_t py_get_size(void) {

    mp_obj_t tuple[3] = {
        mp_obj_new_int(bmp_bpp), mp_obj_new_int(bmp_width),
        mp_obj_new_int(bmp_height)
    };
    return mp_obj_new_tuple(3, tuple);
}
static MP_DEFINE_CONST_FUN_OBJ_0(get_size_obj, py_get_size);

// ---------- bmp_load(filepath) → (width, height, bpp) ----------
static mp_obj_t py_load_bmp(mp_obj_t filepath_obj) {

    // on charge directement le fichier depuis la mémoire flash uniquement
    //le temps de chargement est relativemnt long pour un fichier de 360kO il faut compter environ 1,7s mais uniquement 40ms de rendu sur le buffer de l'écran
    //le chargement est réaliser en appelant des fonction externe en micropython directement il peut erte interressant d'utiliser uen version différente en passant un dataarray directement

    // libère l'ancien
    bmp_data_ref = MP_OBJ_NULL;
    bmp_buf      = NULL;

    // gc.collect()
    mp_obj_t gc_mod = mp_import_name(MP_QSTR_gc, mp_const_none, MP_OBJ_NEW_SMALL_INT(0));
    mp_obj_t collect_fn = mp_load_attr(gc_mod, MP_QSTR_collect);
    mp_call_function_n_kw(collect_fn, 0, 0, NULL);

    // ouverture via l'API MicroPython
    mp_obj_t open_fn = mp_load_global(MP_QSTR_open);

    mp_obj_t open_args[2] = {
        filepath_obj,
        MP_OBJ_NEW_QSTR(MP_QSTR_rb)
    };

    mp_obj_t file = mp_call_function_n_kw(open_fn, 2, 0, open_args); //ici on appel la fonction "open" et on passe le chemin, et le mode rb via open argument

    // lecture complète du fichier
    mp_obj_t read_fn = mp_load_attr(file, MP_QSTR_read); // on lit le fichier
    mp_obj_t data_obj = mp_call_function_n_kw(read_fn, 0, 0, NULL); // et on récupère tous dans un objet data micropython. avantage est que il est gérer par le gc. et est donc détruit si on recharge une autre image.

    // fermeture du fichier
    mp_obj_t close_fn = mp_load_attr(file, MP_QSTR_close);
    mp_call_function_n_kw(close_fn, 0, 0, NULL);

    // fin d'ouverture

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(data_obj, &bufinfo, MP_BUFFER_READ);
    const uint8_t *data = (const uint8_t *)bufinfo.buf;
    size_t data_len = bufinfo.len;

    //on gère les défauts
    if (data_len < 54 || data[0] != 'B' || data[1] != 'M')
        mp_raise_ValueError(MP_ERROR_TEXT("Not a BMP file"));

    uint32_t file_bpp = ru16(data + 28);
    if (file_bpp != 1 && file_bpp != 2 && file_bpp != 4 &&
        file_bpp != 8 && file_bpp != 24)
        mp_raise_ValueError(MP_ERROR_TEXT("Unsupported BMP bpp"));

    if (ru32(data + 30) != 0)
        mp_raise_ValueError(MP_ERROR_TEXT("Compressed BMP not supported"));

    //on récupère les info et on les remet en mode normal
    uint32_t width  = ru32(data + 18);
    uint32_t height = ru32(data + 22);
    uint32_t offset = ru32(data + 10);

    // je passe un pointeur pour la partie du démarrage des data en enlevant la partie de l'entete'
    bmp_data_ref = data_obj;  // maintient le bytes vivant pour le GC
    bmp_buf = data + offset;

    bmp_width  = (int32_t)width;
    bmp_height = (int32_t)height;
    bmp_bpp    = (int32_t)file_bpp;

    return mp_const_none; // je renvoie les info utile. il servent pour l'essentiel au calcul de position qui lui est fait en externe et qu'il ne sert a rien d'intégrer via get_size
}
static MP_DEFINE_CONST_FUN_OBJ_1(load_bmp_obj, py_load_bmp);

// ---------- bmp_draw(fb, hw_w, hw_h, orientation, x, y, decallage) ----------
static mp_obj_t py_draw_bmp(size_t n_args, const mp_obj_t *args) {
    //ici on ecrit le bmp dans le buffer de destination, idéalement celui du driver, mais cela peut être un autre intermédiaire
    // on passe la postion, l'orientation par rapport a lcran et les dimension de l'ecran physique
    // on introduit une notion de décallage qui permet de faire une justification simple en rapide, fait en externe mais pratique

    int32_t x      = mp_obj_get_int(args[0]);
    int32_t y      = mp_obj_get_int(args[1]);
    int32_t dec    = mp_obj_get_int(args[2]);

    int32_t row_bytes = (bmp_width * bmp_bpp + 31) / 32 * 4;

    for (int32_t py = 0; py < bmp_height; py++) {
        int32_t base = (bmp_height - 1) * row_bytes - py * row_bytes;
        for (int32_t px = 0; px < bmp_width; px++) {
            uint8_t c;
            switch (bmp_bpp) {
                case 1:  c = pixel_1bpp (bmp_buf, base, px); break;
                case 4:  c = pixel_4bpp (bmp_buf, base, px); break;
                case 8:  c = pixel_8bpp (bmp_buf, base, px); break;
                default: c = pixel_24bpp(bmp_buf, base, px); break;
            }
            draw_pixel(x + px, y - dec + py, c);
        }
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(draw_bmp_obj, 3, 3, py_draw_bmp);

// ---------- help ----------
static mp_obj_t py_help(void) {
    return mp_obj_new_str(HELP_TEXT, strlen(HELP_TEXT));
}
static MP_DEFINE_CONST_FUN_OBJ_0(help_obj, py_help);

// ---------- point d'entrée natmod ----------
mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args) {
    MP_DYNRUNTIME_INIT_ENTRY
    mp_store_global(MP_QSTR_set_context,     MP_OBJ_FROM_PTR(&set_context_obj));
    mp_store_global(MP_QSTR_set_orientation, MP_OBJ_FROM_PTR(&set_orientation_obj));
    mp_store_global(MP_QSTR_get_orientation, MP_OBJ_FROM_PTR(&get_orientation_obj));
    mp_store_global(MP_QSTR_get_size,        MP_OBJ_FROM_PTR(&get_size_obj));
    mp_store_global(MP_QSTR_load_bmp,       MP_OBJ_FROM_PTR(&load_bmp_obj));
    mp_store_global(MP_QSTR_draw_bmp,       MP_OBJ_FROM_PTR(&draw_bmp_obj));
    mp_store_global(MP_QSTR_help,           MP_OBJ_FROM_PTR(&help_obj));
    MP_DYNRUNTIME_INIT_EXIT
}
