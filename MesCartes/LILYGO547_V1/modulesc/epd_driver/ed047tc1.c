
/******************************************************************************/
/***        include files                                                   ***/
/******************************************************************************/

#include "ed047tc1.h"
#include "i2s.h"
#include "rmt.h"

#include <hal/gpio_ll.h>
#include <xtensa/core-macros.h>

#include <string.h>

/******************************************************************************/
/***        macro definitions                                               ***/
/******************************************************************************/

//ici on décrit les actions directment sur les pattes de conf pour init l'écran, passer des commands, une ligne de pixel et autres

/******************************************************************************/
/***        type definitions                                                ***/
/******************************************************************************/

typedef struct //structure de configuration
{
    bool ep_latch_enable : 1;
    bool power_disable : 1;
    bool pos_power_enable : 1;
    bool neg_power_enable : 1;
    bool ep_stv : 1;
    bool ep_scan_direction : 1;
    bool ep_mode : 1;
    bool ep_output_enable : 1;
} epd_config_register_t;


/******************************************************************************/
/***        local variables                                                 ***/
/******************************************************************************/

static epd_config_register_t config_reg;

/******************************************************************************/
/***        exported functions                                              ***/
/******************************************************************************/

/*
 * Write bits directly using the registers.
 * Won't work for some pins (>= 32).
 */
inline static void fast_gpio_set_hi(gpio_num_t gpio_num)
{
    GPIO.out_w1ts = (1 << gpio_num); //écriture rapide pour le niveau haut
}

inline static void fast_gpio_set_lo(gpio_num_t gpio_num)
{
    GPIO.out_w1tc = (1 << gpio_num); //écriture rapide pour le niveau bas
}

inline static void IRAM_ATTR push_cfg_bit(bool bit)
{
    fast_gpio_set_lo(CFG_CLK); //bitbang sur le registre a décallage pour passer le data de la configuration
    if (bit)
    {
        fast_gpio_set_hi(CFG_DATA);
    }
    else
    {
        fast_gpio_set_lo(CFG_DATA);
    }
    fast_gpio_set_hi(CFG_CLK);
}

static void IRAM_ATTR push_cfg(epd_config_register_t *cfg)
{
    fast_gpio_set_lo(CFG_STR); //je pousse la configuration tel que vue dans la structure

    // push config bits in reverse order
    push_cfg_bit(cfg->ep_output_enable);
    push_cfg_bit(cfg->ep_mode);
    push_cfg_bit(cfg->ep_scan_direction);
    push_cfg_bit(cfg->ep_stv);

    push_cfg_bit(cfg->neg_power_enable);
    push_cfg_bit(cfg->pos_power_enable);
    push_cfg_bit(cfg->power_disable);
    push_cfg_bit(cfg->ep_latch_enable);

    fast_gpio_set_hi(CFG_STR);
}


void IRAM_ATTR busy_delay(uint32_t cycles) //tempo en cycle d'horloge
{
    volatile uint64_t counts = XTHAL_GET_CCOUNT() + cycles;
    while (XTHAL_GET_CCOUNT() < counts) ;
}


void epd_screen_base_init(uint32_t epd_row_width) //configuration pour l'init de l'écran.
{
    config_reg.ep_latch_enable = false;
    config_reg.power_disable = true;
    config_reg.pos_power_enable = false;
    config_reg.neg_power_enable = false;
    config_reg.ep_stv = true;
    config_reg.ep_scan_direction = true;
    config_reg.ep_mode = false;
    config_reg.ep_output_enable = false;

    /* Power Control Output/Off */ //je prépare le registre a décallage
    gpio_set_direction(CFG_DATA, GPIO_MODE_OUTPUT);
    gpio_set_direction(CFG_CLK, GPIO_MODE_OUTPUT);
    gpio_set_direction(CFG_STR, GPIO_MODE_OUTPUT);
    fast_gpio_set_lo(CFG_STR);

    push_cfg(&config_reg); //je balance la configuration

    // Setup I2S
    i2s_bus_config i2s_config; //je récupère la sructure de conf du bus
    // add an offset off dummy bytes to allow for enough timing headroom
    i2s_config.epd_row_width = epd_row_width + 32;
    i2s_config.clock = CKH;
    i2s_config.start_pulse = STH;
    i2s_config.data_0 = D0;
    i2s_config.data_1 = D1;
    i2s_config.data_2 = D2;
    i2s_config.data_3 = D3;
    i2s_config.data_4 = D4;
    i2s_config.data_5 = D5;
    i2s_config.data_6 = D6;
    i2s_config.data_7 = D7;

    i2s_init(&i2s_config); //initialisation du bus i2s

    rmt_init(CKV); // je réveille l'ensemble
}

