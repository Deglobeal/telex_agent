# telex_code_helper.py
"""
AI Code Helper Agent for Telex.im
Stage 3 Backend Task - Build and Integrate AI Agents
"""

from flask import Flask, request, jsonify
import requests
import os
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CodeHelperAgent:
    """AI Agent that provides code assistance to developers"""
    
    def __init__(self):
        self.name = "Python Code Helper"
        self.version = "1.0.0"
        self.supported_languages = [
            'python', 'javascript', 'typescript', 'java', 'go', 
            'rust', 'c++', 'c#', 'php', 'ruby'
        ]
    
    def analyze_code(self, code: str, language: str, question: str = None) -> Dict[str, Any]: #  type: ignore
        """Analyze code and provide suggestions"""
        try:
            response = {
                "analysis": "",
                "suggestions": [],
                "improvements": [],
                "potential_issues": []
            }
            
            # Basic code analysis
            if len(code.strip()) == 0:
                response["analysis"] = "No code provided for analysis."
                return response
            
            # Language-specific analysis
            if language.lower() == 'python':
                response.update(self._analyze_python_code(code, question))
            elif language.lower() in ['javascript', 'typescript']:
                response.update(self._analyze_js_code(code, question))
            else:
                response.update(self._analyze_general_code(code, language, question))
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            return {
                "analysis": f"Error analyzing code: {str(e)}",
                "suggestions": [],
                "improvements": [],
                "potential_issues": []
            }
    
    def _analyze_python_code(self, code: str, question: str = None) -> Dict[str, Any]:  # type: ignore
        """Python-specific code analysis"""
        analysis = {
            "analysis": "Python code analysis completed.",
            "suggestions": [],
            "improvements": [],
            "potential_issues": []
        }
        
        # Check for common Python issues
        if "import *" in code:
            analysis["potential_issues"].append("Avoid using 'import *' as it pollutes the namespace")
            analysis["suggestions"].append("Import specific functions/classes instead")
        
        if "eval(" in code:
            analysis["potential_issues"].append("Use of eval() can be dangerous")
            analysis["suggestions"].append("Consider safer alternatives like ast.literal_eval()")
        
        if "except:" in code or "except Exception:" in code:
            analysis["potential_issues"].append("Bare except clause may catch too many exceptions")
            analysis["suggestions"].append("Catch specific exceptions instead")
        
        # Check code structure
        lines = code.split('\n')
        if len(lines) > 50:
            analysis["improvements"].append("Consider breaking down long code into smaller functions")
        
        if not any("def " in line for line in lines) and len(lines) > 10:
            analysis["improvements"].append("Consider organizing code into functions for better reusability")
        
        return analysis
    
    def _analyze_js_code(self, code: str, question: str = None) -> Dict[str, Any]:  # type: ignore
        """JavaScript/TypeScript-specific code analysis"""
        analysis = {
            "analysis": "JavaScript/TypeScript code analysis completed.",
            "suggestions": [],
            "improvements": [],
            "potential_issues": []
        }
        
        # Check for common JS issues
        if "==" in code and "===" not in code:
            analysis["suggestions"].append("Consider using === instead of == for strict equality checks")
        
        if "var " in code:
            analysis["suggestions"].append("Prefer let/const over var for better scoping")
        
        if "console.log" in code and "test" not in question.lower() if question else True:
            analysis["potential_issues"].append("Remove console.log statements before production deployment")
        
        return analysis
    
    def _analyze_general_code(self, code: str, language: str, question: str = None) -> Dict[str, Any]:  # type: ignore
        """General code analysis for other languages"""
        analysis = {
            "analysis": f"{language.title()} code analysis completed.",
            "suggestions": [
                "Ensure proper error handling",
                "Add comments for complex logic",
                "Follow language-specific best practices"
            ],
            "improvements": [
                "Consider adding unit tests",
                "Review code for potential performance bottlenecks"
            ],
            "potential_issues": []
        }
        
        return analysis
    
    def explain_concept(self, concept: str, language: str = None) -> Dict[str, Any]:   # type: ignore
        """Explain programming concepts"""
        explanations = {
            "oop": "Object-Oriented Programming (OOP) organizes software design around objects and classes rather than functions and logic.",
            "api": "API (Application Programming Interface) defines interactions between multiple software applications.",
            "rest": "REST (Representational State Transfer) is an architectural style for designing networked applications.",
            "mvc": "MVC (Model-View-Controller) separates an application into three interconnected components.",
            "docker": "Docker is a platform for developing, shipping, and running applications in containers.",
            "git": "Git is a distributed version control system for tracking changes in source code."
        }
        
        concept_lower = concept.lower()
        for key, value in explanations.items():
            if key in concept_lower:
                return {
                    "concept": concept,
                    "explanation": value,
                    "examples": self._get_concept_examples(key, language)
                }
        
        return {
            "concept": concept,
            "explanation": f"I'll explain {concept}. This is a programming/development concept that involves...",
            "examples": "Check official documentation for specific examples and implementations."
        }
    
    def _get_concept_examples(self, concept: str, language: str = None) -> str:   # type: ignore
        """Get examples for programming concepts"""
        examples = {
            "oop": {
                "python": "class Dog:\n    def __init__(self, name):\n        self.name = name\n    def bark(self):\n        return 'Woof!'",
                "javascript": "class Dog {\n    constructor(name) {\n        this.name = name;\n    }\n    bark() {\n        return 'Woof!';\n    }\n}"
            },
            "api": {
                "general": "REST APIs use HTTP methods:\nGET /users - retrieve users\nPOST /users - create user\nPUT /users/1 - update user\nDELETE /users/1 - delete user"
            }
        }
        
        if concept in examples:
            if language and language in examples[concept]:
                return examples[concept][language]
            return examples[concept].get("general", examples[concept][list(examples[concept].keys())[0]])
        
        return "Examples available in language-specific documentation."

