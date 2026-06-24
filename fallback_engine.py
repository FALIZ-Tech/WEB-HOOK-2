# Fallback Chat System for API Failures
# This module provides intelligent fallback responses when OpenAI API is unavailable

import random
from typing import Dict, List

class FallbackChatEngine:
    """
    Provides intelligent fallback responses when the main LLM API fails.
    Supports multiple languages and maintains conversation context.
    """

    def __init__(self):
        self.conversation_history = []
        self.fallback_responses = self._initialize_responses()

    def _initialize_responses(self) -> Dict:
        """Initialize fallback response templates for all supported languages"""
        return {
            'en': {
                'greeting': [
                    "Hello! I'm FALIZ Chat Bot. How can I help you today?",
                    "Hi there! I'm here to assist you. What can I do for you?",
                    "Greetings! I'm ready to help. What's on your mind?",
                    "Hey! Nice to meet you. What can I help with?"
                ],
                'greeting_response': [
                    "I'm doing great, thanks for asking! How about you?",
                    "I'm doing well! Ready to assist. How can I help?",
                    "Excellent! Thanks for asking. What brings you here?"
                ],
                'help_offer': [
                    "I'd be happy to help! What do you need?",
                    "Of course! I'm here to assist. What can I do?",
                    "Absolutely! Tell me what you need help with.",
                    "I'm here to help! What's the issue?"
                ],
                'coding_help': [
                    "I can certainly help with coding! What programming language are you working with?",
                    "Coding questions? I'm here for that! What's your project about?",
                    "Sure! I can help with coding. What language or framework?"
                ],
                'question_general': [
                    "That's a great question! While I'm in fallback mode, I can try to help. Can you give me more details?",
                    "Interesting! Tell me more about what you're asking, and I'll do my best to help.",
                    "Good question! What exactly would you like to know?"
                ],
                'farewell': [
                    "Goodbye! Feel free to come back anytime you need help!",
                    "Take care! Thanks for chatting with me!",
                    "See you later! Don't hesitate to return if you need anything!"
                ],
                'thank_you': [
                    "You're welcome! Always happy to help!",
                    "My pleasure! Glad I could assist!",
                    "No problem at all! Feel free to ask anytime!"
                ],
                'confused': [
                    "I'm not sure I fully understand. Can you rephrase that?",
                    "I'm having trouble understanding. Could you explain more clearly?",
                    "Sorry, that's a bit unclear. Can you give me more context?"
                ],
                'fallback_notice': "I'm currently operating in offline mode, but I'll do my best to help. For more advanced features, please check back in a moment.",
                'default': [
                    "That's interesting! Tell me more about it.",
                    "I see! Can you elaborate on that?",
                    "Understood. What else would you like to discuss?",
                    "Got it! How can I assist with that?"
                ]
            },
            'es': {
                'greeting': [
                    "¡Hola! Soy FALIZ Chat Bot. ¿Cómo puedo ayudarte hoy?",
                    "¡Hola! Estoy aquí para ayudarte. ¿Qué necesitas?",
                    "¡Saludos! Estoy listo para asistirte. ¿En qué puedo ayudar?"
                ],
                'greeting_response': [
                    "¡Estoy muy bien, gracias por preguntar! ¿Y tú?",
                    "¡Excelente! Listo para ayudarte. ¿Qué necesitas?",
                    "¡Muy bien! Gracias. ¿Qué te trae por aquí?"
                ],
                'help_offer': [
                    "¡Claro que sí! ¿Qué necesitas?",
                    "Absolutamente, estoy aquí para ayudar. ¿Cuál es el problema?",
                    "¡Por supuesto! Cuéntame qué necesitas."
                ],
                'coding_help': [
                    "¡Claro! ¿Con qué lenguaje de programación trabajas?",
                    "¿Preguntas de código? ¡Estoy aquí! ¿De qué se trata tu proyecto?",
                    "¡Seguro! ¿Qué lenguaje o framework usas?"
                ],
                'question_general': [
                    "¡Buena pregunta! Aunque estoy en modo offline, haré mi mejor esfuerzo. ¿Puedes dar más detalles?",
                    "Interesante. Cuéntame más y haré lo posible para ayudarte.",
                    "¡Buena pregunta! ¿Qué específicamente deseas saber?"
                ],
                'farewell': [
                    "¡Adiós! ¡No dudes en volver cuando necesites ayuda!",
                    "¡Cuídate! ¡Gracias por charlar conmigo!",
                    "¡Hasta luego! ¡Vuelve pronto si necesitas algo!"
                ],
                'thank_you': [
                    "¡De nada! ¡Siempre feliz de ayudar!",
                    "¡Mi placer! ¡Feliz de poder asistir!",
                    "¡Sin problema! ¡Puedes preguntar en cualquier momento!"
                ],
                'confused': [
                    "No estoy seguro de entender bien. ¿Puedes reformular?",
                    "Tengo dificultad para entender. ¿Podrías explicar mejor?",
                    "Disculpa, eso no es muy claro. ¿Puedes dar más contexto?"
                ],
                'fallback_notice': "Estoy funcionando en modo offline, pero haré mi mejor esfuerzo. Para funciones avanzadas, por favor intenta más tarde.",
                'default': [
                    "¡Eso es interesante! Cuéntame más.",
                    "Entiendo. ¿Puedes elaborar?",
                    "Visto. ¿Qué más quieres comentar?",
                    "Entendido. ¿Cómo puedo ayudar con eso?"
                ]
            },
            'fr': {
                'greeting': [
                    "Bonjour! Je suis FALIZ Chat Bot. Comment puis-je vous aider?",
                    "Salut! Je suis ici pour vous aider. Qu'avez-vous besoin?",
                    "Bienvenue! Je suis prêt à vous assister. Comment puis-je aider?"
                ],
                'greeting_response': [
                    "Je vais bien, merci de demander! Et vous?",
                    "Excellent! Prêt à aider. Que puis-je faire?",
                    "Très bien! Merci. Qu'est-ce qui vous amène?"
                ],
                'help_offer': [
                    "Bien sûr! De quoi avez-vous besoin?",
                    "Absolument! Je suis ici pour aider. Quel est le problème?",
                    "Certainement! Dites-moi ce dont vous avez besoin."
                ],
                'coding_help': [
                    "Bien sûr! Quel langage de programmation utilisez-vous?",
                    "Des questions sur la programmation? Je suis là! De quel projet s'agit-il?",
                    "Bien sûr! Quel langage ou framework utilisez-vous?"
                ],
                'question_general': [
                    "Bonne question! Bien que je sois en mode hors ligne, je vais essayer de vous aider. Pouvez-vous donner plus de détails?",
                    "Intéressant. Dites-moi plus et je ferai mon mieux pour vous aider.",
                    "Bonne question! Que voulez-vous savoir exactement?"
                ],
                'farewell': [
                    "Au revoir! N'hésitez pas à revenir si vous avez besoin d'aide!",
                    "À bientôt! Merci de m'avoir parlé!",
                    "À plus tard! Reviens bientôt si tu as besoin de quelque chose!"
                ],
                'thank_you': [
                    "De rien! Toujours heureux de vous aider!",
                    "C'est un plaisir! Heureux d'avoir pu aider!",
                    "Pas de problème! Vous pouvez demander à tout moment!"
                ],
                'confused': [
                    "Je ne suis pas sûr de bien comprendre. Pouvez-vous reformuler?",
                    "J'ai du mal à comprendre. Pouvez-vous expliquer plus clairement?",
                    "Désolé, ce n'est pas très clair. Pouvez-vous donner plus de contexte?"
                ],
                'fallback_notice': "Je fonctionne actuellement en mode hors ligne, mais je ferai mon mieux. Pour des fonctionnalités avancées, veuillez réessayer plus tard.",
                'default': [
                    "C'est intéressant! Dites-moi plus.",
                    "Je vois. Pouvez-vous développer?",
                    "D'accord. Qu'aimeriez-vous d'autre?",
                    "Entendu. Comment puis-je vous aider avec ça?"
                ]
            },
            'pt': {
                'greeting': [
                    "Olá! Sou FALIZ Chat Bot. Como posso ajudá-lo?",
                    "Oi! Estou aqui para ajudar. O que você precisa?",
                    "Bem-vindo! Estou pronto para assistir. Como posso ajudar?"
                ],
                'greeting_response': [
                    "Estou muito bem, obrigado por perguntar! E você?",
                    "Ótimo! Pronto para ajudar. O que posso fazer?",
                    "Muito bem! Obrigado. Que o traz por aqui?"
                ],
                'help_offer': [
                    "Claro! Do que você precisa?",
                    "Absolutamente! Estou aqui para ajudar. Qual é o problema?",
                    "Certamente! Diga-me do que você precisa."
                ],
                'coding_help': [
                    "Claro! Com qual linguagem de programação você trabalha?",
                    "Perguntas de programação? Estou aqui! Do que se trata seu projeto?",
                    "Com certeza! Qual linguagem ou framework você usa?"
                ],
                'question_general': [
                    "Ótima pergunta! Embora eu esteja em modo offline, farei o meu melhor. Pode dar mais detalhes?",
                    "Interessante. Conte-me mais e farei o possível para ajudar.",
                    "Ótima pergunta! O que você quer saber exatamente?"
                ],
                'farewell': [
                    "Adeus! Não hesite em voltar se precisar de ajuda!",
                    "Até mais! Obrigado por conversar comigo!",
                    "Até logo! Volte em breve se precisar de algo!"
                ],
                'thank_you': [
                    "De nada! Sempre feliz em ajudar!",
                    "Meu prazer! Feliz de poder ajudar!",
                    "Sem problema! Você pode perguntar a qualquer momento!"
                ],
                'confused': [
                    "Não tenho certeza se entendi direito. Pode reformular?",
                    "Estou tendo dificuldade em entender. Pode explicar melhor?",
                    "Desculpe, isso não está muito claro. Pode dar mais contexto?"
                ],
                'fallback_notice': "Estou funcionando em modo offline, mas farei o meu melhor. Para recursos avançados, tente novamente mais tarde.",
                'default': [
                    "Isso é interessante! Conte-me mais.",
                    "Entendo. Pode elaborar?",
                    "Certo. Qual mais você gostaria de discutir?",
                    "Entendido. Como posso ajudar com isso?"
                ]
            }
        }

    def detect_intent(self, message: str) -> str:
        """Detect user intent from message content"""
        message_lower = message.lower().strip()
        
        # Greeting patterns
        greetings = ['hello', 'hi', 'hey', 'hola', 'bonjour', 'oi', 'olá', 'salut', 'buenos días', 'buenas tardes']
        if any(g in message_lower for g in greetings):
            return 'greeting'
        
        # How are you patterns
        how_are = ['how are you', 'how do you do', 'how\'s it going', 'cómo estás', 'ça va', 'como você está', 'wie geht']
        if any(q in message_lower for q in how_are):
            return 'greeting_response'
        
        # Help patterns
        help_patterns = ['help me', 'can you help', 'i need help', 'ayuda', 'aide', 'preciso de ajuda', 'hilf mir']
        if any(p in message_lower for p in help_patterns):
            return 'help_offer'
        
        # Coding patterns
        coding_patterns = ['code', 'python', 'javascript', 'java', 'programming', 'programación', 'programmation', 'programação', 'coding', 'debug', 'function', 'class']
        if any(c in message_lower for c in coding_patterns):
            return 'coding_help'
        
        # Farewell patterns
        farewells = ['bye', 'goodbye', 'see you', 'adiós', 'adios', 'au revoir', 'adeus', 'tchau', 'hasta', 'catch you']
        if any(f in message_lower for f in farewells):
            return 'farewell'
        
        # Thank you patterns
        thanks = ['thank you', 'thanks', 'gracias', 'merci', 'obrigado', 'muito obrigado', 'danke', 'merci beaucoup']
        if any(t in message_lower for t in thanks):
            return 'thank_you'
        
        # Default to general question
        return 'default'

    def get_fallback_response(self, message: str, language: str = 'en') -> str:
        """
        Generate a fallback response based on intent and language
        
        Args:
            message: User's message
            language: Detected language code (en, es, fr, pt)
        
        Returns:
            Appropriate fallback response
        """
        # Default to English if language not supported
        if language not in self.fallback_responses:
            language = 'en'
        
        intent = self.detect_intent(message)
        responses = self.fallback_responses[language]
        
        # Get response pool for detected intent
        if intent in responses:
            response_pool = responses[intent]
            if isinstance(response_pool, list):
                response = random.choice(response_pool)
            else:
                response = response_pool
        else:
            response = random.choice(responses['default'])
        
        return response

    def get_contextualized_response(self, message: str, language: str = 'en', conversation_history: List[Dict] = None) -> str:
        """
        Generate response with conversation context awareness
        
        Args:
            message: Current user message
            language: Detected language
            conversation_history: Previous messages for context
        
        Returns:
            Contextual fallback response
        """
        response = self.get_fallback_response(message, language)
        
        # Add context awareness
        if conversation_history and len(conversation_history) > 0:
            last_message = conversation_history[-1] if conversation_history[-1]['role'] == 'assistant' else None
            
            # If we just sent a message, vary the response
            if last_message:
                alt_responses = self.fallback_responses[language].get('default', [response])
                if isinstance(alt_responses, list) and len(alt_responses) > 1:
                    response = random.choice(alt_responses)
        
        return response

    def add_notice(self, response: str, language: str = 'en') -> str:
        """
        Optionally add fallback mode notice to response
        
        Args:
            response: Original response
            language: Language code
        
        Returns:
            Response with optional notice
        """
        # Add notice only on first fallback or occasionally
        if language in self.fallback_responses and random.random() < 0.15:  # 15% chance
            notice = self.fallback_responses[language].get('fallback_notice', '')
            return f"{response}\n\n💡 {notice}"
        
        return response

    def handle_unsupported_language(self, message: str, detected_language: str) -> str:
        """
        Handle messages in languages not fully supported
        
        Args:
            message: User message
            detected_language: Language that was detected
        
        Returns:
            Response in English with explanation
        """
        language_map = {
            'de': 'German',
            'it': 'Italian',
            'ja': 'Japanese',
            'zh': 'Chinese',
            'ru': 'Russian',
            'ko': 'Korean'
        }
        
        lang_name = language_map.get(detected_language, 'this language')
        
        response = (
            f"I detected you're writing in {lang_name}. "
            f"While I primarily support English, Spanish, French, and Portuguese, "
            f"I'll still try to help! You can also write in English if you prefer. "
            f"\n\nWhat can I assist you with?"
        )
        
        return response


# Singleton instance
_fallback_engine = None

def get_fallback_engine() -> FallbackChatEngine:
    """Get or create singleton instance of FallbackChatEngine"""
    global _fallback_engine
    if _fallback_engine is None:
        _fallback_engine = FallbackChatEngine()
    return _fallback_engine


def generate_fallback_response(message: str, language: str = 'en', conversation_history: List[Dict] = None) -> str:
    """
    Quick function to generate fallback response
    
    Args:
        message: User message
        language: Detected language
        conversation_history: Previous messages
    
    Returns:
        Fallback response with context awareness
    """
    engine = get_fallback_engine()
    
    # Check for unsupported language
    supported_languages = ['en', 'es', 'fr', 'pt']
    if language not in supported_languages:
        return engine.handle_unsupported_language(message, language)
    
    response = engine.get_contextualized_response(message, language, conversation_history)
    
    # Occasionally add notice
    response = engine.add_notice(response, language)
    
    return response
