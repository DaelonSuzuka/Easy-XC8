#include "system.h"
#include "os/buttons.h"
#include "os/serial_port.h"
#include "os/stopwatch.h"
#include "os/system_time.h"
#include "peripherals/device_information.h"
#include "peripherals/interrupt.h"
#include "peripherals/oscillator.h"
#include "peripherals/pic_header.h"
#include "peripherals/ports.h"
#include "peripherals/pps.h"
#include "peripherals/timer.h"
#include "peripherals/uart.h"
#include "pins.h"

/* ************************************************************************** */

// Set up the timer for the button isr
static void button_isr_init(void) {
    // Timer 6 configured using MPLABX MCC
    // Period is calculated to be exactly 5ms
    timer6_clock_source(TMR_CLK_FOSC);
    timer6_prescale(TMR_PRE_1_128);
    timer6_postscale(TMR_POST_1_10);
    timer6_period_set(0xF9);
    timer6_interrupt_enable();
    timer6_start();
}

// call scan_buttons() every 5ms
void __interrupt(irq(TMR6), high_priority) button_ISR(void) {
    timer6_IF_clear();

    scan_buttons();
}

/* ************************************************************************** */

static void system_init(void) {
    internal_oscillator_init();
    interrupt_init();
    port_init();
    pins_init();
    device_information_init();
}

static void OS_init(void) {
    uart_config_t config = UART_get_config(2);
    config.baud = _115200;
    config.txPin = PPS_DEBUG_TX_PIN;
    config.rxPin = PPS_DEBUG_RX_PIN;
    serial_port_init(UART_init(config));

    buttons_init(NUMBER_OF_BUTTONS, buttonFunctions);
    button_isr_init();

    system_time_init();
    stopwatch_init();
}

static void application_init(void) {
    // init functions for your modules go here
}

/* ************************************************************************** */

void startup(void) {
    system_init();
    OS_init();

    application_init();

    // Lock the Peripheral Pin Select before proceeding to application code
    pps_lock();
}