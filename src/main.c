// Copyright © 2025 Lucas Martín
// Licensed under the MIT License. See the LICENSE file in the project root for full license text

#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

#include "include/buf.h"
#include "include/arg.h"
#include "include/error.h"
#include "include/slice.h"
#include "include/method.h"

#define STB_DS_IMPLEMENTATION
#include "include/stb_ds.h"

#ifdef _WIN32
#   define DELIM '\\'
#   define MILED '/'
#else
#   define DELIM '/'
#   define MILED '\\'
#endif

#ifndef UNUSED
#   define UNUSED(param) ((void)param)
#endif

#define N (2)
#define DEFAULT_METHOD (METHOD_XA)
#define INSTAGRAM_FILE_PATH ("/connections/followers_and_following/")
#define INSTAGRAM_FOLLOWERS_FILE ("followers_1.html")
#define INSTAGRAM_FOLLOWING_FILE ("following.html")
#define INSTAGRAM_FILE_NAMES ((char*[]){INSTAGRAM_FOLLOWERS_FILE, INSTAGRAM_FOLLOWING_FILE})
#define FILE_PREFIX_HTML ("<html>")
#define FILE_PREFIX_DIV ("<div")

typedef struct {
    const char *program;
    const char *program_path;
    Method method;
    FILE *stream_out[N];
    Buf paths[N];
    Buf out[N];
} Pargs;

typedef enum {
    PREFIX_NONE,
    PREFIX_HTML,
    PREFIX_DIV,
} Prefix;

typedef struct {
    char *key;
    int value;
} Dict;

Dict *dict_build(Buf buf);
Buf dict_build_base_from_raw(const char *contents, size_t len, const char *file, FILE *stream_out);
Buf dict_build_base_from_html(const char *contents, size_t len, const char *file, FILE *stream_out);
Buf dict_build_base_from_div(const char *contents, size_t len, const char *file, FILE *stream_out);

size_t dict_compar_to_raw(Dict *dict, const char *contents, size_t len, const char *file, FILE *stream_out);
size_t dict_compar_to_html(Dict *dict, const char *contents, size_t len, const char *file, FILE *stream_out);
size_t dict_compar_to_div(Dict *dict, const char *contents, size_t len, const char *file, FILE *stream_out);

Prefix prefix_from_char(const char *buffer);
const char *prefix_to_char(Prefix prefix);

bool starts_with(const char *buffer, const char *prefix);
bool starts_withxl(const char *buffer, const char *prefix, size_t plen);
void replace(char *buffer, const char old, const char new);
const char *find(const char *hay_stack, const char needle);
const char *findr(const char *hay_stack, const char needle);
size_t findi(const char *hay_stack, const char needle);
size_t findri(const char *hay_stack, const char needle);

void div_ensure_english(Slice contents, const char *file);

void usage(void);
void quit(int exit_code);
void swap_buf(Buf *a, Buf *b);
char *file_read(const char *file_path, size_t *readed_len);

void args_parse(void);
bool args_add_path(const char *path);
size_t arg_idx(const char *other, void *extra);
const char *arg_extract_set_value(const char *arg);

void print_error(const char *msg, ...);
void print_add_path_error(const char *path);
void print_matching_list_title(void);
void print_matching_list_end(size_t count);

ARG_DECLARE_FUNCTIONS_FOR(help);
ARG_DECLARE_FUNCTIONS_FOR(file_format_help);
ARG_DECLARE_FUNCTIONS_FOR(instagram_folder);
ARG_DECLARE_FUNCTIONS_FOR(method);
ARG_DECLARE_FUNCTIONS_FOR(file_X_out);

Arg ARGS[] = {
    ARG_DEFINE(help, "--help"),
    ARG_DEFINE(file_format_help, "--file-format-help"),
    ARG_DEFINE(instagram_folder, "--instagram-folder"),
    ARG_DEFINE(method, "--method"),
    ARG_DEFINE(file_X_out, "--file-X-out"),
};
#define ARG_COUNT (sizeof(ARGS) / sizeof(ARGS[0]))

