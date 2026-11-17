/******************************************************************************/
/***        include files                                                   ***/
/******************************************************************************/

#include "epd_driver.h"
#include "ed047tc1.h"

#include <esp_assert.h>
#include <esp_heap_caps.h>
#include <esp_log.h>
#include <esp_types.h>

#include <string.h>


/******************************************************************************/
/***        macro definitions                                               ***/
/******************************************************************************/

#include "definition.h"

/******************************************************************************/
/***        type definitions                                                ***/
/******************************************************************************/

typedef struct
{
    uint8_t *image_buffer;
    Rect_t area;
    int32_t frame;
    DrawMode_t mode;
} OutputParams;

/******************************************************************************/
/***        local function prototypes                                       ***/
/******************************************************************************/

/**
 * @brief output a row to the display.
 */
static void write_row(uint32_t output_time_dus);

/**
 * @brief skip a display row
 */
static void skip_row(uint8_t pipeline_finish_time);

static void reset_lut(uint8_t *lut_mem, DrawMode_t mode);

static void update_LUT(uint8_t *lut_mem, uint8_t k, DrawMode_t mode);

static void nibble_shift_buffer_right(uint8_t *buf, uint32_t len);


/******************************************************************************/
/***        exported variables                                              ***/
/******************************************************************************/

/******************************************************************************/
/***        local variables                                                 ***/
/******************************************************************************/

/**
 * @brief status tracker for row skipping
 */
static uint32_t skipping;

/* 4bpp Contrast cycles in order of contrast (Darkest first).  */
static const int32_t contrast_cycles_4[15] = {30, 30, 20, 20, 30, 30, 30, 40, 40, 50, 50, 50, 100, 200, 300};

static const int32_t contrast_cycles_4_white[15] = {10, 10, 8, 8, 8, 8, 8, 10, 10, 15, 15, 20, 20, 100, 300};

// Heap space to use for the EPD output lookup table, which
// is calculated for each cycle.
static uint8_t *conversion_lut;

// Simple x and y coordinate
typedef struct {
    uint16_t x; //x
    uint16_t y; //y
    uint16_t w; //largeur
    uint16_t h; //hauteur

} Coord_xy;


/******************************************************************************/
/***        exported functions                                              ***/
/******************************************************************************/

void epd_screen_init()
{
    skipping = 0;
    epd_screen_base_init(EPD_WIDTH); //on lance l'init. la taille est passer mais elle reste fixe puisque lier a l'écran. donc mise en definition.h

    conversion_lut = (uint8_t *)heap_caps_malloc(1 << 16, MALLOC_CAP_8BIT);
    assert(conversion_lut != NULL);

}

Coord_xy rotate(uint16_t x, uint16_t y,uint16_t w,uint16_t h) {

    int16_t phyX=0;
    int16_t phyY=0;
    int16_t areaH=0;
    int16_t areaW=0;

    switch (screen_rotation) {
        case 0:
            phyX=x;
            phyY=y;
            areaH=h;
            areaW=w;
            break;
        case 90:
            phyX = y;
            phyY = EPD_HEIGHT - 1 - x;
            areaW=h;
            areaH=w;
            break;
        case 180:
            phyX = EPD_WIDTH - 1 - x;
            phyY = EPD_HEIGHT - 1 - y;
            areaH=h;
            areaW=w;
            break;
        case 270:
            phyX = EPD_WIDTH - 1 - y;
            phyY = x;
            areaW=h;
            areaH=w;
            break;
    }
    Coord_xy coord = { phyX, phyY,areaW,areaH};
    return coord;
}

