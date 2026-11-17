/**
 * Implements a 8bit parallel interface to transmit pixel
 * data to the display, based on the Intel 8080 (I80) peripheral.
 */
#ifndef _I2S_H_
#define _I2S_H_

#include <driver/gpio.h>
#include <esp_attr.h>
#include <stdint.h>

typedef struct
{
    gpio_num_t data_0;
    gpio_num_t data_1;
    gpio_num_t data_2;
    gpio_num_t data_3;
    gpio_num_t data_4;
    gpio_num_t data_5;
    gpio_num_t data_6;
    gpio_num_t data_7;
    gpio_num_t clock;
    gpio_num_t start_pulse;
    uint32_t epd_row_width;
} i2s_bus_config;

void i2s_init(i2s_bus_config *cfg);
volatile uint8_t IRAM_ATTR *i2s_line_buffer();
void i2s_send_line();
bool i2s_is_busy();
void i2s_deinit();

#endif