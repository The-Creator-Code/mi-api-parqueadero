from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Memoria temporal para los parqueaderos (ESP32) ---
estado_parqueadero = {
    "p1": "LIBRE",
    "p2": "LIBRE"
}

# --- Memoria temporal para usuarios registrados ---
usuarios_registrados = []


# ========================================================
# RUTAS PARA EL CONTROL DE PARQUEADEROS
# ========================================================

@app.route('/api/estacionamiento', methods=['POST'])
def recibir_datos():
    global estado_parqueadero
    data = request.json  
    if data:
        estado_parqueadero["p1"] = data.get('p1', 'LIBRE')
        estado_parqueadero["p2"] = data.get('p2', 'LIBRE')
        print(f"\n[ESP32] Actualizado -> P1: {estado_parqueadero['p1']} | P2: {estado_parqueadero['p2']}")
    return jsonify({"status": "actualizado"}), 200

@app.route('/api/estacionamiento', methods=['GET'])
def entregar_datos():
    return jsonify(estado_parqueadero), 200


# ========================================================
# RUTA REQUERIDA: REGISTRO DE USUARIOS (Offline-First)
# ========================================================

@app.route('/api/registro', methods=['POST'])
def registrar_usuario():
    global usuarios_registrados
    data = request.json
    
    # 1. Validar que el JSON contenga todos los nuevos campos obligatorios
    campos_requeridos = ['nombre', 'correo', 'contrasena', 'tipo_usuario']
    if not data or not all(campo in data for campo in campos_requeridos):
        return jsonify({
            "status": "error", 
            "message": "Datos incompletos. Se requiere: nombre, correo, contrasena y tipo_usuario."
        }), 400
        
    # 2. Estructurar el nuevo registro
    nuevo_usuario = {
        "nombre": data.get('nombre'),
        "correo": data.get('correo'),
        "contrasena": data.get('contrasena'),  # En producción se encripta, para el prototipo es funcional así
        "tipo_usuario": data.get('tipo_usuario') # Ejemplo: "Estudiante", "Docente", etc.
    }
    
    # 3. Almacenar en la lista del servidor
    usuarios_registrados.append(nuevo_usuario)
    
    # Monitoreo en la consola de Render
    print(f"\n[NUBE] ¡Usuario Sincronizado! -> {nuevo_usuario['nombre']} ({nuevo_usuario['tipo_usuario']})")
    
    return jsonify({
        "status": "sincronizado", 
        "message": "Usuario registrado exitosamente en la nube."
    }), 201


# ========================================================
# RUTA EXTRA: VER USUARIOS REGISTRADOS
# ========================================================

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    # Te servirá para verificar desde el navegador o Postman quiénes se han registrado
    return jsonify(usuarios_registrados), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
