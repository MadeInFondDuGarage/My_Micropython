add_library(usermod_T547 INTERFACE)

target_compile_definitions(usermod_T547 INTERFACE
    MODULE_T547_ENABLED=1
    MICROPY_PY_FILE_LIKE=1
)

# Chemin vers les sources LilyGo-EPD47 esp32s3
set(LILYGO_EPD_DIR ${CMAKE_CURRENT_LIST_DIR}/epd_driver)

target_sources(usermod_T547 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}/t547.c
    ${LILYGO_EPD_DIR}/epd_driver.c
    ${LILYGO_EPD_DIR}/ed047tc1.c
    ${LILYGO_EPD_DIR}/i2s.c
    ${LILYGO_EPD_DIR}/rmt.c
)

target_include_directories(usermod_T547 INTERFACE
    ${CMAKE_CURRENT_LIST_DIR}
    ${LILYGO_EPD_DIR}
)

target_link_libraries(usermod INTERFACE usermod_T547 idf::esp_lcd)
