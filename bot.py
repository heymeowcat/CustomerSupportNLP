from flask import Flask, request, jsonify
import sqlite3
import requests

app = Flask(__name__)


def get_solution(issue):
    conn = sqlite3.connect('knowledgebase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT solution FROM solutions WHERE issue LIKE ?", ('%' + issue + '%',))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def raise_ticket(customer_issue):
    ticket_data = {
        'customer_issue': customer_issue,
        'status': 'unresolved'
    }
    
    print("Ticket raised with data:", ticket_data)  
    return "Ticket raised successfully. Our support team will get back to you."


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'response': 'Please provide an issue for troubleshooting.'}), 400
    
    solution = get_solution(user_input.lower())
    
    if solution:
        return jsonify({'response': solution}), 200
    else:
        ticket_response = raise_ticket(user_input)
        return jsonify({'response': f'No solution found. {ticket_response}'}), 200

if __name__ == '__main__':
    app.run(debug=True)

