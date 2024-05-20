import machine
import network
import time
import AHT21
import ENS160
import settings
import urequests

# boot pattern
led = machine.Pin("LED", machine.Pin.OUT)
print("Playing LED boot pattern...")
led.on()
time.sleep(0.5)
led.off()
time.sleep(0.5)
led.on()
time.sleep(0.5)
led.off()
time.sleep(0.5)
led.on()
time.sleep(0.5)
led.off()
time.sleep(0.5)

# set up
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
aht = AHT21.AHT21(i2c)
ens = ENS160.ENS160(i2c)
ens.reset()
time.sleep(0.5)
ens.operating_mode = 2
time.sleep(2.0)

# connect to wifi
wifi_con_attempt:int = 0
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
while wlan.isconnected() == False:

    wifi_con_attempt = wifi_con_attempt + 1

    # blip light
    led.on()
    time.sleep(0.1)
    led.off()
    
    print("Attempt #" + str(wifi_con_attempt) + " to connect to wifi...")
    wlan.connect(settings.ssid, settings.password)
    time.sleep(3)
print("Connected to wifi after " + str(wifi_con_attempt) + " tries!")
my_ip:str = str(wlan.ifconfig()[0])
print("My IP Address: " + my_ip)

# create watchdog timer
wdt = machine.WDT(timeout=8388) # 8,388 ms is the limit (8.388 seconds)
wdt.feed()
print("Watchdog timer now activated.")

# Enter infinite loop
while True:

    # take reading from ENS160
    print("Taking ENS160 measurements... ")
    aqi:int = ens.AQI
    eco2:int = ens.CO2
    tvoc:int = ens.TVOC
    wdt.feed()
    
    # take reading from AHT21
    print("Taking AHT21 measurements...")
    rht = aht.read()
    humidity:float = rht[0]
    humidity = humidity / 100
    temperature:float = rht[1]
    wdt.feed()

    # create json body
    body = {"aqi": aqi, "eco2": eco2, "tvoc": tvoc, "humidity": humidity, "temperature": temperature}
    print("Measurements taken! " + str(body))
    wdt.feed()
    
    # make HTTP call
    print("Making HTTP call...")
    wdt.feed()
    pr = urequests.post(settings.post_url, json=body)
    wdt.feed()
    pr.close()
    print("HTTP call made!")

    # wait for time
    next_loop:int = time.ticks_ms() + (1000 * settings.sample_time_seconds)
    while (time.ticks_ms() < next_loop):
        print("Sampling next in " + str(round((next_loop - time.ticks_ms()) / 1000, 0)) + " seconds...")
        time.sleep(1)
        wdt.feed()