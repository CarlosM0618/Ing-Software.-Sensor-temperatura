import network, time
from machine import Pin
import dht

# Nota: Usamos 'requests', si te da error cámbialo a 'urequests' en la siguiente línea
try:
    import requests
except ImportError:
    import urequests as requests

# ── Configuración — CAMBIA ESTOS VALORES ────
WIFI_SSID     = "Galaxy S25 Ultra de Carlos"
WIFI_PASS     = "Penesillo6969"
BOT_TOKEN     = "8664030013:AAH-MgtPHX-g7gWyypvAjOsEfAUrubt8P-U"
CHAT_ID       = "8603533169"
UMBRAL_TEMP   = 30   

sensor = dht.DHT11(Pin(4))

# ── Variables para el Bot ───────────────────
historial_alertas = []  # Aquí guardaremos las últimas 5 alertas
last_update_id = 0      # Para no leer el mismo mensaje dos veces

# ── Conectar a WiFi ─────────────────────────
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    print("Conectando a WiFi", end="")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
    print(f"\n✓ Conectado: {wlan.ifconfig()[0]}")

# ── Enviar mensaje a Telegram ────────────────
def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=data)
        r.close()
    except Exception as e:
        print(f"✗ Error Telegram: {e}")

# ── Leer comandos de Telegram ────────────────
def procesar_comandos():
    global UMBRAL_TEMP, last_update_id  # Necesario para poder modificar el umbral global
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=1"
    try:
        r = requests.get(url)
        datos = r.json()
        r.close()

        if "result" in datos:
            for mensaje in datos["result"]:
                last_update_id = mensaje["update_id"]
                
                if "message" in mensaje and "text" in mensaje["message"]:
                    texto = mensaje["message"]["text"].strip().lower()
                    chat_id_remitente = str(mensaje["message"]["chat"]["id"])

                    # Ignorar mensajes de otros chats por seguridad
                    if chat_id_remitente != CHAT_ID:
                        continue
                    
                    print(f"Comando recibido: {texto}")

                    # 1. Comando /temp
                    if texto == "/temp":
                        try:
                            sensor.measure()
                            t = sensor.temperature()
                            h = sensor.humidity()
                            enviar_telegram(f"📊 <b>Estado actual:</b>\n🌡 Temp: {t}°C\n💧 Humedad: {h}%\n⚙️ Umbral: {UMBRAL_TEMP}°C")
                        except OSError:
                            enviar_telegram("⚠ Error leyendo el sensor en este momento.")

                    # 2. Comando /limite n
                    elif texto.startswith("/limite"):
                        partes = texto.split()
                        if len(partes) == 2:
                            try:
                                nuevo_limite = int(partes[1])
                                UMBRAL_TEMP = nuevo_limite
                                enviar_telegram(f"✅ Umbral actualizado a: <b>{UMBRAL_TEMP}°C</b>")
                            except ValueError:
                                enviar_telegram("⚠ El límite debe ser un número. Ejemplo: /limite 35")
                        else:
                            enviar_telegram("⚠ Formato incorrecto. Usa: /limite [numero]")

                    # 3. Comando /historial
                    elif texto == "/historial":
                        if len(historial_alertas) == 0:
                            enviar_telegram("📝 No hay alertas registradas aún.")
                        else:
                            msg_historial = "📜 <b>Últimas 5 alertas:</b>\n"
                            for i, alerta in enumerate(historial_alertas, 1):
                                msg_historial += f"{i}. {alerta}\n"
                            enviar_telegram(msg_historial)

    except Exception:
        pass # Ignoramos errores de red momentáneos al buscar mensajes

# ── Programa principal ───────────────────────
conectar_wifi()

alerta_enviada = False
contador_ciclos = 0

print(f"=== SISTEMA LISTO — Umbral inicial: {UMBRAL_TEMP}°C ===")
enviar_telegram("🤖 <b>Bot iniciado.</b> Comandos listos:\n/temp - Temperatura actual\n/limite [n] - Cambiar umbral\n/historial - Ver últimas alertas")

while True:
    # 1. Escuchar a Telegram cada 2 segundos
    procesar_comandos()

    # 2. Leer sensor físico cada 10 segundos (5 ciclos de 2 segundos)
    if contador_ciclos % 5 == 0:
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum  = sensor.humidity()
            print(f"Lectura interna -> {temp}°C | {hum}% | Umbral: {UMBRAL_TEMP}°C")

            if temp >= UMBRAL_TEMP and not alerta_enviada:
                msg = (f"🚨 <b>ALERTA DE TEMPERATURA</b>\n\n"
                       f"🌡 Temperatura: <b>{temp}°C</b>\n"
                       f"💧 Humedad: {hum}%\n"
                       f"⚠️ Supera el umbral de {UMBRAL_TEMP}°C\n"
                       f"📍 ESP32 — UAG Ingeniería de Software")
                enviar_telegram(msg)
                alerta_enviada = True
                
                # Guardar en el historial
                registro = f"{temp}°C (Umbral era {UMBRAL_TEMP}°C)"
                historial_alertas.append(registro)
                # Mantener solo los últimos 5
                if len(historial_alertas) > 5:
                    historial_alertas.pop(0)

            elif temp < UMBRAL_TEMP and alerta_enviada:
                enviar_telegram(f"✅ Temperatura normalizada: {temp}°C")
                alerta_enviada = False

        except OSError:
            print("⚠ Error de sensor")

    contador_ciclos += 1
    time.sleep(2)  