# Initialize the agent
code_agent = CodeHelperAgent()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent": code_agent.name,
        "version": code_agent.version
    })

@app.route('/a2a/agent/codeHelper', methods=['POST'])
def handle_code_help():
    """
    Main endpoint for Telex.im A2A protocol
    Expected JSON format from Telex:
    {
        "message": "user message",
        "channel_id": "channel-uuid",
        "user_id": "user-uuid",
        "context": {"language": "python", "type": "analysis"}
    }
    """
    try:
        data = request.get_json()
        logger.info(f"Received request: {data}")
        
        if not data:
            return jsonify({
                "response": "Invalid request: No JSON data provided",
                "error": True
            }), 400
        
        user_message = data.get('message', '').strip()
        context = data.get('context', {})
        channel_id = data.get('channel_id')
        user_id = data.get('user_id')
        
        if not user_message:
            return jsonify({
                "response": "Please provide a message or code to analyze",
                "error": True
            }), 400
        
        # Process the user's message
        response = process_user_message(user_message, context)
        
        logger.info(f"Sending response: {response}")
        
        return jsonify({
            "response": response,
            "channel_id": channel_id,
            "user_id": user_id,
            "agent": code_agent.name,
            "timestamp": os.times().elapsed  # Using a simple timestamp alternative
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "response": f"Error processing your request: {str(e)}",
            "error": True
        }), 500

def process_user_message(message: str, context: Dict[str, Any]) -> str:
    """Process user message and generate appropriate response"""
    message_lower = message.lower()
    
    # Check if it's a code analysis request
    if any(keyword in message_lower for keyword in ['analyze', 'review', 'check code', 'what\'s wrong']):
        return handle_code_analysis(message, context)
    
    # Check if it's a concept explanation request
    elif any(keyword in message_lower for keyword in ['explain', 'what is', 'how does']):
        return handle_concept_explanation(message, context)
    
    # Check if it's a help request
    elif any(keyword in message_lower for keyword in ['help', 'support', 'assist']):
        return get_help_message()
    
    # Default: general code assistance
    else:
        return handle_general_assistance(message, context)

def handle_code_analysis(message: str, context: Dict[str, Any]) -> str:
    """Handle code analysis requests"""
    # Extract code and language from message (simplified)
    language = context.get('language', 'python')
    
    # In a real implementation, you'd parse the code from the message
    # For now, we'll use the message as code
    code = extract_code_from_message(message)
    
    if not code:
        return "Please provide the code you'd like me to analyze. You can paste it directly in your message."
    
    analysis = code_agent.analyze_code(code, language, message)
    
    response = f"🔍 **Code Analysis for {language.title()}**\n\n"
    response += f"**Analysis:** {analysis['analysis']}\n\n"
    
    if analysis['potential_issues']:
        response += "⚠️ **Potential Issues:**\n"
        for issue in analysis['potential_issues']:
            response += f"• {issue}\n"
        response += "\n"
    
    if analysis['suggestions']:
        response += "💡 **Suggestions:**\n"
        for suggestion in analysis['suggestions']:
            response += f"• {suggestion}\n"
        response += "\n"
    
    if analysis['improvements']:
        response += "🚀 **Improvements:**\n"
        for improvement in analysis['improvements']:
            response += f"• {improvement}\n"
    
    return response

