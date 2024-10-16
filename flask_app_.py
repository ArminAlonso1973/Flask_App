import os
from openai import OpenAI, OpenAIError
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializar el cliente de OpenAI con la clave API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("La clave API de OpenAI no se cargó. Revisa el archivo .env.")

print(f"OpenAI API Key: {OPENAI_API_KEY}")  # Confirmar si la API Key está cargada correctamente

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Inicializar el cliente de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Inicializar la aplicación Flask
app = Flask(__name__)

# Ruta del webhook para recibir mensajes de WhatsApp
@app.route("/webhook", methods=['POST'])
def webhook():
    print("Solicitud recibida en el webhook.")  # Confirmar que el webhook recibió la solicitud

    # Obtener el mensaje entrante y el número del remitente
    incoming_msg = request.values.get('Body', '').lower()
    from_number = request.values.get('From', '')
    
    print(f"Mensaje recibido: {incoming_msg} de {from_number}")  # Mostrar el mensaje recibido y el número del remitente

    # Preparar una respuesta predeterminada si OpenAI falla
    response_text = "Lo siento, no pude generar una respuesta en este momento."

    # Usar OpenAI para generar una respuesta utilizando el asistente predefinido
    try:
        print("Intentando generar una respuesta con OpenAI...")
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            assistant="asst_k2PfqVu3sM9Kl6U2ryjFiJjs",
            messages=[
                {"role": "user", "content": incoming_msg},
            ],
            max_tokens=50
        )
        response_text = response.choices[0].message.content.strip()
        print(f"Respuesta generada por OpenAI: {response_text}")
    except OpenAIError as e:
        print(f"Error al generar respuesta de OpenAI: {e}")
    except Exception as ex:
        print(f"Otro error ocurrió: {ex}")

    # Crear una respuesta de Twilio para enviar la respuesta generada de vuelta al remitente
    resp = MessagingResponse()
    resp.message(response_text)

    return str(resp)

if __name__ == "__main__":
    # Correr la aplicación Flask en el puerto 5001
    if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
