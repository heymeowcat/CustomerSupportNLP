from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
import sqlite3
from fuzzywuzzy import fuzz
import spacy

nlp = spacy.load("en_core_web_sm")

class ActionExtractIssueSymptom(Action):
    def name(self) -> Text:
        return "action_extract_issue_symptom"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        message = tracker.latest_message.get('text')
        doc = nlp(message)

        issue = None
        symptom = None

        for chunk in doc.noun_chunks:
            if "router" in chunk.text or "modem" in chunk.text or "internet" in chunk.text:
                issue = chunk.text
                break

        for token in doc:
            if token.pos_ == "VERB" or token.pos_ == "ADJ":
                symptom = token.text
                break

        if not issue:
            issue = "device"

        if not symptom:
            symptom = "problem"

        return [SlotSet("issue", issue), SlotSet("symptom", symptom), FollowupAction("action_provide_solution")]

class ActionProvideSolution(Action):
    def name(self) -> Text:
        return "action_provide_solution"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        issue = tracker.get_slot("issue")
        symptom = tracker.get_slot("symptom")
        solution = self.get_solution_from_kb(issue, symptom)
        department = None

        if solution:
            dispatcher.utter_message(text=f"I understand you're having an issue with your {issue} that's {symptom}. Here's a possible solution: {solution}")
        else:
            department = self.get_department(issue, symptom)
            dispatcher.utter_message(text=f"I'm sorry, I couldn't find a specific solution for your {issue} {symptom} issue. This might be handled by our {department} department. Would you like me to create a ticket for further assistance?")
        
        dispatcher.utter_message(text="Is there anything else I can help you with?")
        
        return [SlotSet("department", department)]

    def get_solution_from_kb(self, issue: Text, symptom: Text) -> Text:
        conn = sqlite3.connect('knowledge_base.db')
        c = conn.cursor()
        c.execute("SELECT solution FROM solutions WHERE issue LIKE ? AND symptom LIKE ?", 
                  ('%' + issue + '%', '%' + symptom + '%'))
        result = c.fetchone()
        if not result:
            c.execute("SELECT solution FROM solutions WHERE issue LIKE ? OR symptom LIKE ?", 
                      ('%' + issue + '%', '%' + symptom + '%'))
            result = c.fetchone()
        conn.close()
        return result[0] if result else None

    def get_department(self, issue: Text, symptom: Text) -> Text:
        conn = sqlite3.connect('knowledge_base.db')
        c = conn.cursor()
        c.execute("SELECT department FROM departments")
        departments = c.fetchall()
        conn.close()

        combined_text = f"{issue} {symptom}"
        best_match = None
        highest_score = 0
        for dept in departments:
            score = fuzz.token_set_ratio(combined_text.lower(), dept[0].lower())
            if score > highest_score:
                highest_score = score
                best_match = dept[0]

        return best_match

class ActionCreateTicket(Action):
    def name(self) -> Text:
        return "action_create_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        issue = tracker.get_slot("issue")
        symptom = tracker.get_slot("symptom")
        department = tracker.get_slot("department")
        
        # Extract relevant info from the chat history
        chat_history = tracker.events
        relevant_info = self.extract_relevant_info(chat_history)

        # Create ticket in the database
        ticket_id = self.create_ticket_in_db(issue, symptom, department, relevant_info)

        ticket_info = f"Ticket ID: {ticket_id}, Issue: {issue}, Symptom: {symptom}, Relevant Info: {relevant_info}"
        
        dispatcher.utter_message(text=f"I've created a ticket for the {department} department with the following information: {ticket_info}")
        dispatcher.utter_message(text="Is there anything else I can help you with?")
        
        return [SlotSet("ticket_info", ticket_info)]

    def extract_relevant_info(self, chat_history: List[Dict[Text, Any]]) -> Text:
        relevant_info = ""
        for event in chat_history:
            if event.get("event") == "user" and event.get("text"):
                relevant_info += event.get("text") + " "
        return relevant_info.strip()

    def create_ticket_in_db(self, issue: Text, symptom: Text, department: Text, relevant_info: Text) -> int:
        conn = sqlite3.connect('tickets.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tickets
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      issue TEXT,
                      symptom TEXT,
                      department TEXT,
                      relevant_info TEXT)''')
        c.execute("INSERT INTO tickets (issue, symptom, department, relevant_info) VALUES (?, ?, ?, ?)",
                  (issue, symptom, department, relevant_info))
        ticket_id = c.lastrowid
        conn.commit()
        conn.close()
        return ticket_id