void epd_screen_push_pixels(Rect_t area, int16_t time, int8_t color) //ici je construit et pousse les lignes sur une zone avec une couleur. comme on ne travaille pas avec le buffer on écrase le visuel
{// cette fonction sert surtout pour nettoyer une zone ou tous l'écran. elle n'a pas vocation a servir pour dessiner -> voir buffer si on veut desiner.
    uint8_t row[EPD_LINE_BYTES]; //= { 0 }; //construction d'une ligne vide 0 étant noir.
    memset(row, 0, EPD_LINE_BYTES);
    const uint8_t color_choice[4] = { DARK_BYTE, CLEAR_BYTE, 0x00, 0xFF };

    int16_t xxx=0;
    int16_t yyy=0;
    int16_t areaH=0;
    int16_t areaW=0;

    switch (screen_rotation) {
        case 0:
            xxx=area.x;
            yyy=area.y;
            areaH=area.height;
            areaW=area.width;
            break;
        case 90:
            xxx = area.y;
            yyy = EPD_HEIGHT  - area.x - area.width;
            areaW=area.height;
            areaH=area.width;
            break;
        case 180:
            xxx= EPD_WIDTH  - area.x-area.width;
            yyy = EPD_HEIGHT  - area.y - area.height;
            areaH=area.height;
            areaW=area.width;
            break;
        case 270:
            xxx = EPD_WIDTH  - area.y - area.height;
            yyy = area.x;
            areaW=area.height;
            areaH=area.width;
            break;
    }


    for (uint32_t i = 0; i < areaW; i++) //sur la largeur de la zone
    {
        uint32_t position = i + (xxx % 4); // je calcul le décalage pour trouver le premier bit sur la ligne (modulo de 4 car on est 2 pixel par octet et don 1 pixel par quartet)
        uint8_t mask = color_choice[color] & (0b00000011 << (2 * (position % 4)));//je construit un masque en fonction de la couleur, soit noir soit blanc pas de gris ici.
        row[xxx / 4 + position / 4] |= mask;//j'applique le masque sur la zone de la ligne prévue
    }

    epd_screen_start_frame(); //je lance le remplissage de l'écran

    for (int32_t i = 0; i < EPD_HEIGHT; i++) //je balaye toutes les lignes
    {
        // before are of interest: skip
        if (i < yyy)
        {   //je ne suis pas dans la zone je saute les lignes
            skip_row(time);
            // start area of interest: set row data
        }
        else if (i == yyy) //je suis au début de la zone
        {
            memcpy(epd_screen_line_buffer(), row, EPD_LINE_BYTES); //je copie en momoire ma ligne

            write_row(time * 10); //et j'écrit
            // load nop row if done with area
        }
        else if (i > yyy + areaH +2) //si je suis sortie je skip les lignes
        {
            skip_row(time);
            // output the same as before
        }
        else
        {
            write_row(time * 10); // si je suis entre le début et la fin de la zone je rmplie de ligne
        }
    }

    epd_screen_end_frame();
}



void epd_copy_to_screenbuffer(Rect_t image_area, uint8_t *imagebuffer, uint8_t *screenbuffer) //je copy un buffer image dans le buffer ecran
{
    assert(imagebuffer != NULL || screenbuffer != NULL);


    for (uint32_t i = 0; i < image_area.width * image_area.height; i++)
    {

        int32_t xxx = image_area.x + i % image_area.width;
        int32_t yyy = image_area.y + i / image_area.width;

        Coord_xy coord = rotate(xxx, yyy, image_area.width,image_area.height);
        int32_t xx = coord.x;
        int32_t yy = coord.y;

        uint32_t value_index = i;
        // for images of uneven width,
        // consume an additional nibble per row.

        if (image_area.width % 2)
        {
            value_index += i / image_area.width;
        }

        uint8_t val = (value_index % 2) ? (imagebuffer[value_index / 2] & 0xF0) >> 4
        : imagebuffer[value_index / 2] & 0x0F;


        if (xx < 0 || xx >= EPD_WIDTH)
        {
            continue;
        }

        if (yy < 0 || yy >= EPD_HEIGHT)
        {
            continue;
        }

        uint8_t *buf_ptr = &screenbuffer[yy * EPD_WIDTH / 2 + xx / 2];

        if (xx % 2)
        {
            *buf_ptr = (*buf_ptr & 0x0F) | (val << 4);
        }
        else
        {
            *buf_ptr = (*buf_ptr & 0xF0) | val;
        }
    }

}

