import machine, network, time
from config import config
def wlan_connect():
    print("start wlan connection")
    wifi_pin = machine.Pin(2, machine.Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config["wifi_ssid"], config["wifi_password"])
    wifi_pin.off()
    while not wlan.isconnected():
        wifi_pin.toggle()
        time.sleep(0.2)
    wifi_pin.on()
    print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    return ip


