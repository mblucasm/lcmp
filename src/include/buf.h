// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#ifndef BUF_H
#define BUF_H

#include <stddef.h>
#include <stdbool.h>
#include "slice.h"

#define BUFCAP (1024)
#define buf_catm(bufp, ...) _buf_catm((bufp), __VA_ARGS__, NULL)

typedef struct {
    char *buf;
    size_t len;
    size_t cap;
} Buf;

bool _buf_catm(Buf *buf, ...);
bool buf_put(Buf *buf, const char *put);
bool buf_cat(Buf *buf, const char *cat);
void buf_res(Buf *buf);
void buf_del(Buf *buf);
bool buf_put_slice(Buf *buf, Slice slice);
char *buf_app_slice(Buf *buf, Slice slice);

#endif // BUF_H
