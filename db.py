import sqlite3

def init_db():
    conn = sqlite3.connect('knowledgebase.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS solutions
                      (id INTEGER PRIMARY KEY, issue TEXT, solution TEXT)''')
    cursor.execute('''INSERT OR IGNORE INTO solutions (issue, solution)
                      VALUES 
                      ('wifi not working', 'Please restart your router. If that does not work, check the cable connections.'),
                      ('slow internet', 'Try resetting your router. If the problem persists, contact your ISP.'),
                      ('unable to connect', 'Make sure your modem is connected and the correct password is entered.'),
                      ('overheating', 'Check for overheating by ensuring the modem is in a well-ventilated space.')''')
    conn.commit()
    conn.close()

init_db()
