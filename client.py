import requests
import json
import time
import pandas as pd
from psi_utils import hash_and_encrypt, P

client_private_key = 654321

class Client:
    def __init__(self):
        self.url = "http://127.0.0.1:5000/api"
        self.visited_places = [] 
        self.start_time = 1740324310
        self.time_window = 150 # possible risk time window

    def create_checkpoint(self):
        response = requests.post(f"{self.url}/checkpoint")
        return response.json()["checkpoint_id"]
        
    def at_home(self):
        self.visited_places += [("HOME", self._get_current_time())]

    def _get_current_time(self):
        return int((int(time.time()) - self.start_time) / 1800)
    
    def scan(self, target_checkpoint_id):

        if len(self.visited_places) == 0 or self.visited_places[-1][0] == "HOME":
            self.visited_places.append((target_checkpoint_id, self._get_current_time()))
        else:
            source_checkpoint_id, source_time = self.visited_places[-1]
            self.visited_places.append((target_checkpoint_id, self._get_current_time()))
            response = requests.post(f"{self.url}/scan", json={"source_checkpoint_id": source_checkpoint_id, "source_time": source_time, "target_checkpoint_id": target_checkpoint_id, "target_time": self._get_current_time()})
            print(response.json())

    def report(self):
        """
            to add a safety feature!!!!!!!!!!!!!!
        """
        time_now = self._get_current_time()
        submit = [{"checkpoint_id": place[0], "time": place[1]} for place in self.visited_places if place[1] >= time_now-self.time_window and place[0] != "HOME"]
        
        response = requests.post(f"{self.url}/risk", json={"visited_place": submit})
        print(response.json())

    def is_safe(self):
        time_now = self._get_current_time()
        submit = [{"checkpoint_id": place[0], "time": place[1]} for place in self.visited_places if place[1] >= time_now-self.time_window and place[0] != "HOME"]

        print(submit)
        response = requests.post(f"{self.url}/safe", json={"visited_place": submit})
        print(response.json())
    
    def is_safe_psi(self):
        time_now = self._get_current_time()
        submit = [{"checkpoint_id": place[0], "time": place[1]} for place in self.visited_places if place[1] >= time_now-self.time_window and place[0] != "HOME"]
        # to Dataframe
        submit = pd.DataFrame(submit)
        # to encrypted
        submit['encrypted'] = submit.apply(
            lambda row: hash_and_encrypt(row['checkpoint_id'] + str(row['time']), client_private_key), axis=1
        )
        print("-------------------------------------------")
        print("client sending encrypted data to server")
        print("-------------------------------------------")

        print(submit['encrypted'])
        response = requests.post(f"{self.url}/safe_psi", json={"client_data_encrpted": submit['encrypted'].tolist()})
        # print(response.json())
        
        client_data_double_encrypted = response.json()["client_data_encrpted"]
        server_data_encrypted = response.json()["server_data_encrpted"]
        server_data_encrypted_df = pd.DataFrame(server_data_encrypted, columns=['encrypted', 'risk'])
        # print(server_data_encrypted_df)
        # server_data_encrypted_df['encrypted'] = server_data_encrypted_df['encrypted'].astype(int) 


        server_data_encrypted_df['double_encrypted'] = server_data_encrypted_df['encrypted'].apply(
            lambda enc: pow(enc, client_private_key, P)
        )
        print("-------------------------------------------")
        print("client double encrypting data from server")
        print("-------------------------------------------")

        print(server_data_encrypted_df['double_encrypted'])
        # print(server_data_encrypted_df)

        # print(client_data_double_encrypted)
        
        # find intersection bwteen client_data_double_encrypted and server_data_encrypted_df['double_encrypted'] and get risks
        matched = pd.merge(pd.DataFrame(client_data_double_encrypted, columns=['double_encrypted']), server_data_encrypted_df, on='double_encrypted', how='inner')
        if 'high' in matched['risk'].values:
            print("There are high risk in the visited places.")
        elif 'medium' in matched['risk'].values:
            print("There are medium risk in the visited places.")
        else:
            print("There is no high risk in the visited places.")
        


if __name__ == '__main__':
    client = Client()
    cpt1 = client.create_checkpoint()
    cpt2 = client.create_checkpoint()
    cpt3 = client.create_checkpoint()

    client.scan(cpt1)
    client.at_home()
    client.scan(cpt2)
    client.scan(cpt3)
    client.scan(cpt1)
    client.scan(cpt2)

    client.report()
    client.is_safe_psi()




