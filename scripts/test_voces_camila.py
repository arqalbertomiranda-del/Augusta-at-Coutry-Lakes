# -*- coding: utf-8 -*-
import requests, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KEY     = "sk_64cc732491128013d3f56570a4ce42d35b4b997b8a03f260"
OUT     = r"C:\Users\alber\Boma Desarrollos\Automatizaciones Boma - Documentos\05. Augusta\outputs\camila-augusta-reel-2026-05-15"
HEADERS = {"xi-api-key": KEY, "Content-Type": "application/json"}
SCRIPT  = "Elegir dónde vivir no es una decisión... es una declaración. Augusta at Country Lakes. La privada más exclusiva frente al mejor campo de golf de Latinoamérica."

# Tres variaciones de emoción — Ana María mexicana
VARIANTS = [
    ("Ana-Maria-v4", {"stability": 0.15, "similarity_boost": 0.80, "style": 0.90, "use_speaker_boost": True}),
]

for name, settings in VARIANTS:
    body = {"text": SCRIPT, "model_id": "eleven_multilingual_v2", "voice_settings": settings}
    r = requests.post(
        "https://api.elevenlabs.io/v1/text-to-speech/m7yTemJqdIqrcNleANfX",
        headers=HEADERS, json=body, timeout=60
    )
    if r.status_code == 200:
        path = f"{OUT}\\voz-{name.lower()}.mp3"
        open(path, "wb").write(r.content)
        print(f"{name} OK  stability={settings['stability']}  style={settings['style']}  -> voz-{name.lower()}.mp3")
    else:
        print(f"{name} FAILED: {r.status_code} {r.text[:200]}")
