"""boot.py

Runs on every boot (including wake from deep sleep).

Purpose:
- Keep boot-time side effects minimal.
- Disable radios by default for deterministic startup and lower power/EMI.
"""

import gc
import config
import network
import bluetooth

def disable_wifi():
    try:
        network.WLAN(network.STA_IF).active(False)
        network.WLAN(network.AP_IF).active(False)
    except Exception:
        pass
    
def disable_bluetooth():
    try:
        bluetooth.disable()
    except Exception:
        pass

def disable_wifi_bluetooth():
    if getattr(config, "DISABLE_WIFI", False):
        disable_wifi()
    if getattr(config, "DISABLE_BLUETOOTH", False):
        disable_bluetooth()

disable_wifi_bluetooth()
gc.collect()
