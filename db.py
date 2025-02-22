import pymysql
from dotenv import load_dotenv
import os
from IDGenerator import IDGenerator

class DBService:
    def __init__(self):
        load_dotenv()
        self.MYSQL_HOST = os.getenv("MYSQL_HOST")
        self.MYSQL_PORT = os.getenv("MYSQL_PORT")
        self.MYSQL_USER = os.getenv("MYSQL_USER")
        self.MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
        self.MYSQL_DB = os.getenv("MYSQL_DB")
        self.id_generator = IDGenerator()

        # connect to database
        self.connection = self._connect_db()

    def _connect_db(self):
        return pymysql.connect(host=self.MYSQL_HOST,
                                port=int(self.MYSQL_PORT),
                                user=self.MYSQL_USER,
                                password=self.MYSQL_PASSWORD,
                                database=self.MYSQL_DB)
    def create_checkpoint(self):
        """
            create a checkpoint and return the checkpoint_id
        """
        cursor = self.connection.cursor()
        checkpoint_id = self.id_generator.get_id()
        cursor.execute("INSERT INTO checkpoints (checkpoint_id) VALUES (%s)", (checkpoint_id,))
        self.connection.commit()
        return checkpoint_id
    
    def add_an_edge(self, source_checkpoint_id, source_time, target_checkpoint_id, target_time):
        """
            add an edge to the transmission table
        """
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO transmissions (source_checkpoint_id, source_time, target_checkpoint_id, target_time) VALUES (%s, %s, %s, %s)", (source_checkpoint_id, source_time, target_checkpoint_id, target_time))
        self.connection.commit()

    def set_risk(self, visited_place: list, risk):
        """
            set the risk of a checkpoint at a specific time
            -visited_place: [{""checkpoint_id": "xxx", "time": 123}, ...]
        """

        result = []
        for place in visited_place:
            print(place)
            result += self._get_all_checkpoints(place["checkpoint_id"], place["time"], risk) 
        return list(set(result))

    def _get_all_checkpoints(self, checkpoint_id, source_time, time_window=3, current_depth=0, results=None):
        """
            recursive function to find the target_time and target_checkpoint of a given checkpoint:
            - time-window: the maximum depth of the search
        """
        # check if the current depth exceeds the time window
        if results is None:
            results = []

        # if the current depth exceeds the time window, return results
            return results

        cursor = self.connection.cursor()
        query = """
            SELECT target_time, target_checkpoint 
            FROM checkpoints 
            WHERE source_checkpoint = %s 
            AND ABS(source_time - %s) = (
                SELECT MIN(ABS(source_time - %s))
                FROM checkpoints
                WHERE source_checkpoint = %s
            )
            LIMIT 1
        """
        cursor.execute(query, (checkpoint_id, source_time, source_time, checkpoint_id))
        result = cursor.fetchone()
        print(result)
        if result:
            target_time, target_checkpoint = result
            # calculate time difference
            time_diff = abs(target_time - source_time)
            results.append({
                "source_checkpoint": checkpoint_id,
                "target_time": target_time,
                "time_diff": time_diff,
                "target_checkpoint": target_checkpoint
            })
            print(f"Depth {current_depth}: {checkpoint_id} -> {target_checkpoint}, time_diff: {time_diff}")
            # recursive call
            if target_checkpoint:
                return self._get_all_checkpoints(target_checkpoint, target_time, time_window, current_depth + 1, results)
            else:
                return results
        else:
            return results
