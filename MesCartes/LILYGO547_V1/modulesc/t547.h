#ifndef __t547_H__
#define __t547_H__

#include "py/runtime.h"
#include "py/objstr.h"


typedef struct _t547_obj_t
{
    mp_obj_base_t base;
    bool owns_fb;
    uint8_t *front_fb;    // framebuffer
} t547_obj_t;

mp_obj_t t547_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args);

#endif
