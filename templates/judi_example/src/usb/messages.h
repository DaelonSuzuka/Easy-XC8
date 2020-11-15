#ifndef _MESSAGES_H_
#define _MESSAGES_H_

#include "os/json/json_messages.h"
#include "os/json/json_node.h"
#include "os/usb.h"
#include "os/usb_port.h"

/* ************************************************************************** */
// project specific message components

extern const json_node_t updateAutoMode[];
extern const json_node_t updateAutoTable[];
extern const json_node_t updateAntenna[];
extern const json_node_t updateFrequency[];

/* ************************************************************************** */

extern void respond(json_buffer_t *buf);

#endif // _MESSAGES_H_