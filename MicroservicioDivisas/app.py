from flask import Flask, request, jsonify
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError
import os
import time

app = Flask(__name__)

# ====== Config ======
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB_NAME", "divisas")
CACHE_TTL = 60           # segundos
HISTORY_MAX = 1000       # máximo registros en memoria

# ====== Tasas estáticas ======
STATIC_RATES = {
    ("USD", "EUR"): 0.85,
    ("EUR", "USD"): 1.18,
    ("USD", "COP"): 3800.0,
    ("COP", "USD"): 0.000263,
}

# ====== Caché e historial en memoria (fallback) ======
_rate_cache_mem = {}     # key -> (rate, ts)
_history_mem = []        # lista de registros (más reciente primero)

# ====== Mongo (opcional) ======
mongo_available = False
rates_col = None
conversions_col = None

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    client.server_info()  # fuerza conexión
    db = client[MONGO_DB]
    rates_col = db["rates_cache"]
    conversions_col = db["conversions"]
    # índices (key único y TTL sobre createdAt)
    rates_col.create_index([("key", ASCENDING)], unique=True)
    rates_col.create_index([("createdAt", ASCENDING)], expireAfterSeconds=CACHE_TTL)
    conversions_col.create_index([("createdAt", ASCENDING)])
    mongo_available = True
except (PyMongoError, ServerSelectionTimeoutError):
    mongo_available = False

# ====== Utilidades simples ======
def key_pair(a, b):
    return f"{a.upper()}_{b.upper()}"

def get_cached_rate(a, b):
    k = key_pair(a, b)
    # intento Mongo
    if mongo_available and rates_col is not None:
        try:
            doc = rates_col.find_one({"key": k})
            if doc and "rate" in doc:
                return float(doc["rate"])
        except PyMongoError:
            pass
    # fallback memoria
    entry = _rate_cache_mem.get(k)
    if entry:
        rate, ts = entry
        if time.time() - ts < CACHE_TTL:
            return rate
        else:
            _rate_cache_mem.pop(k, None)
    return None

def set_cached_rate(a, b, rate):
    k = key_pair(a, b)
    now = datetime.now(timezone.utc)
    if mongo_available and rates_col is not None:
        try:
            rates_col.update_one({"key": k}, {"$set": {"rate": float(rate), "createdAt": now}}, upsert=True)
            return
        except PyMongoError:
            pass
    _rate_cache_mem[k] = (float(rate), time.time())

def save_conversion(a, b, amount, rate, converted):
    rec = {
        "from": a, "to": b,
        "amount": float(amount), "rate": float(rate), "converted": float(converted),
        "createdAt": datetime.now(timezone.utc)
    }
    if mongo_available and conversions_col is not None:
        try:
            conversions_col.insert_one(rec)
            return
        except PyMongoError:
            pass
    # fallback memoria (isoformat para facilitar serialización)
    rec_mem = rec.copy()
    rec_mem["createdAt"] = rec_mem["createdAt"].isoformat()
    _history_mem.insert(0, rec_mem)
    if len(_history_mem) > HISTORY_MAX:
        _history_mem.pop()

def get_static_rate(a, b):
    if a.upper() == b.upper():
        return 1.0
    return STATIC_RATES.get((a.upper(), b.upper()), 1.0)  # fallback 1.0

# ====== Endpoints ======
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mongo": mongo_available, "static_rates": len(STATIC_RATES)}), 200

@app.route("/convert", methods=["GET", "POST"])
def convert():
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Body JSON requerido"}), 400
        src = data.get("from")
        dst = data.get("to")
        amt = data.get("amount")
    else:
        src = request.args.get("from")
        dst = request.args.get("to")
        amt = request.args.get("amount")

    if not src or not dst or amt is None:
        return jsonify({"error": "Parámetros requeridos: from, to, amount"}), 400

    try:
        amt_val = float(amt)
    except (ValueError, TypeError):
        return jsonify({"error": "amount debe ser numérico"}), 400

    src = src.upper(); dst = dst.upper()

    rate = get_cached_rate(src, dst)
    if rate is None:
        rate = get_static_rate(src, dst)
        set_cached_rate(src, dst, rate)

    converted = round(amt_val * rate, 6)
    save_conversion(src, dst, amt_val, rate, converted)

    return jsonify({"from": src, "to": dst, "amount": amt_val, "rate": rate, "converted": converted}), 200

@app.route("/history", methods=["GET"])
def history():
    try:
        limit = int(request.args.get("limit", 20))
    except (ValueError, TypeError):
        limit = 20

    if mongo_available and conversions_col is not None:
        try:
            docs = conversions_col.find().sort("createdAt", -1).limit(limit)
            out = []
            for d in docs:
                out.append({
                    "from": d.get("from"),
                    "to": d.get("to"),
                    "amount": float(d.get("amount")),
                    "rate": float(d.get("rate")),
                    "converted": float(d.get("converted")),
                    "createdAt": d.get("createdAt").isoformat() if d.get("createdAt") else None
                })
            return jsonify(out), 200
        except PyMongoError:
            pass

    # fallback memoria
    return jsonify(_history_mem[:max(1, min(limit, len(_history_mem)))]), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
