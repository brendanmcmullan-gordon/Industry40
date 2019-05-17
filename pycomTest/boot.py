
import machine

from network import WLAN



wifi_ssid = 'E220_2.4'
wifi_pass = 'GordonICT'

if machine.reset_cause() != machine.SOFT_RESET:
        
    wlan = WLAN(mode=WLAN.STA)
    
    wlan.connect(wifi_ssid, auth=(WLAN.WPA2, wifi_pass), timeout=5000)

    while not wlan.isconnected(): 
         machine.idle()

print('Connected to wifi')
print(wlan.ifconfig())
machine.main('main.py')