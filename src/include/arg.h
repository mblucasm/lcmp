// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#ifndef ARG_H
#define ARG_H

#include <stdbool.h>

#define ARG_DEFINE(DEFINE_NAME, Alias) {.alias = Alias, .desc = arg_funcs_##DEFINE_NAME##_desc, .short_desc = arg_funcs_##DEFINE_NAME##_short_desc, .match = arg_funcs_##DEFINE_NAME##_match, .action = arg_funcs_##DEFINE_NAME##_action}
#define ARG_DECLARE_FUNCTIONS_FOR(DEFINE_NAME) \
    void *arg_funcs_##DEFINE_NAME##_desc(Arg self, void *extra); \
    void *arg_funcs_##DEFINE_NAME##_short_desc(Arg self, void *extra); \
    bool arg_funcs_##DEFINE_NAME##_match(Arg self, const char *other, void *extra); \
    void *arg_funcs_##DEFINE_NAME##_action(Arg self, void *extra)
//

typedef struct Arg Arg;
typedef bool (*ArgMatch)(Arg self, const char *other, void *extra);
typedef void *(*ArgDesc)(Arg self, void *extra);
typedef void *(*ArgAction)(Arg self, void *extra);

struct Arg {
    const char *alias;
    ArgDesc desc;
    ArgDesc short_desc;
    ArgMatch match;
    ArgAction action;
};

char *arg_shift(int *argc, char ***argv);

#endif // ARG_H
