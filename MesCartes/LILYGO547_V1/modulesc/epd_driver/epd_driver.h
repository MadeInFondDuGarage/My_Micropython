/**
 * A high-level library for drawing to an EPD.
 */

#ifndef _EPD_DRIVER_H_
#define _EPD_DRIVER_H_


/******************************************************************************/
/***        include files                                                   ***/
/******************************************************************************/

#include <esp_attr.h>

#include <stdbool.h>
#include <stdint.h>

/******************************************************************************/
/***        macro definitions                                               ***/
/******************************************************************************/

#include "definition.h"

/******************************************************************************/
/***        type definitions                                                ***/
/******************************************************************************/

/**
 * @brief An area on the display.
 */
typedef struct
{
    int32_t x;      /** Horizontal position. */
    int32_t y;      /** Vertical position. */
    int32_t width;  /** Area / image width, must be positive. */
    int32_t height; /** Area / image height, must be positive. */
} Rect_t;



/******************************************************************************/
/***        exported variables                                              ***/
/******************************************************************************/

/******************************************************************************/
/***        exported functions                                              ***/
/******************************************************************************/

/**
 * @brief Initialize the ePaper display
 */
void epd_screen_init();

/**
 * @brief Enable display power supply.
 */
void epd_screen_poweron();

/**
 * @brief Disable display power supply.
 */
void epd_screen_poweroff();

/**
 * @brief copy d'un buffer externe dans le buffer ecran (interne ou pas)'
 */
void epd_copy_to_screenbuffer();

/**
 * @brief nettoyage de la zone du buffer
 */
void epd_buf_clean(Rect_t area, uint8_t color ,uint8_t *framebuffer);

/**
 * @brief Clear the whole screen by flashing it.
 */
void epd_screen_clear();

void epd_screen_poweroff_all();

/**
 * @brief Clear an area by flashing it.
 *
 * @param area The area to clear.
 */
void epd_screen_clear_area(Rect_t area);

/**
 * @brief Clear an area by flashing it.
 *
 * @param area       The area to clear.
 * @param cycles     The number of black-to-white clear cycles.
 * @param cycle_time Length of a cycle. Default: 50 (us).
 */
void epd_screen_clear_area_cycles(Rect_t area, int32_t cycles, int32_t cycle_time);

/**
 * @brief Darken / lighten an area for a given time.
 *
 * @param area  The area to darken / lighten.
 * @param time  The time in us to apply voltage to each pixel.
 * @param color 1: lighten, 0: darken.
 */
void epd_screen_push_pixels(Rect_t area, int16_t time, int8_t color);


/**
 * @brief Rectancle representing the whole screen area.
 */
Rect_t epd_full_screen();


/**
 * @brief Draw a picture to a given area, with some draw mode.
 *
 * @note The image area is not cleared before drawing. For example, this can be
 *       used for pixel-aligned clearing.
 *
 * @param area The display area to draw to. `width` and `height` of the area
 *             must correspond to the image dimensions in pixels.
 * @param data The image data, as a buffer of 4 bit wide brightness values.
 *             Pixel data is packed (two pixels per byte). A byte cannot wrap
 *             over multiple rows, images of uneven width must add a padding
 *             nibble per line.
 */
void epd_screen_print(Rect_t area, uint8_t *data, DrawMode_t mode);

#endif
/******************************************************************************/
/***        END OF FILE                                                     ***/
/******************************************************************************/