void epd_screen_clear_area(Rect_t area) // je nettoie l'écran sur une zone précise. uniquement l'écran pas le buffer
{
    epd_screen_clear_area_cycles(area, 2, 20); //ici on a par défaut 4 cycle a 50ms, mais on peut réduire le nombre de clignotement et augmenter le temps
    // c'est comment augmenter le tmp d'exposition, plus il est long plus les pixel migre vers la surface . a utiliser surtout pour du clean. pas pour de l'affichage
}


void epd_buf_clean(Rect_t area, uint8_t color ,uint8_t *framebuffer) //je nettoie le buffer sur la zone prévue
{
    int8_t backcolor = 255 - color;
    for (uint32_t i = 0; i < area.width * area.height; i++)
    {

        int32_t xxx = area.x + i % area.width;
        int32_t yyy = area.y + i / area.width;

        Coord_xy coord = rotate(xxx, yyy, area.width,area.height);
        int32_t xx = coord.x;
        int32_t yy = coord.y;

        if (xx < 0 || xx >= EPD_WIDTH)
        {
            continue;
        }
        if (yy < 0 || yy >= EPD_HEIGHT)
        {
            continue;
        }
        uint8_t *buf_ptr = &framebuffer[yy * EPD_WIDTH / 2 + xx / 2];
        if (xx % 2)
        {
            *buf_ptr = (*buf_ptr & 0x0F) | (backcolor << 4);
        }
        else
        {
            *buf_ptr = (*buf_ptr & 0xF0) | backcolor;
        }
    }

}

void epd_screen_clear_area_cycles(Rect_t area, int32_t cycles, int32_t cycle_time) // je nettoie l'écran sur un surface dedider avec un nombre de cycle dédier
{
    const int16_t white_time = cycle_time; //la duré est la durer de maintient charge des pixel, durée longue = augmentation du contraste (migration des pixels plus fort)
    const int16_t dark_time = cycle_time;


    for (int c = 0; c < cycles; c++) { //nombre de cycle complet
        for (int i = 0; i < 5; i++) {
            epd_screen_push_pixels(area, dark_time, 0); //nombre de cycle par couleur (4 noirs)
        }
        for (int i = 0; i < 10; i++) {
            epd_screen_push_pixels(area, white_time, 1); //nombre de cycle par couleur (4 blanches)
        }
        for (int i = 0; i < 2; i++) {
            epd_screen_push_pixels(area, white_time, 2);//nombre de cycle par couleur (4 blanches)
        }
    }
}


Rect_t epd_full_screen() //définition d'une area par défaut. de la taille de l'écran
{
    Rect_t area = {.x = 0, .y = 0, .width = EPD_WIDTH, .height = EPD_HEIGHT};
    return area;
}

void epd_screen_clear() //ici on éfface tout l'écran
{
    epd_screen_clear_area(epd_full_screen());
}


void IRAM_ATTR calc_epd_input_4bpp(uint32_t *line_data, uint8_t *epd_input,
                                   uint8_t k, uint8_t *conversion_lut)
{
    uint32_t *wide_epd_input = (uint32_t *)epd_input;
    uint16_t *line_data_16 = (uint16_t *)line_data;

    // this is reversed for little-endian, but this is later compensated
    // through the output peripheral.
    for (uint32_t j = 0; j < EPD_WIDTH / 16; j++)
    {
        uint16_t v1 = *(line_data_16++);
        uint16_t v2 = *(line_data_16++);
        uint16_t v3 = *(line_data_16++);
        uint16_t v4 = *(line_data_16++);
        uint32_t pixel = (conversion_lut[v1]) << 0  |
                         (conversion_lut[v2]) << 8  |
                         (conversion_lut[v3]) << 16 |
                         (conversion_lut[v4]) << 24;
        wide_epd_input[j] = pixel;
    }
}


