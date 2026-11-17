#include "i2s.h"
#include <esp_heap_caps.h>
#include "esp_lcd_panel_io.h"
#include "definition.h"

static esp_lcd_panel_io_handle_t io_handle = NULL;
static esp_lcd_i80_bus_handle_t i80_bus = NULL;
static volatile bool output_done = true;
static uint8_t line_buffer[EPD_ROW_BUFFER_SIZE] = {0};

volatile uint8_t *i2s_line_buffer()
{
    return line_buffer;
}

bool IRAM_ATTR i2s_is_busy()
{
    return !output_done;
}

void IRAM_ATTR i2s_send_line()
{
    output_done = false;
    esp_lcd_panel_io_tx_color(io_handle, 0, line_buffer, EPD_ROW_BUFFER_SIZE);
}

static bool notify_trans_done(esp_lcd_panel_io_handle_t panel_io,
                              esp_lcd_panel_io_event_data_t *edata,
                              void *user_ctx)
{
    output_done = true;
    return output_done;
}

void i2s_init(i2s_bus_config *cfg)
{
    if (i80_bus != NULL) return; // bus déjà initialisé, hardware survit au reset soft

    esp_lcd_i80_bus_config_t bus_config = {
        .clk_src = LCD_CLK_SRC_PLL160M,
        .dc_gpio_num = cfg->start_pulse,
        .wr_gpio_num = cfg->clock,
        .data_gpio_nums = {
            cfg->data_6, cfg->data_7,
            cfg->data_4, cfg->data_5,
            cfg->data_2, cfg->data_3,
            cfg->data_0, cfg->data_1,
        },
        .bus_width = 8,
        .max_transfer_bytes = EPD_ROW_BUFFER_SIZE
    };
    ESP_ERROR_CHECK(esp_lcd_new_i80_bus(&bus_config, &i80_bus));

    esp_lcd_panel_io_i80_config_t io_config = {
        .cs_gpio_num = -1,
        .pclk_hz = 10 * 1000 * 1000,
        .trans_queue_depth = 10,
        .dc_levels = {
            .dc_idle_level = 0,
            .dc_cmd_level = 1,
            .dc_dummy_level = 0,
            .dc_data_level = 0,
        },
        .on_color_trans_done = notify_trans_done,
        .user_ctx = NULL,
        .lcd_cmd_bits = 10,
        .lcd_param_bits = 0,
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_i80(i80_bus, &io_config, &io_handle));
}

void i2s_deinit()
{
    if (i80_bus == NULL) return;
    esp_lcd_panel_io_del(io_handle);
    esp_lcd_del_i80_bus(i80_bus);
    io_handle = NULL;
    i80_bus = NULL;
}
