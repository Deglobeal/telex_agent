from flask import Flask, request, jsonify
import os
import logging
import time
import uuid
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Define the Code Helper Agent
class CodeHelperAgent:
    def __init__(self):
        self.name = "Python Code Helper"
        self.version = "1.0.0"
    # Analyze code and provide suggestions
    def analyze_code(self, code: str, language: str) -> dict:
        """Analyze code and provide suggestions"""
        suggestions = []
        issues = []
        # Basic checks
        if not code.strip():
            return {"analysis": "No code provided"}
        
        # Python-specific checks
        if language.lower() == 'python':
            if "import *" in code:
                issues.append("Avoid 'import *' - it pollutes namespace")
                suggestions.append("Import specific functions instead")
            # Check for use of eval

            if "eval(" in code:
                issues.append("eval() can be dangerous")
                suggestions.append("Use ast.literal_eval() or safer alternatives")
            
            if "except:" in code:
                issues.append("Bare except clause")
                suggestions.append("Catch specific exceptions")
        
        # General code quality checks
        lines = code.split('\n')
        if len(lines) > 50:
            suggestions.append("Consider breaking code into smaller functions")
        
        return {
            "analysis": f"Analyzed {language} code with {len(lines)} lines",
            "suggestions": suggestions,
            "issues": issues,
            "line_count": len(lines)
        }
    # Explain programming concepts
    def explain_concept(self, concept: str) -> str:
        """Explain programming concepts"""
        concepts = {
            "oop": "Object-Oriented Programming organizes code around objects with properties and methods. It uses concepts like encapsulation, inheritance, and polymorphism.",
            "api": "API (Application Programming Interface) allows different software to communicate. REST APIs use HTTP methods like GET, POST, PUT, DELETE.",
            "rest": "REST is an architectural style for building web services using HTTP methods. It's stateless and uses standard HTTP status codes.",
            "mvc": "MVC (Model-View-Controller) separates application into three components: Model (data), View (UI), Controller (logic).",
            "docker": "Docker containers package applications with all dependencies, ensuring consistency across environments.",
            "git": "Git is a distributed version control system for tracking code changes. It allows branching, merging, and collaboration."
        }
        # Return explanation or default message
        return concepts.get(concept.lower(), f"{concept} is a programming concept worth learning! I can explain OOP, API, REST, MVC, Docker, Git.")

# Initialize agent
agent = CodeHelperAgent()
# Helper functions for JSON-RPC handling
def extract_user_message(data):
    """Extract user message from JSON-RPC request"""
    try:
        message_obj = data.get('params', {}).get('message', {})
        parts = message_obj.get('parts', [])
        
        # Extract text from all parts
        message_texts = []
        for part in parts:
            if part.get('kind') == 'text':
                message_texts.append(part.get('text', ''))
            elif part.get('kind') == 'data':
                data_items = part.get('data', [])
                for item in data_items:
                    if item.get('kind') == 'text':
                        message_texts.append(item.get('text', ''))
        
        return ' '.join(filter(None, message_texts)).strip()
    except Exception as e:
        logger.error(f"Error extracting message: {str(e)}")
        return ""
# Create JSON-RPC response
def create_jsonrpc_response(request_id, response_text, user_message=None, state="completed"):
    """Create JSON-RPC 2.0 response"""
    task_id = str(uuid.uuid4())
    context_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    # Build history
    history = []
    if user_message and state == "completed":
        history.append({
            "kind": "message",
            "role": "user", 
            "parts": [
                {
                    "kind": "text",
                    "text": user_message,
                    "data": None,
                    "file_url": None
                }
            ],
            "messageId": str(uuid.uuid4()),
            "taskId": None,
            "metadata": None
        })
    # Append agent response to history
    history.append({
        "kind": "message",
        "role": "agent",
        "parts": [
            {
                "kind": "text",
                "text": response_text,
                "data": None,
                "file_url": None
            }
        ],
        "messageId": str(uuid.uuid4()),
        "taskId": task_id,
        "metadata": None
    })
    
    # Build artifacts
    artifacts = [
        {
            "artifactId": str(uuid.uuid4()),
            "name": "assistantResponse",
            "parts": [
                {
                    "kind": "text",
                    "text": response_text,
                    "data": None,
                    "file_url": None
                }
            ]
        }
    ]
    # Construct final response
    return {
        "jsonrpc": "2.0", # JSON-RPC version 
        # Unique request ID
        "id": request_id or "",
        "result": {
            "id": task_id,
            "contextId": context_id,
            "status": {
                "state": state,
                "timestamp": timestamp,
                "message": {
                    "kind": "message",
                    "role": "agent",
                    "parts": [
                        {
                            "kind": "text",
                            "text": response_text,
                            "data": None,
                            "file_url": None
                        }
                    ],
                    # Unique message ID
                    "messageId": str(uuid.uuid4()),
                    "taskId": task_id,
                    "metadata": None
                }
            },
            "artifacts": artifacts,
            "history": history,
            "kind": "task"
        }
    }