int ARGC = 0;
char **ARGV = NULL;
Buf BUF = {0};
Pargs PARGS = {0};
Error ERROR = {0};
const Dict *DICT = NULL;

int main(int argc, char **argv) {

    ARGC = argc;
    ARGV = argv;
    PARGS = (Pargs){0};
    PARGS.program_path = arg_shift(&ARGC, &ARGV);
    const char *program = findr(PARGS.program_path, DELIM);
    PARGS.program = program ? program + 1 : PARGS.program_path;
    PARGS.method = DEFAULT_METHOD;
    
    args_parse();
    
    if(PARGS.method != DEFAULT_METHOD) {
        swap_buf(PARGS.paths + 0, PARGS.paths + 1);
        swap_buf(PARGS.out + 0, PARGS.out + 1);
    }

    for(size_t i = 0; i < N; ++i) {
        PARGS.stream_out[i] = fopen(PARGS.out[i].buf, "wb");
        if(!PARGS.stream_out[i] && PARGS.out[i].buf) {
            print_error("%s: Could not open file %s -> %s\n", PARGS.program, PARGS.out[i].buf, strerror(errno));
            quit(1);
        }
    }

    if(!PARGS.paths[0].buf || !PARGS.paths[1].buf) {
        int got = N;
        for(size_t i = 0; i < N; ++i) if(!PARGS.paths[i].buf) --got;
        print_error("%s: No input files. Needed %d but got %d ", PARGS.program, N, got);
        if(got) fprintf(stderr, "['%s'", PARGS.paths[0].buf);
        for(int i = 1; i < got; ++i) fprintf(stderr, ", '%s'", PARGS.paths[i].buf);
        if(got) fprintf(stderr, "]");
        fprintf(stderr, "\n");
        quit(1);
    }

    if(PARGS.out[0].buf && PARGS.out[1].buf && !strcmp(PARGS.out[0].buf, PARGS.out[1].buf)) {
        print_error("%s: Specified the same output file for file 1 and file 2 (%s). This is not permited\n", PARGS.program, PARGS.out[0].buf);
        quit(1);
    }

    size_t len;
    const char *contents = file_read(PARGS.paths[0].buf, &len);
    if(!contents) {
        print_error("%s: Could not get contents of '%s' (%s) -> %s\n", PARGS.program, PARGS.paths[0].buf, error_to_char(ERROR.type), ERROR.info[1]);
        if(ERROR.type == ERROR_MALLOC) fprintf(stderr, "Not enough mem to store the hole file\n");
        quit(1);
    }

    Prefix prefix = prefix_from_char(contents);
    switch(prefix) {
        case PREFIX_DIV:  BUF = dict_build_base_from_div (contents, len, PARGS.paths[0].buf, PARGS.stream_out[0]); break;
        case PREFIX_NONE: BUF = dict_build_base_from_raw (contents, len, PARGS.paths[0].buf, PARGS.stream_out[0]); break;
        case PREFIX_HTML: BUF = dict_build_base_from_html(contents, len, PARGS.paths[0].buf, PARGS.stream_out[0]); break;
    } free((char*)contents);

    Dict *dict = dict_build(BUF);
    DICT = dict;

    contents = file_read(PARGS.paths[1].buf, &len);
    if(!contents) {
        print_error("%s: Could not get contents of '%s' (%s) -> %s\n", PARGS.program, PARGS.paths[0].buf, error_to_char(ERROR.type), ERROR.info[1]);
        if(ERROR.type == ERROR_MALLOC) fprintf(stderr, "Not enough mem to store the hole file\n");
        quit(1);
    }

    size_t count = 0;
    prefix = prefix_from_char(contents);
    print_matching_list_title();
    switch(prefix) {
        case PREFIX_DIV:  count = dict_compar_to_div (dict, contents, len, PARGS.paths[1].buf, PARGS.stream_out[1]); break;
        case PREFIX_NONE: count = dict_compar_to_raw (dict, contents, len, PARGS.paths[1].buf, PARGS.stream_out[1]); break;
        case PREFIX_HTML: count = dict_compar_to_html(dict, contents, len, PARGS.paths[1].buf, PARGS.stream_out[1]); break;
    } free((char*)contents);
    print_matching_list_end(count);
    
    quit(0);
    return 0;
}

