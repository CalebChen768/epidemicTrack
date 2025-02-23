from flask import Flask, request, jsonify
from db import DBService

app = Flask(__name__)

# create db connection
db_service = DBService()

@app.route('/api/checkpoint', methods=['POST'])
def create_checkpoint():
    checkpoint_id = db_service.create_checkpoint()
    return jsonify({"checkpoint_id": checkpoint_id})

@app.route('/api/scan', methods=['POST'])
def scan():
    source_checkpoint_id = request.json['source_checkpoint_id']
    source_time = request.json['source_time']
    target_checkpoint_id = request.json['target_checkpoint_id']
    target_time = request.json['target_time']
    db_service.add_an_edge(source_checkpoint_id, source_time, target_checkpoint_id, target_time)
    return jsonify({"message": "success"})

@app.route('/api/risk', methods=['POST'])
def set_risk():
    visited_place = request.json['visited_place']
    db_service.set_risk(visited_place)
    return jsonify({"message": "success"})

@app.route('/api/safe', methods=['POST'])
def get_risk():
    visited_place = request.json['visited_place']
    risk_level = db_service.get_risk_level(visited_place)
    return jsonify({"risk_level": risk_level})

if __name__ == '__main__':  
    app.run(port=5000, debug=True)
