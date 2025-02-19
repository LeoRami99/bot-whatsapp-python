import requests
from app.services.database import get_bot_credentials
from typing import Dict, Any

def send_whatsapp_message(bot_id: str, to: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envía un mensaje de WhatsApp usando el _payload_ completo almacenado en la base de datos.
    Se espera que el campo "response" ya contenga la estructura exacta que requiere la API de WhatsApp.
    """
    credentials = get_bot_credentials(bot_id)
    if not credentials:
        return {"error": "Bot no encontrado"}
    
    headers = {
        "Authorization": f"Bearer {credentials['ACCESS_TOKEN']}",
        "Content-Type": "application/json"
    }
    
    # Obtenemos el payload ya formateado desde la BD.
    payload = response_data.get("response")
    if not payload:
        return {"error": "No se encontró el payload en la respuesta"}
    
    # Se asegura de asignar el destinatario.
    payload["to"] = to

    print("payload", payload)
    response = requests.post(credentials["WHATSAPP_API_URL"], headers=headers, json=payload)
    print("rta", response.json())
    
    return response.json()