from flask import Flask, request, jsonify
from rasa.core.agent import Agent
from rasa.utils.endpoints import EndpointConfig
import asyncio


app = Flask(__name__)
agent = Agent.load("./models/20241019-160027-symmetric-result.tar",  action_endpoint=EndpointConfig(url="http://localhost:5055/webhook"))

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').strip().lower()
    if not user_input:
        return jsonify({'response': "I didn't catch that. Could you please repeat your question or issue?"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    parsed_data = loop.run_until_complete(agent.handle_text(user_input))

    if parsed_data:
        rasa_response = parsed_data[0].get('text', '')
        return jsonify({'response': rasa_response}), 200
    else:
        return jsonify({'response': "I'm having trouble understanding. Could you rephrase your question or provide more details about your issue?"}), 200

if __name__ == '__main__':
    app.run(debug=True)