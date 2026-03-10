import network
import socket
from machine import Pin
from time import sleep
 
led = Pin(2, Pin.OUT)
led.off()
 
ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid="ESP32_RCP", password="n1gg3rb4ll5", authmode=3)
 
sleep(2)
print("Red WiFi creada: ESP32_RCP")
print("Conectate y abre: http://192.168.4.1")
 
def web_page():
    html = 
    return html
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)
print("Servidor listo!")
 
while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
 
    if '/on' in request:
       
    elif '/off' in request:
        
 
    conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
    conn.send(web_page())
    conn.close()