void usage(void) {
    size_t max = strlen(ARGS[0].alias);
    for(size_t i = 1; i < ARG_COUNT; ++i) {
        size_t len = strlen(ARGS[i].alias);
        if(max < len) max = len;
    }
    printf("usage: %s <file1> <file2> [commands]\n\n", PARGS.program);
    printf("commands:\n");
    for(size_t i = 0; i < ARG_COUNT; ++i) {
        printf("  %-*s    ", (int)max, ARGS[i].alias);
        ARGS[i].short_desc(ARGS[i], (char*)PARGS.program);
    }
}

void quit(int exit_code) {
    Dict *dict = (Dict*)DICT;
    if(exit_code) fprintf(stderr, "\nSee %s %s\n", PARGS.program, ARGS[0].alias);
    for(size_t i = 0; i < N; ++i) {
        buf_del(PARGS.out + i);
        buf_del(PARGS.paths + i);
        if(PARGS.stream_out[i]) fclose(PARGS.stream_out[i]);
    }
    shfree(dict);
    buf_del(&BUF);
    printf("%c<Exit Code %d>\n", '\n'*(!(bool)exit_code), exit_code);
    exit(exit_code);
}

void print_error(const char *msg, ...) {
    va_list va;
    va_start(va, msg);
    fprintf(stderr, "\033[0;31m");
    fprintf(stderr, "ERROR: ");
    fprintf(stderr, "\033[0m");
    vfprintf(stderr, msg, va);
    va_end(va);
}

const char *findr(const char *hay_stack, const char needle) {
    size_t len = strlen(hay_stack);
    for(size_t i = 0; i < len; ++i) if(hay_stack[len - i - 1] == needle) return hay_stack + (len - i - 1);
    return NULL;
}

bool starts_with(const char *buffer, const char *prefix) {
    size_t len = strlen(buffer);
    size_t plen = strlen(prefix);
    if(len < plen) return false;
    for(size_t i = 0; i < plen; ++i) if(prefix[i] != buffer[i]) return false;
    return true;
}

bool starts_withxl(const char *buffer, const char *prefix, size_t plen) {
    size_t len = strlen(buffer);
    if(len < plen) return false;
    for(size_t i = 0; i < plen; ++i) if(prefix[i] != buffer[i]) return false;
    return true;
}

void replace(char *buffer, const char old, const char new) {
    for(size_t i = 0; i < strlen(buffer); ++i) if(buffer[i] == old) buffer[i] = new;
}

const char *find(const char *hay_stack, const char needle) {
    for(size_t i = 0; i < strlen(hay_stack); ++i) if(hay_stack[i] == needle) return hay_stack + i;
    return NULL;
}

size_t findri(const char *hay_stack, const char needle) {
    size_t len = strlen(hay_stack);
    for(size_t i = 0; i < len; ++i) if(hay_stack[len - i - 1] == needle) return len - i - 1;
    return len;
}

size_t findi(const char *hay_stack, const char needle) {
    size_t len = strlen(hay_stack);
    for(size_t i = 0; i < len; ++i) if(hay_stack[i] == needle) return i;
    return len;
}

const char *arg_extract_set_value(const char *arg) {
    const char *ptr = find(arg, '=');
    return ptr ? ptr + 1 : arg_shift(&ARGC, &ARGV);
}

