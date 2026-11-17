#include "rmt.h"
#include "driver/rmt_tx.h"
#include "esp_log.h"

static rmt_channel_handle_t rmt_chan = NULL;
static rmt_encoder_handle_t copy_encoder = NULL;

void rmt_init(gpio_num_t pin)
{
    if (rmt_chan != NULL) return; // hardware survit au reset soft

    rmt_tx_channel_config_t chan_config = {
        .gpio_num = pin,
        .clk_src = RMT_CLK_SRC_DEFAULT,
        .resolution_hz = 10 * 1000 * 1000, // 10MHz = 0.1us resolution
        .mem_block_symbols = 64,
        .trans_queue_depth = 4,
    };
    ESP_ERROR_CHECK(rmt_new_tx_channel(&chan_config, &rmt_chan));

    rmt_copy_encoder_config_t copy_encoder_config = {};
    ESP_ERROR_CHECK(rmt_new_copy_encoder(&copy_encoder_config, &copy_encoder));

    ESP_ERROR_CHECK(rmt_enable(rmt_chan));
}

void rmt_deinit()
{
    if (rmt_chan == NULL) return;
    rmt_disable(rmt_chan);
    rmt_del_channel(rmt_chan);
    rmt_del_encoder(copy_encoder);
    rmt_chan = NULL;
    copy_encoder = NULL;
}

void IRAM_ATTR rmt_pulse_ckv_ticks(uint16_t high_time_ticks, uint16_t low_time_ticks, bool wait)
{
    rmt_symbol_word_t symbol = {
        .level0    = 1,
        .duration0 = high_time_ticks > 0 ? high_time_ticks : low_time_ticks,
        .level1    = 0,
        .duration1 = high_time_ticks > 0 ? low_time_ticks  : 0,
    };

    rmt_transmit_config_t tx_config = {
        .loop_count = 0,
    };
    rmt_transmit(rmt_chan, copy_encoder, &symbol, sizeof(symbol), &tx_config);
    if (wait) {
        rmt_tx_wait_all_done(rmt_chan, 1000);
    }
}

void IRAM_ATTR rmt_pulse_ckv_us(uint16_t high_time_us, uint16_t low_time_us, bool wait)
{
    rmt_pulse_ckv_ticks(10 * high_time_us, 10 * low_time_us, wait);
}