static inline uint32_t min(uint32_t a, uint32_t b) //renvoie la valeur la plus petite entre les 2
{
    return a < b ? a : b;
}

static void IRAM_ATTR provide_and_feed(OutputParams *params)
{
    uint8_t line[EPD_WIDTH / 2];//init du buffer de la ligne
    memset(line, 255, EPD_WIDTH / 2); //je la remplie avec 255 qui ne fait rien (transparent en gros)
    Rect_t area = params->area;

    if (area.x < 0) area.x=0;
    if (area.y < 0) area.y=0;
    // positionnement au début de la zone dans le framebuffer
    //uint8_t *img_buffer = params->image_buffer + area.y * (EPD_WIDTH / 2);
    uint8_t *img_buffer = params->image_buffer 
                    + area.y * (EPD_WIDTH / 2) //position en y
                    + (area.x > 0 ? area.x / 2 : 0); //position en x

    if (params->frame == 0) reset_lut(conversion_lut, params->mode);
    update_LUT(conversion_lut, params->frame, params->mode);

    const int32_t *contrast_lut = (params->mode == WHITE_ON_BLACK)
        ? contrast_cycles_4_white : contrast_cycles_4;

    epd_screen_start_frame();
    for (int32_t i = 0; i < EPD_HEIGHT; i++)
    {
        if (i < area.y || i >= area.y + area.height) //je suis en dehors la zone y je skip les lignes
        {
            skip_row(contrast_lut[params->frame]);
            continue;
        }

        uint32_t *lp;
        bool shifted = false;

        if (area.width == EPD_WIDTH && area.x == 0)//si la taille est égal a la ligne
        {
            lp = (uint32_t *)img_buffer;//je prend toute la ligne
        }
        else
        {
            uint8_t *buf_start = (uint8_t *)line + (area.x > 0 ? area.x / 2 : 0); //adresse du pointeur de début c'est l'adresse de la ligne plus le décallage du x
            uint32_t line_bytes = min(area.width / 2 + area.width % 2, //je dimensionne la taile soit la largeur passer en paramètre soit lécran inclu le décallage. comme il exist forcment un taille, pour quoi on regard avec la largeur ?
                          EPD_WIDTH / 2 - area.x / 2);
            line_bytes = min(line_bytes, EPD_WIDTH / 2 - (uint32_t)(buf_start - line));
            memcpy(buf_start, img_buffer, line_bytes);
            if (area.width % 2 == 1 && area.x / 2 + area.width / 2 + 1 < EPD_WIDTH)
                *(buf_start + line_bytes - 1) |= 0xF0;
            if (area.x % 2 == 1 && area.x < EPD_WIDTH)
            {
                shifted = true;
                nibble_shift_buffer_right(buf_start,
                    min(line_bytes + 1, (uint32_t)line + EPD_WIDTH / 2 - (uint32_t)buf_start));
            }
            lp = (uint32_t *)line;
        }

        img_buffer += EPD_WIDTH / 2;

        uint8_t output[EPD_WIDTH / 2];
        memset(output, 0xFF, EPD_WIDTH / 2);
        memcpy(output, lp, EPD_WIDTH / 2);
        calc_epd_input_4bpp((uint32_t *)output, epd_screen_line_buffer(),
                            params->frame, conversion_lut);
        write_row(contrast_lut[params->frame]);
        if (shifted) memset(line, 255, EPD_WIDTH / 2);
    }
    if (!skipping) write_row(contrast_lut[params->frame]);
    epd_screen_end_frame();
}

