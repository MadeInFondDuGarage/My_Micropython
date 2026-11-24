// Driver waveform (16 niveaux de gris, 15 frames) en natmod.
// Ne connait que la table d'ABI du HAL (epd_abi.h). Aucun appel ESP-IDF direct.

#include "py/dynruntime.h"
#include "epd_abi.h"

#define EPD_WIDTH  960
#define EPD_HEIGHT 540

typedef enum {
    BLACK_ON_WHITE = 1 << 0,
    WHITE_ON_WHITE = 1 << 1,
    WHITE_ON_BLACK = 1 << 2,
} DrawMode_t;

typedef struct { int32_t x, y, width, height; } Rect_t;

// ---------- help ----------
static const char HELP_TEXT[] =
"render_draw_4bpp\n"
"\n"
"Fonctions:\n"
"  init() initialise le driver, nécéssite le conneteur du hal de l'écran :init(screen.get_connector())\n"
"  deinit() libère la mémoire lier au table LUT de lécran, et eteint l'écran. l'écran, hal, reste actif pour monter un autre drivers par exemple \n"
"  get_context() renvoie les infos du buffer, de la largeur et hauteur physique de l'écran et de l'orientation initial) \n"
"  show() affiche le buffer, passer par le hal via le connecteur, ou par un buffer externe passer au hal. \n"
"  show([x,y,h,w][mode]) en options, on peut passer la zone a afficher, et aussi le mode, black_on_white, white_on_black \n"
"  width() renvoie la largeur, tiens compte de l'orientation passer \n"
"  height() renvoie la hauteur, tiens compte de l'orientation passer \n"
"  clean_screen([x,y,w,h]) nettoie l'écran le x,y,w,h sont en options pour une zone préçise\n"
"  clean_buffer([x,y,w,h][color]) nettoie le buffer, le x,y,w,h sont en options pour une zone préçise, la couleur pour l'arrière plan, si vide tous le buffer est remis sur blanc \n"
"  set_orientation() définie en degres la rotation de l'écran 0,90,180,260 \n"
"  get_orientation() récupère l'orientation actuel de l'écran\n"
"Option:\n"
"  push(time_us, color [, x, y, w, h]) ecrit un pixel directement sur l'écran sans passer par le buffer, ncéssite une durée et un couleur. la taille est une options. \n"
"Options special tuning:\n"
"  set_contrast(durees [, white]) : passe une table de constraste pour ajuster le rendu, 15 valeurs (en 1/10 us par ligne), 1..65535. white=True: table WHITE_ON_BLACK sinon on passe le noir \n"
"  get_contrast([ white]) : renvoie la table de constraste, si white = True (get_contrst(True) ) renvoie la table pour le blanc \n";

/* libc minimale : dynruntime 1.28.0 ne fournit plus memset/memcpy.
 * "no-tree-loop-distribute-patterns" empêche GCC de retransformer ces boucles en appel à memset/memcpy. */
#define NOPAT __attribute__((optimize("no-tree-loop-distribute-patterns")))

NOPAT void *memset(void *s, int c, size_t n)
{
    uint8_t *p = (uint8_t *)s;
    uint8_t b = (uint8_t)c;
    while (n && ((uintptr_t)p & 3)) { *p++ = b; n--; }
    uint32_t w = (uint32_t)b * 0x01010101u;
    uint32_t *q = (uint32_t *)p;
    while (n >= 4) { *q++ = w; n -= 4; }
    p = (uint8_t *)q;
    while (n--) { *p++ = b; }
    return s;
}

NOPAT void *memcpy(void *d, const void *s, size_t n)
{
    uint8_t *dp = (uint8_t *)d;
    const uint8_t *sp = (const uint8_t *)s;
    if ((((uintptr_t)dp | (uintptr_t)sp) & 3) == 0) {
        uint32_t *dq = (uint32_t *)dp;
        const uint32_t *sq = (const uint32_t *)sp;
        while (n >= 4) { *dq++ = *sq++; n -= 4; }
        dp = (uint8_t *)dq;
        sp = (const uint8_t *)sq;
    }
    while (n--) { *dp++ = *sp++; }
    return d;
}

NOPAT void *memmove(void *d, const void *s, size_t n)
{
    uint8_t *dp = (uint8_t *)d;
    const uint8_t *sp = (const uint8_t *)s;
    if (dp <= sp || dp >= sp + n) {
        while (n--) { *dp++ = *sp++; }
    } else {
        dp += n; sp += n;
        while (n--) { *--dp = *--sp; }
    }
    return d;
}

