import sqlite3

conn = sqlite3.connect('knowledge_base.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS solutions
             (id INTEGER PRIMARY KEY,
              issue TEXT,
              symptom TEXT,
              solution TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS departments
             (id INTEGER PRIMARY KEY,
              department TEXT)''')

# Add sample data
solutions = [
    ('router', 'overheating', 'Ensure proper ventilation around the router and check for any obstructions. If the problem persists, consider replacing the router.'),
    ('router', 'temperature is too high', 'Move the router to a cooler location, ensure proper ventilation, and check for any dust buildup. Clean if necessary.'),
    ('modem', 'temperature is too high', 'Ensure the modem is in a well-ventilated area. If the problem persists, contact your ISP for a potential replacement.'),
    ('wi-fi', 'weak signal', 'Move closer to the router, check for interference from other devices, or consider using a Wi-Fi extender.'),
    ('internet speed', 'very slow', 'Run a speed test, restart your modem and router, and check for any ongoing service issues in your area.'),
    ('connection', 'keeps dropping', 'Check all cable connections, restart your modem and router, and ensure there are no service outages in your area.'),
    ('router', 'restarts randomly', 'Check power supply, update firmware, and ensure proper ventilation. If the issue persists, the router may need replacement.'),
    ('modem', 'lights are blinking', 'Check the pattern of blinking lights and consult your modems manual for specific troubleshooting steps.'),
    ('phone', 'connect to Wi-Fi', 'Forget the network and reconnect, ensure you are using the correct password, and restart your phone.'),
    ('ethernet', 'not working', 'Check cable connections, try a different Ethernet port, and ensure your computer s network adapter is functioning properly.'),
    ('upload speed', 'extremely slow', 'Check your service plan, run a speed test, and contact your ISP if the speeds are significantly below what you re paying for.')
]

for solution in solutions:
    c.execute("INSERT INTO solutions (issue, symptom, solution) VALUES (?, ?, ?)", solution)

departments = [
    ('Technical Support',),
    ('Networking',),
    ('Customer Service',),
    ('Billing',),
    ('Hardware Support',)
]

for department in departments:
    c.execute("INSERT INTO departments (department) VALUES (?)", department)

conn.commit()
conn.close()