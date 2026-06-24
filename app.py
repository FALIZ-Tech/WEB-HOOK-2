from flask import Flask, render_template, request, jsonify, session
from functools import wraps
import uuid
import json
from datetime import datetime
from config import Config, config as config_map
from database import Database
from language_detector import LanguageDetector
from llm_handler import LLMHandler
import os

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config_map[env])

# Validate configuration
try:
    Config.validate_config()
except ValueError as e:
    print(f"Configuration Error: {e}")
    print("Please set the OPENAI_API_KEY environment variable.")

# Initialize database
db = Database()

# Initialize LLM handler
llm_handler = LLMHandler()

def get_or_create_user_id():
    """Get or create user ID from session/cookies"""
    if 'user_id' not in session:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
    return session['user_id']

def require_user(f):
    """Decorator to ensure user exists in database"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_or_create_user_id()
        user = db.get_user(user_id)
        
        if not user:
            db.create_user(user_id)
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/')
@require_user
def index():
    """Serve main chat interface"""
    user_id = session['user_id']
    user = db.get_user(user_id)
    
    return render_template('index.html', 
                         user_id=user_id,
                         language_preference=user.get('language_preference') if user else None)

@app.route('/api/chat', methods=['POST'])
@require_user
def chat():
    """Handle chat messages"""
    user_id = session['user_id']
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_message = data['message'].strip()
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    if len(user_message) > 5000:
        return jsonify({'error': 'Message too long (max 5000 characters)'}), 400
    
    try:
        # Get or create user
        user = db.get_user(user_id)
        if not user:
            db.create_user(user_id)
            user = db.get_user(user_id)
        
        # Detect language from user message
        detected_language = LanguageDetector.detect_language(user_message)
        detected_languages = LanguageDetector.detect_mixed_languages(user_message)
        
        # Update user language preference if not set
        if not user.get('language_preference'):
            db.create_user(user_id, detected_language)
        
        # Get or create conversation
        latest_conv = db.get_latest_conversation(user_id)
        
        if latest_conv:
            conversation_id = latest_conv['conversation_id']
        else:
            conversation_id = db.create_conversation(user_id)
        
        # Store user message
        db.store_message(conversation_id, user_id, 'user', user_message, detected_language)
        
        # Get conversation history (excluding the message we just stored)
        history = db.get_conversation_history(conversation_id, limit=50)
        
        # Generate response from LLM
        response_text, error_msg = llm_handler.generate_response(
            user_message,
            history,
            detected_languages
        )
        
        if error_msg:
            return jsonify({
                'error': error_msg,
                'type': 'llm_error'
            }), 500
        
        # Store assistant response
        db.store_message(conversation_id, user_id, 'assistant', response_text, detected_language)
        
        return jsonify({
            'response': response_text,
            'detected_language': detected_language,
            'language_name': LanguageDetector.get_language_name(detected_language),
            'conversation_id': conversation_id,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.',
            'type': 'server_error'
        }), 500

@app.route('/api/conversation/<int:conversation_id>', methods=['GET'])
@require_user
def get_conversation(conversation_id):
    """Get conversation history"""
    try:
        history = db.get_conversation_history(conversation_id)
        return jsonify({'messages': history}), 200
    except Exception as e:
        print(f"Error retrieving conversation: {str(e)}")
        return jsonify({'error': 'Failed to retrieve conversation'}), 500

@app.route('/api/conversations', methods=['GET'])
@require_user
def get_conversations():
    """Get user's conversations"""
    user_id = session['user_id']
    try:
        conversations = db.get_user_conversations(user_id, limit=20)
        return jsonify({'conversations': conversations}), 200
    except Exception as e:
        print(f"Error retrieving conversations: {str(e)}")
        return jsonify({'error': 'Failed to retrieve conversations'}), 500

@app.route('/api/new-conversation', methods=['POST'])
@require_user
def new_conversation():
    """Create new conversation"""
    user_id = session['user_id']
    try:
        conversation_id = db.create_conversation(user_id)
        return jsonify({'conversation_id': conversation_id}), 201
    except Exception as e:
        print(f"Error creating conversation: {str(e)}")
        return jsonify({'error': 'Failed to create conversation'}), 500

@app.route('/api/delete-conversation/<int:conversation_id>', methods=['DELETE'])
@require_user
def delete_conversation(conversation_id):
    """Delete a conversation"""
    try:
        db.delete_conversation(conversation_id)
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"Error deleting conversation: {str(e)}")
        return jsonify({'error': 'Failed to delete conversation'}), 500

@app.route('/api/user-info', methods=['GET'])
@require_user
def user_info():
    """Get user information"""
    user_id = session['user_id']
    try:
        user = db.get_user(user_id)
        return jsonify({
            'user_id': user_id,
            'language_preference': user.get('language_preference') if user else None
        }), 200
    except Exception as e:
        print(f"Error retrieving user info: {str(e)}")
        return jsonify({'error': 'Failed to retrieve user info'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'llm_configured': LLMHandler.is_configured()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.before_request
def before_request():
    """Ensure session is secure"""
    if not app.debug:
        session.permanent = True

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
