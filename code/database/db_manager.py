import sqlite3
import json
from pathlib import Path

class DatabaseManager:
    """Gestionnaire simple de la base de données"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.db_path = Path(__file__).parent.parent / "data" / "snake.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        if not self.db_path.exists():
            with sqlite3.connect(self.db_path) as conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS parties (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date_creation TEXT NOT NULL,
                        date_modification TEXT NOT NULL,
                        score INTEGER DEFAULT 0,
                        longueur INTEGER DEFAULT 0,
                        est_terminee INTEGER DEFAULT 0,
                        corps TEXT NOT NULL,
                        direction TEXT NOT NULL,
                        fruits TEXT NOT NULL,
                        fruits_manges INTEGER DEFAULT 0
                    );
                """)
                conn.commit()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def sauvegarder_partie(self, partie_data):
        """Sauvegarde ou met à jour une partie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if partie_data.get('id'):
            # Mise à jour
            cursor.execute("""
                UPDATE parties SET
                    date_modification = ?,
                    score = ?,
                    longueur = ?,
                    est_terminee = ?,
                    corps = ?,
                    direction = ?,
                    fruits = ?,
                    fruits_manges = ?
                WHERE id = ?
            """, (
                partie_data['date_modification'],
                partie_data['score'],
                partie_data['longueur'],
                1 if partie_data.get('est_terminee', False) else 0,
                json.dumps(partie_data['corps']),
                partie_data['direction'],
                json.dumps(partie_data['fruits']),
                partie_data['fruits_manges'],
                partie_data['id']
            ))
            conn.commit()
            conn.close()
            return partie_data['id']
        else:
            # Nouvelle insertion
            cursor.execute("""
                INSERT INTO parties (
                    date_creation, date_modification, score, longueur,
                    est_terminee, corps, direction, fruits, fruits_manges
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                partie_data['date_creation'],
                partie_data['date_modification'],
                partie_data['score'],
                partie_data['longueur'],
                0,
                json.dumps(partie_data['corps']),
                partie_data['direction'],
                json.dumps(partie_data['fruits']),
                partie_data['fruits_manges']
            ))
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
    
    def get_derniere_partie(self):
        """Récupère la dernière partie non terminée"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM parties 
            WHERE est_terminee = 0 
            ORDER BY date_modification DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return self._row_to_dict(row) if row else None
    
    def get_toutes_parties(self):
        """Récupère toutes les parties"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parties ORDER BY date_modification DESC")
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row) for row in rows] if rows else []
    
    def get_meilleurs_scores(self, limit=5):
        """Récupère les meilleurs scores"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM parties 
            WHERE est_terminee = 1 
            ORDER BY score DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_dict(row) for row in rows] if rows else []
    
    def supprimer_partie(self, id_partie):
        """Supprime une partie"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM parties WHERE id = ?", (id_partie,))
        conn.commit()
        conn.close()
    
    def _row_to_dict(self, row):
        return {
            'id': row[0],
            'date_creation': row[1],
            'date_modification': row[2],
            'score': row[3],
            'longueur': row[4],
            'est_terminee': bool(row[5]),
            'corps': json.loads(row[6]),
            'direction': row[7],
            'fruits': json.loads(row[8]),
            'fruits_manges': row[9]
        }