# Process user message and generate response
def process_user_message(user_message):
    """Process user message and return appropriate response"""
    if not user_message:
        return "Please provide a message for analysis."
    
    user_message_lower = user_message.lower()
    # Determine action based on keywords
    if any(word in user_message_lower for word in ['analyze', 'review', 'check code']):
        return (
            "🔍 **Code Analysis Ready**\n\n"
            "I can analyze your code!\n\n"
            "**How to use:**\n"
            "1️⃣ Paste your code directly in the message\n"
            "2️⃣ Specify the language if not Python\n"
            "3️⃣ I'll provide suggestions and improvements\n\n"
            "**Example:**\n"
            "\"Analyze this Python code:\n```python\ndef calculate(a, b):\n    return a + b\n```\""
        )
    # Analyze code if code snippet is detected
    elif any(word in user_message_lower for word in ['explain', 'what is', 'tell me about']):
        concepts = ['oop', 'api', 'rest', 'mvc', 'docker', 'git']
        found_concept = next((c for c in concepts if c in user_message_lower), 'programming')
        explanation = agent.explain_concept(found_concept)
        return f"📚 **{found_concept.upper()} Explanation**\n\n{explanation}"
    elif 'help' in user_message_lower:
        return (
            "🤖 **Code Helper Agent - Help**\n\n"
            "**I can help you with:**\n"
            "• 🔍 Code Analysis\n"
            "• 📚 Concept Explanations\n"
            "• 💡 Best Practices\n\n"
            "**Try these commands:**\n"
            "- analyze this code\n"
            "- explain OOP\n"
            "- what is REST API"
        )
    # Default welcome message
    else:
        return (
            "👋 **Welcome to Code Helper!**\n\n"
            "I'm your AI programming assistant.\n\n"
            "• 🔍 Analyze and review your code\n"
            "• 📚 Explain programming concepts\n"
            "• 💡 Suggest best practices\n\n"
            "Type 'help' to see options!"
        )
# Flask endpoints
@app.route('/')
def home():
    return jsonify({
        "status": "success",
        "data": {
            "message": "Telex AI Code Helper Agent is live! 🚀",
            "agent": agent.name,
            "actions": [
                {
                    "name": "Analyze Code",
                    "description": "Analyzes code and suggests improvements.",
                    "type": "text"
                },
                {
                    "name": "Explain Concept",
                    "description": "Explains programming concepts (OOP, API, REST, etc.)",
                    "type": "text"
                }
            ]
        },
        "meta": {
            "channel_id": None,
            "user_id": None,
            "timestamp": time.time()
        }
    })
# Health check endpoint
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "success",
        "data": {
            "message": "Service is healthy 💚",
            "agent": agent.name,
            "actions": [
                {
                    "name": "Analyze Code",
                    "description": "Analyzes code and suggests improvements",
                    "type": "text"
                },
                {
                    "name": "Explain Concept",
                    "description": "Explains programming concepts (OOP, REST, API, etc.)",
                    "type": "text"
                }
            ]
        },
        "meta": {
            "channel_id": None,
            "user_id": None,
            "timestamp": time.time()
        }
    })
# Workflow configuration endpoint
@app.route('/workflow', methods=['GET'])
def workflow():
    """Telex.im workflow configuration"""
    workflow_json = {
        "active": True,
        "category": "development",
        "description": "AI-powered code analysis and programming assistance",
        "id": "python_code_helper_v1",
        "long_description": "You are a helpful code assistant that provides code analysis, programming explanations, and development guidance. Your primary function is to help developers with code review, concept explanations, and best practices across multiple programming languages including Python, JavaScript, TypeScript, Java, and more.",
        "name": "python_code_helper",
        "nodes": [
            {
                "id": "code_helper_agent",
                "name": "Code Helper Agent",
                "parameters": {},
                "position": [500, 200],
                "type": "a2a/python-a2a-node",
                "typeVersion": 1,
                "url": "https://web-production-a4d44.up.railway.app/a2a/agent/codeHelper"
            }
        ],
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "short_description": "AI code analysis and programming help"
    }
    return jsonify(workflow_json)
