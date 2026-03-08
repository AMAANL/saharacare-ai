import os
import requests
import json

from dotenv import load_dotenv

def generate_hindi_audio(text, target_language='hi-IN'):
    load_dotenv()
    sarvam_key = os.environ.get("SARVAM_API_KEY")
    if not sarvam_key or sarvam_key == "your_sarvam_api_key_here":
        print("Sarvam API key not found or is default.")
    
    if sarvam_key and sarvam_key != "your_sarvam_api_key_here":
        url = "https://api.sarvam.ai/text-to-speech"
        headers = {
            "api-subscription-key": sarvam_key,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [text],
            "target_language_code": target_language,
            "speaker": "shruti",
            "pace": 1.0,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v3" 
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                audio = data.get('audios', [''])[0] 
                return {"type": "base64", "data": audio}
            else:
                print(f"Sarvam API Failed with {response.status_code}: {response.text}")
        except Exception as e:
            print("Error calling Sarvam TTS:", e)

    import urllib.parse
    encoded_text = urllib.parse.quote(text)
    # Map the iso code for Google TTS (e.g. en-IN -> en)
    g_lang = target_language.split('-')[0]
    fallback_url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&q={encoded_text}&tl={g_lang}"
    return {"type": "url", "data": fallback_url}
