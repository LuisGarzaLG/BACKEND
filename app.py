from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import subprocess
import json
import tempfile

app = Flask(__name__)
CORS(app)

# Ruta raíz que acepta GET y POST
@app.route('/', methods=['GET'])
def home():
    # Parámetros de simulación por defecto
    default_data = {
        "num_personas": 100,
        "tiempo_simulacion": 1000,
        "tiempo_llegadas": 2,
        "duracion_bn": [1, 3],
        "duracion_color": [4, 10],
        "impresoras_bn": 2,
        "impresoras_color": 2
    }

    # Guardar en archivo temporal y ejecutar simulador.py
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_input:
        json.dump(default_data, temp_input)
        temp_input_path = temp_input.name

    try:
        resultado = subprocess.check_output(['python', 'simulador.py', temp_input_path], text=True)
        registros = json.loads(resultado)
        return jsonify(registros)  # Puedes retornar HTML si prefieres
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Fallo al ejecutar la simulación", "detalles": e.output}), 500


@app.route('/api/simular', methods=['POST', 'OPTIONS'])
@cross_origin()
def simular():
    data = request.json

    # Guardar datos en un archivo temporal
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_input:
        json.dump(data, temp_input)
        temp_input_path = temp_input.name

    # Ejecutar simulador.py y capturar salida
    try:
        resultado = subprocess.check_output(['python', 'simulador.py', temp_input_path], text=True)
        registros = json.loads(resultado)
        return jsonify(registros)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Fallo al ejecutar la simulación", "detalles": e.output}), 500

if __name__ == '__main__':
    app.run(debug=True)
