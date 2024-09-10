import os
import logging
import boto3
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Configura tu token de Telegram
TELEGRAM_TOKEN = "7414869114:AAH5HBwNavRid8EJ0ASBuuOZ2aDeJnCsnPs"

# Configura el cliente de Amazon Bedrock
client = boto3.client('bedrock-runtime', region_name='us-east-1')  # Asegúrate de que la región es correcta

# Configura el logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def bedrock_response(user_input):
    try:
        # Cuerpo de la solicitud para Bedrock
        body = {
            "messages": [
                {"role": "user", "content": user_input}  # El mensaje del usuario
            ],
            "max_tokens": 300,  # Número máximo de tokens
            "anthropic_version": "bedrock-2023-05-31"  # Usa la versión correcta de Bedrock
        }

        # Convertir el cuerpo a JSON y luego a bytes
        body_bytes = json.dumps(body).encode('utf-8')

        # Llamada a la API de Bedrock
        response = client.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20240620-v1:0',  # Model ID correcto
            body=body_bytes,
            contentType='application/json'
        )

        # Leer la respuesta como bytes y convertir a string
        result = response['body'].read().decode('utf-8')

        # Imprimir la respuesta completa en los logs para depuración
        logger.info(f"Respuesta completa de Bedrock: {json.dumps(json.loads(result), indent=4)}")

        # Convertir la respuesta a JSON
        result_json = json.loads(result)

        # Extraer el contenido de la respuesta
        if "content" in result_json and len(result_json["content"]) > 0:
            # Verificar si el tipo de contenido es texto y devolverlo
            for item in result_json["content"]:
                if item["type"] == "text":
                    return item["text"]
        else:
            return "Lo siento, no pude generar una respuesta."

    except Exception as e:
        logger.error(f"Error en Bedrock: {e}")
        return "Lo siento, hubo un error al procesar tu solicitud."
# Función para manejar los mensajes de los usuarios
async def handle_message(update: Update, context):
    user_input = update.message.text
    logger.info(f"Mensaje recibido: {user_input}")
    try:
        # Obtener la respuesta de Bedrock
        bedrock_reply = bedrock_response(user_input)
        logger.info(f"Respuesta de Bedrock: {bedrock_reply}")

        # Verificar que la respuesta no esté vacía
        if bedrock_reply.strip() == "":
            bedrock_reply = "Lo siento, no pude generar una respuesta."

        # Enviar la respuesta al usuario
        await update.message.reply_text(bedrock_reply)

    except Exception as e:
        logger.error(f"Error en handle_message: {e}")
        await update.message.reply_text("Lo siento, hubo un error al procesar tu mensaje.")

# Manejador del comando /start
async def start(update: Update, context):
    await update.message.reply_text("¡Hola! Soy un bot impulsado por IA. Envíame un mensaje y te responderé.")

# Configuración del bot
if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()