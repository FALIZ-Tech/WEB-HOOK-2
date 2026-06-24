import os
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from config import Config
from prompt_engine import PromptEngine

class LLMHandler:
    """OpenAI LLM handler for chat responses"""
    
    def __init__(self):
        if not Config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.LLM_MODEL
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS
    
    def generate_response(self, user_message, conversation_history, user_languages):
        """Generate response from LLM
        
        Args:
            user_message: The current user message
            conversation_history: List of previous messages with role and content
            user_languages: List of detected languages or single language code
        
        Returns:
            tuple: (response_text, error_message)
        """
        try:
            # Get system prompt based on user languages
            system_prompt = PromptEngine.get_system_prompt(user_languages)
            
            # Format conversation for LLM
            formatted_history = PromptEngine.format_conversation_for_llm(conversation_history)
            
            # Build messages for LLM
            messages = [
                {"role": "system", "content": system_prompt},
                *formatted_history,
                {"role": "user", "content": user_message}
            ]
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract response text
            response_text = response.choices[0].message.content
            
            return response_text, None
        
        except RateLimitError:
            error_msg = "Rate limit exceeded. Please wait a moment and try again."
            return None, error_msg
        
        except APIConnectionError:
            error_msg = "Connection error. Please check your internet connection."
            return None, error_msg
        
        except APIError as e:
            error_msg = f"API Error: {str(e)}"
            return None, error_msg
        
        except ValueError as e:
            error_msg = f"Configuration Error: {str(e)}"
            return None, error_msg
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            return None, error_msg
    
    @staticmethod
    def is_configured():
        """Check if LLM is properly configured"""
        return bool(Config.OPENAI_API_KEY)
