#include "config.h"
#include "system.h"

/* ************************************************************************** */

// These warnings are only a problem using XC8-cc driver in C99 mode
#ifdef __XC8_CC_C99__

// Disable "unused variable" warning
#pragma warning disable 1090

// Disable warning spam about reset vectors
#pragma warning disable 2020

// Disable warning spam about unused functions
#pragma warning disable 520

// Disable "expression generates no code"
#pragma warning disable 759

// Disable "pointer in expression may have no targets"
#pragma warning disable 1498

#endif // __XC8_CC_C99__

/* ************************************************************************** */

void main(void) {
    startup();

    while (1) {
        // empty mainloop
    }
}