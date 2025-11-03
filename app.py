from flask import Flask, request, jsonify
import os
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CodeHelperAgent:
    def __init__(self):
        self.name = "Python Code Helper"
        self.version = "1.0.0"
    
    def analyze_code(self, code: str, language: str) -> dict:
        """Analyze code and provide suggestions"""
        suggestions = []
        issues = []
        
        if not code.strip():
            return {"analysis": "No code provided"}
        
        # Python-specific checks
        if language.lower() == 'python':
            if "import *" in code:
                issues.append("Avoid 'import *' - it pollutes namespace")
                suggestions.append("Import specific functions instead")
            
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
        
        return concepts.get(concept.lower(), f"{concept} is a programming concept worth learning! I can explain OOP, API, REST, MVC, Docker, Git.")

# Initialize agent
agent = CodeHelperAgent()

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

@app.route('/workflow', methods=['GET'])
def workflow():
    """Telex.im workflow configuration"""
    workflow_json = {
        "active": True,
        "category": "development",
        "description": "AI-powered code analysis and programming assistance",
        "id": "python_code_helper_v1",
        "long_description": "A helpful AI agent providing code analysis, explanations, and best practices for developers using multiple programming languages.",
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
        "settings": {
            "executionOrder": "v1"
        },
        "short_description": "AI code analysis and programming help"
    }
    return jsonify(workflow_json)

@app.route('/a2a/agent/codeHelper', methods=['POST'])
def handle_agent():
    """Main agent endpoint for Telex.im"""
    try:
        data = request.get_json(silent=True) or {}
        user_message = data.get('message', '').strip()
        context = data.get('context', {})
        channel_id = data.get('channel_id', 'unknown')
        user_id = data.get('user_id', 'unknown')

        if not user_message:
            response_msg = "❌ Please provide a 'message' in your JSON payload."
        else:
            user_message_lower = user_message.lower()

            if any(word in user_message_lower for word in ['analyze', 'review', 'check code']):
                language = context.get('language', 'python')
                response_msg = (
                    f"🔍 **Code Analysis Ready**\n\n"
                    f"I can analyze your {language} code!\n\n"
                    "**How to use:**\n"
                    "1️⃣ Paste your code directly in the message\n"
                    "2️⃣ Specify the language if not Python\n"
                    "3️⃣ I'll provide suggestions and improvements\n\n"
                    "**Example:**\n"
                    "\"Analyze this Python code:\n```python\ndef calculate(a, b):\n    return a + b\n```\""
                )
            elif any(word in user_message_lower for word in ['explain', 'what is', 'tell me about']):
                concepts = ['oop', 'api', 'rest', 'mvc', 'docker', 'git']
                found_concept = next((c for c in concepts if c in user_message_lower), 'programming')
                explanation = agent.explain_concept(found_concept)
                response_msg = f"📚 **{found_concept.upper()} Explanation**\n\n{explanation}"
            elif 'help' in user_message_lower:
                response_msg = (
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
            else:
                response_msg = (
                    "👋 **Welcome to Code Helper!**\n\n"
                    "I'm your AI programming assistant.\n\n"
                    "• 🔍 Analyze and review your code\n"
                    "• 📚 Explain programming concepts\n"
                    "• 💡 Suggest best practices\n\n"
                    "Type 'help' to see options!"
                )

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'

    print("🚀 Starting Telex Code Helper Agent...")
    print(f"📍 Local URL: http://localhost:{port}")
    print("📋 Available Endpoints:")
    print(f"   GET  /              - Home")
    print(f"   GET  /health        - Health check")
    print(f"   GET  /workflow      - Telex workflow JSON")
    print(f"   POST /a2a/agent/codeHelper - Main Telex A2A endpoint")

    app.run(host='0.0.0.0', port=port, debug=debug)