/* état du module (.bss) */
static const epd_abi_t *hal;
static uint8_t *conversion_lut;
static int32_t rotation;   // détenue par le driver, poussée au HAL
static uint16_t contrast_dark[15];   // durées actives (modifiables a l'exécution), init depuis les défauts
static uint16_t contrast_white[15];

/* 4bpp Contrast cycles in order of contrast (Darkest first). */
static const int32_t contrast_cycles_4[15]       = {12, 12, 8, 8, 12, 12, 12, 16, 16, 20, 20, 20, 40, 80, 120};
static const int32_t contrast_cycles_4_white[15] = {12, 12, 8, 8, 12, 12, 12, 16, 16, 20, 20, 20, 40, 80, 120};//{10, 10, 8, 8, 8, 8, 8, 10, 10, 15, 15, 20, 20, 100, 300};

static inline uint32_t min(uint32_t a, uint32_t b) { return a < b ? a : b; }

static void reset_lut(uint8_t *lut_mem, DrawMode_t mode)
{
    switch (mode)
    {
    case BLACK_ON_WHITE:
        memset(lut_mem, 0x55, (1 << 16));
        break;
    case WHITE_ON_BLACK:
    case WHITE_ON_WHITE:
        memset(lut_mem, 0xAA, (1 << 16));
        break;
    default: // mode validé dans show()
        break;
    }
}

static void update_LUT(uint8_t *lut_mem, uint8_t k, DrawMode_t mode)
{
    if (mode == BLACK_ON_WHITE || mode == WHITE_ON_WHITE)
    {
        k = 15 - k;
    }
    // reset the pixels which are not to be lightened / darkened any longer in the current frame
    for (uint32_t l = k; l < (1 << 16); l += 16)
    {
        lut_mem[l] &= 0xFC;
    }
    for (uint32_t l = (k << 4); l < (1 << 16); l += (1 << 8))
    {
        for (uint32_t p = 0; p < 16; p++)
        {
            lut_mem[l + p] &= 0xF3;
        }
    }
    for (uint32_t l = (k << 8); l < (1 << 16); l += (1 << 12))
    {
        for (uint32_t p = 0; p < (1 << 8); p++)
        {
            lut_mem[l + p] &= 0xCF;
        }
    }
    for (uint32_t p = (k << 12); p < ((k + 1) << 12); p++)
    {
        lut_mem[p] &= 0x3F;
    }
}

static void calc_epd_input_4bpp(const uint32_t *line_data, uint8_t *epd_input, const uint8_t *lut)
{
    uint32_t *wide_epd_input = (uint32_t *)epd_input;
    const uint16_t *line_data_16 = (const uint16_t *)line_data;

    // this is reversed for little-endian, but this is later compensated through the output peripheral.
    for (uint32_t j = 0; j < EPD_WIDTH / 16; j++)
    {
        uint16_t v1 = *(line_data_16++);
        uint16_t v2 = *(line_data_16++);
        uint16_t v3 = *(line_data_16++);
        uint16_t v4 = *(line_data_16++);
        uint32_t pixel = (lut[v1]) << 0  |
                         (lut[v2]) << 8  |
                         (lut[v3]) << 16 |
                         (lut[v4]) << 24;
        wide_epd_input[j] = pixel;
    }
}

static void nibble_shift_buffer_right(uint8_t *buf, uint32_t len)
{
    uint8_t carry = 0xF;
    for (uint32_t i = 0; i < len; i++)
    {
        uint8_t val = buf[i];
        buf[i] = (val << 4) | carry;
        carry = (val & 0xF0) >> 4;
    }
}