char *file_read(const char *file_path, size_t *readed_len) {
    error_set(&ERROR, ERROR_NO_ERROR, file_path, NULL);
    FILE *f = fopen(file_path, "rb");
    char *buffer = NULL;
    if(f) {
        if(fseek(f, 0, SEEK_END) == 0) {
            size_t len = ftell(f);
            rewind(f);
            buffer = malloc(sizeof(char) * (len + 1));
            if(buffer == NULL) error_set_typen_goto(&ERROR, ERROR_MALLOC, defer1);
            size_t rlen;
            if((rlen = fread(buffer, sizeof(char), len, f)) == len) {
                buffer[len] = '\0';
                if(readed_len) *readed_len = len;
            } else error_setn_goto(&ERROR, ERROR_FREAD, file_path, strerror(errno), defer2);
        } else error_setn_goto(&ERROR, ERROR_FSEEK, file_path, strerror(errno), defer1);
        fclose(f);
    } else error_set(&ERROR, ERROR_OPENING_FILE, file_path, strerror(errno));
    return buffer;
    defer2:
        free(buffer);
        buffer = NULL;
    defer1:
        fclose(f);
        return buffer;
}

const char *prefix_to_char(Prefix prefix) {
    switch(prefix) {
        case PREFIX_HTML: return FILE_PREFIX_HTML;
        case PREFIX_DIV: return FILE_PREFIX_DIV;
        default: return NULL;
    }
}

Prefix prefix_from_char(const char *buffer) {
    if(starts_with(buffer, prefix_to_char(PREFIX_HTML))) return PREFIX_HTML;
    if(starts_with(buffer, prefix_to_char(PREFIX_DIV))) return PREFIX_DIV;
    return PREFIX_NONE;
}

Buf dict_build_base_from_raw(const char *contents, size_t len, const char *file, FILE *stream_out) {
    Buf buf = {0};
    size_t count = 0;
    Slice slice = slice_newl(contents, len);
    while(slice.len > 0) {
        Slice name = slice_slice(&slice, '\n', true);
        Slice chop = slice_slices(&name, slice_new(">>"), true);
        if(!name.len) name = chop;
        name = slice_trim(name);
        if(name.len > 0) {
            char *dst = buf_app_slice(&buf, name);
            if(stream_out) fprintf(stream_out, "%zu >> %s\n", ++count, dst);
            if(!dst) {
                print_error("%s: Ran out of mem when trying to store the list extracted from '%s'\n", PARGS.program, file);
                printf("This is a terminal error\n");
                quit(1);
            }
        }
    } return buf;
}

Buf dict_build_base_from_html(const char *contents, size_t len, const char *file, FILE *stream_out) {
    Buf buf = {0};
    size_t count = 0;
    Slice dcs = slice_new(".com/");
    Slice slice = slice_newl(contents, len);
    while(slice.len > 0) {
        (void)slice_slices(&slice, dcs, true);
        Slice name = slice_trim(slice_slice(&slice, '"', true));
        if(name.len > 0) {
            char *dst = buf_app_slice(&buf, name);
            if(stream_out) fprintf(stream_out, "%zu >> %s\n", ++count, dst);
            if(!dst) {
                print_error("%s: Ran out of mem when trying to store the list extracted from '%s'\n", PARGS.program, file);
                printf("This is a terminal error\n");
                quit(1);
            }
        }
    } return buf;
}

Buf dict_build_base_from_div(const char *contents, size_t len, const char *file, FILE *stream_out) {
    Buf buf = {0};
    size_t count = 0;
    Slice aeq = slice_new("alt=\"");
    Slice slice = slice_newl(contents, len);
    div_ensure_english(slice, file);
    while(slice.len > 0) {
        (void)slice_slices(&slice, aeq, true);
        Slice name = slice_trim(slice_slice(&slice, '\'', true));
        if(name.len > 0) {
            char *dst = buf_app_slice(&buf, name);
            if(stream_out) fprintf(stream_out, "%zu >> %s\n", ++count, dst);
            if(!dst) {
                print_error("%s: Ran out of mem when trying to store the list extracted from '%s'\n", PARGS.program, file);
                printf("This is a terminal error\n");
                quit(1);
            }
        }
    } return buf;
}

