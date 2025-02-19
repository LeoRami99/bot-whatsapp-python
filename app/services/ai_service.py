import openai
import os
from google import genai
from app.services.database import get_bot_credentials
from google.genai import types

def generate_gpt_response(api_key, bot_id, prompt, system_instruction):
    credentials = get_bot_credentials(bot_id)
    if not credentials or "OPENAI_API_KEY" not in credentials:
        return "API Key de OpenAI no encontrada en la base de datos."
    
    openai.api_key = api_key
    system_instruction = credentials.get("GPT_SYSTEM_INSTRUCTION", "Responde de manera concisa y profesional.")
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

def generate_gemini_response(api_key, bot_id, prompt, system_instruction):
    client=genai.Client(api_key=api_key)
 
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        config=types.GenerateContentConfig(
        system_instruction=system_instruction),
        contents=[prompt]
    )



    return response.text if hasattr(response, "text") else "Error en la respuesta de Gemini"

def choose_ia(api_key, bot_id, model_ia: str, prompt: str, system_instruction: str):
    options = {
        "chatgpt": lambda prompt: generate_gpt_response(api_key, bot_id, prompt, system_instruction),
        "gemini": lambda prompt: generate_gemini_response(api_key, bot_id, prompt, system_instruction)
    }
    return options.get(model_ia, lambda _: lambda _: "Modelo no encontrado")

def generate_ai_response(api_key, bot_id, model_ia: str, prompt: str, system_instruction: str):
    return choose_ia(api_key, bot_id, model_ia, prompt, system_instruction)(prompt)