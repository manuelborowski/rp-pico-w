import network, machine
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
from config import config

wifi_pin = machine.Pin(2, machine.Pin.OUT)

def connect():
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
    
def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    print(connection)
    return connection


def webpage(temperature, state):
    html = f"""
        <!DOCTYPE html>
        <html>
        <body>
        <form action="./lighton">
        <input type="submit" value="Light on" />
        </form>
        <form action="./lightoff">
        <input type="submit" value="Light off" />
        </form>
        <p>LED is {state}</p>
        <p>Temperature is {temperature}</p>
        </body>
        </html>
    """
    return str(html)


def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            state = 'ON'
        elif request =='/lightoff?':
            pico_led.off()
            state = 'OFF'
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection) 
except KeyboardInterrupt:
    machine.reset()