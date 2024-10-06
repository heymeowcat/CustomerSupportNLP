
#  Customer Support Chatbot POC

  A Python-based customer support chatbot using Rasa, Flask, and SQLite.

##  Overview


This chatbot is designed to handle customer support queries, match them with predefined solutions, and create support tickets for unresolved issues.


##  Components

-  `actions.py`: Custom actions for Rasa
-  `bot.py`: Flask API for the Rasa agent
-  `chat_app.py`: Simple test interface using Streamlit

##  Requirements
[Refer setting up your environment](https://rasa.com/docs/rasa/installation/environment-set-up/#:~:text=Python%20Environment%20Setup&text=Currently,%20rasa%20supports%20the%20following,is%20not%20functional%20in%203.4.)
-  Python 3.9.17
-  `pip install setuptools=58.0.4`  (if rasa is not installing)
-  See `requirements.txt` for other dependencies

  

##  Setup

 
1. Clone the repository
2. Install dependencies:
 `pip install -r requirements.txt` 
3. Set up and train the Rasa model (refer to Rasa documentation)

  

##  Usage

1. Start the Rasa action server:
 `rasa run actions` 
 
2. In another terminal, run the Flask API:
 `python bot.py` 
 
3. For testing, run the Streamlit chat interface:
 `streamlit run chat_app.py` 

##  Databases

The project uses two SQLite databases:
-  `knowledgebase.db`: Stores issues and solutions
-  `support_tickets.db`: Stores unresolved issues as tickets

 
Ensure these are properly set up before running the application.