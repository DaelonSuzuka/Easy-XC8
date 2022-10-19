#include "messages.h"
#include "os/json/json_print.h"
#include "os/judi/hash.h"
#include "os/judi/judi.h"
#include "os/judi/message_builder.h"
#include "os/serial_port.h"
#include "system.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/* ************************************************************************** */

#define HASH(number) buf->tokens[number].hash

void respond(json_buffer_t *buf) {
    for (uint8_t i = 0; i < buf->tokensParsed; i++) {
        switch (HASH(i)) {
        case hash_request:
            switch (HASH(++i)) {
            case hash_device_info:
                add_nodes(updatePreamble);
                add_nodes(deviceInfo);
                print_message(usb_print);
                break;
            }
            break;
        }
    }
}