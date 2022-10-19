#ifndef _SYSTEM_H_
#define _SYSTEM_H_

#include <stdint.h>

/* ************************************************************************** */
/*  System information

    Various information about the system, made available at runtime.
*/

// product name
extern const char productName[];

// product software version
extern const char productVersion[];

// compilation information
extern const uint16_t xc8Version;
extern const char processorModel[];
extern const char compileDate[];
extern const char compileTime[];

/* ************************************************************************** */

// initialize the system
extern void startup(void);

#endif // _SYSTEM_H_