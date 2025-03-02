#ifndef METHOD_H
#define METHOD_H

typedef enum {
    METHOD_AA,
    METHOD_AX,
    METHOD_XA,
} Method;

const char *method_to_char(Method method);
Method method_from_char(const char *buf);

#endif // METHOD_H