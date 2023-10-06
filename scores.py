USE_JSON = False

if USE_JSON:
    import json
    import os
    import uuid

    DATABASE="scores.json"

    def init_scores():
        print("initing scores")
        if not os.path.isfile(DATABASE):
            data = []
            with open(DATABASE, 'w') as f:
                json.dump(data, f)

    def add_score(time_taken, user_name, source_word):
        id = uuid.uuid4().int
        data = []
        with open(DATABASE, 'r') as f:
            data = json.load(f)
        with open(DATABASE, 'w') as f:
            data.append((id, time_taken, user_name, source_word))
            json.dump(data, f)
        return id

    def get_scores():
        scores = []
        with open(DATABASE, 'r') as f:
            scores = json.load(f)
            scores.sort(key=lambda score: score[1])
        return scores
else:
    import sqlite3
    import os

    DATABASE="scores.db"

    def init_scores():
        print("initing scores")
        if not os.path.isfile(DATABASE):
            print("doesnt exist so createe")
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('''CREATE TABLE scores (time_taken real, user_name text, source_word text)''')
            conn.commit()
            conn.close()

    def add_score(time_taken, user_name, source_word):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO scores VALUES (?, ?, ?)", (time_taken, user_name, source_word,))
        lastrowid = c.lastrowid
        conn.commit()
        conn.close()
        return lastrowid

    def get_scores():
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("SELECT rowid,* FROM scores ORDER BY time_taken ASC")
        scores = c.fetchall()
        conn.close()
        return scores




