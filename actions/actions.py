import sqlite3
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List
from fuzzywuzzy import fuzz
import logging

class ActionGetBestMatchingSolution(Action):
    def name(self) -> Text:
        return "action_get_best_matching_solution"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text').lower()

        best_match = self.get_best_matching_solution(user_message)

        if best_match:
            matched_issue, solution = best_match
            dispatcher.utter_message(
                text=f"I understand you're having an issue with {matched_issue}. Here's what you can try: {solution}"
            )
        else:
            dispatcher.utter_message(text="I couldn't find a specific solution for your issue. I'll raise a support ticket for you.")
            ticket_response = self.raise_ticket(user_message)
            dispatcher.utter_message(text=ticket_response)

        return []

    def get_best_matching_solution(self, issue: Text) -> Any:
        try:
            conn = sqlite3.connect('knowledgebase.db')
            cursor = conn.cursor()

            cursor.execute("SELECT issue, solution FROM solutions")
            all_solutions = cursor.fetchall()
            conn.close()

            best_match = None
            highest_score = 0

            # Use fuzzy matching to find the best match for the user's issue
            for db_issue, solution in all_solutions:
                score = fuzz.token_set_ratio(issue.lower(), db_issue.lower())
                if score > highest_score:
                    highest_score = score
                    best_match = (db_issue, solution)

            # Consider it a match if the score is above a certain threshold
            if best_match and highest_score > 60:
                return best_match

        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")

        return None

    def raise_ticket(self, customer_issue: Text) -> Text:
        try:
            conn = sqlite3.connect('support_tickets.db')
            cursor = conn.cursor()

            cursor.execute('''CREATE TABLE IF NOT EXISTS tickets
                            (id INTEGER PRIMARY KEY, customer_issue TEXT, status TEXT)''')

            cursor.execute("INSERT INTO tickets (customer_issue, status) VALUES (?, ?)",
                           (customer_issue, 'unresolved'))
            conn.commit()
            conn.close()

            return "I've created a support ticket for your issue. Our team will get back to you soon."
        
        except sqlite3.Error as e:
            logging.error(f"Database error while raising ticket: {e}")
            return "There was an issue while raising the ticket. Please try again later."
        
        except Exception as e:
            logging.error(f"Unexpected error while raising ticket: {e}")
            return "An unexpected error occurred while raising the ticket. Please try again later."