size_t dict_compar_to_raw(Dict *dict, const char *contents, size_t len, const char *file, FILE *stream_out) {
    UNUSED(file);
    Buf buf = {0};
    size_t count = 0;
    size_t count2 = 0;
    Slice slice = slice_newl(contents, len);
    while(slice.len > 0) {
        Slice name = slice_slice(&slice, '\n', true);
        Slice chop = slice_slices(&name, slice_new(">>"), true);
        if(!name.len) name = chop;
        name = slice_trim(name);
        if(name.len > 0) {
            buf_put_slice(&buf, name);
            if(stream_out) fprintf(stream_out, "%zu >> %s\n", ++count2, buf.buf);
            if((PARGS.method == METHOD_AA) ^ (shgeti(dict, buf.buf) == -1)) printf("%zu >> %.*s\n", ++count, (int)name.len, name.ptr);
        }
    } buf_del(&buf);
    return count;
}

size_t dict_compar_to_html(Dict *dict, const char *contents, size_t len, const char *file, FILE *stream_out) {
    UNUSED(file);
    Buf buf = {0};
    size_t count = 0;
    size_t count2 = 0;
    Slice dcs = slice_new(".com/");
    Slice slice = slice_newl(contents, len);
    while(slice.len > 0) {
        (void)slice_slices(&slice, dcs, true);
        Slice name = slice_trim(slice_slice(&slice, '"', true));
        if(name.len > 0) {
            buf_put_slice(&buf, name);
            if(stream_out) fprintf(stream_out, "%zu >> %s\n", ++count2, buf.buf);
            if((PARGS.method == METHOD_AA) ^ (shgeti(dict, buf.buf) == -1)) printf("%zu >> %.*s\n", ++count, (int)name.len, name.ptr);
        }
    } buf_del(&buf);
    return count;
}

size_t dict_compar_to_div(Dict *dict, const char *contents, size_t len, const char *file, FILE *stream_out) {
    Buf buf = {0};
    size_t count = 0;
    size_t count2 = 0;
    Slice aeq = slice_new("alt=\"");
    Slice slice = slice_newl(contents, len);
    div_ensure_english(slice, file);
    while(slice.len > 0) {
        (void)slice_slices(&slice, aeq, true);
        Slice name = slice_trim(slice_slice(&slice, '\'', true));
        if(name.len > 0) {
            buf_put_slice(&buf, name);
            if(stream_out) fprintf(stream_out, "%zu >> %s\n", ++count2, buf.buf);
            if((PARGS.method == METHOD_AA) ^ (shgeti(dict, buf.buf) == -1)) printf("%zu >> %.*s\n", ++count, (int)name.len, name.ptr);
        }
    } buf_del(&buf);
    return count;
}

Dict *dict_build(Buf buf) {
    Dict *dict = NULL;
    char *ptr = buf.buf;
    while(ptr < buf.buf + buf.len) {
        shput(dict, ptr, 1);
        ptr += strlen(ptr) + 1;
    } return dict;
}

void div_ensure_english(Slice contents, const char *file) {
    if(!slice_find(contents, slice_new("'s profile picture"), NULL)) {
        print_error("%s: Could not parse <div> file '%s'\n", PARGS.program, file);
        fprintf(stderr, "Seems like your Instagram's language is NOT English\n");
        fprintf(stderr, "Please try switching it to English in settings and try again or try other file formats\n\n");
        fprintf(stderr, "[NOTE]: It could also be that no followers/ing where present on that <div> file\n");
        quit(1);
    }
}

void *arg_funcs_help_desc(Arg self, void *extra) {
    UNUSED(extra);
    printf("Displays general usage information. If followed by another command, provides detailed help about that command\n\n");
    printf("Examples:\n");    
    printf("  %s %-*s   # Show general help\n", PARGS.program, (int)(strlen(ARGS[4].alias) + strlen(self.alias)), self.alias);
    printf("  %s %s %s  # Show help for %s\n", PARGS.program, self.alias, ARGS[4].alias, ARGS[4].alias);
    return NULL;
}

void *arg_funcs_help_short_desc(Arg self, void *extra) {
    UNUSED(extra);
    printf("Show general help or usage details for a specific command (e.g., %s %s %s)\n", PARGS.program, self.alias, ARGS[3].alias);
    return NULL;
}

bool arg_funcs_help_match(Arg self, const char *other, void *extra) {
    UNUSED(extra);
    return !strcmp(self.alias, other);
}

