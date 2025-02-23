import pymysql
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# MySQL configuration
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# initialize MySQL
def init_mysql():
    connection = pymysql.connect(host=MYSQL_HOST,
                                port=int(MYSQL_PORT),
                                 user=MYSQL_USER,
                                 password=MYSQL_PASSWORD,
                                 database=MYSQL_DB)
    cursor = connection.cursor()

    # create location table: location_id
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkpoints (
        checkpoint_id VARCHAR(10) PRIMARY KEY
    );
    """)

    # create transmission table: source_checkpoint_id, source_time, target_checkpoint_id, target_time
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transmissions (
        id INT AUTO_INCREMENT PRIMARY KEY, 
        source_checkpoint_id VARCHAR(10),
        source_time INT,
        target_checkpoint_id VARCHAR(10) NOT NULL,
        target_time INT NOT NULL,
        INDEX idx_source (source_checkpoint_id, source_time),     
        UNIQUE KEY (source_checkpoint_id, source_time, target_checkpoint_id, target_time),  
        FOREIGN KEY (source_checkpoint_id) REFERENCES checkpoints(checkpoint_id) ON DELETE CASCADE,
        FOREIGN KEY (target_checkpoint_id) REFERENCES checkpoints(checkpoint_id) ON DELETE CASCADE
    );

    """)
    
    # create risk table: checkpoint_id, time, risk
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks (
        checkpoint_id VARCHAR(10),
        time INT,
        risk ENUM('medium', 'high') NOT NULL,
        PRIMARY KEY (checkpoint_id, time),
        FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(checkpoint_id) ON DELETE CASCADE
    );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risks_psi (
        encrypted DECIMAL(40, 0) PRIMARY KEY,
        risk ENUM('medium', 'high') NOT NULL
    );
    """)

    connection.commit()

    print("""
    --------------------------------
    Checkpoints database initialized
    --------------------------------
    """)
    connection.close()


if __name__ == "__main__":
    init_mysql()