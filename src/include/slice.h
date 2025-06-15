// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#ifndef SLICE_H
#define SLICE_H

#include <stddef.h>
#include <stdbool.h>

typedef struct {
    const char *ptr;
    size_t len;
} Slice;

Slice slice_new(const char *ptr);
Slice slice_newl(const char *ptr, size_t len);
Slice slice_slice(Slice *s, const char delim, bool skipDelim);
Slice slice_slices(Slice *s, Slice delim, bool skipDelim);
Slice slice_trim_left(Slice s);
Slice slice_trim_right(Slice s);
Slice slice_trim(Slice s);
bool slice_find(Slice hayStack, Slice needle, size_t *idx);
bool slice_eq(Slice s1, Slice s2);

#endif // SLICE_H