void *arg_funcs_help_action(Arg self, void *extra) {
    UNUSED(extra);
    const char *next = arg_shift(&ARGC, &ARGV);
    if(next && starts_with(next, "--")) {
        for(size_t i = 0; i < ARG_COUNT; ++i) {
            if(ARGS[i].match(ARGS[i], next, NULL)) {
                ARGS[i].desc(ARGS[i], NULL);
                quit(0);
            }
        }
        print_error("%s: Command after %s command (%s) is unknown\n", PARGS.program, self.alias, next);
        quit(1);
    }
    usage();
    quit(0);
    return NULL;
}

void *arg_funcs_file_format_help_desc(Arg self, void *extra) {
    UNUSED(self);
    UNUSED(extra);
    printf("Explains the accepted file formats for input lists\n\n");
    self.action(self, NULL);
    return NULL;
}

void *arg_funcs_file_format_help_short_desc(Arg self, void *extra) {
    UNUSED(self);
    UNUSED(extra);
    printf("Displays information about supported input file formats\n");
    return NULL;
}

bool arg_funcs_file_format_help_match(Arg self, const char *other, void *extra) {
    UNUSED(extra);
    return !strcmp(self.alias, other);
}

void *arg_funcs_file_format_help_action(Arg self, void *extra) {
    UNUSED(self);
    UNUSED(extra);
    printf("Accepted formats:\n");
    printf("  - Raw text files: Each line is considered a unique element\n");
    printf("      Option 1:\n");
    printf("        instance1\n");
    printf("        instance2\n");
    printf("        instance3\n");
    printf("        ...\n");
    printf("      Option 2:\n");
    printf("        %%s >> instance1\n");
    printf("        %%s >> instance2\n");
    printf("        %%s >> instance3\n");
    printf("        ...\n");
    printf("  - HTML files: Extracts Instagram followers/following from downloaded data\n");
    printf("  - <div> elements: Allows manual extraction by copying and pasting a <div> containing Instagram followers/following\n\n");
    printf("File detection:\n");
    printf("  - Files starting with \"%s\" are treated as HTML\n", FILE_PREFIX_HTML);
    printf("  - Files starting with \"%s\" are treated as <div> elements\n", FILE_PREFIX_DIV);
    printf("  - Otherwise, they are treated as plain text\n");
    quit(0);
    return NULL;
}

void *arg_funcs_instagram_folder_desc(Arg self, void *extra) {
    UNUSED(extra);
    printf("Specifies the path to an Instagram data folder, using it to extract the following files:\n");
    printf("  - '%s' as the first list/file\n", INSTAGRAM_FOLLOWERS_FILE);
    printf("  - '%s' as the second list/file\n\n", INSTAGRAM_FOLLOWING_FILE);
    printf("How to get your Instagram data:\n");
    printf("  1. Go to Instagram > Settings > Your Activity > Download your information (Written on (Date) 03/2025)\n");
    printf("  2. Request a download in HTML format (JSON parsing is not implemented yet)\n");
    printf("  3. Once downloaded, extract the ZIP file and use its root folder with this option (beware, it might spill all the files everywhere)\n\n");
    printf("This option accepts both:\n");
    printf("  - An argument with '=' (e.g., %s %s=<path/to/folder>)\n", PARGS.program, self.alias);
    printf("  - A space-separated argument (e.g., %s %s <path/to/folder>)\n", PARGS.program, self.alias);
    return NULL;
}

void *arg_funcs_instagram_folder_short_desc(Arg self, void *extra) {
    UNUSED(extra);
    printf("Use an Instagram data folder as input (see '%s %s %s')\n", PARGS.program, ARGS[0].alias, self.alias);
    return NULL;
}

bool arg_funcs_instagram_folder_match(Arg self, const char *other, void *extra) {
    UNUSED(extra);
    if(!strcmp(self.alias, other)) return true;
    buf_put(&BUF, self.alias);
    buf_cat(&BUF, "=");
    return starts_with(other, BUF.buf);
}

