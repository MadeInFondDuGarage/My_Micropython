// render_glyph_4bpp.c - natmod MicroPython dynamique (.mpy)
// ESP32S3 - MicroPython 1.28
// Rendu texte Hershey (segments) vers framebuffer 4bpp
// Structure et noms calqués sur renderdisplay.py

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
"  set_font_size(int) : passe la taille de la font en pixel\n"
"  set_titre(int) : passe le type de titre de 1 a 6, augmente la taille, 1 est le plus gros comme sur les traitement de texte\n"
"  set_font('font/mafont.bin') : passe un .bin compatible construit avec les extension inkscape. il s'agit de la string du nom avec le chemin'\n"
"  draw_text('text',x,y,couleur(int),background couleur(int),justif(int), centrage vertical(int)): passe le texte, sa position, la couleur en 4bpp, couleur d'arrière plan 0,16 4bpp, si -1 n'éfface pas le buffer avant,justif=0(Gauche),1(centrer),2(droite),3(Libre), vertical=0(haut),1(centre),2(bas)\n"
"  get_zone() : renvoie un tupple avec les infos de position x,y du début du texte et largeur, hauteur.\n";

// ---------- contexte écran ----------
static uint8_t  *BUF;
static int32_t   HwWIDTH;
static int32_t   HwHEIGHT;
static int32_t   WIDTH ; // largeur logique (selon orientation)
static int32_t   HEIGHT; //  hauteur logique (selon orientation)
static int32_t   ORIENTATION;

// ---------- état texte ----------
static int32_t   X;
static int32_t   Y;
static int32_t   FONT_SIZE;
static int32_t   SCALE; // Q8.8
static float     TITRE;
static int32_t   FONT_UNITS_HEIGHT;

// texte parsé
#define MAX_TEXT_LEN 256
typedef struct { uint16_t codepoint; uint8_t style; } parsed_char_t;
static parsed_char_t PARSED_TEXT[MAX_TEXT_LEN];
static int32_t       PARSED_LEN;

// ---------- font en mémoire ----------
static mp_obj_t       font_data_ref = MP_OBJ_NULL;
static const uint8_t *font_data;
static uint16_t       glyph_count;
static int16_t        ascent;
static int16_t        descent;

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

