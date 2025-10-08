from flask import Flask, request, jsonify
import requests
import time
import os
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
from datetime import datetime, timezone

app = Flask(__name__)

# Config
EXCHANGE_API = "https://api.exchangerate.host/convert"
CACHE_TTL = 60  # segundos para cache simple de tasas
REQUEST_TIMEOUT = 8  # segundos

# Configuración de MongoDB local
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB_NAME = "divisas"


# Fallback cache en memoria (por si Mongo no responde)
_rate_cache_inmemory = {}

# Inicializar cliente mongo (se intentará conectar al inicio)
mongo_client = None
db = None
rates_cache_col = None
conversions_col = None
mongo_available = False

def init_mongo():
    global mongo_client, db, rates_cache_col, conversions_col, mongo_available
    try:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)  # 3s timeout
        # fuerza la conexión (lanzará excepción si no puede conectar)
        mongo_client.server_info()
        db = mongo_client[MONGO_DB_NAME]
        rates_cache_col = db["rates_cache"]
        conversions_col = db["conversions"]
        # Crear TTL index en rates_cache para que los documentos caduquen automáticamente
        rates_cache_col.create_index([("key", ASCENDING)], unique=True)
        rates_cache_col.create_index([("createdAt", ASCENDING)], expireAfterSeconds=CACHE_TTL)
        # Crear índice de timestamp en conversions para consultas ordenadas
        conversions_col.create_index([("createdAt", ASCENDING)])
        mongo_available = True
        print("MongoDB conectado correctamente:", MONGO_URI, "DB:", MONGO_DB_NAME)
    except (PyMongoError, ServerSelectionTimeoutError) as e:
        mongo_available = False
        print("Warning: no se pudo conectar a MongoDB:", e)
        # dejamos la caché en memoria

init_mongo()

def _make_key(from_code: str, to_code: str) -> str:
    return f"{from_code.upper()}_{to_code.upper()}"

def get_cached_rate(from_code: str, to_code: str):
    key = _make_key(from_code, to_code)
    if mongo_available and rates_cache_col is not None:
        try:
            doc = rates_cache_col.find_one({"key": key})
            if doc and "rate" in doc:
                # Si existe, devolvemos la tasa (TTL en Mongo eliminará doc cuando expire)
                return float(doc["rate"])
        except PyMongoError as e:
            # log y fallback a memoria
            print("Warning: fallo lectura caché Mongo:", e)

    #caché en memoria
    entry = _rate_cache_inmemory.get(key)
    if entry:
        rate, ts = entry
        if time.time() - ts < CACHE_TTL:
            return rate
        else:
            # expiró
            _rate_cache_inmemory.pop(key, None)
    return None

#    Intenta persistir la tasa en MongoDB con createdAt para el TTL. También actualiza la caché en memoria.
def set_cached_rate(from_code: str, to_code: str, rate: float):
    
    key = _make_key(from_code, to_code)
    now = datetime.now(timezone.utc)
    if mongo_available and rates_cache_col is not None:
        try:
            rates_cache_col.update_one(
                {"key": key},
                {"$set": {"rate": float(rate), "createdAt": now}},
                upsert=True
            )
            return
        except PyMongoError as e:
            print("Warning: fallo escritura caché Mongo:", e)

    # fallback: caché en memoria
    _rate_cache_inmemory[key] = (float(rate), time.time())

def save_conversion_record(from_code: str, to_code: str, amount: float, rate: float, converted: float):
   
    if not (mongo_available and conversions_col is not None):
        return
    try:
        conversions_col.insert_one({
            "from": from_code,
            "to": to_code,
            "amount": float(amount),
            "rate": float(rate),
            "converted": float(converted),
            "createdAt": datetime.now(timezone.utc)
        })
    except PyMongoError as e:
        print("Warning: fallo al guardar registro de conversión:", e)

