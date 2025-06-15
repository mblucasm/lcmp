// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#include "include/slice.h"
#include <ctype.h>
#include <string.h>

Slice slice_new(const char *ptr) {
    return (Slice) {
        .ptr = ptr,
        .len = strlen(ptr),
    };
}

Slice slice_newl(const char *ptr, size_t len) {
    return (Slice) {
        .ptr = ptr,
        .len = len,
    };
}

Slice slice_slice(Slice *s, const char delim, bool skipDelim) {
    size_t i = 0;
    while (i < s->len && s->ptr[i] != delim) ++i;
    Slice ret = slice_newl(s->ptr, i);
    s->ptr += i;
    s->len -= i;
    if(skipDelim && s->len != 0) {
        ++s->ptr;
        --s->len;
    } return ret;
}

bool slice_find(Slice hayStack, Slice needle, size_t *idx) {
    if(needle.len > hayStack.len) return false;
    for(size_t i = 0; i < hayStack.len - needle.len + 1; ++i) {
        if(hayStack.ptr[i] == needle.ptr[0]) {
            if(slice_eq(slice_newl(hayStack.ptr + i, needle.len), needle)) {
                if(idx) *idx = i;
                return true;
            }
        }
    } return false;
}

bool slice_eq(Slice s1, Slice s2) {
    if(s1.len != s2.len) return false;
    if(s1.len == 0) return true;
    return memcmp(s1.ptr, s2.ptr, sizeof(char) * s1.len) == 0;
}

Slice slice_slices(Slice *s, Slice delim, bool skipDelim) {
    size_t idx  = s->len;
    slice_find(*s, delim, &idx);
    Slice rem = slice_newl(s->ptr, idx);
    s->ptr += idx;
    s->len -= idx;
    if(skipDelim && s->len >= delim.len) {
        s->ptr += delim.len;
        s->len -= delim.len;
    }
    return rem;
}

Slice slice_trim_left(Slice s) {
    size_t i = 0;
    while(i < s.len && isspace(s.ptr[i])) ++i;
    return slice_newl(s.ptr + i, s.len - i);
}

Slice slice_trim_right(Slice s) {
    size_t i = 0;
    while(i < s.len && isspace(s.ptr[s.len - i - 1])) ++i;
    return slice_newl(s.ptr, s.len - i);
}

Slice slice_trim(Slice s) {
    return slice_trim_left(slice_trim_right(s));
}
