#pragma once

#ifndef ALWAYS_INLINE
#    define ALWAYS_INLINE inline __attribute__((always_inline))
#endif

#ifdef __cplusplus
#    ifndef __BEGIN_CDECLS
#        define __BEGIN_CDECLS extern "C" {
#        define __END_CDECLS }
#    else
#        define __BEGIN_CDECLS
#        define __END_CDECLS
#    endif
#endif