def fetch_rate_external(from_code: str, to_code: str):
    """
    Obtiene la tasa usando exchangerate.host (no requiere API key).
    Devuelve float (rate) o lanza excepción con detalle.
    """
    params = {"from": from_code, "to": to_code, "amount": 1}
    try:
        r = requests.get(EXCHANGE_API, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Error de conexión a API externa: {e}")

    try:
        j = r.json()
    except ValueError:
        # respuesta no es JSON
        raise RuntimeError(f"Respuesta no JSON de la API externa: {r.text}")

    if not j.get("success", False):
        raise RuntimeError(f"API de tasas no respondió correctamente. payload: {j}")

    if "info" in j and "rate" in j["info"]:
        return float(j["info"]["rate"])
    if "result" in j:
        return float(j["result"])

    raise RuntimeError(f"Respuesta inesperada de la API externa: {j}")



#TASAS ESTATICAS, SI NO SE CONENCTA A LA API
def fetch_rate_with_fallback(from_code: str, to_code: str):
    try:
        return fetch_rate_external(from_code, to_code)
    except Exception as e:
        print("Warning: fallo al obtener tasa externa:", e)
        static_rates = {
            ("USD", "EUR"): 0.85,
            ("EUR", "USD"): 1.18,
            ("USD", "COP"): 3800.0,
            ("COP", "USD"): 0.000263,
        }
        key = (from_code.upper(), to_code.upper())
        if key in static_rates:
            print("Usando tasa estática para", key, "=", static_rates[key])
            return static_rates[key]
        print("No hay tasa estática para", key, "-> fallback 1.0")
        return 1.0

@app.route("/health", methods=["GET"])
def health():
    status = {"status": "ok", "mongo": mongo_available}
    return jsonify(status), 200

@app.route("/convert", methods=["GET", "POST"])
def convert():
    """
    Soporta:
     - GET /convert?from=USD&to=EUR&amount=100
     - POST /convert  -> JSON body: {"from":"USD","to":"EUR","amount":100}
    """
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Body JSON requerido y Content-Type: application/json"}), 400
        from_code = data.get("from")
        to_code = data.get("to")
        amount = data.get("amount")
    else:
        from_code = request.args.get("from")
        to_code = request.args.get("to")
        amount = request.args.get("amount")

    if not from_code or not to_code or amount is None:
        return jsonify({"error": "Parámetros requeridos: from, to, amount"}), 400

    try:
        amount_value = float(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "El parámetro amount debe ser numérico"}), 400

    from_code = from_code.upper()
    to_code = to_code.upper()

    # Checar cache (Mongo o memoria)
    rate = get_cached_rate(from_code, to_code)
    if rate is None:
        try:
            rate = fetch_rate_with_fallback(from_code, to_code)
            set_cached_rate(from_code, to_code, rate)
        except Exception as e:
            return jsonify({"error": "Error al obtener la tasa", "detail": str(e)}), 502

    converted = amount_value * rate

    # Guardar un registro de conversión (si Mongo disponible)
    save_conversion_record(from_code, to_code, amount_value, rate, converted)

    return jsonify({
        "from": from_code,
        "to": to_code,
        "amount": amount_value,
        "rate": rate,
        "converted": round(converted, 6)
    }), 200

@app.route("/history", methods=["GET"])
def history():
    """
    Endpoint para revisar el historial de conversiones guardadas (solo si Mongo disponible).
    Permite ?limit=10
    """
    if not (mongo_available and conversions_col is not None):
        return jsonify({"error": "Historial no disponible (MongoDB no conectado)"}), 503
    try:
        limit = int(request.args.get("limit", 20))
        docs = list(conversions_col.find().sort("createdAt", -1).limit(limit))
        # convertir ObjectId/Datetime a serializable
        results = []
        for d in docs:
            results.append({
                "from": d.get("from"),
                "to": d.get("to"),
                "amount": float(d.get("amount")),
                "rate": float(d.get("rate")),
                "converted": float(d.get("converted")),
                "createdAt": d.get("createdAt").isoformat() if d.get("createdAt") else None
            })
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": "Error al leer historial", "detail": str(e)}), 500

if __name__ == "__main__":
    # DEBUG True solo en desarrollo
    app.run(host="0.0.0.0", port=5000, debug=True)
