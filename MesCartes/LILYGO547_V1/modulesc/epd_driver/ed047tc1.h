#ifndef _ED047TC1_H_
#define _ED047TC1_H_


/******************************************************************************/
/***        include files                                                   ***/
/******************************************************************************/

#include <driver/gpio.h>
#include <esp_attr.h>   // IRAM_ATTR — no longer transitively included in ESP32 Arduino core 3.x

#include <stdint.h>

/******************************************************************************/
/***        macro definitions                                               ***/
/******************************************************************************/

#include "definition.h"

/******************************************************************************/
/***        type definitions                                                ***/
/******************************************************************************/

/******************************************************************************/
/***        exported variables                                              ***/
/******************************************************************************/

/******************************************************************************/
/***        exported functions                                              ***/
/******************************************************************************/

void epd_screen_base_init(uint32_t epd_row_width);
void epd_screen_poweron();
void epd_screen_poweroff();

/**
 * @brief Start a draw cycle.
 */
void epd_screen_start_frame();

/**
 * @brief End a draw cycle.
 */
void epd_screen_end_frame();

/**
 * @brief output row data
 *
 * @note Waits until all previously submitted data has been written.
 *       Then, the following operations are initiated:
 *
 *           1. Previously submitted data is latched to the output register.
 *           2. The RMT peripheral is set up to pulse the vertical (gate) driver
 *              for `output_time_dus` / 10 microseconds.
 *           3. The I2S peripheral starts transmission of the current buffer to
 *              the source driver.
 *           4. The line buffers are switched.
 *
 *       This sequence of operations allows for pipelining data preparation and
 *       transfer, reducing total refresh times.
 */
void  epd_screen_print_row(uint32_t output_time_dus);

/**
 * @brief Skip a row without writing to it.
 */
void  epd_screen_skip_row();

/**
 * @brief Get the currently writable line buffer.
 */
uint8_t *  epd_screen_line_buffer();


#endif
/******************************************************************************/
/***        END OF FILE                                                     ***/
/******************************************************************************/