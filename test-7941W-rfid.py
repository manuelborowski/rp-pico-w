import machine, network, ntptime
import urequests as requests
import binascii
import time
from time import sleep
from config import config
resp_len = 2405


#mpremote connect port:/dev/ttyS3 run test-7941W-rfid.py
#beep transistor C1815


read_uid = bytearray(b'\xab\xba\x00\x10\x00\x10')

beep_pin = machine.Pin(6, machine.Pin.OUT)
register_ok_pin = machine.Pin(7, machine.Pin.OUT)
register_nok_pin = machine.Pin(8, machine.Pin.OUT)


def wlan_connect():
    print("start wlan connection")
    wifi_pin = machine.Pin(2, machine.Pin.OUT)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config["wifi_ssid"], config["wifi_password"])
    wifi_pin.off()
    while not wlan.isconnected():
        wifi_pin.toggle()
        sleep(0.2)
    wifi_pin.on()
    print(wlan.ifconfig())
    ip = wlan.ifconfig()[0]
    return ip


def set_correct_datetime():
    print("Set correct date and time")
    ntptime.settime()

def beep(freq=1000, wait=200):
    p6 = machine.PWM(beep_pin, freq=freq, duty_u16=30000)
    time.sleep_ms(wait)
    p6.deinit()

def test_timer_blink(timer):
    register_nok_pin.toggle()

def main():
    print("start main")
    wlan_connect()
    set_correct_datetime()
    rfid_serial = machine.UART(0, baudrate=115200, bits=8, parity=None, stop=1, timeout=100)
    hour_offset = int(config["time_hour_offset"])
    ctr = 0
    prev_code = ""
    register_ok_pin.off()
    register_nok_pin.off()

    machine.Timer(mode=machine.Timer.PERIODIC, period=500, callback=test_timer_blink)


    while True:
        rfid_serial.write(read_uid)
        rcv_raw = rfid_serial.read(resp_len)
        if rcv_raw:
            rcv = binascii.hexlify(rcv_raw).decode("UTF-8")
            if rcv[6:8] == "81": # valid uid received
                code = rcv[10:18]
                if code != prev_code or ctr > 10:
                    register_ok_pin.off()
                    register_nok_pin.off()
                    # beep()
                    p6 = machine.PWM(beep_pin, freq=1000, duty_u16=30000)
                    t = time.localtime()
                    timestamp = f"{t[0]}-{t[1]}-{t[2]}T{t[3] + hour_offset}:{t[4]}:{t[5]}"
                    ret = requests.post(f"{config['api_url']}/api/registration/add", headers={'x-api-key': config['api_key']},
                                        json={"location_key": config["location"], "badge_code": code, "timestamp": timestamp})
                    p6.deinit()
                    if ret.status_code == 200:
                        res = ret.json()
                        print(res)
                        if res["status"]:
                            register_ok_pin.on()
                        else:
                            register_nok_pin.on()
                    print(code)
                    ctr = 0
                prev_code = code
                ctr += 1


if __name__ == "__main__":
    main()