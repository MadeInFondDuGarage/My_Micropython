// mpconfigboard.h

// ------------------------
// Identité de la carte
// ------------------------
#define MICROPY_HW_BOARD_NAME        "2_SCREEN_E_INK"
#define MICROPY_HW_MCU_NAME          "ESP32S3"

// ------------------------
// Modules MicroPython
// ------------------------
// Réseau (utilise lwIP/IDF). Aligné avec CONFIG_ESP_WIFI_ENABLED=y dans sdkconfig.board.
#define MICROPY_PY_NETWORK           (0)
#define MICROPY_PY_NETWORK_WLAN      (0)

// Bluetooth via NimBLE. Aligné avec CONFIG_BT_ENABLED=y et CONFIG_BT_NIMBLE_ENABLED=y.
#define MICROPY_PY_BLUETOOTH         (0)
#define MICROPY_BLUETOOTH_NIMBLE     (0)
#define MICROPY_PY_ESPNOW            (0)

// ------------------------
// Broches "par défaut" (facultatif, à adapter à TON PCB)
// ------------------------
#define MICROPY_VFS_ROM              (1)

#define MICROPY_PY_MACHINE_I2S       (0)

#define MICROPY_PY_MACHINE_DAC       (0)

// I2C0 par défaut : SCL=GPIO9, SDA=GPIO8
#define MICROPY_HW_I2C0_SCL          (17)
#define MICROPY_HW_I2C0_SDA          (18)

// SPI "par défaut" : SCK=GPIO12, MOSI=GPIO11, MISO=GPIO13, CS=GPIO10
#define MICROPY_HW_SPI_SCK           (11)
#define MICROPY_HW_SPI_MOSI          (15)
#define MICROPY_HW_SPI_MISO          (16)
#define MICROPY_HW_SPI_CS            (42)


// UART0 "par défaut" (si tu veux utiliser un UART en plus de l’USB-CDC) : TX=GPIO43, RX=GPIO44

#define MICROPY_HW_UART0_TX          (37)
#define MICROPY_HW_UART0_RX          (36)

// Ne pas mapper USB D-/D+ (ESP32-S3 utilise USB interne sur GPIO19/20)
#define MICROPY_PY_MACHINE_BITSTREAM  (0)
/*#ifdef SOC_RMT_SUPPORTED*/
//#define SOC_RMT_SUPPORTED              (0)
/*#else
#define SOC_RMT_SUPPORTED              (0)
#endif
*/

