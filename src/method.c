// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#include "include/method.h"
#include <string.h>

const char *method_to_char(Method method) {
    switch(method) {
        case METHOD_AA: return "AA";
        case METHOD_AX: return "AX";
        case METHOD_XA: return "XA";
        default: return NULL;
    }
}

Method method_from_char(const char *buf) {
    if(!buf) return -1; 
    if(strcmp(buf, method_to_char(METHOD_AA)) == 0) return METHOD_AA;
    if(strcmp(buf, method_to_char(METHOD_AX)) == 0) return METHOD_AX;
    if(strcmp(buf, method_to_char(METHOD_XA)) == 0) return METHOD_XA;
    return -1;
}
