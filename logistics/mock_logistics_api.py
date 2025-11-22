# mock_logistics_api.py
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/schedule", methods=["POST"])
def schedule_delivery():
    data = request.get_json()
    items = data.get("items", {})
    if not items:
        return jsonify({"success": False, "message": "No items provided"}), 400

    # Simulate delivery ETA (2 hours from now)
    eta = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"success": True, "eta": eta, "items_count": len(items)})

if __name__ == "__main__":
    app.run(port=5001)
