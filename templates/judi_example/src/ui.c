#include "ui.h"
#include "os/buttons.h"
#include "os/logging.h"
#include "os/serial_port.h"
#include "os/shell/shell.h"
#include "os/system_time.h"
#include "os/usb.h"
#include "pins.h"
static uint8_t LOG_LEVEL = L_SILENT;

/* ************************************************************************** */

//
#define HELLOS_PER_SECOND 1
#define HELLO_WORLD_COOLDOWN 1000 / HELLOS_PER_SECOND

bool attempt_hello_world(void) {
    static system_time_t lastAttempt = 0;
    if (time_since(lastAttempt) < HELLO_WORLD_COOLDOWN) {
        return false;
    }
    lastAttempt = get_current_time();

    println("hello world!");

    return true;
}

/* -------------------------------------------------------------------------- */

void ui_idle_block(void) {
    // background tasks go here

    attempt_hello_world();

    shell_update(getch());

    usb_update();
}

/* ************************************************************************** */

void btn_one_hold(void) {
    LOG_TRACE({ println("one"); });

    while (btn_is_down(ONE)) {
        ui_idle_block();
    }
}

void btn_two_hold(void) {
    LOG_TRACE({ println("two"); });

    while (btn_is_down(TWO)) {
        ui_idle_block();
    }
}

/* -------------------------------------------------------------------------- */

void ui_mainloop(void) {
    log_register();

    while (1) {
        if (btn_is_down(ONE)) {
            btn_one_hold();
        }
        if (btn_is_down(TWO)) {
            btn_two_hold();
        }

        ui_idle_block();
    }
}