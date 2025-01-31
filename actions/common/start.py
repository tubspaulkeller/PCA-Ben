from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, FollowupAction, AllSlotsReset, Restarted, SessionStarted, ActionExecuted, UserUttered
from actions.common.common import get_credentials
import os
class Start(Action):
    def name(self) -> Text:
        return "action_start"
    async def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not tracker.get_slot('game_modus'):   
            # it depends if a group mode or a single play mode is activated. 
            # in single play mode: the chatbot gives a introduction to game rules   
            if tracker.get_slot('is_user'):

                btn_lst = [
                {"title": "Lass uns starten! 🎮", "payload": "/OKK"}
                ]
                text = "❗ALLGEMEINE SPIELHINWEISE❗\nDu hast eine begrenzte Zeitspanne (Countdown), um dir Gedanken über die Antwort auf die Fragen zu machen. Wenn dann der Hinweis kommt, zu antworten, musst du schnell handeln, sonst verlierst du Punkte! Außerdem kannst du Abzeichen und Sterne verdienen sowie Level aufsteigen, wenn du erfolgreich bist!\n\nDas Quiz beinhaltet sechs Fragen (2x Single-Choice, 2x Multiple-Choice, 2x offene Fragen). Die Buttons zum Antworten der Single- und Multiple-Choice Fragen kommen, sobald der Timer abgelaufen ist. Um offene Fragen zu beantworten, verwende bitte vor deiner Antwort ein '#' und antworte kurz nach Ablauf des Timers, z.B. # Antwort.\n\nWährend des Quiz kannst du mir jederzeit Fragen zur aktuellen Quiz-Frage stellen. Dazu setzt du einfach '@Ben' vor deine Frage, z.B. '@Ben Wie geht es dir?'.\nMit '# restart' kannst du das Spiel neustarten.\n\nBist du bereit für diese Herausforderung? 😎"
            else: 
            # in group mode the users can select a specific play mode 
                btn_lst = [
                {"title": "A (KLMK)", "payload": "/KLMK"},
                {"title": "B (KLOK)", "payload": "/KLOK"},
                {"title": "C (KL)", "payload": "/KL"} 
                ]
                text="❗ALLGEMEINE SPIELHINWEISE❗\n\nIhr habt eine begrenzte Zeitspanne (Countdown), um euch Gedanken über die Antwort auf die Fragen zu machen. Wenn dann der Hinweis kommt, zu antworten, müsst ihr schnell handeln, sonst verliert ihr Punkte! Außerdem könnt ihr Abzeichen und Sterne verdienen sowie Level aufsteigen, wenn ihr erfolgreich seid!\n\nWährend des Quiz könnt ihr jederzeit Fragen zur aktuellen Quiz-Frage stellen oder Informationen zu euren Punkten, Abzeichen, Sternen und eurem Levelstand, sowie ggf. zu denen eures Gegners, erfragen. Dazu setzt ihr einfach '@Ben' vor eure Frage.\nMit '# restart' kannst du das Spiel neustarten.\n\nSeid ihr bereit für diese Herausforderung?!\nBitte wählt einen Spielmodus (KLMK = Wettbebwerb + Kollaboration, KLOK = Wettbewerb ohne Kollaboration, KL = Kollaboration) aus, indem einer von euch auf den entsprechenden Button klickt. 😎"  
            dispatcher.utter_message(text=text, buttons=btn_lst)
            return
        else:
            print("\033[94mdont call start again\033[0m")
            return [UserUtteranceReverted()]

class ActionIGreet(Action):
    def name(self) -> Text:
        return "action_send_greet"

    async def run(self, dispatcher, tracker, domain):
        # data = {
        #         "intent": {
        #             "name": "/greet",
        #             "confidence": 1.0,
        #         }
        #     }
            
       # await delete_session_in_db(tracker)
        btn_lst = [
                {"title": "Hi Ben! Lass uns loslegen. 😊", "payload": "/greet"},
                ]
        dispatcher.utter_message(text="Hey, 🤘\nich bin Ben, der Lern-Moderator von Quizmania und ich freue mich auf einen weiteren spannenden Spieltag voller gemeinsamer Quiz-Abenteuer. 🧠💡\nViel Glück 🎰🍀", buttons=btn_lst)
        # BUTTON und dann mit INTENT follow up get_channel_members callen!
        #return [UserUttered(text="/greet", parse_data=data), FollowupAction("action_get_channel_members")]
