import json
import os
import threading

from flask import Flask, jsonify, render_template, request

from pipeline import run, RESULTS_PATH

app = Flask(__name__)

# Common Property24 commercial search paths, keyed by a friendly label.
REGIONS = {
    "Cape Town": {
        "path": "commercial-property-for-sale/cape-town/western-cape/432",
        "city": "Cape Town",
        "province": "Western Cape",
    },
    "Johannesburg": {
        "path": "commercial-property-for-sale/johannesburg/gauteng/9",
        "city": "Johannesburg",
        "province": "Gauteng",
    },
    "Pretoria": {
        "path": "commercial-property-for-sale/pretoria/gauteng/10",
        "city": "Pretoria",
        "province": "Gauteng",
    },
    "Durban": {
        "path": "commercial-property-for-sale/durban/kwazulu-natal/145",
        "city": "Durban",
        "province": "KwaZulu-Natal",
    },
}

_run_lock = threading.Lock()
_run_status = {"running": False, "region": None, "error": None}


def _load_results():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.route("/")
def index():
    return render_template("index.html", regions=list(REGIONS.keys()))


@app.route("/api/regions")
def api_regions():
    return jsonify(list(REGIONS.keys()))


@app.route("/api/results")
def api_results():
    return jsonify(_load_results())


@app.route("/api/status")
def api_status():
    return jsonify(_run_status)


@app.route("/api/scrape", methods=["POST"])
def api_scrape():
    region = request.json.get("region")
    max_pages = int(request.json.get("max_pages", 2))
    if region not in REGIONS:
        return jsonify({"error": "unknown region"}), 400
    if _run_status["running"]:
        return jsonify({"error": "a scrape is already running"}), 409

    def worker():
        with _run_lock:
            _run_status.update({"running": True, "region": region, "error": None})
            try:
                cfg = REGIONS[region]
                run(cfg["path"], max_pages=max_pages, city_hint=cfg["city"], province_hint=cfg["province"])
            except Exception as e:
                _run_status["error"] = str(e)
            finally:
                _run_status["running"] = False

    threading.Thread(target=worker, daemon=True).start()
    return jsonify({"started": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
