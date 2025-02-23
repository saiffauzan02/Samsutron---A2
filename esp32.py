import network
import time
import urequests
import dht
import json
from machine import Pin

# Konfigurasi WiFi
SSID = "JUS KODE"
PASSWORD = "12345678"
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

# Konfigurasi Server Flask (MongoDB)
SERVER_URL = "http://192.168.1.29:5000/kirim_data"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-niSYlwXxufMxTCJOSStDVRGhN3rEJw"
DEVICE_LABEL = "esp-tempest-tech"
VARIABLE_LABEL_TEMP = "temperature"
VARIABLE_LABEL_HUM = "humidity"

# Inisialisasi sensor DHT11
sensor = dht.DHT11(Pin(27))

def connect_wifi(timeout=10):
    """Menghubungkan ke WiFi dengan batas waktu."""
    if not sta_if.isconnected():
        print("Menghubungkan ke WiFi...")
        sta_if.connect(SSID, PASSWORD)
        start_time = time.time()
        
        while not sta_if.isconnected():
            if time.time() - start_time > timeout:
                print("[ERROR] Gagal terhubung ke WiFi.")
                return False
            time.sleep(1)
            print("Menunggu koneksi WiFi...")
    
    print("Terhubung ke WiFi:", sta_if.ifconfig())
    return True

def send_data_to_flask(temp, hum):
    """Mengirim data ke server Flask (MongoDB)."""
    payload = json.dumps({"temperature": temp, "kelembapan": hum})
    headers = {"Content-Type": "application/json"}
    
    try:
        response = urequests.post(SERVER_URL, data=payload, headers=headers)
        print(f"[Flask] Status Code: {response.status_code}")
        print(f"[Flask] Response: {response.text}")
        response.close()
    except Exception as e:
        print("[ERROR] Gagal mengirim data ke Flask:", e)

def send_data_to_ubidots(temp, hum):
    """Mengirim data ke Ubidots."""
    url = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
    headers = {"X-Auth-Token": UBIDOTS_TOKEN, "Content-Type": "application/json"}
    payload = json.dumps({VARIABLE_LABEL_TEMP: temp, VARIABLE_LABEL_HUM: hum})

    try:
        response = urequests.post(url, headers=headers, data=payload)
        print(f"[Ubidots] Status Code: {response.status_code}")
        print(f"[Ubidots] Response: {response.text}")
        response.close()
    except Exception as e:
        print("[ERROR] Gagal mengirim data ke Ubidots:", e)

def main():
    if not connect_wifi():
        return  # Keluar jika WiFi gagal terhubung
    
    while True:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            print(f"Temperature: {temp}°C")
            print(f"Kelembapan: {hum}%")
            
            # Kirim data ke Flask (MongoDB)
            send_data_to_flask(temp, hum)
            
            # Kirim data ke Ubidots
            send_data_to_ubidots(temp, hum)
        
        except OSError:
            print("[ERROR] Gagal membaca sensor.")
        
        time.sleep(5)  # Kirim data setiap 5 detik

if __name__ == '__main__':
    main()

