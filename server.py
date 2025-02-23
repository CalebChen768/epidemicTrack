from flask import Flask, request, jsonify
from db import DBService
import pandas as pd
from psi_utils import P
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
# limiter
limiter = Limiter(
    get_remote_address,  
    app=app
)
# create db connection
db_service = DBService()

server_private_key = 123456




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
    # ----------------------------------
    # this part is additional security feature
    # the server encrypts the data before storing it,
    # but I still kept the original way in the code. (just for testing)
    db_service.set_risk_with_psi(visited_place)
    # ----------------------------------


    return jsonify({"message": "success"})

@app.route('/api/safe', methods=['POST'])
@limiter.limit("2 per minite") 
def get_risk():
    visited_place = request.json['visited_place']
    risk_level = db_service.get_risk_level(visited_place)
    return jsonify({"risk_level": risk_level})

@app.route('/api/safe_psi', methods=['POST'])
@limiter.limit("2 per minite") 
def get_risk_psi():
    client_data_encrpted = pd.DataFrame({
        'encrypted': request.json['client_data_encrpted'],
        })
    server_from_client = client_data_encrpted.copy()
    server_from_client['double_encrypted'] = server_from_client['encrypted'].apply(
        lambda enc: pow(enc, server_private_key, P)
        )
    print("-------------------------------------------")
    print("Server double encrypting data from client")
    print("-------------------------------------------")

    print(server_from_client)

    server_data_encrpted = db_service.get_risk_level_psi()
    # print(server_data_encrpted)
    
    return jsonify({"server_data_encrpted": server_data_encrpted, "client_data_encrpted": server_from_client['double_encrypted'].tolist()})



if __name__ == '__main__':  
    app.run(port=5000)
