import hashlib
import random
import pandas as pd

# generate a large prime number p and a generator g
P = 2**127 - 1
G = 5

server_private_key = 2**49 * 3
client_private_key = 123

def hash_and_encrypt(value, private_key):
    hashed = int(hashlib.sha256(value.encode()).hexdigest(), 16) % P
    return pow(G, hashed * private_key, P)

server_data = pd.DataFrame({
    'checkpoint_id': ['4fzSij2rRB', '4fzSij2rRB', 'DYFYZlbmRZ', 'Jl2pflh9QD', 'LM+EsCBTS3', 'LM+EsCBTS3', 'LM+EsCBTS3', 'zZ4i2BORTB', 'zZ4i2BORTB'],
    'time': [4, 6, 3, 2, 1, 5, 6, 2, 5],
    'risk': ['medium', 'medium', 'medium', 'medium', 'high', 'medium', 'medium', 'medium', 'high']
})

client_data = pd.DataFrame({
    'checkpoint_id': ['4fzSij2rRB', 'LM+EsCBTS3', 'randomID'],
    'time': [4, 9, 7]
})

if __name__ == '__main__':
    # server encrypts the data
    server_data['encrypted'] = server_data.apply(
        lambda row: hash_and_encrypt(row['checkpoint_id'] + str(row['time']), server_private_key), axis=1
    )

    # client encrypts the data
    client_data['encrypted'] = client_data.apply(
        lambda row: hash_and_encrypt(row['checkpoint_id'] + str(row['time']), client_private_key), axis=1
    )

    # exchange the encrypted data
    client_from_server = server_data[['encrypted']].copy()
    client_from_server['double_encrypted'] = client_from_server['encrypted'].apply(
        lambda enc: pow(enc, client_private_key, P)
    )

    server_from_client = client_data[['encrypted']].copy()
    print(server_from_client.dtypes)
    server_from_client['double_encrypted'] = server_from_client['encrypted'].apply(
        lambda enc: pow(enc, server_private_key, P)
    )

    # server sends the double encrypted data to the client
    client_final_data = server_from_client.copy()

    # client calculates the intersection
    client_intersection = set(client_from_server['double_encrypted']).intersection(set(client_final_data['double_encrypted']))
    print(client_intersection)
