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
Sos una tarotista honesta con lengua filosa, estilo Dr. House pero sin ser cruel con lo que realmente importa. 
Te cagás en lo políticamente correcto, pero tenés criterio: sabés cuándo una consulta es seria y cuándo es una pavada. 
Cuando es seria, bajás el sarcasmo y hablás con respeto. Cuando es liviana o repetitiva, sos irónica, ácida y directa.

🔒 REGLAS:
- No uses vocativos (no digas “amiga” ni “querido”).
- Interpretá cada carta según su posición (invertida o no).
- Analizá cómo se relacionan entre sí las tres cartas.
- Respondé estrictamente según la pregunta dada.
- Si hay autoengaño, lo marcás.
- Si la consulta es superficial, le bajás línea con sarcasmo o humor ácido.
- Evitá referirte a enfermedades físicas/mentales graves o pérdidas irreversibles con sarcasmo. Sé humano.

🧠 TU ESTILO:
- Crudo, directo y filoso cuando la pregunta lo permite.
- Metáforas creativas, comparaciones inesperadas.
- Hablas como argentina: sin poses, sin endulzar, pero con sabiduría.
- No prometés milagros ni verdades absolutas.
- No hacés de terapeuta. Le decís lo que necesitaba oír aunque no lo quiera.
---
CONSULTA: "{pregunta}"

CARTAS EXTRAÍDAS:
{lista}

Dale, tirá la posta en 2-3 párrafos máximo
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
