// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#ifndef ERROR_H
#define ERROR_H

#include <errno.h>

#define error_setn_goto(errorp, type, info0, info1, label) do {error_set(errorp, type, info0, info1); goto label;} while(0)
#define error_set_typen_goto(errorp, type, label) do {error_set_type(errorp, type); goto label;} while(0)

typedef enum {
    ERROR_NO_ERROR,
    ERROR_OPENING_FILE,
    ERROR_MALLOC,
    ERROR_FSEEK,
    ERROR_FWRITE,
    ERROR_FILE_WAS_NULL,
    ERROR_FREAD,
    ERROR_COUNT,
} ErrorType;

typedef struct {
    ErrorType type;
    const char *info[2];
} Error;

void error_set(Error *error, ErrorType type, const char *info0, const char *info1);
void error_set_type(Error *error, ErrorType type);
char *error_to_char(ErrorType type);

#endif // ERROR_H
