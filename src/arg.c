// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#include "include/arg.h"
#include <stddef.h>

char *arg_shift(int *argc, char ***argv) {
    char *arg = NULL;
    if(*argc > 0) {
        arg = **argv;
        --(*argc); 
        ++(*argv);
    } return arg;
}
