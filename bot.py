from flask import Flask, request, jsonify
import sqlite3
from rasa.core.agent import Agent
import asyncio

app = Flask(__name__)

agent = Agent.load("./models/20241004-134844-adaptive-radian.tar.gz")


def get_solution(issue):
    conn = sqlite3.connect('knowledgebase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT solution FROM solutions WHERE issue LIKE ?", ('%' + issue + '%',))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def raise_ticket(customer_issue):
    conn = sqlite3.connect('support_tickets.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets
                      (id INTEGER PRIMARY KEY, customer_issue TEXT, status TEXT)''')
    cursor.execute("INSERT INTO tickets (customer_issue, status) VALUES (?, ?)",
                   (customer_issue, 'unresolved'))
    conn.commit()
    conn.close()
    ticket_data = {
        'customer_issue': customer_issue,
        'status': 'unresolved'
    }
    print("Ticket raised with data:", ticket_data) 
    return "Ticket raised successfully. Our support team will get back to you."

# Endpoint for chat handling
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'response': 'Please provide an issue for troubleshooting.'}), 400

    # Run the Rasa agent asynchronously to handle text
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    parsed_data = loop.run_until_complete(agent.handle_text(user_input.lower()))

    if parsed_data:
        rasa_response = parsed_data[0].get('text', 'I am not sure how to help with that.')
        # Check if the intent is troubleshooting-related and if a solution exists
        solution = get_solution(user_input.lower())
        
        if solution:
            return jsonify({'response': solution}), 200
        else:
            # If Rasa responds with something generic (like a greeting or small talk), we return it
            if 'troubleshoot' in parsed_data[0].get('intent', {}).get('name', '').lower():
                # Raise a ticket for unresolved troubleshooting issues
                ticket_response = raise_ticket(user_input)
                return jsonify({'response': f'No solution found. {ticket_response}'}), 200
            else:
                # If it's just small talk, return the bot's response
                return jsonify({'response': rasa_response}), 200
    else:
        return jsonify({'response': 'Sorry, I didn’t understand that. Can you please repeat?'})

if __name__ == '__main__':
    app.run(debug=True)
