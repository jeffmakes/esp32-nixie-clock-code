import utime as time
import network
from machine import Pin
import uasyncio as asyncio

from captiveportal import WebServer
from dns import DNSServer

class EspNixie:
    def __init__(self):
        print("espnixie init!")
        self.if_ap = None
        self.if_sta = None
        self.webserver = None
        self.dnsserver = None

    def ap_init(self):
        print("Initialising AP")
        self.if_ap = network.WLAN(network.AP_IF)
        self.if_ap.active(True)
        self.if_ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.0.4', '192.168.0.4'))
        self.if_ap.config(essid='Nixie Clock Config')
        print("AP initialised")

    def sta_init(self):
        print ("Initialising STA")
        self.if_sta = network.WLAN(network.STA_IF)
        self.if_sta.active(True)
        ssid = "VM000190-2G"
        password = "cxbssmue"
        self.if_sta.connect(ssid, password)  # Connect to an AP
        t = time.ticks_ms()
        while not self.if_sta.isconnected():
            if time.ticks_ms() - t > 10000:
                print ("Timed out connecting to network {}".format(ssid))
                break
        if self.if_sta.isconnected():
            print ("Connected to network {}".format(ssid))

    def web_init(self):
        print("Initialising webserver")
        self.webserver = WebServer(address=self.if_ap.ifconfig()[0], port=80, debug=2)

    def main(self):
        led = Pin(2, Pin.OUT)
        enabled = False

        self.ap_init()
        self.dnsserver = DNSServer(self.if_ap.ifconfig()[0])
        self.dnsserver.run()

        loop = asyncio.get_event_loop()

        loop.create_task(self.dnsserver.run())  # Schedule ASAP
        self.web_init()
        loop.run_forever()

        for i in range(6):
            led.value(not led.value())
            time.sleep_ms(100)

        while True:
            led.value(enabled)
            time.sleep_ms(100)
            print("status " + str(enabled))
            enabled = not enabled
