from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Memoria temporal para los parqueaderos ---
# Estados posibles: "LIBRE", "OCUPADO", "RESERVADO"
estado_parqueadero = {
    "p1": "LIBRE",
    "p2": "LIBRE"
}

# --- Memoria temporal para usuarios registrados ---
usuarios_registrados = []


# ========================================================
# 1. CONTROL DE PARQUEADEROS (Telemetría ESP32 y App)
# ========================================================

@app.route('/api/estacionamiento', methods=['POST'])
def recibir_datos():
    global estado_parqueadero
    data = request.json  
    
    if data:
        for p in ["p1", "p2"]:
            estado_sensor = data.get(p) # Lo que ve el ultrasonido ("LIBRE" o "OCUPADO")
            estado_actual = estado_parqueadero[p] # Lo que está guardado en la nube
            
            # Si está RESERVADO, el sensor solo puede cambiarlo si el carro FÍSICAMENTE llega
            if estado_actual == "RESERVADO":
                if estado_sensor == "OCUPADO":
                    estado_parqueadero[p] = "OCUPADO" # Llegó el carro de la reserva
                # Si el sensor dice "LIBRE", lo ignoramos para mantener el cupo apartado
            else:
                # Si el estado actual es LIBRE u OCUPADO, se obedece ciegamente al sensor
                if estado_sensor:
                    estado_parqueadero[p] = estado_sensor
                    
        print(f"\n[SISTEMA] Estado Actualizado -> P1: {estado_parqueadero['p1']} | P2: {estado_parqueadero['p2']}")
        
    # Devolvemos el estado real para que el ESP32 sepa si le cambiaron algo en la nube
    return jsonify(estado_parqueadero), 200

@app.route('/api/estacionamiento', methods=['GET'])
def entregar_datos():
    return jsonify(estado_parqueadero), 200


# ========================================================
# 2. ACCIÓN: Reservar un espacio desde la App Móvil
# ========================================================

@app.route('/api/reservar', methods=['POST'])
def reservar_parqueadero():
    global estado_parqueadero
    data = request.json
    parqueadero = data.get('parqueadero') # Espera "p1" o "p2"
    
    if parqueadero not in estado_parqueadero:
        return jsonify({"status": "error", "message": "Espacio no válido"}), 404
        
    if estado_parqueadero[parqueadero] == "LIBRE":
        estado_parqueadero[parqueadero] = "RESERVADO"
        print(f"\n[NUBE] ¡Espacio {parqueadero} ha sido RESERVADO desde la App!")
        return jsonify({
            "status": "exito", 
            "message": f"El espacio {parqueadero} se reservó correctamente."
        }), 200
    else:
        return jsonify({
            "status": "error", 
            "message": f"No se puede reservar. El espacio está {estado_parqueadero[parqueadero]}."
        }), 400


# ========================================================
# 3. ACCIÓN: Registro de Usuarios (Modo Offline-First)
# ========================================================

@app.route('/api/registro', methods=['POST'])
def registrar_usuario():
    global usuarios_registrados
    data = request.json
    
    # Validar que el JSON contenga todos los campos obligatorios
    campos_requeridos = ['nombre', 'correo', 'contrasena', 'tipo_usuario']
    if not data or not all(campo in data for campo in campos_requeridos):
        return jsonify({
            "status": "error", 
            "message": "Datos incompletos. Se requiere: nombre, correo, contrasena y tipo_usuario."
        }), 400
        
    # Estructurar el nuevo registro
    nuevo_usuario = {
        "nombre": data.get('nombre'),
        "correo": data.get('correo'),
        "contrasena": data.get('contrasena'),
        "tipo_usuario": data.get('tipo_usuario')
    }
    
    # Almacenar en la lista interna
    usuarios_registrados.append(nuevo_usuario)
    print(f"\n[NUBE] ¡Usuario Sincronizado! -> {nuevo_usuario['nombre']} ({nuevo_usuario['tipo_usuario']})")
    
    return jsonify({
        "status": "sincronizado", 
        "message": "Usuario registrado exitosamente en la nube."
    }), 201


# ========================================================
# 4. CONSULTA: Ver Usuarios Registrados
# ========================================================

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    # Ahora sí, aquí está la función para listar los usuarios en formato JSON
    return jsonify(usuarios_registrados), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