def handle_concept_explanation(message: str, context: Dict[str, Any]) -> str:
    """Handle programming concept explanations"""
    # Extract concept from message (simplified)
    concepts = ['oop', 'api', 'rest', 'mvc', 'docker', 'git', 'programming', 'code']
    found_concept = None
    
    for concept in concepts:
        if concept in message.lower():
            found_concept = concept
            break
    
    if not found_concept:
        # Try to extract the first non-common word as concept
        words = message.lower().split()
        common_words = ['what', 'is', 'explain', 'how', 'does', 'work', 'the', 'a', 'an']
        for word in words:
            if word not in common_words and len(word) > 2:
                found_concept = word
                break
    
    if not found_concept:
        found_concept = "programming concept"
    
    language = context.get('language')
    explanation = code_agent.explain_concept(found_concept, language) # type: ignore
    
    response = f"📚 **Explanation: {explanation['concept'].title()}**\n\n"
    response += f"{explanation['explanation']}\n\n"
    response += f"**Examples:**\n{explanation['examples']}\n\n"
    response += "Need more details? Feel free to ask!"
    
    return response

def handle_general_assistance(message: str, context: Dict[str, Any]) -> str:
    """Handle general assistance requests"""
    return f"🤖 **Code Helper Agent**\n\nI received your message: \"{message}\"\n\nI can help you with:\n• Code analysis and review\n• Programming concept explanations\n• Best practices and suggestions\n\nTry asking me to analyze some code or explain a programming concept!"

def get_help_message() -> str:
    """Return help message"""
    return """
🤖 **Code Helper Agent - Help**

I can assist you with:

**🔍 Code Analysis**
• Analyze your code for potential issues
• Suggest improvements and best practices
• Review code structure and organization

**📚 Concept Explanations**
• Explain programming concepts (OOP, APIs, REST, etc.)
• Provide examples in different languages
• Clarify development methodologies

**💡 General Assistance**
• Programming best practices
• Code review suggestions
• Development guidance

**Supported Languages:** Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, PHP, Ruby

**Examples:**
• "Can you analyze this Python code?"
• "Explain OOP in JavaScript"
• "Help me review this function"
• "What's wrong with this code?"

Just paste your code or ask your question!
"""

def extract_code_from_message(message: str) -> str:
    """Extract code from message (simplified implementation)"""
    # In a real implementation, you'd use more sophisticated parsing
    # For now, return the message as code if it looks like code
    code_indicators = ['def ', 'class ', 'function ', 'import ', 'var ', 'let ', 'const ', 'public ', 'private ']
    
    if any(indicator in message for indicator in code_indicators):
        return message
    
    # If message has multiple lines and looks like code
    if '\n' in message and len(message) > 20:
        return message
    
    return ""

# Workflow JSON for Telex.im integration
WORKFLOW_JSON = {
    "active": True,
    "category": "development",
    "description": "AI-powered code analysis and programming assistance",
    "id": "python_code_helper_v1",
    "long_description": """
You are a helpful code assistant that provides code analysis, programming explanations, and development guidance.

Your primary function is to help developers with:
- Code review and analysis across multiple programming languages
- Explaining programming concepts and best practices
- Suggesting improvements and identifying potential issues
- Providing programming guidance and support

When responding:
- Always be constructive and helpful in code reviews
- Provide specific, actionable suggestions
- Include examples when explaining concepts
- Adapt explanations to the user's apparent skill level
- Focus on best practices and maintainable code

Supported languages: Python, JavaScript, TypeScript, Java, Go, Rust, C++, C#, PHP, Ruby
""",
    "name": "python_code_helper",
    "nodes": [
        {
            "id": "code_helper_agent",
            "name": "Code Helper Agent",
            "parameters": {},
            "position": [500, 200],
            "type": "a2a/python-a2a-node",
            "typeVersion": 1,
            "url": "https://your-deployment-url/a2a/agent/codeHelper"
        }
    ],
    "pinData": {},
    "settings": {
        "executionOrder": "v1"
    },
    "short_description": "AI code analysis and programming assistance"
}

@app.route('/workflow', methods=['GET'])
def get_workflow():
    """Return the workflow JSON for Telex.im"""
    return jsonify(WORKFLOW_JSON)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Code Helper Agent on port {port}")
    logger.info(f"Workflow available at: /workflow")
    logger.info(f"Health check at: /health")
    logger.info(f"Main agent endpoint at: /a2a/agent/codeHelper")
    
    app.run(host='0.0.0.0', port=port, debug=debug)