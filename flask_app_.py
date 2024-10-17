# Importaciones y configuración inicial
import os
from openai import OpenAI, OpenAIError
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import logging
from dotenv import load_dotenv

load_dotenv()  # Carga variables de entorno desde .env

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicialización de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("Falta la clave OPENAI_API_KEY.")
    raise ValueError("La clave API de OpenAI no se cargó. Revisa los secretos de Render.")
client = OpenAI(api_key=OPENAI_API_KEY)
logger.debug("OPENAI_API_KEY cargada correctamente.")

# Inicialización de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    logger.error("Faltan las credenciales de Twilio.")
    raise ValueError("Las credenciales de Twilio no se cargaron. Revisa los secretos de Render.")
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Inicialización de Flask
app = Flask(__name__)

# Rutas de Flask
@app.route("/", methods=['GET'])
def home():
    return "Bienvenido al servidor Flask."

@app.route("/webhook", methods=['POST'])
def webhook():
    logger.debug("Webhook ha sido llamado.")
    incoming_msg = request.values.get('Body', '').lower()
    from_number = request.values.get('From', '')
    logger.debug(f"Mensaje recibido: {incoming_msg} de {from_number}")
    
    response_text = "Lo siento, no pude generar una respuesta en este momento."
    
    try:
        logger.debug("Intentando generar una respuesta con OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            assistant="asst_k2PfqVu3sM9Kl6U2ryjFiJjs",  # Error: este parámetro no es válido
            messages=[
                {"role": "user", "content": incoming_msg},
            ],
            max_tokens=50
        )
        response_text = response.choices[0].message.content.strip()
        logger.debug(f"Respuesta generada por OpenAI: {response_text}")
    except OpenAIError as e:
        logger.error(f"Error al generar respuesta de OpenAI: {e}")
    except Exception as ex:
        logger.error(f"Otro error ocurrió: {ex}")
    
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=True)