// ---------- draw_line interne (Bresenham) ----------
static void draw_line(int32_t x1, int32_t y1, int32_t x2, int32_t y2, uint8_t color) {
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

// ---------- scale Q8.8 ----------
static inline int32_t scale_coord(int32_t v, int32_t scale_q8) {
    return (v * scale_q8) >> 8;
}
static inline int32_t _compute_scale(int32_t font_size_px) {
    return (font_size_px << 8) / FONT_UNITS_HEIGHT;
}

// ---------- lecture int8 signé dans font_data ----------
static inline int32_t read_s8(uint32_t offset) {
    uint8_t v = font_data[offset];
    return v > 127 ? v - 256 : v;
}

// ---------- recherche offset d'un codepoint dans l'index ----------
static uint32_t find_glyph_offset(uint16_t codepoint) {
    for (uint16_t i = 0; i < glyph_count; i++) {
        uint32_t base = 6 + i * 6;
        uint16_t code = font_data[base] | (font_data[base+1] << 8);
        if (code == codepoint)
            return font_data[base+2] | (font_data[base+3] << 8) |
                   ((uint32_t)font_data[base+4] << 16) | ((uint32_t)font_data[base+5] << 24);
    }
    return 0;
}

// ---------- _parse_styled interne ----------
static void _parse_styled(const char *text, int32_t len) {
    PARSED_LEN = 0;
    uint8_t style = 0;
    int32_t i = 0;
    while (i < len && PARSED_LEN < MAX_TEXT_LEN) {
        uint8_t b0 = (uint8_t)text[i];
        uint16_t cp;
        int32_t char_len;

        if (b0 < 0x80) {
            cp = b0; char_len = 1;
        } else if ((b0 & 0xE0) == 0xC0 && i+1 < len) {
            cp = ((b0 & 0x1F) << 6) | ((uint8_t)text[i+1] & 0x3F);
            char_len = 2;
        } else if ((b0 & 0xF0) == 0xE0 && i+2 < len) {
            cp = ((b0 & 0x0F) << 12) | (((uint8_t)text[i+1] & 0x3F) << 6) | ((uint8_t)text[i+2] & 0x3F);
            char_len = 3;
        } else {
            cp = b0; char_len = 1;
        }

        if (cp == '<') {
            int32_t end = i + 1;
            while (end < len && text[end] != '>') end++;
            if (end >= len) {
                PARSED_TEXT[PARSED_LEN].codepoint = (uint16_t)text[i];
                PARSED_TEXT[PARSED_LEN].style = style;
                PARSED_LEN++; continue;
            }
            char tag[16];
            int32_t tlen = end - i - 1;
            if (tlen > 15) tlen = 15;
            for (int32_t k = 0; k < tlen; k++) {
                char c = text[i+1+k];
                tag[k] = (c >= 'A' && c <= 'Z') ? c + 32 : c;
            }
            tag[tlen] = 0;
            if      ((tag[0]=='b' && tlen==1) ||
                     (tlen==6 && tag[0]=='s'))   style |=  1; // b, strong
            else if ((tag[0]=='i' && tlen==1) ||
                     (tlen==2 && tag[0]=='e'))   style |=  2; // i, em
            else if (tag[0]=='/' && tag[1]=='b') style &= ~1; // /b, /strong
            else if (tag[0]=='/' && tag[1]=='i') style &= ~2; // /i, /em
            i = end + 1;
        } else {
            PARSED_TEXT[PARSED_LEN].codepoint = cp;
            PARSED_TEXT[PARSED_LEN].style = style;
            PARSED_LEN++;
            i += char_len;
        }
    }
}

//---- max -----
static int32_t max(int32_t a, int32_t b) {
    int32_t max;
    if (a>b){max=a;}
    else {max=b;}

    return max;
}
//---- min -----
static int32_t min(int32_t a, int32_t b) {
    int32_t min;
    if (a<b){min=a;}
    else {min=b;}

    return min;
}
// ---------- get_zone interne (sans arguments, utilise X, Y, SCALE) ----------
static void _get_zone(int32_t *out_x, int32_t *out_y, int32_t *out_w, int32_t *out_h) {
    int32_t min_y = 0, max_y = 0;
    int32_t cx = X;
    int32_t advance = 0;

    for (int32_t i = 0; i < PARSED_LEN; i++) {
        uint32_t offset = find_glyph_offset(PARSED_TEXT[i].codepoint);
        if (offset == 0) { cx += FONT_SIZE / 3; continue; }

        advance         = font_data[offset];
        int32_t seg_count = font_data[offset + 1];

        for (int32_t s = 0; s < seg_count; s++) {
            int32_t b  = offset + 2 + s * 4;
            int32_t Y1 = scale_coord(read_s8(b + 1), SCALE);
            int32_t Y2 = scale_coord(read_s8(b + 3), SCALE);
            if (Y1 > max_y || Y2 > max_y)
                {max_y = max(Y1,Y2);}
            if (Y1 < min_y || Y2 < min_y)
                {min_y=min(Y1,Y2);}
        }
        cx += scale_coord(advance, SCALE);
    }

    *out_x = X;
    *out_y = Y - 2 - max_y;
    *out_w = (cx + scale_coord(advance, SCALE)) - X;
    *out_h = max(max_y,min_y) - min(max_y,min_y) + 4;
}

// ========== fonctions exposées ==========

// ---------- set_context(BUF, HwWIDTH, HwHEIGHT) ----------
static mp_obj_t py_set_context(size_t n_args, const mp_obj_t *args) {
    mp_buffer_info_t fbinfo;
    mp_get_buffer_raise(args[0], &fbinfo, MP_BUFFER_WRITE);
    BUF      = (uint8_t *)fbinfo.buf;
    HwWIDTH  = mp_obj_get_int(args[1]);
    HwHEIGHT = mp_obj_get_int(args[2]);
    ORIENTATION = mp_obj_get_int(args[3]);
    WIDTH    = HwWIDTH; // mis à jour par set_orientation si besoin

    // ---------- init des variable ---------- obligatoire en natmod a faire dans un void, décalration simple en tete
    X           = 0;
    Y           = 0;
    FONT_SIZE   = 30;
    SCALE       = 256; // Q8.8
    TITRE       = 1.0f;
    FONT_UNITS_HEIGHT = 120;

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

// ---------- glyph_load(filepath) ----------
static mp_obj_t py_set_font(mp_obj_t filepath_obj) {
    mp_obj_t open_fn = mp_load_global(MP_QSTR_open);
    mp_obj_t open_args[2] = { filepath_obj, MP_OBJ_NEW_QSTR(MP_QSTR_rb) };
    mp_obj_t file = mp_call_function_n_kw(open_fn, 2, 0, open_args);

    mp_obj_t read_fn = mp_load_attr(file, MP_QSTR_read);
    mp_obj_t data_obj = mp_call_function_n_kw(read_fn, 0, 0, NULL);

    mp_obj_t close_fn = mp_load_attr(file, MP_QSTR_close);
    mp_call_function_n_kw(close_fn, 0, 0, NULL);

    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(data_obj, &bufinfo, MP_BUFFER_READ);

    if (bufinfo.len < 6)
        mp_raise_ValueError(MP_ERROR_TEXT("Font data too short"));

    //---version C de  read_header ---
    // libère l'ancien avant de charger le nouveau
    font_data_ref = MP_OBJ_NULL;
    font_data     = NULL;

    // appel gc.collect()
    mp_obj_t gc_mod = mp_import_name(MP_QSTR_gc, mp_const_none, MP_OBJ_NEW_SMALL_INT(0));
    mp_obj_t collect_fn = mp_load_attr(gc_mod, MP_QSTR_collect);
    mp_call_function_n_kw(collect_fn, 0, 0, NULL);

    // puis charger le nouveau
    font_data_ref = data_obj;
    font_data     = (const uint8_t *)bufinfo.buf;
    glyph_count   = font_data[0] | (font_data[1] << 8);
    ascent        = (int16_t)(font_data[2] | (font_data[3] << 8));
    descent       = (int16_t)(font_data[4] | (font_data[5] << 8));


    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(set_font_obj, py_set_font);


// ---------- get_zone() → (x, y, w, h) ----------
static mp_obj_t py_get_zone(void) {
    if (font_data == NULL)
        mp_raise_ValueError(MP_ERROR_TEXT("No font loaded"));
    int32_t zx, zy, zw, zh;
    _get_zone(&zx, &zy, &zw, &zh);
    mp_obj_t tuple[4] = {
        mp_obj_new_int(zx), mp_obj_new_int(zy),
        mp_obj_new_int(zw), mp_obj_new_int(zh)
    };
    return mp_obj_new_tuple(4, tuple);
}
static MP_DEFINE_CONST_FUN_OBJ_0(get_zone_obj, py_get_zone);

// ---------- draw_text(x, y, color, backcolor, justif, centre) ----------
// justif : 0=L, 1=G, 2=D, 3=C
// centre : 0=H, 1=C
static mp_obj_t py_draw_text(size_t n_args, const mp_obj_t *args) {
    if (font_data == NULL)
        mp_raise_ValueError(MP_ERROR_TEXT("No font loaded"));

    size_t len;

    const char *text   = mp_obj_str_get_data(args[0], &len);
    int32_t x          = mp_obj_get_int(args[1]);
    int32_t y          = mp_obj_get_int(args[2]);
    uint8_t color      = (uint8_t)mp_obj_get_int(args[3]);
    int32_t backcolor  = mp_obj_get_int(args[4]);
    int32_t justif     = mp_obj_get_int(args[5]); // 0=G,1=C,2=D,3=L
    int32_t centre     = mp_obj_get_int(args[6]); // 0=H,1=C,2=B

    _parse_styled(text, (int32_t)len);

    // calcul SCALE depuis font_size * TITRE (identique à _compute_scale Python)
    SCALE     = _compute_scale((int32_t)(FONT_SIZE * TITRE));

    // position initiale pour get_zone
    X = x;
    Y = y;

    // justification
    int32_t zx, zy, zw, zh;
    _get_zone(&zx, &zy, &zw, &zh);

    if (justif == 0)      x = 5;
    else if (justif == 2) x = WIDTH - zw;
    else if (justif == 1) x = WIDTH / 2 - zw / 2;

    // centrage vertical
    if (centre == 0)      y = y + zh + 2;
    else if (centre == 1) y = y + zh / 2;

    X = x;
    Y = y;

    // nettoyage arrière-plan (_clean Python)
    if (backcolor > -1) {
        _get_zone(&zx, &zy, &zw, &zh);
        uint8_t bgc = (uint8_t)backcolor;
        for (int32_t h = 0; h < zh; h++)
            draw_line(zx, zy + h, zx + zw, zy + h, bgc);
    }

    // rendu — calqué sur draw_text Python
    int32_t cx = x;
    for (int32_t i = 0; i < PARSED_LEN; i++) {
        uint32_t offset = find_glyph_offset(PARSED_TEXT[i].codepoint);
        if (offset == 0) { cx += FONT_SIZE / 3; continue; }

        int32_t advance   = font_data[offset];
        int32_t seg_count = font_data[offset + 1];
        uint8_t style     = PARSED_TEXT[i].style;

        int32_t gras_max = (style & 1) ? 3 : 1;

        for (int32_t s = 0; s < seg_count; s++) {
            int32_t b  = offset + 2 + s * 4;
            int32_t x1 = read_s8(b);
            int32_t y1 = read_s8(b + 1);
            int32_t x2 = read_s8(b + 2);
            int32_t y2 = read_s8(b + 3);

            int32_t style_ligne_1 = (style & 2) ? scale_coord(y1, SCALE) / 3 : 0;
            int32_t style_ligne_2 = (style & 2) ? scale_coord(y2, SCALE) / 3 : 0;

            for (int32_t gras = 0; gras < gras_max; gras++) {
                draw_line(
                    cx + gras + style_ligne_1 + scale_coord(x1, SCALE),
                    y  - scale_coord(y1, SCALE),
                    cx + gras + style_ligne_2 + scale_coord(x2, SCALE),
                    y  - scale_coord(y2, SCALE),
                    color
                );
            }
        }
        cx += scale_coord(advance, SCALE);
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(draw_text_obj, 7, 7, py_draw_text);

// ---------- set_font_size(font_size_px) ----------
static mp_obj_t py_set_font_size(mp_obj_t fs_obj) {
    FONT_SIZE = mp_obj_get_int(fs_obj);
    SCALE     = _compute_scale(FONT_SIZE);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(set_font_size_obj, py_set_font_size);

// ---------- set_titre(niveau) ----------
// ratio identique au Python : 0=1.0, 1=2.0, 2=1.9, 3=1.7, 4=1.5, 5=1.3, 6=1.2
static mp_obj_t py_set_titre(mp_obj_t t_obj) {
    static const int32_t ratio_q8[8] = {256,512,486,435,384,333,307,256};
    int32_t t = mp_obj_get_int(t_obj);
    if (t < 0 || t > 6) t = 0;
    // on stocke TITRE comme Q8.8 entier pour éviter le float
    TITRE = ratio_q8[t] / 256.0f;
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(set_titre_obj, py_set_titre);

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
    mp_store_global(MP_QSTR_set_font,      MP_OBJ_FROM_PTR(&set_font_obj));
    mp_store_global(MP_QSTR_get_zone,        MP_OBJ_FROM_PTR(&get_zone_obj));
    mp_store_global(MP_QSTR_draw_text,       MP_OBJ_FROM_PTR(&draw_text_obj));
    mp_store_global(MP_QSTR_set_font_size,   MP_OBJ_FROM_PTR(&set_font_size_obj));
    mp_store_global(MP_QSTR_set_titre,       MP_OBJ_FROM_PTR(&set_titre_obj));
    mp_store_global(MP_QSTR_help,           MP_OBJ_FROM_PTR(&help_obj));
    MP_DYNRUNTIME_INIT_EXIT
}
