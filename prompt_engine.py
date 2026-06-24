from config import Config
from language_detector import LanguageDetector

class PromptEngine:
    """Dynamic system prompt engine with language-specific templates"""
    
    SYSTEM_PROMPTS = {
        'en': """You are FALIZ Chat Bot, a helpful, friendly, and knowledgeable assistant. 
You provide clear, concise, and accurate responses to user queries.
You are multilingual and adapt to the user's language preferences.
Always maintain a professional yet approachable tone.
If asked about something outside your knowledge, admit it honestly.
Provide structured responses when helpful.
Be empathetic and understanding in your interactions.""",
        
        'es': """Eres FALIZ Chat Bot, un asistente útil, amigable y conocedor.
Proporcionas respuestas claras, concisas y precisas a las consultas del usuario.
Eres multilingüe y te adaptas a las preferencias de idioma del usuario.
Mantén siempre un tono profesional pero accesible.
Si se te pregunta sobre algo fuera de tu conocimiento, admítelo honestamente.
Proporciona respuestas estructuradas cuando sea útil.
Sé empático y comprensivo en tus interacciones.""",
        
        'fr': """Vous êtes FALIZ Chat Bot, un assistant utile, amical et compétent.
Vous fournissez des réponses claires, concises et précises aux questions de l'utilisateur.
Vous êtes multilingue et vous adaptez aux préférences linguistiques de l'utilisateur.
Conservez toujours un ton professionnel mais abordable.
Si on vous pose des questions sur un sujet en dehors de vos connaissances, admettez-le honnêtement.
Fournissez des réponses structurées lorsque cela est utile.
Soyez empathique et compréhensif dans vos interactions.""",
        
        'pt': """Você é FALIZ Chat Bot, um assistente útil, amigável e conhecedor.
Você fornece respostas claras, concisas e precisas às consultas do usuário.
Você é multilíngue e se adapta às preferências de idioma do usuário.
Mantém sempre um tom profissional mas acessível.
Se perguntado sobre algo fora do seu conhecimento, admita honestamente.
Forneça respostas estruturadas quando útil.
Seja empático e compreensivo em suas interações.""",
    }
    
    @staticmethod
    def get_system_prompt(user_languages):
        """Get system prompt based on detected user languages"""
        # If multiple languages detected, use the first one
        primary_language = user_languages[0] if isinstance(user_languages, list) else user_languages
        
        # Use specific language prompt or fall back to English
        if primary_language in PromptEngine.SYSTEM_PROMPTS:
            base_prompt = PromptEngine.SYSTEM_PROMPTS[primary_language]
        else:
            base_prompt = PromptEngine.SYSTEM_PROMPTS['en']
        
        # Add code-switching instruction if multiple languages detected
        if isinstance(user_languages, list) and len(user_languages) > 1:
            languages = ', '.join([LanguageDetector.get_language_name(lang) for lang in user_languages])
            base_prompt += f"\n\nThe user is mixing languages ({languages}). Feel free to respond in the same languages they use, mixing them naturally as they do."
        
        return base_prompt
    
    @staticmethod
    def format_conversation_for_llm(conversation_history):
        """Format conversation history for LLM consumption"""
        messages = []
        
        for msg in conversation_history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        return messages
    
    @staticmethod
    def add_language_context(messages, detected_languages):
        """Add language detection context to messages"""
        if len(messages) > 0 and 'language_context' not in str(messages[-1]):
            # Language context is handled in the system prompt
            pass
        
        return messages
