/******************************************************************************/
/***        include files                                                   ***/
/******************************************************************************/

#ifndef _EPD_DEFINITION_
#define _EPD_DEFINITION_
/******************************************************************************/
/***        pin definitions                                               ***/
/******************************************************************************/

/* Config Reggister Control */
#define CFG_DATA GPIO_NUM_13
#define CFG_CLK GPIO_NUM_12
#define CFG_STR GPIO_NUM_0

/* Control Lines */
#define CKV GPIO_NUM_38
#define STH GPIO_NUM_40

/* Edges */
#define CKH GPIO_NUM_41

/* Data Lines */
#define D7 GPIO_NUM_7
#define D6 GPIO_NUM_6
#define D5 GPIO_NUM_5
#define D4 GPIO_NUM_4
#define D3 GPIO_NUM_3
#define D2 GPIO_NUM_2
#define D1 GPIO_NUM_1
#define D0 GPIO_NUM_8

/******************************************************************************/
/***        screen definitions                                               ***/
/******************************************************************************/
/**
 * @brief Width of the display area in pixels.
 */
#define EPD_WIDTH 960

/**
 * @brief Height of the display area in pixels.
 */
#define EPD_HEIGHT 540

/*
 * @brief number of bytes needed for one line of EPD pixel data.
 */

#define EPD_LINE_BYTES EPD_WIDTH / 4
// EPD_ROW_BUFFER_SIZE = EPD_WIDTH / 4 = 240 bytes, EPD_WIDTH / 4 + 8 bytes de padding pour l'alignement DMA.
#define EPD_ROW_BUFFER_SIZE (EPD_WIDTH / 4 + 8)

/*00 = no-op
01 = noir
10 = blanc
11 = no-op*/
//sur un octet donc 2 pixels
#define CLEAR_BYTE 0B10101010
#define DARK_BYTE 0B01010101


#ifndef _swap_int
#define _swap_int(a, b) \
{                   \
    int32_t t = a;      \
    a = b;          \
    b = t;          \
}
#endif

typedef enum
{
    BLACK =  0,
    WHITE =  1,
} Background_t;

/**
 * @brief The image drawing mode.
 */
typedef enum
{   BLACK_ON_WHITE = 1 << 0, /** Draw black / grayscale image on a white display. */
    WHITE_ON_WHITE = 1 << 1, /** "Draw with white ink" on a white display. */
    WHITE_ON_BLACK = 1 << 2, /** Draw with white ink on a black display. */
} DrawMode_t;

typedef enum
{
    LANDSCAPE = 0,
    PORTRAIT = 90,
    R_LANDSCAPE = 180,
    R_PORTRAIT = 270,
} Rotation_t;

extern Rotation_t screen_rotation;

/*----------------------------------------------*/
/* TJpgDec System Configurations R0.03          */
/*----------------------------------------------*/

#define	JD_SZBUF		512
/* Specifies size of stream input buffer */

#define JD_FORMAT		2
/* Specifies output pixel format.
/  0: RGB888 (24-bit/pix)
/  1: RGB565 (16-bit/pix)
/  2: Grayscale (8-bit/pix)
*/

#define	JD_USE_SCALE	1
/* Switches output descaling feature.
/  0: Disable
/  1: Enable
*/

#define JD_FASTDECODE	0
/* Optimization level
/  0: Basic optimization. Suitable for 8/16-bit MCUs.
/  1: + 32-bit barrel shifter. Suitable for 32-bit MCUs.
/  2: + Table conversion for huffman decoding (wants 6 << HUFF_BIT bytes of RAM)
*/

#endif