static void provide_and_feed(const uint8_t *fb, Rect_t area, int32_t frame, DrawMode_t mode)
{
    uint8_t line[EPD_WIDTH / 2] __attribute__((aligned(4)));
    memset(line, 255, EPD_WIDTH / 2);

    if (area.x < 0) area.x = 0;
    if (area.y < 0) area.y = 0;

    // positionnement au début de la zone dans le framebuffer
    const uint8_t *img_buffer = fb
                    + area.y * (EPD_WIDTH / 2)
                    + (area.x > 0 ? area.x / 2 : 0);

    if (frame == 0) reset_lut(conversion_lut, mode);
    update_LUT(conversion_lut, frame, mode);

    const uint16_t contrast = (mode == WHITE_ON_BLACK) ? contrast_white[frame]
                                                       : contrast_dark[frame];

    // Pré-calcul des bornes et masques hors boucle pour ne pas pénaliser le timing par ligne
    const uint32_t line_cap = EPD_WIDTH / 2;
    uint32_t x_offset_bytes = (area.x > 0) ? (uint32_t)(area.x / 2) : 0;
    if (x_offset_bytes > line_cap) x_offset_bytes = line_cap;

    const uint32_t avail_bytes = line_cap - x_offset_bytes;
    uint32_t req_bytes = (area.width > 0) ? (uint32_t)(area.width / 2 + area.width % 2) : 0;
    const uint32_t line_bytes = min(req_bytes, avail_bytes);

    const bool full_line = (area.width == (int32_t)EPD_WIDTH && area.x == 0);
    const bool need_odd_width_mask = !full_line && (area.width % 2 == 1) && (line_bytes > 0);
    const bool need_odd_x_shift = !full_line && (area.x > 0) && (area.x % 2 == 1) && (line_bytes > 0);
    const uint32_t shift_len = need_odd_x_shift ? min(line_bytes + 1, avail_bytes) : 0;
    uint8_t *const buf_start = line + x_offset_bytes;

    // ex "skipping" du HAL : vrai si la dernière ligne traitée était une écriture
    bool last_was_write = false;

    hal->start_frame();
    for (int32_t i = 0; i < EPD_HEIGHT; i++)
    {
        if (i < area.y || i >= area.y + area.height) // hors zone: je saute
        {
            hal->skip_row(contrast);
            last_was_write = false;
            continue;
        }

        const uint32_t *lp;
        bool shifted = false;

        if (full_line) // ligne entière
        {
            lp = (const uint32_t *)img_buffer;
        }
        else if (line_bytes > 0)
        {
            memcpy(buf_start, img_buffer, line_bytes);
            if (need_odd_width_mask) {
                buf_start[line_bytes - 1] |= 0xF0;
            }
            if (need_odd_x_shift) {
                shifted = true;
                nibble_shift_buffer_right(buf_start, shift_len);
            }
            lp = (const uint32_t *)line;
        }
        else
        {
            lp = (const uint32_t *)line;
        }

        img_buffer += EPD_WIDTH / 2;

        // double copie lp -> output supprimée : la conversion lit directement lp
        calc_epd_input_4bpp(lp, hal->line_buffer(), conversion_lut);
        hal->write_row(contrast);
        last_was_write = true;
        if (shifted) memset(line, 255, EPD_WIDTH / 2);
    }
    if (last_was_write) hal->write_row(contrast);
    hal->end_frame();
}

/******************************************************************************/
/***        API MicroPython                                                 ***/
/******************************************************************************/

