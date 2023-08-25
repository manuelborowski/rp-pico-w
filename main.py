import machine, time

print("Hello world")
l = machine.Pin("LED", machine.Pin.OUT)
while True:
    l.toggle()
    time.sleep(1)
