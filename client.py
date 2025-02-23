import requests
import json
import time

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
    client.is_safe()




