from fastapi import APIRouter, Request, HTTPException
from app.services.whatsapp import send_whatsapp_message
from app.services.ai_service import generate_ai_response
from app.services.database import get_bot_response, get_bot_credentials

webhook_router = APIRouter()

from fastapi import APIRouter, Request, HTTPException
from app.services.database import get_bot_credentials, get_bot_response
from app.services.ai_service import generate_ai_response
from app.services.whatsapp import send_whatsapp_message

webhook_router = APIRouter()

@webhook_router.get("/webhook/{bot_id}")
def verify_webhook(bot_id: str, request: Request):
    credentials = get_bot_credentials(bot_id)
    if not credentials:
        raise HTTPException(status_code=404, detail="Bot no encontrado")
    
    verify_token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if verify_token == credentials.get("VERIFY_TOKEN"):
        return int(challenge) if challenge and challenge.isdigit() else challenge
    else:
        return ("Token inválido", 403)

@webhook_router.post("/webhook/{bot_id}")
async def receive_message(bot_id: str, request: Request):
    data = await request.json()
    credentials = get_bot_credentials(bot_id)
    if not credentials:
        raise HTTPException(status_code=404, detail="Credenciales no encontradas")
    
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                phone_number = message.get("from", "")
                if not phone_number:
                    continue
                
                # Extraer el contenido del mensaje según su tipo
                message_text = ""
                if "text" in message:
                    text_content = message.get("text", "")
                    if isinstance(text_content, dict):
                        message_text = text_content.get("body", "").strip()
                    else:
                        message_text = str(text_content).strip()
                elif "interactive" in message:
                    interactive = message.get("interactive", {})
                    # Para respuestas de botón y lista, usamos el "id" del botón o fila,
                    # ya que ese valor es el que se desea procesar
                    if "button_reply" in interactive:
                        message_text = interactive["button_reply"].get("id", "").strip()
                    elif "list_reply" in interactive:
                        message_text = interactive["list_reply"].get("id", "").strip()
                    else:
                        message_text = ""
                # Puedes agregar más condiciones para otros tipos de mensajes

                if not message_text:
                    print("Mensaje vacío recibido, se ignora.")
                    continue

                print(f"Mensaje recibido: {message_text}")

                rta_bd = get_bot_response(bot_id, message_text)

                
                if rta_bd and rta_bd.get("response", {}).get("try_ai", False):
                    ia_settings = credentials.get("IA_SETTINGS", {})
                    model_ia = ia_settings.get("MODEL", "chatgpt")
                    api_key = ia_settings.get("API_KEY", "")
                    system_instruction = ia_settings.get("SYSTEM_INSTRUCTION", "Responde de manera clara y profesional.")

                    if not api_key:
                        response_text = "⚠️ No puedo procesar tu solicitud en este momento."
                    else:
                        response_text = generate_ai_response(api_key, bot_id, model_ia, message_text, system_instruction)
                    
                    # Ajustamos la salida de la IA para que tenga el formato exacto que requiere WhatsApp.
                    response_data = {
                        "response": {
                            "messaging_product": "whatsapp",
                            "type": "text",
                            "text": {"body": response_text}
                        }
                    }
                else:
                    response_data = rta_bd

                send_whatsapp_message(bot_id, phone_number, response_data)

    return {"status": "ok"}