#ifndef _TOOLCHAIN_HOST_CHECK_H_
#define _TOOLCHAIN_HOST_CHECK_H_

/*
 * Optional helpers for host unit tests (*_test.c).
 * Not required — plain printf + return codes are fine.
 */

#include <stdio.h>

#define CHECK(cond)                                                                                \
    do {                                                                                           \
        if (!(cond)) {                                                                             \
            fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond);                       \
            return 1;                                                                              \
        }                                                                                          \
    } while (0)

#define CHECK_MSG(cond, msg)                                                                       \
    do {                                                                                           \
        if (!(cond)) {                                                                             \
            fprintf(stderr, "FAIL %s:%d: %s (%s)\n", __FILE__, __LINE__, #cond, (msg));          \
            return 1;                                                                              \
        }                                                                                          \
    } while (0)

#endif /* _TOOLCHAIN_HOST_CHECK_H_ */