# JSON-RPC 2.0 endpoint for Telex.im
@app.route('/a2a/lingflow', methods=['POST'])
def handle_lingflow():
    """Handle JSON-RPC 2.0 requests for Telex.im"""
    try:
        data = request.get_json(silent=True) or {}
        
        # Extract JSON-RPC fields
        jsonrpc_version = data.get('jsonrpc', '2.0')
        request_id = data.get('id', '')
        method = data.get('method', '')
        
        # Handle empty request
        if not data:
            response_data = create_jsonrpc_response(
                request_id="", 
                response_text="Empty request received. Please provide valid JSON-RPC 2.0 data.",
                state="failed"
            )
            return jsonify(response_data)
        
        # Handle unknown methods
        if method != 'message/send':
            response_data = create_jsonrpc_response(
                request_id=request_id,
                response_text="Unknown method. Use 'message/send' or 'help'.",
                state="failed"
            )
            return jsonify(response_data)
        
        # Extract and process user message
        user_message = extract_user_message(data)
        response_text = process_user_message(user_message)
        
        # Create successful response
        response_data = create_jsonrpc_response(
            request_id=request_id,
            response_text=response_text,
            user_message=user_message
        )
        
        return jsonify(response_data)
        # Handle exceptions
    except Exception as e:
        logger.error(f"Error processing lingflow request: {str(e)}")
        response_data = create_jsonrpc_response(
            request_id=data.get('id', ''), # type: ignore
            response_text=f"Error processing request: {str(e)}",
            state="failed"
        )
        return jsonify(response_data)

# Keep the existing endpoint for backward compatibility
@app.route('/a2a/agent/codeHelper', methods=['POST'])
def handle_agent():
    """Main agent endpoint for Telex.im"""
    try: # Extract request data
        data = request.get_json(silent=True) or {}
        user_message = data.get('message', '').strip()
        context = data.get('context', {})
        channel_id = data.get('channel_id', 'unknown')
        user_id = data.get('user_id', 'unknown')

        if not user_message:
            response_msg = "❌ Please provide a 'message' in your JSON payload."
        else:
            response_msg = process_user_message(user_message)
        # Return structured response
        return jsonify({
            "status": "success",
            "data": {
                "message": response_msg,
                "agent": agent.name,
                "actions": [
                    {
                        "name": "Analyze Code",
                        "description": "Analyzes code and suggests improvements",
                        "type": "text"
                    },
                    {
                        "name": "Explain Concept",
                        "description": "Explains programming concepts (OOP, REST, API, etc.)",
                        "type": "text"
                    }
                ]
            },
            "meta": {
                "channel_id": channel_id,
                "user_id": user_id,
                "timestamp": time.time()
            }
        })
    # Handle exceptions
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "status": "error",
            "data": {
                "message": "❌ Sorry, I encountered an error processing your request. Please try again.",
                "agent": agent.name,
                "actions": []
            },
            "meta": {
                "channel_id": None,
                "user_id": None,
                "timestamp": time.time()
            }
        }), 500
# Handle invalid request methods
@app.route('/a2a/agent/codeHelper', methods=['GET'])
def handle_agent_get():
    return jsonify({
        "status": "error",
        "data": {
            "message": "❌ Invalid request method. Please use POST for this endpoint.",
            "agent": agent.name,
            "actions": []
        },
        "meta": {
            "channel_id": None,
            "user_id": None,
            "timestamp": time.time()
        }
    }), 405
# Run the Flask app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    print("🚀 Starting Telex Code Helper Agent...")
    print(f"📍 Local URL: http://localhost:{port}")
    print("📋 Available Endpoints:")
    print(f"   GET  /              - Home")
    print(f"   GET  /health        - Health check")
    print(f"   GET  /workflow      - Telex workflow JSON")
    print(f"   POST /a2a/lingflow  - JSON-RPC 2.0 endpoint")
    print(f"   POST /a2a/agent/codeHelper - Main Telex A2A endpoint")

    app.run(host='0.0.0.0', port=port, debug=debug)