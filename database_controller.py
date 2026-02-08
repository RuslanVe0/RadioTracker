import sqlite3
import utils.utils
import uuid
import hashlib



class Controller():
    
    
    
    def __init__(self, path: str = "database/database.db"):
        self.connector = sqlite3.connect(path)
        self.cur = self.connector.cursor()

    
    def __repr__(self):
        return f"Controller connector={self.connector}>"
    
    def add_artist_song_new(self, song_name: str, artist: str, added: str, last_played: str, song_location: str, source: str):
        mini_hash = hashlib.sha256(str(uuid.uuid4()).encode("utf-8", errors="ignore")).hexdigest()[:-59]
        self.cur.execute(f'INSERT INTO MusicData(song, artist, added,\
        last_played, song_location, source, mini_hash, time) VALUES ("{song_name}", "{artist}","{added}","{last_played}", "{song_location}", "{source}", "{mini_hash}", "n/a")')
        self.connector.commit()
    
    def find(self, column: str, value: str):
        located: str = self.cur.execute(f"SELECT {column} FROM MusicData").fetchall()
        for elements in located:
            if value in elements: return True
        return False
    
    def modify(self, column: str, value: str, primary: str) -> None:
        self.cur.execute(f'UPDATE MusicData SET {column} = "{value}" WHERE song = "{primary}"')
        self.connector.commit()
        
    def delete_all(self):
        self.cur.execute("DELETE FROM MusicData")
        self.connector.commit()
    
    def fetch_all(self):
        return self.cur.execute("SELECT * FROM MusicData").fetchall()
    
    def findr(self, column: str, value: str):
        located: str = self.cur.execute(f'SELECT * FROM MusicData WHERE {column}="{value}"').fetchall()
        return located