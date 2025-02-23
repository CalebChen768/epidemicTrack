import pymysql
from dotenv import load_dotenv
import os
from IDGenerator import IDGenerator
import pandas as pd
from decimal import Decimal

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

    def set_risk(self, visited_place: list):
        """
            set the risk of a checkpoint at a specific time
            -visited_place: [{""checkpoint_id": "xxx", "time": 123}, ...]
        """

        result = []
        data = []
        for place in visited_place:
            # print("place:", place)
            data += [(place["checkpoint_id"], place["time"], "high")]
            result += self._get_all_checkpoints(place["checkpoint_id"], place["time"], place["time"]) 

        # group by target_checkpoint and target_time, then get the row with the minimum time_diff
        df = pd.DataFrame(result)
        filtered_df = df.loc[df.groupby(['target_checkpoint', 'target_time'])['time_diff'].idxmin()]

        result = filtered_df.to_dict(orient='records')

        data += [(res["target_checkpoint"], res["target_time"], res["risk"]) for res in result]
        cursor = self.connection.cursor()
        sql = """
        INSERT INTO risks (checkpoint_id, time, risk)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            risk = CASE 
                WHEN risk = 'medium' AND VALUES(risk) = 'high' THEN 'high'
                ELSE risk
            END;
        """

        cursor.executemany(sql, data)
        self.connection.commit()

        return result
    

    # ------------------------------------
    # additional security feature
    def set_risk_with_psi(self, visited_place: list):
        """
            same with set_risk, but with encrypted data for PSI
        """        
        from psi_utils import hash_and_encrypt
        from server import server_private_key

        result = []
        data = []
        for place in visited_place:
            # print("place:", place)
            data += [(place["checkpoint_id"], place["time"], "high")]
            result += self._get_all_checkpoints(place["checkpoint_id"], place["time"], place["time"]) 

        # group by target_checkpoint and target_time, then get the row with the minimum time_diff
        df = pd.DataFrame(result)
        filtered_df = df.loc[df.groupby(['target_checkpoint', 'target_time'])['time_diff'].idxmin()]

        result = filtered_df.to_dict(orient='records')

        data += [(res["target_checkpoint"], res["target_time"], res["risk"]) for res in result]
       
        server_data = pd.DataFrame(data, columns=['checkpoint_id', 'time', 'risk'])
        server_data['encrypted'] = server_data.apply(
            lambda row: Decimal(hash_and_encrypt(row['checkpoint_id'] + str(row['time']), server_private_key)), axis=1
        )

        # save ['encrypted', 'risk' ] to the database
        cursor = self.connection.cursor()
        sql = """
        INSERT INTO risks_psi (encrypted, risk)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE 
            risk = CASE 
                WHEN risk = 'medium' AND VALUES(risk) = 'high' THEN 'high'
                ELSE risk
            END;
        """

        print("saved data:")
        # print(server_data)
        cursor.executemany(sql, server_data[['encrypted', 'risk']].values.tolist())
        self.connection.commit()
        return server_data[['encrypted', 'risk']].to_dict(orient='records')
    # ------------------------------------
        

    def _get_all_checkpoints(self, checkpoint_id, source_time, start_time, time_window=5, current_depth=0, final_results=None):
        """
            recursive function to find the target_time and target_checkpoint of a given checkpoint:
            - time-window: the maximum depth of the search
        """
        # check if the current depth exceeds the time window
        if final_results is None:
            final_results = []

        # if the current depth exceeds the time window, return results
        print(current_depth, time_window)
        if current_depth >= time_window:
            return final_results

        cursor = self.connection.cursor()
        query = """
            SELECT target_time, target_checkpoint_id
            FROM transmissions
            WHERE source_checkpoint_id = %s
            AND source_time = %s
        """

        cursor.execute(query, (checkpoint_id, source_time))
        results = cursor.fetchall()  
        # print(final_results)
        if results:
            for result in results:
                # print("result:", result)
                target_time, target_checkpoint = result
                # calculate time difference
                time_diff = abs(target_time - start_time)
                final_results.append({
                    "source_checkpoint": checkpoint_id,
                    "target_time": target_time,
                    "time_diff": time_diff,
                    "target_checkpoint": target_checkpoint,
                    "risk": "medium"
                })
                # print(f"Depth {current_depth}: {checkpoint_id} -> {target_checkpoint}, time_diff: {time_diff}")
                # recursive call
                if target_checkpoint:
                    final_results += self._get_all_checkpoints(target_checkpoint, target_time, start_time, time_window, current_depth + 1)
            return final_results
        else:
            return final_results
        

    def get_risk_level(self, visited_place: list):
        """
        Check the highest risk level among visited places.
        """
        cursor = self.connection.cursor()

        sql = """
        SELECT risk
        FROM risks 
        WHERE (checkpoint_id, time) IN ({})
        ORDER BY FIELD(risk, 'high', 'medium')  
        LIMIT 1;
        """.format(', '.join(['(%s, %s)'] * len(visited_place)))

        params = [item for place in visited_place for item in (place['checkpoint_id'], place['time'])]

        cursor.execute(sql, params)
        result = cursor.fetchone()

        return result[0] if result else "low"

            
    def get_risk_level_psi(self):
        """
        Get the risk level from the encrypted data
        """
        cursor = self.connection.cursor()

        sql = """
        SELECT encrypted, risk
        FROM risks_psi;
        """

        cursor.execute(sql)
        result = cursor.fetchall()
        # print("fetched data")
        result = [(int(row[0]), row[1]) for row in result]
        # print(result)
        return result