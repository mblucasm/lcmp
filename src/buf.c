// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#include "include/buf.h"
#include <string.h>
#include <stdlib.h>
#include <stdarg.h>

static size_t maxst(size_t a, size_t b) {
    return a < b ? b : a;
}

bool buf_cat(Buf *buf, const char *cat) {
    size_t len = strlen(cat);
    if(buf->cap < buf->len + len + 1) {
        size_t newcap = buf->cap + maxst(BUFCAP, len + 1);
        char *dst = realloc(buf->buf, sizeof(char) * newcap);
        if(dst == NULL) return false;
        buf->cap = newcap;
        buf->buf = dst;
    } 
    memcpy(buf->buf + (sizeof(char) * buf->len), cat, sizeof(char) * len);
    buf->len += len;
    buf->buf[buf->len] = '\0';
    return true;
}

bool buf_put(Buf *buf, const char *put) {
    size_t len = strlen(put);
    if(buf->cap < len + 1) {
        size_t newcap = buf->cap + maxst(BUFCAP, len + 1);
        char *dst = realloc(buf->buf, sizeof(char) * newcap);
        if(dst == NULL) return false;
        buf->cap = newcap;
        buf->buf = dst;
    } 
    memcpy(buf->buf, put, sizeof(char) * len);
    buf->len = len;
    buf->buf[buf->len] = '\0';
    return true;
}

bool _buf_catm(Buf *buf, ...) {
    char *varg;
    va_list va;
    va_start(va, buf);
    bool ret = true;
    while((varg = va_arg(va, char*)) != NULL) {
        if(!buf_cat(buf, varg)) {
            ret = false;
            break;
        }
    }
    va_end(va);
    return ret;
}

char *buf_app_slice(Buf *buf, Slice slice) {
    if(buf->cap < buf->len + 1 + slice.len + 1) {
        size_t newcap = buf->cap + maxst(BUFCAP, 1 + slice.len + 1);
        char *dst = realloc(buf->buf, sizeof(char) * newcap);
        if(dst == NULL) return NULL;
        buf->cap = newcap;
        buf->buf = dst;
    } 
    char *dst = buf->buf + (sizeof(char) * (buf->len + (buf->len != 0)));
    memcpy(dst, slice.ptr, sizeof(char) * slice.len);
    buf->len += slice.len + (buf->len != 0);
    buf->buf[buf->len] = '\0';
    return dst;
}

bool buf_put_slice(Buf *buf, Slice slice) {
    if(buf->cap < slice.len + 1) {
        size_t newcap = buf->cap + maxst(BUFCAP, slice.len + 1);
        char *dst = realloc(buf->buf, sizeof(char) * newcap);
        if(dst == NULL) return false;
        buf->cap = newcap;
        buf->buf = dst;
    } 
    memcpy(buf->buf, slice.ptr, sizeof(char) * slice.len);
    buf->len = slice.len;
    buf->buf[buf->len] = '\0';
    return true;
}

void buf_res(Buf *buf) {
    buf->buf = NULL;
    buf->cap = 0;
    buf->len = 0;
}

void buf_del(Buf *buf) {
    free(buf->buf);
    buf_res(buf);
}