void IRAM_ATTR epd_screen_print(Rect_t area, uint8_t *data, DrawMode_t mode)//je lance l'écriture de l'image passer en data sur la zone prévue
{
    uint8_t frame_count = 15;//je le fait 16 fois pour les 16 niveau de contraste (le zéro compte)
    esp_rom_delay_us(10000);
    for (uint8_t k = 0; k < frame_count; k++)// area est la zone réel a imprimer
    {
        OutputParams p = { .area = area,  .image_buffer = data, .frame = k, .mode = mode };
        provide_and_feed(&p); //je construit et ecrit
        esp_rom_delay_us(10000);//petite attente entre chaque passage.
    }   
    
}

/******************************************************************************/
/***        local functions                                                 ***/
/******************************************************************************/


static void write_row(uint32_t output_time_dus)
{
    // avoid too light output after skipping on some displays
    if (skipping)
    {
        //micropause volontaire pour éviter les effet de blur
    }
    skipping = 0;
    epd_screen_print_row(output_time_dus);
}


static void skip_row(uint8_t pipeline_finish_time)
{
    // output previously loaded row, fill buffer with no-ops.
    if (skipping == 0)//je viends de quitter une ligne dessiner, j'ai le skipping a 0
    {
        memset(epd_screen_line_buffer(), 0, EPD_LINE_BYTES); //je charge donc la ligne avec des 0 pour ne rien écrire
        epd_screen_print_row(pipeline_finish_time); //je balance la ligne avec une durée plus faible que du write pluisque je veut pas écrire
    }
    else if (skipping < 2) // je suis juste a la sortie du skip 2 ligne plus loin je continue d'évacuer les lignes en mémoire écran 
    {
        epd_screen_print_row(10);
    }
    else
    {
        // epd_output_row(5);
        epd_screen_skip_row();//ici je skip la ligne directement en basculant la synchro vertical.
    }
    skipping++;
}



static void IRAM_ATTR reset_lut(uint8_t *lut_mem, DrawMode_t mode) //reset le ligne du lut (lier au timing du mode noir et blanc)
{
    switch (mode)
    {
    case BLACK_ON_WHITE:
        memset(lut_mem, 0x55, (1 << 16)); // sur un mode noir sur blanc on met des 55 partout
        break;
    case WHITE_ON_BLACK: //ici je fait rien
    case WHITE_ON_WHITE:
        memset(lut_mem, 0xAA, (1 << 16)); //là je met des AA
        break;
    default:
        ESP_LOGW("epd_driver", "unknown draw mode %d!", mode);
        break;
    }
}


static void IRAM_ATTR update_LUT(uint8_t *lut_mem, uint8_t k, DrawMode_t mode) //je met a jour le lut en fonction des infos reçu
{
    if (mode == BLACK_ON_WHITE || mode == WHITE_ON_WHITE) //suivant le mode j'inverse la lecure de la talbe de référence le blanc deviens noir.
    {
        k = 15 - k;
    }
    //il s'agit de remettre la frame K avec une lut adapter par rapport a la duré max de 16 frame pour faire une image sur ls 16 niveau de gris.
    // reset the pixels which are not to be lightened / darkened 
    // any longer in the current frame
    for (uint32_t l = k; l < (1 << 16); l += 16) // on étage tous suivant sa valeurs
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



static void IRAM_ATTR nibble_shift_buffer_right(uint8_t *buf, uint32_t len)
//C'est utilisé dans provide_and_feed quand area.x % 2 == 1 — quand la zone commence sur un pixel impair, il faut décaler d'un quartet
//  pour aligner les pixels sur la bonne position dans le buffer 4bpp.
//Le carry initial à 0xF correspond à du blanc (valeur max) pour ne pas introduire de pixel noir parasite en début de ligne.
{
    uint8_t carry = 0xF;
    for (uint32_t i = 0; i < len; i++)
    {
        uint8_t val = buf[i];
        buf[i] = (val << 4) | carry;
        carry = (val & 0xF0) >> 4;
    }
}


/******************************************************************************/
/***        END OF FILE                                                     ***/
/******************************************************************************/
