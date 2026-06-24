"""
Main Flask Application - FALIZ Multilingual Chat Bot
Integrates all modules with fallback support
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from config import Config
from database import Database
from language_detector import LanguageDetector
from prompt_engine import PromptEngine
from llm_handler import LLMHandler
from fallback_engine import generate_fallback_response

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.config.from_object(Config)

# Initialize modules
db = Database(app.config['DATABASE_PATH'])
language_detector = LanguageDetector()
prompt_engine = PromptEngine()
llm_handler = LLMHandler()

# Initialize database
db.init_db()


@app.before_request
def before_request():
    """Set up request context"""
    request.start_time = datetime.now()


@app.after_request
def after_request(response):
    """Log request details"""
    if hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds()
        print(f"[{request.method}] {request.path} - {response.status_code} ({duration:.3f}s)")
    return response


# ==================== Web Routes ====================

@app.route('/')
def index():
    """Serve main chat interface"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error loading template: {e}")
        return jsonify({'error': 'Failed to load chat interface'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'api_available': llm_handler.is_api_available()
    })


# ==================== API Routes ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    Accepts message and conversation_id, returns response with language detection
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if not conversation_id:
            return jsonify({'error': 'Conversation ID is required'}), 400
        
        # Detect language
        detected_language = language_detector.detect(user_message)
        print(f"Detected language: {detected_language}")
        
        # Store user message in database
        db.add_message(conversation_id, 'user', user_message, detected_language)
        
        # Get conversation history
        conversation_history = db.get_conversation_messages(conversation_id)
        
        # Get system prompt with language-specific template
        system_prompt = prompt_engine.get_system_prompt(detected_language)
        
        # Prepare messages for LLM
        messages_for_llm = []
        
        # Add system prompt
        messages_for_llm.append({
            'role': 'system',
            'content': system_prompt
        })
        
        # Add conversation history
        for msg in conversation_history:
            messages_for_llm.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Get response from LLM
        try:
            response_text = llm_handler.get_response(messages_for_llm, detected_language)
            is_fallback = False
        except Exception as llm_error:
            print(f"LLM Error: {llm_error}")
            print("Falling back to offline mode...")
            
            # Use fallback response
            response_text = generate_fallback_response(
                user_message,
                detected_language,
                conversation_history
            )
            is_fallback = True
        
        # Store bot response in database
        db.add_message(conversation_id, 'assistant', response_text, detected_language)
        
        # Return response
        return jsonify({
            'response': response_text,
            'detected_language': detected_language,
            'conversation_id': conversation_id,
            'is_fallback': is_fallback,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/new-conversation', methods=['POST'])
def new_conversation():
    """Create a new conversation"""
    try:
        conversation_id = db.create_conversation()
        return jsonify({
            'conversation_id': conversation_id,
            'created_at': datetime.now().isoformat()
        }), 201
    except Exception as e:
        print(f"Error creating conversation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    try:
        conversations = db.get_conversations()
        return jsonify({'conversations': conversations}), 200
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversation/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get specific conversation with all messages"""
    try:
        messages = db.get_conversation_messages(conversation_id)
        
        if not messages:
            return jsonify({
                'conversation_id': conversation_id,
                'messages': [],
                'message': 'No messages found for this conversation'
            }), 200
        
        return jsonify({
            'conversation_id': conversation_id,
            'messages': messages,
            'message_count': len(messages)
        }), 200
    except Exception as e:
        print(f"Error fetching conversation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-conversation/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation and all its messages"""
    try:
        db.delete_conversation(conversation_id)
        return jsonify({
            'message': 'Conversation deleted successfully',
            'conversation_id': conversation_id
        }), 200
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get chat statistics"""
    try:
        stats = db.get_statistics()
        return jsonify(stats), 200
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/language-detect', methods=['POST'])
def detect_language():
    """Standalone language detection endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        detected_language = language_detector.detect(text)
        confidence = language_detector.detect_confidence(text)
        
        return jsonify({
            'text': text,
            'detected_language': detected_language,
            'confidence': confidence
        }), 200
    except Exception as e:
        print(f"Error detecting language: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


# ==================== CLI Commands ====================

@app.cli.command()
def reset_db():
    """Reset the database"""
    try:
        db.reset_db()
        print("✅ Database reset successfully!")
    except Exception as e:
        print(f"❌ Error resetting database: {e}")


@app.cli.command()
def init_db_cmd():
    """Initialize the database"""
    try:
        db.init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")


@app.cli.command()
def test_llm():
    """Test LLM connection"""
    print("Testing LLM connection...")
    try:
        if llm_handler.is_api_available():
            print("✅ LLM API is available")
            
            # Test with simple message
            test_response = llm_handler.get_response([
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': 'Say hello briefly.'}
            ], 'en')
            
            print(f"✅ Test response: {test_response}")
        else:
            print("⚠️  LLM API key not found")
            print("Using fallback mode")
    except Exception as e:
        print(f"❌ Error testing LLM: {e}")


@app.cli.command()
def test_language_detection():
    """Test language detection"""
    print("Testing language detection...")
    
    test_messages = [
        "Hello, how are you?",
        "Hola, ¿cómo estás?",
        "Bonjour, comment allez-vous?",
        "Olá, como você está?"
    ]
    
    for msg in test_messages:
        lang = language_detector.detect(msg)
        confidence = language_detector.detect_confidence(msg)
        print(f"  '{msg}' → {lang} (confidence: {confidence:.2%})")


@app.cli.command()
def show_stats():
    """Show database statistics"""
    try:
        stats = db.get_statistics()
        print("\n📊 Chat Statistics:")
        print(f"  Total Conversations: {stats.get('total_conversations', 0)}")
        print(f"  Total Messages: {stats.get('total_messages', 0)}")
        print(f"  Languages Used: {', '.join(stats.get('languages_used', []))}")
    except Exception as e:
        print(f"❌ Error fetching statistics: {e}")


# ==================== Main ====================

if __name__ == '__main__':
    # Determine host and port from environment or defaults
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════╗
    ║   🤖 FALIZ CHAT BOT - Starting      ║
    ║      Multilingual AI Assistant      ║
    ╚══════════════════════════════════════╝
    
    🌐 Server: {host}:{port}
    🔍 Debug Mode: {debug}
    🗄️  Database: {app.config['DATABASE_PATH']}
    ⚙️  LLM API: {'Available' if llm_handler.is_api_available() else 'Not configured (using fallback)'}
    
    Access at: http://{host}:{port}
    Press Ctrl+C to stop
    """)
    
    app.run(host=host, port=port, debug=debug)
