from flask import Flask, request, jsonify, send_from_directory
import os
from flask_cors import CORS
from openai import AzureOpenAI
import json
import random
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear instancia Flask con carpeta del frontend compilado
app = Flask(
    __name__,
    static_folder="../frontend/dist",
    static_url_path=""
)
CORS(app)

# Configuración Azure OpenAI
API_KEY         = os.environ['AZURE_API_KEY']
ENDPOINT        = os.environ['AZURE_ENDPOINT']
DEPLOYMENT_NAME = os.environ['AZURE_DEPLOYMENT']
API_VERSION     = os.environ['AZURE_API_VERSION']

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT
)

# Cargar cartas
with open("mazo.json", "r", encoding="utf-8") as f:
    cartas = json.load(f)

# Servir el frontend como SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    target = path if path and os.path.exists(os.path.join(app.static_folder, path)) else 'index.html'
    return send_from_directory(app.static_folder, target)

# Endpoint: tirar cartas
@app.route('/api/tirada', methods=['POST'])
def tirar_cartas():
    data = request.get_json()
    pregunta = data.get('pregunta', '').strip()

    if not pregunta:
        return jsonify({'error': 'Falta la pregunta'}), 400

    seleccion = random.sample(cartas, 3)

    for carta in seleccion:
        carta['invertida'] = random.choice([True, False])

    return jsonify({
        'pregunta': pregunta,
        'cartas': seleccion
    })

# Endpoint: interpretar
@app.route('/api/interpretar', methods=['POST'])
def interpretar():
    data = request.get_json()
    pregunta = data.get('pregunta', '')
    cartas = data.get('cartas', [])

    if not pregunta or not cartas:
        return jsonify({'error': 'Faltan datos'}), 400

    prompt = generar_prompt(pregunta, cartas)

    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        texto = response.choices[0].message.content.strip()
        return jsonify({'respuesta': texto})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Prompt
def generar_prompt(pregunta, cartas):
    lista = "\n".join([
        f"{i+1}. {c['nombre']} — {'invertida' if c.get('invertida') else 'derecha'}"
        for i, c in enumerate(cartas)
    ])
    return f"""
Sos ese amigo que te dice las cosas como son, sin filtro y con la verdad por delante. 
Sos lector de tarot, pero no de esos new age que te endulzan todo - vos le das al clavo aunque duela.

REGLAS:
- Interpretá cada carta según su posición (derecha/invertida) - esto es clave, no te hagas el boludo.
- Mostrá cómo las tres cartas se conectan y qué historia cuentan juntas.
- Enfocate en la pregunta específica, no divagues ni repitas obviedades.
- Usá metáforas filosas, sin miedo al impacto.
- Si el consultante está preguntando algo estúpido o superficial, ponelo en evidencia con humor ácido.
- Sé directo, sarcástico, pero nunca cruel con temas sensibles.

ESTILO:
- Argento, irónico, con frases picantes pero que dejan enseñanza.
- Nada de dulzura gratuita ni mensajes de autoayuda.
- Hablás como si estuvieras en confianza con alguien que necesita una cachetada simbólica.
- El tono es tipo “Dr. House del tarot”.

---
CONSULTA: "{pregunta}"

CARTAS EXTRAÍDAS:
{lista}

Dale, tirá la posta en 2-3 párrafos máximo
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