// init(connector)
static mp_obj_t epd_init(mp_obj_t table_in)
{
    hal = (const epd_abi_t *)(uintptr_t)mp_obj_get_int(table_in);
    if (hal->version != EPD_ABI_VERSION) {
        hal = NULL;
        mp_raise_ValueError(MP_ERROR_TEXT("abi version"));
    }
    // ce driver est compilé pour une taille fixe (boucles et buffers de ligne)
    if (hal->width != EPD_WIDTH || hal->height != EPD_HEIGHT) {
        hal = NULL;
        mp_raise_ValueError(MP_ERROR_TEXT("screen size"));
    }
    if (conversion_lut != NULL) {      // ré-init: pas de fuite
        hal->free(conversion_lut);
        conversion_lut = NULL;
    }
    conversion_lut = (uint8_t *)hal->alloc(1 << 16, 1); // RAM interne si possible
    if (conversion_lut == NULL) {
        mp_raise_ValueError(MP_ERROR_TEXT("lut alloc"));
    }
    for (int i = 0; i < 15; i++) {      // retour aux durées par défaut
        contrast_dark[i]  = contrast_cycles_4[i];
        contrast_white[i] = contrast_cycles_4_white[i];
    }
    rotation = 0;
    hal->set_rotation(rotation);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(epd_init_obj, epd_init);

// deinit() : libère la LUT avant de décharger le module
static mp_obj_t epd_deinit(void)
{
    if (hal != NULL) {
        hal->poweroff();               // sécurité: écran jamais laissé alimenté
        if (conversion_lut != NULL) hal->free(conversion_lut);
    }
    conversion_lut = NULL;
    hal = NULL;
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(epd_deinit_obj, epd_deinit);

static void get_area(size_t n_args, const mp_obj_t *args, size_t first, Rect_t *area)
{
    if (n_args >= first + 4) {
        int32_t x = mp_obj_get_int(args[first]);
        int32_t y = mp_obj_get_int(args[first + 1]);
        int32_t w = mp_obj_get_int(args[first + 2]);
        int32_t h = mp_obj_get_int(args[first + 3]);

        // Clamp des bords haut/gauche si négatifs, en ajustant w/h
        if (x < 0) x = 0;
        if (y < 0) y = 0;
        if (x > (int32_t)EPD_WIDTH) x = (int32_t)EPD_WIDTH;
        if (y > (int32_t)EPD_HEIGHT) y = (int32_t)EPD_HEIGHT;

        // Clamp des bords droit/bas sur les dimensions physiques
        if (x + w > (int32_t)EPD_WIDTH) w = (int32_t)EPD_WIDTH - x;
        if (y + h > (int32_t)EPD_HEIGHT) h = (int32_t)EPD_HEIGHT - y;

        area->x      = x;
        area->y      = y;
        area->width  = w;
        area->height = h;
    }
}

static void check_ready(void)
{
    if (hal == NULL) mp_raise_ValueError(MP_ERROR_TEXT("not init"));
}

// get_context() : renvoie le contexte de lécran, le buffer, la largeur, la hauteur et la rotation initial. pour initialise
static mp_obj_t epd_get_context(void)
{
    if (hal->fb == NULL || hal->fb_size < (EPD_WIDTH / 2) * EPD_HEIGHT) {
        mp_raise_ValueError(MP_ERROR_TEXT("no framebuffer"));
    }

    mp_obj_t tuple[4] = {
        mp_obj_new_bytearray_by_ref((EPD_WIDTH / 2) * EPD_HEIGHT, hal->fb),
        mp_obj_new_int(EPD_WIDTH),
        mp_obj_new_int(EPD_HEIGHT),
        mp_obj_new_int(rotation)
    };

    return mp_obj_new_tuple(4, tuple);
}
static MP_DEFINE_CONST_FUN_OBJ_0(epd_get_context_obj, epd_get_context);

// show([x, y, w, h [, mode]]) : le framebuffer vient du connecteur, le driver gère l'alimentation
static mp_obj_t epd_show(size_t n_args, const mp_obj_t *args)
{
    if (hal == NULL || conversion_lut == NULL) {
        mp_raise_ValueError(MP_ERROR_TEXT("not init"));
    }
    const uint8_t *fb = hal->fb;   // relu a chaque appel: suit un éventuel nouveau T547()
    if (fb == NULL || hal->fb_size < (EPD_WIDTH / 2) * EPD_HEIGHT) {
        mp_raise_ValueError(MP_ERROR_TEXT("no framebuffer"));
    }

    Rect_t area = {0, 0, EPD_WIDTH, EPD_HEIGHT};
    get_area(n_args, args, 0, &area);
    DrawMode_t mode = BLACK_ON_WHITE;
    if (n_args == 5) {
        mode = (DrawMode_t)mp_obj_get_int(args[4]);
    }
    if (mode != BLACK_ON_WHITE && mode != WHITE_ON_WHITE && mode != WHITE_ON_BLACK) {
        mp_raise_ValueError(MP_ERROR_TEXT("mode"));
    }

    hal->poweron();

    uint32_t delai = 10000;
    uint32_t delay_boucle = 10000;
    delai = mp_obj_get_int(args[5]);
    delay_boucle = mp_obj_get_int(args[6]);

    hal->delay_us(delai); //10000->1000
    for (int32_t k = 0; k < 15; k++)
    {
        provide_and_feed(fb, area, k, mode);
        hal->delay_us(delay_boucle); //10000 -> 1000 petite attente entre chaque passage
    }
    hal->poweroff();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(epd_show_obj, 0, 6, epd_show);

// recette de nettoyage (ex epd_screen_clear_area_cycles) : propre au driver
static void clear_cycles(int32_t x, int32_t y, int32_t w, int32_t h, int32_t cycles, int32_t cycle_time)
{
    for (int32_t c = 0; c < cycles; c++) {
        for (int i = 0; i < 5; i++)  hal->push_pixels(x, y, w, h, cycle_time, 0);
        for (int i = 0; i < 10; i++) hal->push_pixels(x, y, w, h, cycle_time, 1);
        for (int i = 0; i < 2; i++)  hal->push_pixels(x, y, w, h, cycle_time, 2);
    }
}

// clean_screen([x, y, w, h]) : 2 cycles de 17 passes a 20us. Plein écran: rotation forcée à 0 le temps du clear.
static mp_obj_t epd_clean_screen(size_t n_args, const mp_obj_t *args)
{
    check_ready();
    Rect_t a = {0, 0, EPD_WIDTH, EPD_HEIGHT};

    uint32_t cycle= mp_obj_get_int(args[4]);
    uint32_t ms=mp_obj_get_int(args[5]);
    get_area(n_args, args, 0, &a);
    bool full = (a.x == 0 && a.y == 0 && a.width == EPD_WIDTH && a.height == EPD_HEIGHT);
    if (full) hal->set_rotation(0);
    hal->poweron();
    clear_cycles(a.x, a.y, a.width, a.height, cycle, ms);//passage a 20->10 du fait de l'ajustement du contraste
    hal->poweroff();
    if (full) hal->set_rotation(rotation);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(epd_clean_screen_obj, 0, 6, epd_clean_screen);

// clean_buffer([x, y, w, h,][ color]) : nettoie une zone du framebuffer (l'écran est piloté par le driver)
static mp_obj_t epd_clean_buffer(size_t n_args, const mp_obj_t *args) {

    check_ready();
    Rect_t area = {0, 0, EPD_WIDTH, EPD_HEIGHT};
    int32_t color=0;
    if (n_args==1){
        color=mp_obj_get_int(args[0]);
    }
    if (n_args>=4)
    {
    get_area(n_args, args, 0, &area);
    }
    if (n_args==5) color=mp_obj_get_int(args[4]); /*si j'ai des argument c'est au moins la taille donc je met la couleur par défaut le blanc*/

    if(color>254) color=254;

    hal->clean_buffer(area.x,area.y,area.width,area.height,color,hal->fb);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(epd_clean_buffer_obj, 0, 5, epd_clean_buffer);

// push(time_us, color [, x, y, w, h]) : remplissage direct d'une zone (ex t547.push), ecran seulement
static mp_obj_t epd_push(size_t n_args, const mp_obj_t *args)
{
    check_ready();
    Rect_t a = {0, 0, EPD_WIDTH, EPD_HEIGHT};
    get_area(n_args, args, 2, &a);
    bool full = (a.x == 0 && a.y == 0 && a.width == EPD_WIDTH && a.height == EPD_HEIGHT);
    if (full) hal->set_rotation(0);
    hal->poweron();
    hal->push_pixels(a.x, a.y, a.width, a.height, mp_obj_get_int(args[0]), mp_obj_get_int(args[1]));
    hal->poweroff();
    if (full) hal->set_rotation(rotation);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(epd_push_obj, 2, 6, epd_push);

// orientation(deg) / get_orientation() : la valeur vit ici, le HAL en reçoit une copie
static mp_obj_t epd_set_orientation(mp_obj_t deg_in)
{
    check_ready();
    int32_t deg = mp_obj_get_int(deg_in);
    if (deg != 0 && deg != 90 && deg != 180 && deg != 270) {
        mp_raise_ValueError(MP_ERROR_TEXT("rotation"));
    }
    rotation = deg;
    hal->set_rotation(rotation);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(epd_set_orientation_obj, epd_set_orientation);

static mp_obj_t epd_get_orientation(void)
{
    return mp_obj_new_int(rotation);
}
static MP_DEFINE_CONST_FUN_OBJ_0(epd_get_orientation_obj, epd_get_orientation);

// set_contrast(durees [, white]) : 15 valeurs (en 1/10 us par ligne), 1..65535. white=True: table WHITE_ON_BLACK
static mp_obj_t epd_set_contrast(size_t n_args, const mp_obj_t *args)
{
    check_ready();
    size_t len;
    mp_obj_t *items;
    mp_obj_get_array(args[0], &len, &items);
    if (len != 15) mp_raise_ValueError(MP_ERROR_TEXT("15 values"));
    uint16_t tmp[15];
    for (int i = 0; i < 15; i++) {
        mp_int_t v = mp_obj_get_int(items[i]);
        if (v < 1 || v > 65535) mp_raise_ValueError(MP_ERROR_TEXT("range"));
        tmp[i] = (uint16_t)v;
    }
    bool white = (n_args > 1) && mp_obj_is_true(args[1]);
    uint16_t *dst = white ? contrast_white : contrast_dark;
    for (int i = 0; i < 15; i++) dst[i] = tmp[i];
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(epd_set_contrast_obj, 1, 2, epd_set_contrast);

// get_contrast([white]) : durées actuelles
static mp_obj_t epd_get_contrast(size_t n_args, const mp_obj_t *args)
{
    check_ready();
    bool white = (n_args > 0) && mp_obj_is_true(args[0]);
    const uint16_t *src = white ? contrast_white : contrast_dark;
    mp_obj_t items[15];
    for (int i = 0; i < 15; i++) items[i] = mp_obj_new_int(src[i]);
    return mp_obj_new_list(15, items);
}
static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(epd_get_contrast_obj, 0, 1, epd_get_contrast);

// width() / height() : dimensions logiques (tiennent compte de la rotation détenue par le driver)
static mp_obj_t epd_width(void)
{
    check_ready();
    return mp_obj_new_int((rotation == 90 || rotation == 270) ? hal->height : hal->width);
}
static MP_DEFINE_CONST_FUN_OBJ_0(epd_width_obj, epd_width);

static mp_obj_t epd_height(void)
{
    check_ready();
    return mp_obj_new_int((rotation == 90 || rotation == 270) ? hal->width : hal->height);
}
static MP_DEFINE_CONST_FUN_OBJ_0(epd_height_obj, epd_height);

// ---------- help ----------
static mp_obj_t py_help(void) {
    return mp_obj_new_str(HELP_TEXT, strlen(HELP_TEXT));
}
static MP_DEFINE_CONST_FUN_OBJ_0(help_obj, py_help);

mp_obj_t mpy_init(mp_obj_fun_bc_t *self, size_t n_args, size_t n_kw, mp_obj_t *args)
{
    MP_DYNRUNTIME_INIT_ENTRY

    mp_store_global(MP_QSTR_init,   MP_OBJ_FROM_PTR(&epd_init_obj));
    mp_store_global(MP_QSTR_deinit, MP_OBJ_FROM_PTR(&epd_deinit_obj));
    mp_store_global(MP_QSTR_get_context, MP_OBJ_FROM_PTR(&epd_get_context_obj));
    mp_store_global(MP_QSTR_show,   MP_OBJ_FROM_PTR(&epd_show_obj));
    mp_store_global(MP_QSTR_set_contrast, MP_OBJ_FROM_PTR(&epd_set_contrast_obj));
    mp_store_global(MP_QSTR_get_contrast, MP_OBJ_FROM_PTR(&epd_get_contrast_obj));
    mp_store_global(MP_QSTR_width,  MP_OBJ_FROM_PTR(&epd_width_obj));
    mp_store_global(MP_QSTR_height, MP_OBJ_FROM_PTR(&epd_height_obj));
    mp_store_global(MP_QSTR_clean_screen,  MP_OBJ_FROM_PTR(&epd_clean_screen_obj));
    mp_store_global(MP_QSTR_clean_buffer,  MP_OBJ_FROM_PTR(&epd_clean_buffer_obj));
    mp_store_global(MP_QSTR_push,   MP_OBJ_FROM_PTR(&epd_push_obj));
    mp_store_global(MP_QSTR_set_orientation,     MP_OBJ_FROM_PTR(&epd_set_orientation_obj));
    mp_store_global(MP_QSTR_get_orientation, MP_OBJ_FROM_PTR(&epd_get_orientation_obj));
    mp_store_global(MP_QSTR_help,           MP_OBJ_FROM_PTR(&help_obj));
    mp_store_global(MP_QSTR_BLACK_ON_WHITE, MP_OBJ_NEW_SMALL_INT(BLACK_ON_WHITE));
    mp_store_global(MP_QSTR_WHITE_ON_WHITE, MP_OBJ_NEW_SMALL_INT(WHITE_ON_WHITE));
    mp_store_global(MP_QSTR_WHITE_ON_BLACK, MP_OBJ_NEW_SMALL_INT(WHITE_ON_BLACK));

    MP_DYNRUNTIME_INIT_EXIT
}
