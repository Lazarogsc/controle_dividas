import sqlite3
from constants import DATABASE_PATH


class Database:

    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_PATH)

    def configurar_banco(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico (
                id INTEGER PRIMARY KEY,
                descricao TEXT,
                valor REAL,
                mes TEXT
            )
        ''')
        self.conn.commit()

    def registrar_divida_paga(self, descricao, valor, mes):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO historico (descricao, valor, mes) VALUES (?, ?, ?)
        ''', (descricao, valor, mes))
        self.conn.commit()

    def get_historico(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, descricao, valor, mes FROM historico')
        dividas_pagas = cursor.fetchall()
        self.conn.close()
        return dividas_pagas
    
    def delete_history(self, id_):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM historico WHERE id = ?', (id_,))
        self.conn.commit()
    

database = Database()