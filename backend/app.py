from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from openai import AzureOpenAI
import json
import random
from dotenv import load_dotenv
app = Flask(
    __name__,
    static_folder="../frontend/dist",  # o "build" según tu configuración
    static_url_path=""
)
app = Flask(__name__)
CORS(app)

load_dotenv()  # carga .env en desarrollo
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

# Cargar cartas del mazo
with open("mazo.json", "r", encoding="utf-8") as f:
    cartas = json.load(f)

@app.route('/api/tirada', methods=['POST'])
def tirar_cartas():
    data = request.get_json()
    pregunta = data.get('pregunta', '').strip()

    if not pregunta:
        return jsonify({'error': 'Falta la pregunta'}), 400

    seleccion = random.sample(cartas, 3)

    # Agregamos campo "invertida": True/False
    for carta in seleccion:
        carta['invertida'] = random.choice([True, False])

    return jsonify({
        'pregunta': pregunta,
        'cartas': seleccion
    })

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


def generar_prompt(pregunta, cartas):
    # Construye la lista numerada con posición de cada carta
    lista = "\n".join([
        f"{i+1}. {c['nombre']} — {'invertida' if c.get('invertida') else 'derecha'}"
        for i, c in enumerate(cartas)
    ])

    # Prompt con tono ácido, metáforas y claridad
    return f"""
Sos ese amigo que te dice las cosas como son, sin filtro y con la verdad por delante. 
Sos lector de tarot, pero no de esos new age que te endulzan todo - vos le das al clavo aunque duela.

REGLAS:
- Interpretá cada carta según su posición (derecha/invertida) - esto es clave, no te hagas el boludo
- Mostrá cómo las tres cartas se conectan y qué historia cuentan juntas
- Enfocate en la pregunta específica, no divagues
- Usá metáforas filosas que peguen en el hueso
- Sé directo 

Tu estilo:
- No uses vocativos. 
- Hablás como argentino, sin poses
- Mezclás sabiduría con sarcasmo inteligente
- Si hay algo que el consultante no quiere ver, se lo remarcás
- Usás comparaciones y metáforas para mejorar el mensaje.
- No prometés milagros ni boludeces, decís lo que ES.

---
CONSULTA: "{pregunta}"

CARTAS EXTRAÍDAS:
{lista}

Dale, tirá la posta en 2-3 párrafos máximo. Que se entienda, que duela si hace falta, pero que ayude.
"""

if __name__ == '__main__':
    app.run(debug=True)
