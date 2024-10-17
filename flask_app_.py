# Importaciones necesarias
from openai import OpenAI
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Inicializar OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Inicializar Twilio
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Inicializar Flask
app = Flask(__name__)

# IDs del asistente y thread existentes
ASSISTANT_ID = "asst_k2PfqVu3sM9Kl6U2ryjFiJjs"
THREAD_ID = "thread_viOeVZEjSW5dF8Z4tcRx4DJC"

@app.route("/webhook", methods=['POST'])
def webhook():
    logger.debug("Webhook ha sido llamado.")
    incoming_msg = request.values.get('Body', '').lower()
    from_number = request.values.get('From', '')
    logger.debug(f"Mensaje recibido: {incoming_msg} de {from_number}")
    
    try:
        # Agregar el mensaje del usuario al thread existente
        client.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=incoming_msg
        )
        
        # Ejecutar el asistente
        run = client.beta.threads.runs.create(
            thread_id=THREAD_ID,
            assistant_id=ASSISTANT_ID
        )
        
        # Esperar a que el asistente complete la ejecución
        while run.status not in ["completed", "failed"]:
            run = client.beta.threads.runs.retrieve(
                thread_id=THREAD_ID,
                run_id=run.id
            )
        
        if run.status == "completed":
            # Obtener la respuesta del asistente
            messages = client.beta.threads.messages.list(thread_id=THREAD_ID)
            assistant_response = next(msg.content[0].text.value for msg in messages if msg.role == "assistant")
        else:
            assistant_response = "Lo siento, hubo un problema al procesar tu solicitud."

    except Exception as e:
        logger.error(f"Error al procesar la solicitud: {e}")
        assistant_response = "Ocurrió un error al procesar tu mensaje."

    # Respuesta de Twilio
    resp = MessagingResponse()
    resp.message(assistant_response)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)