void *arg_funcs_instagram_folder_action(Arg self, void *extra) {
    const char *ptr = arg_extract_set_value(extra);
    if(!ptr || *ptr == '\0') {
        print_error("%s: Expected folder after %s command\n", PARGS.program, self.alias);
        quit(1);
    }
    if(starts_with(ptr, "--")) {
        print_error("%s: Expected folder after %s command, instead got another command (%s)\n", PARGS.program, self.alias, ptr);
        quit(1);
    }
    for(size_t i = 0; i < N; ++i) {
        buf_res(&BUF);
        buf_catm(&BUF, ptr, INSTAGRAM_FILE_PATH, INSTAGRAM_FILE_NAMES[i]);
        replace(BUF.buf, MILED, DELIM);
        if(!args_add_path(BUF.buf)) {
            print_add_path_error(BUF.buf);
            quit(1);
        }
    } 
    return NULL;
}

void *arg_funcs_method_desc(Arg self, void *extra) {
    UNUSED(extra);
    printf("Defines how the input lists/files are compared. Available methods:\n");
    printf("  - %s: Elements present in both lists/files\n", method_to_char(METHOD_AA));
    printf("  - %s: Elements in the first list/file but not in the second\n", method_to_char(METHOD_AX));
    printf("  - %s: Elements in the second list/file but not in the first\n\n", method_to_char(METHOD_XA));
    printf("This option accepts both:\n");
    printf("  - An argument with '=' (e.g., %s %s=%s)\n", PARGS.program, self.alias, method_to_char(METHOD_XA));
    printf("  - A space-separated argument (e.g., %s %s %s)\n\n", PARGS.program, self.alias, method_to_char(METHOD_XA));
    printf("Default method is set to be %s\n", method_to_char(DEFAULT_METHOD));
    return NULL;
}

void *arg_funcs_method_short_desc(Arg self, void *extra) {
    UNUSED(self);
    UNUSED(extra);
    printf("Set the list/file comparison method (%s, %s, %s) (default: %s)\n", method_to_char(METHOD_AA), method_to_char(METHOD_AX), method_to_char(METHOD_XA), method_to_char(DEFAULT_METHOD));
    return NULL;
}

bool arg_funcs_method_match(Arg self, const char *other, void *extra) {
    UNUSED(extra);
    if(!strcmp(self.alias, other)) return true;
    buf_put(&BUF, self.alias);
    buf_cat(&BUF, "=");
    return starts_with(other, BUF.buf);
}

void *arg_funcs_method_action(Arg self, void *extra) {
    const char *ptr = arg_extract_set_value(extra);
    if(!ptr || *ptr == '\0') {
        print_error("%s: Expected method after %s command\n", PARGS.program, self.alias);
        quit(1);
    }
    if(starts_with(ptr, "--")) {
        print_error("%s: Expected method after %s command, instead got another command (%s)\n", PARGS.program, self.alias, ptr);
        quit(1);
    }
    Method method = method_from_char(ptr);
    if(method == (Method)(-1)) {    
        print_error("%s: Got unknown method (%s) after %s command\n", PARGS.program, ptr, self.alias);
        quit(1);
    }
    PARGS.method = method;
    return NULL;
}

void *arg_funcs_file_X_out_desc(Arg self, void *extra) {
    UNUSED(extra);
    printf("Specifies the output file where the instances of list/file <X> will be saved\n");
    printf("<X> must be in [1, %d], referring to the first, second, ... input lists/files\n\n", N);
    printf("This option accepts both:\n");
    printf("  - An argument with '=' (e.g., %s %s=result.txt)\n", PARGS.program, self.alias);
    printf("  - A space-separated argument (e.g., %s %s result.txt)\n\n", PARGS.program, self.alias);
    printf("Example:\n");
    printf("  %s file1 file2 %s=result.txt  # Save the list/file <X> instances to 'result.txt'\n", PARGS.program, self.alias);
    printf("  %s file1 file2 %s=out.txt     # Save the list/file <X> instances to 'out.txt'\n", PARGS.program, self.alias);
    return NULL;
}

void *arg_funcs_file_X_out_short_desc(Arg self, void *extra) {
    UNUSED(self);
    UNUSED(extra);
    printf("Set the output file for list/file <X>\n");
    return NULL;
}

