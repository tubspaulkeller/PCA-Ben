from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, FollowupAction, AllSlotsReset, Restarted
from actions.game.gamemodehandler import GameModeHandler
from actions.common.common import async_connect_to_db, delete_folder, create_folder_if_not_exists, get_credentials, setup_logging
from actions.common.reset import reset_points
from actions.game.competition.competitionmodehandler import CompetitionModeHandler
from actions.timestamps.timestamphandler import TimestampHandler
from actions.session.sessionhandler import SessionHandler
from actions.image_gen.text_on_image_gen import add_text_to_achievements_image
from actions.achievements.achievementshandler import AchievementHandler
from actions.common.common import ask_openai
import os
import logging
import asyncio
logger = setup_logging()


class ActionLeaderboard(Action):
    def name(self) -> Text:
        return "action_leaderboard"

    async def run(self, dispatcher, tracker, domain):
        try:
            session_handler = SessionHandler()
            game_mode_handler = GameModeHandler()
            competition_mode_handler = CompetitionModeHandler()
            achievements_handler = AchievementHandler()
            session = await session_handler.get_session_object(tracker)
            game_modus = tracker.get_slot("game_modus")
            if game_modus:
                loop = '_'.join(game_modus.split('_')[2:])

            filter = session_handler.get_session_filter(tracker)

            path = "actions/image_gen/output/%s/%s" % (loop, tracker.sender_id)
            folder_path = create_folder_if_not_exists(path)
            image_name = "achievements_%s.png" % session['group_title']
            output_path = os.path.join(path, image_name)

            input_path = 'actions/image_gen/input/result.png'
            add_text_to_achievements_image(input_path, output_path, session)
            await game_mode_handler.telegram_bot_send_message('photo', tracker.sender_id, output_path)
            
            await asyncio.sleep(2)
            
            session = await session_handler.get_session_object(tracker)
            total_badges = session['achievements']
            level = session['level']
            stars = session['stars']
            # Dictionary for mapping
            name_mapping = {
                "KORREKTE_ANTWORT": "Erste korrekte Frage",
                "QUIZ_MASTER": "Quiz Master",
                "SCHNELLES_ANTWORTEN": "Schnelles Antworten",
                "TEAMWORK": "Teamwork",
                "SINGLE_CHOICE": "Single Choice",
                "MULTIPLE_CHOICE": "Multiple Choice",
                "NATURTALENT": "Naturtalent",
                "OFFENE_FRAGE": "Offene Frage",
                "GOAL": "Ziel",
                "GESAMTSIEGER": "Gesamtsieger"
            }

            # list of mapped names
            mapped_achievements = [name_mapping[achievement]
                                   for achievement in total_badges]
            badges = ', '.join(mapped_achievements)
            total_points = session['total_points']
            max_game_points = await session_handler.max_points()
            max_level = int(get_credentials("MAX_LEVEL"))
            goal = tracker.get_slot("goal") if tracker.get_slot("goal") is not None else None
            team_name = tracker.get_slot("teamname_value") if tracker.get_slot(
                "teamname_value") is not None else None

            if loop == 'KL' or loop == 'KLMK':
                # openai
                role = "Du bist ein sehr guter Student von einem höheren Semester. Du hast herausragendes Wissen über die Vorlesung 'Einführung in die Wirtschaftsinfomratik.\
                Du befindest dich mit in einem Quiz-Spiel wobei Studierende der Wirtschaftsinformatik versuchen Quizfragen zu lösen.\
                Das Quiz-Spiel hat sechs Fragen (2x Single-Choice, 2x Multiple-Choice und 2x Offene Fragen). \
                Die Spieler hatten für jede Frage einne bestimmten Zeitraum, um sich zu besprechen. \
                Der Zeitraum ist abhängig von der Frageart und kann zwischen 60 und 100 Sekunden betragen.\
                Dabei spielen die Studierenden entweder gegen ein andere Gruppe oder versuchen als Team die Fragen zu beantworten.\
                Du bist ein Chatbot namens Ben, der als Moderator dient. Die Gruppe mit ihrem Teamnamen: %s haben am Anfang folgendes Ziel festgelegt %s." % (team_name, goal)
                msg = "Überprüfe mit der gemachten Punktzahl:%s von %s und deren verdienten Abzeichen, die sie während des Quizes gesammelt haben:%s, Level: %s von %s Level, wie gut sie ihr Ziel erreicht haben. Fasse dich bei deiner Bewertung kurz (maximal 2 Sätze) und sei dabei motivierend inkl. Emojis. Verabschiede dich anschließend" % (
                    total_points, max_game_points, badges, level, max_level)
                ben_answer = ask_openai(role, msg)
                dispatcher.utter_message(text=ben_answer)
            if loop == 'KLOK':
                await competition_mode_handler.print_leaderboard(tracker.get_slot('leaderboard_entry'), dispatcher, loop, tracker.sender_id)
                dispatcher.utter_message(text="Das Quiz ist geschafft! Ich hoffe, ihr hattet viel Spaß! 😄🤗 Bis zum nächsten Mal! 👋🚀")
            if loop == 'KLMK':
                await competition_mode_handler.print_leaderboard(tracker.get_slot('leaderboard_entry'), dispatcher, loop, tracker.sender_id)
                dispatcher.utter_message(
                    text="Ich hoffe, ihr hattet viel Spaß beim Quiz! 😄🤗 Macht weiter so und bis zum nächsten Mal! 👋👋🚀")
            if loop == 'OKK':
                dispatcher.utter_message(text="Ich hoffe, du hattest viel Spaß beim Quiz! 😄🤗 Mach weiter so und bis zum nächsten Mal! 👋👋🚀")
                
            await asyncio.sleep(1)
            delete_folder(path)
            return [FollowupAction("action_new_game")]
        except Exception as e:
            logger.exception(e)
