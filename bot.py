from flask import Flask, request, jsonify
import sqlite3
from rasa.core.agent import Agent
import asyncio
from fuzzywuzzy import fuzz

app = Flask(__name__)
agent = Agent.load("./models/20241004-134844-adaptive-radian.tar.gz")

def get_best_matching_solution(issue):
    conn = sqlite3.connect('knowledgebase.db')
    cursor = conn.cursor()
    cursor.execute("SELECT issue, solution FROM solutions")
    all_solutions = cursor.fetchall()
    conn.close()

    best_match = None
    highest_score = 0

    for db_issue, solution in all_solutions:
        score = fuzz.token_set_ratio(issue.lower(), db_issue.lower())
        if score > highest_score:
            highest_score = score
            best_match = (db_issue, solution)

    if best_match and highest_score > 60:  # Threshold for considering it a match
        return best_match
    return None

def raise_ticket(customer_issue):
    conn = sqlite3.connect('support_tickets.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tickets
                      (id INTEGER PRIMARY KEY, customer_issue TEXT, status TEXT)''')
    cursor.execute("INSERT INTO tickets (customer_issue, status) VALUES (?, ?)",
                   (customer_issue, 'unresolved'))
    conn.commit()
    conn.close()
    print(f"Ticket raised for issue: {customer_issue}")
    return "I've created a support ticket for your issue. Our team will get back to you soon."

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip().lower()
    if not user_input:
        return jsonify({'response': "I didn't catch that. Could you please repeat your question or issue?"}), 400

    # First, check if the input directly matches a known issue
    best_match = get_best_matching_solution(user_input)
    if best_match:
        matched_issue, solution = best_match
        return jsonify({'response': f"I understand you're having an issue with {matched_issue}. Here's what you can try: {solution}"}), 200

    # If no direct match, use Rasa for intent classification
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    parsed_data = loop.run_until_complete(agent.handle_text(user_input))

    if parsed_data:
        intent = parsed_data[0].get('intent', {}).get('name', '').lower()
        rasa_response = parsed_data[0].get('text', '')

        if any(keyword in intent for keyword in ['troubleshoot', 'problem', 'issue']):
            ticket_response = raise_ticket(user_input)
            return jsonify({'response': f"I'm sorry, I don't have a specific solution for that issue. {ticket_response}"}), 200
        else:
            # For non-troubleshooting intents, return Rasa's response
            return jsonify({'response': rasa_response}), 200
    else:
        return jsonify({'response': "I'm having trouble understanding. Could you rephrase your question or provide more details about your issue?"}), 200

if __name__ == '__main__':
    app.run(debug=True)