bool arg_funcs_file_X_out_match(Arg self, const char *other, void *extra) {
    UNUSED(extra);
    size_t X = findi(self.alias, 'X');
    if(!starts_withxl(other, self.alias, X)) return false;
    const char *dash = find(other + X, '-');
    if(!dash || (dash - other - X) == 0) return false;
    size_t idx = findri(self.alias, '-');
    buf_put(&BUF, self.alias + idx);
    buf_cat(&BUF, "=");
    return !strcmp(dash, self.alias + idx) || starts_with(dash, BUF.buf);
}

void *arg_funcs_file_X_out_action(Arg self, void *extra) {
    const char *ptr = arg_extract_set_value(extra);
    size_t X = findi(self.alias, 'X');
    int target = *((char*)extra + X) - '1';
    if(!(0 <= target && target < N) || *((char*)extra + X + 1) != '-') {
        print_error("%s: Target specified by %s command is invalid\n", PARGS.program, self.alias);
        fprintf(stderr, "X needs to be a number that belongs to [1, %d], instead got %.*s\n", N, (int)(findri(extra, '-') - X), (char*)extra + X);
        quit(1);    
    }
    if(!ptr || *ptr == '\0') {
        print_error("%s: Expected output path after %s command\n", PARGS.program, self.alias);
        quit(1);
    }
    if(starts_with(ptr, "--")) {
        print_error("%s: Expected output path after %s command, instead got another command (%s)\n", PARGS.program, self.alias, ptr);
        quit(1);
    }
    if((PARGS.out + target)->buf) {
        print_error("%s: Tried to specify output path ('%s') with '%s' for file/list %d when it already had an output path specified ('%s')\n", PARGS.program, ptr, extra, target + 1, (PARGS.out + target)->buf);
        quit(1);
    }
    buf_put(PARGS.out + target, ptr);
    return NULL;
}

void print_add_path_error(const char *path) {
    print_error("%s: You only can specify %d files\n", PARGS.program, N);
    fprintf(stderr, "Tried to add '%s' when ['%s'", path, PARGS.paths[0].buf);
    for(size_t i = 1; i < N; ++i) fprintf(stderr, ", '%s'", PARGS.paths[i].buf);
    fprintf(stderr, "] were already specified\n");
}

bool args_add_path(const char *path) {
    for(size_t i = 0; i < N; ++i) {
        if(!PARGS.paths[i].buf) {
            buf_put(&PARGS.paths[i], path);
            return true;
        } 
    } return false;
}

size_t arg_idx(const char *other, void *extra) {
    for(size_t i = 0; i < ARG_COUNT; ++i) if(ARGS[i].match(ARGS[i], other, extra)) return i;
    return ARG_COUNT;
}

void args_parse(void) {
    while(ARGC > 0) {
        const char *arg = arg_shift(&ARGC, &ARGV);
        size_t idx = arg_idx(arg, NULL);
        if(idx < ARG_COUNT) {
            ARGS[idx].action(ARGS[idx], (void*)arg);
        } else if(starts_with(arg, "--")) {
            print_error("%s: Command '%s' is unknown\n", PARGS.program, arg);
            quit(1);
        } else if(!args_add_path(arg)) {
            print_add_path_error(arg);
            quit(1);
        }
    }
}

void swap_buf(Buf *a, Buf *b) {
    Buf temp = *a;
    *a = *b;
    *b = temp;
}

void print_matching_list_title(void) {
    switch(PARGS.method) {
        case METHOD_AA: 
            printf("=====================MATCHING LIST=====================\n");
            break;
        default:
            printf("===================NOT MATCHING LIST===================\n");
            break;
    }
}

void print_matching_list_end(size_t count) {
    switch(PARGS.method) {
        case METHOD_AA: 
            printf("===================MATCHING LIST END===================\n");
            printf("Total matches = %zu\n", count);
            break;
        default:
            printf("=================NOT MATCHING LIST END=================\n");
            printf("Total mismatches = %zu\n", count);
            break;
    }
}
