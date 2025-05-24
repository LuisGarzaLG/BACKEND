from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import subprocess
import json
import tempfile

app = Flask(__name__)
CORS(app)

# Ruta raíz que acepta GET y POST
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.json
        return jsonify({
            "mensaje": "Datos recibidos en POST /",
            "contenido": data
        }), 200
    else:
        return "Servidor Flask activo. Envía POST con JSON a esta misma URL (/)", 200

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
