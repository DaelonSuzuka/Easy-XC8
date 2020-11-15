#ifndef _PROJECT_VARIABLES_H_
#define _PROJECT_VARIABLES_H_

#include <stdint.h>

/* ************************************************************************** */
/*  Project Information

    This is data that's pulled from project.yaml and other sources
*/
/* [[[cog

cog.outl()
cog.outl(f'#define PRODUCT_NAME "{utils.project.name}"')
cog.outl(f'#define PRODUCT_VERSION "{utils.project.sw_version}"')
cog.outl()

]]] */

#define PRODUCT_NAME "Project-Template"
#define PRODUCT_VERSION "0.0.1"

/* [[[end]]] */

/* ************************************************************************** */
/*  Project Variables

    Preprocessor definitions aren't available at runtime, so let's shove them
    into variables.
*/

// product name
extern const char productName[];

// product software version
extern const char productVersion[];

// compilation information
extern const uint16_t xc8Version;
extern const char compileDate[];
extern const char compileTime[];

#endif // _PROJECT_VARIABLES_H_