void epd_screen_poweron() //fonction de reveill de l'écran, allumage des pipes.
{
    config_reg.ep_scan_direction = true;
    config_reg.power_disable = false;
    push_cfg(&config_reg);
    busy_delay(100 * 240);
    config_reg.neg_power_enable = true;
    push_cfg(&config_reg);
    busy_delay(500 * 240);
    config_reg.pos_power_enable = true;
    push_cfg(&config_reg);
    busy_delay(100 * 240);
    config_reg.ep_stv = true;
    push_cfg(&config_reg);
    fast_gpio_set_hi(STH);
}

void epd_screen_poweroff() //on éteint les pipes. ce qui réduit la consommation et léchauffement inutile
{
    config_reg.pos_power_enable = false;
    push_cfg(&config_reg);
    busy_delay(10 * 240);
    config_reg.neg_power_enable = false;
    push_cfg(&config_reg);
    busy_delay(100 * 240);
    config_reg.power_disable = true;
    push_cfg(&config_reg);

    config_reg.ep_stv = false;
    push_cfg(&config_reg);
}

void epd_screen_poweroff_all() // ici a retravailler car il manque le deinit de le l'i2s et du rmt TODO
{
    memset(&config_reg, 0, sizeof(config_reg));
    push_cfg(&config_reg);
    i2s_deinit();
    rmt_deinit();

}

void epd_screen_start_frame() //on prépare l'écran a l'envoie de ligne
{
    while (i2s_is_busy()) ; //je vérifier que le bus n'est pas occuppé

    config_reg.ep_mode = true; //de la même façons ont fait la conf et on l'envoie
    push_cfg(&config_reg);

    rmt_pulse_ckv_us(1, 1, true);

    // This is very timing-sensitive!
    config_reg.ep_stv = false;
    push_cfg(&config_reg);
    busy_delay(240);
    rmt_pulse_ckv_us(10, 10, false);
    config_reg.ep_stv = true;
    push_cfg(&config_reg);
    rmt_pulse_ckv_us(0, 10, true);

    config_reg.ep_output_enable = true;
    push_cfg(&config_reg);

    rmt_pulse_ckv_us(1, 1, true); //en gros arriver ici, l'écran esrt sur la première ligne et au premier pixel en mode standby
}

static inline void latch_row() //balance un signal de verrouillage de la ligne. ceci via le registre a décallage.
{
    config_reg.ep_latch_enable = true;
    push_cfg(&config_reg);

    config_reg.ep_latch_enable = false;
    push_cfg(&config_reg);
}

void  epd_screen_skip_row() //ici je skip la ligne directement en basculant la synchro vertical.
{
    // According to the spec, the OC4 maximum CKV frequency is 200kHz.
    rmt_pulse_ckv_ticks(45, 5, false);
}

void  epd_screen_print_row(uint32_t output_time_dus) //on envoie une ligne 
{
    while (i2s_is_busy()); //on vérifie que le bus est dispo

    latch_row(); // on signifie a l'écran que l'on verrouille la ligne

    rmt_pulse_ckv_ticks(output_time_dus, 50, false); // on balance l'impulsion de d'affichage. plus l'impulsion est longue plus le contraste sera elever.

    i2s_send_line(); // on balance la ligne
    
}

void epd_screen_end_frame() // en fin d'écran on envoie l'info de fin de trame (cela peut c faire avant la fin aussi pour gagner du temps)
{
    config_reg.ep_output_enable = false;
    push_cfg(&config_reg);
    config_reg.ep_mode = false;
    push_cfg(&config_reg);
    rmt_pulse_ckv_us(1, 1, true);
    rmt_pulse_ckv_us(1, 1, true);
}


uint8_t *  epd_screen_line_buffer() //ici je récupère le pointeur qui vas vers le buffer de la ligne i2s. il 'sagit d'un passe plat entre ce niveau le i2s et le epd. 
{
    return (uint8_t *)i2s_line_buffer();
}

/******************************************************************************/
/***        local functions                                                 ***/
/******************************************************************************/

/******************************************************************************/
/***        END OF FILE                                                     ***/
/******************************************************************************/
