# app.py
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
        "message": "🚀 Telex Code Helper Agent is Running!",
        "status": "active",
        "endpoints": {
            "GET /health": "Health check",
            "GET /workflow": "Telex workflow JSON", 
            "POST /a2a/agent/codeHelper": "Main agent endpoint (use POST)"
        },
        "usage": "Use POST method for /a2a/agent/codeHelper with JSON payload"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "agent": agent.name,
        "version": agent.version,
        "timestamp": time.time()
    })

@app.route('/workflow', methods=['GET'])
def workflow():
    """Telex.im workflow configuration"""
    workflow_json = {
        "active": True,
        "category": "development",
        "description": "AI-powered code analysis and programming assistance",
        "id": "python_code_helper_v1",
        "long_description": "You are a helpful code assistant that provides code analysis, programming explanations, and development guidance. You help developers with code review, concept explanations, and best practices across multiple programming languages including Python, JavaScript, TypeScript, Java, and more.",
        "name": "python_code_helper",
        "nodes": [
            {
                "id": "code_helper_agent",
                "name": "Code Helper Agent",
                "parameters": {},
                "position": [500, 200],
                "type": "a2a/python-a2a-node",
                "typeVersion": 1,
                "url": "https://your-deployment-url.herokuapp.com/a2a/agent/codeHelper"
            }
        ],
        "pinData": {},
        "settings": {
            "executionOrder": "v1"
        },
        "short_description": "AI code analysis and programming help"
    }
    return jsonify(workflow_json)

@app.route('/a2a/agent/codeHelper', methods=['POST'])
def handle_agent():
    """Main agent endpoint for Telex.im - ONLY ACCEPTS POST"""
    try:
        # Get data from Telex.im
        data = request.get_json()
        
        if not data:
            return jsonify({
                "response": "❌ No JSON data received. Please send a POST request with JSON payload.",
                "error": True
            }), 400
        
        user_message = data.get('message', '').strip()
        context = data.get('context', {})
        channel_id = data.get('channel_id', 'unknown')
        user_id = data.get('user_id', 'unknown')
        
        if not user_message:
            return jsonify({
                "response": "❌ Please provide a 'message' in your JSON payload.",
                "error": True
            }), 400
        
        logger.info(f"Processing message from user {user_id}: {user_message}")
        
        # Process the message
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ['analyze', 'review', 'check code']):
            language = context.get('language', 'python')
            response = f"""🔍 **Code Analysis Ready**

I can analyze your {language} code! 

**How to use:**
1. Paste your code directly in the message
2. Specify the language if not Python
3. I'll provide suggestions and improvements

**Example:**
"Analyze this Python code:
```python
def calculate(a, b):
    return a + b
```" """
        
        elif any(word in user_message_lower for word in ['explain', 'what is', 'tell me about']):
            concepts = ['oop', 'api', 'rest', 'mvc', 'docker', 'git']
            found_concept = next((c for c in concepts if c in user_message_lower), 'programming')
            explanation = agent.explain_concept(found_concept)
            response = f"📚 **{found_concept.upper()} Explanation**\n\n{explanation}"
        
        elif 'help' in user_message_lower:
            response = """🤖 **Code Helper Agent - Help**

**I can help you with:**
• 🔍 **Code Analysis** - Review your code for improvements
• 📚 **Concept Explanations** - Explain programming concepts
• 💡 **Best Practices** - Suggest improvements

**Supported Languages:**
Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, PHP, Ruby

**Try these commands:**
- "analyze this code: [your code]"
- "explain OOP"
- "help with JavaScript"
- "what is REST API"

Just paste your code or ask a question!"""
        
        else:
            response = """👋 **Welcome to Code Helper!**

I'm your AI programming assistant. I can:

• 🔍 Analyze and review your code
• 📚 Explain programming concepts  
• 💡 Suggest best practices

**Quick start:** 
Type "help" for full options
or paste your code for analysis!"""
        
        # Return Telex.im compatible response
        return jsonify({
            "response": response,
            "channel_id": channel_id,
            "user_id": user_id,
            "agent": agent.name,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "response": "❌ Sorry, I encountered an error processing your request. Please try again.",
            "error": True
        }), 500

# Add a GET endpoint for testing with helpful message
@app.route('/a2a/agent/codeHelper', methods=['GET'])
def handle_agent_get():
    return jsonify({
        "error": "Method Not Allowed",
        "message": "This endpoint only accepts POST requests",
        "usage": {
            "method": "POST",
            "content-type": "application/json",
            "example_payload": {
                "message": "help",
                "channel_id": "your-channel-id",
                "user_id": "your-user-id",
                "context": {"language": "python"}
            }
        }
    }), 405

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting Telex Code Helper Agent...")
    print(f"📍 Local URL: http://localhost:{port}")
    print("📋 Available Endpoints:")
    print(f"   GET  http://localhost:{port}/          - Home page")
    print(f"   GET  http://localhost:{port}/health    - Health check") 
    print(f"   GET  http://localhost:{port}/workflow  - Telex workflow")
    print(f"   POST http://localhost:{port}/a2a/agent/codeHelper - Main agent")
    print("\n⚠️  Remember: Use POST method for /a2a/agent/codeHelper")
    
    app.run(host='0.0.0.0', port=port, debug=debug)