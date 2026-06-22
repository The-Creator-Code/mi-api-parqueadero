from flask import Flask, request, jsonify

app = Flask(__name__)

# Memoria temporal para almacenar el estado en vivo de los parqueaderos
estado_parqueadero = {
    "p1": "LIBRE",
    "p2": "LIBRE"
}

# 1. El ESP32 usa esta ruta para GUARDAR los datos
@app.route('/api/estacionamiento', methods=['POST'])
def recibir_datos():
    global estado_parqueadero
    data = request.json  
    
    # Actualizamos la memoria del servidor
    estado_parqueadero["p1"] = data.get('p1', 'LIBRE')
    estado_parqueadero["p2"] = data.get('p2', 'LIBRE')
    
    print(f"\n[ESP32] Actualizado -> P1: {estado_parqueadero['p1']} | P2: {estado_parqueadero['p2']}")
    return jsonify({"status": "actualizado"}), 200

# 2. Tu App de Android usará esta ruta para LEER los datos
@app.route('/api/estacionamiento', methods=['GET'])
def entregar_datos():
    return jsonify(estado_parqueadero), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)