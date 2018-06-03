import utime
import network
from machine import Pin


def net_init():
    if_ap = network.WLAN(network.AP_IF)
    if_ap.active(True)
    if_ap.config(essid='Nixie Clock Config')

def main():
    led = Pin(2, Pin.OUT)
    enabled = False

    net_init();

    while True:
        led.value(enabled)
        utime.sleep_ms(100)
        print("status " + str(enabled))
        enabled = not enabled


if __name__ == '__main__':
    main()
