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

    