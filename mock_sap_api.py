from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock endpoint to mimic SAP API behavior
@app.route('/sap-api', methods=['POST'])
def sap_api():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400

    # Log the received data (in real SAP API, you'd process it here)
    print("Received data:", data)

    # Mock response simulating successful data processing
    return jsonify({"status": "success", "message": "Data received and processed by SAP mock API"}), 200

if __name__ == '__main__':
    app.run(port=5002, debug=True)
