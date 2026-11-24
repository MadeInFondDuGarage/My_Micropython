// Table d'ABI HAL -> natmod. Volontairement sans aucune dépendance (stdint seulement),
// pour pouvoir être incluse côté firmware ET côté natmod.
#ifndef _EPD_ABI_H_
#define _EPD_ABI_H_

#include <stdint.h>

#define EPD_ABI_VERSION 4

typedef struct
{
    uint32_t version;
    uint32_t width;                 // dimensions physiques de l'écran (pixels)
    uint32_t height;
    uint8_t *fb;                    // framebuffer 4bpp canonique (NULL tant qu'aucun T547 n'existe)
    uint32_t fb_size;               // taille en octets
    void     (*poweron)(void);
    void     (*poweroff)(void);
    void     (*start_frame)(void);
    void     (*end_frame)(void);
    void     (*write_row)(uint32_t output_time_dus);
    void     (*skip_row)(uint16_t pipeline_finish_time);
    uint8_t *(*line_buffer)(void);
    void     (*delay_us)(uint32_t us);
    void     (*push_pixels)(int32_t x, int32_t y, int32_t w, int32_t h, int32_t time_us, int32_t color); // zone, remplissage direct (color: 0 noir, 1 blanc), ecran seulement
    void     (*set_rotation)(int32_t deg); // 0/90/180/270, la valeur est détenue par le driver et poussée ici
    void    *(*alloc)(uint32_t size, int internal); // internal=1: RAM interne, 0: PSRAM (repli sur l'autre si plein)
    void     (*free)(void *ptr);
    void     (*clean_buffer)(int32_t x, int32_t y, int32_t w, int32_t h, int32_t color,uint8_t *fb);//lancement du netoyage du buffer aussi depuis le drv.
} epd_abi_t;

/** Adresse de la table (le "connecteur"), a passer a init() du natmod. */
uintptr_t epd_hal_table(void);

/** Renseigne le framebuffer dans la table (appelé par t547.c). */
void epd_hal_set_fb(uint8_t *fb, uint32_t size);

#endif
