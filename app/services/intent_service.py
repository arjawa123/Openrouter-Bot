from enum import Enum
from typing import List, Dict, Optional
from loguru import logger
from app.services.llm.llm_service import llm_service

class Intent(str, Enum):
    CHAT = "chat"
    TASK_ADD = "task_add"
    TASK_LIST = "task_list"
    NOTE_ADD = "note_add"
    NOTE_LIST = "note_list"
    RESEARCH = "research"
    CODE = "code"
    REMEMBER = "remember"
    MEMORY_QUERY = "memory_query"

class IntentService:
    async def detect_intent(self, user_input: str) -> Intent:
        """
        Detects the user's intent using a fast LLM.
        """
        system_prompt = """
        You are an intent detection specialist for a personal AI assistant.
        Analyze the user's input and classify it into one of these categories:
        - chat: General conversation or questions.
        - task_add: Adding a new todo or task (e.g., "Remind me to...", "Add to my list", "I need to...").
        - task_list: Listing or checking todos.
        - note_add: Saving a new note, snippet, or information.
        - note_list: Searching or listing notes.
        - research: Asking to research a topic or providing a URL to analyze.
        - code: Programming questions or code generation.
        - remember: Asking the assistant to remember a specific fact (e.g., "Remember that...").
        - memory_query: Asking what the assistant remembers about something.

        Respond with ONLY the category name.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User input: {user_input}"}
        ]

        try:
            response = await llm_service.generate_response(
                messages=messages,
                mode="assistant",
                temperature=0,
                max_tokens=20
            )
            
            intent_str = response.content.strip().lower()
            for intent in Intent:
                if intent.value in intent_str:
                    return intent
            
            return Intent.CHAT
        except Exception as e:
            logger.error(f"Intent detection failed: {str(e)}")
            return Intent.CHAT

    async def extract_entity(self, intent: Intent, user_input: str) -> dict:
        """
        Extracts the relevant part of the input and optional metadata like due_at.
        Returns a dict with 'content' and potentially 'due_at'.
        """
        system_prompt = f"""
        Extract the core content and any time/date for the action: {intent.value}.
        For due_at: If a time is mentioned (e.g., "at 5pm", "tomorrow", "on Friday"), 
        extract it in ISO format (YYYY-MM-DD HH:MM:SS) assuming today is {{current_date}}.
        If no time is mentioned, return null for due_at.

        Respond ONLY with a JSON object:
        {{"content": "extracted text", "due_at": "ISO_TIMESTAMP_OR_NULL"}}
        """

        from datetime import datetime
        current_date = datetime.now().strftime("%A, %Y-%m-%d %H:%M:%S")

        messages = [
            {"role": "system", "content": system_prompt.format(current_date=current_date)},
            {"role": "user", "content": f"Input: {user_input}"}
        ]

        try:
            response = await llm_service.generate_response(
                messages=messages,
                mode="assistant",
                temperature=0,
                max_tokens=150
            )
            import json
            # Clean up potential markdown formatting in response
            cleaned_response = response.content.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except Exception as e:
            logger.error(f"Entity extraction failed: {str(e)}")
            return {"content": user_input, "due_at": None}


intent_service = IntentService()
