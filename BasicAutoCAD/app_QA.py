#!/usr/bin/env python3
"""
Flask API for AutoDraw AI Agent
Provides REST endpoints for AutoCAD drawing automation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import logging
import tempfile
import zipfile
from datetime import datetime
from typing import Dict, List, Optional
import traceback

from autodraw_ai_agent_QA_2 import AutoDrawAIAgent
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global agent instance
agent = None

def get_agent() -> AutoDrawAIAgent:
    """Get or create the AutoDraw AI Agent instance"""
    global agent
    if agent is None:
        try:
            agent = AutoDrawAIAgent()
            logger.info("AutoDraw AI Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AutoDraw AI Agent: {e}")
            raise
    return agent

def validate_autocad_connection():
    """Validate AutoCAD connection"""
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        try:
            autocad = win32com.client.GetActiveObject("AutoCAD.Application")
            logger.info(f"AutoCAD connection verified: {autocad.Name}")
            return True
        except Exception as e:
            logger.error(f"AutoCAD not accessible: {e}")
            return False
        finally:
            pythoncom.CoUninitialize()
    except ImportError:
        logger.error("pywin32 not installed")
        return False


@app.route('/api/v1/fixture', methods=['POST'])
def draw_fixture():
    """Draw any fixture type from specifications"""
    
    from datetime import datetime
    
    # Log every API call with timestamp
    logger.info(f"=== API CALL RECEIVED at {datetime.now().isoformat()} ===")
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'fixture_type' not in data:
            return jsonify({"error": "Missing 'fixture_type' field"}), 400
        if 'specifications' not in data:
            return jsonify({"error": "Missing 'specifications' field"}), 400
        
        fixture_type = data['fixture_type']
        specs = data['specifications']
        
        # Get agent and draw
        agent = get_agent()
        result = agent.draw_fixture(fixture_type, specs)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": f"{fixture_type} fixture created successfully",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error drawing fixture: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check AutoCAD connection
        autocad_ok = validate_autocad_connection()
        
        # Check OpenAI API key
        openai_ok = bool(os.getenv('OPENAI_API_KEY'))
        
        status = "healthy" if autocad_ok and openai_ok else "unhealthy"
        
        return jsonify({
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "autocad_connection": autocad_ok,
            "openai_api_key": openai_ok,
            "version": "1.0.0"
        }), 200 if status == "healthy" else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/draw', methods=['POST'])
def create_drawing():
    """Create a drawing from specifications"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'specifications' not in data:
            return jsonify({"error": "Missing 'specifications' field"}), 400
        
        specs = data['specifications']
        
        # Get agent
        agent = get_agent()
        
        # Execute drawing
        result = agent.create_complete_drawing(specs)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Drawing created successfully",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error creating drawing: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/natural', methods=['POST'])
def process_natural_language():
    """Process natural language request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        natural_text = data['text']
        
        # Get agent
        agent = get_agent()
        
        # Process natural language
        result = agent.process_natural_language_request(natural_text)
        
        if result:
            return jsonify({
                "success": True,
                "specifications": result,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to parse natural language request",
                "timestamp": datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error processing natural language: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/natural-draw', methods=['POST'])
def natural_language_draw():
    """Process natural language and create drawing in one step"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'text' not in data:
            return jsonify({"error": "Missing 'text' field"}), 400
        
        natural_text = data['text']
        
        # Get agent
        agent = get_agent()
        
        # Process natural language and create drawing
        result = agent.create_complete_drawing(natural_text)
        
        if result.get("success"):
            return jsonify({
                "success": True,
                "message": "Drawing created successfully from natural language",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result.get("error", "Unknown error"),
                "timestamp": datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error in natural language draw: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/batch', methods=['POST'])
def batch_process():
    """Process multiple drawing requests"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'requests' not in data:
            return jsonify({"error": "Missing 'requests' field"}), 400
        
        requests_list = data['requests']
        if not isinstance(requests_list, list):
            return jsonify({"error": "'requests' must be a list"}), 400
        
        # Get agent
        agent = get_agent()
        
        # Process batch requests
        results = agent.batch_process_requests(requests_list)
        
        successful = sum(1 for r in results if r.get("success"))
        
        return jsonify({
            "success": True,
            "total_requests": len(requests_list),
            "successful": successful,
            "failed": len(requests_list) - successful,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/commands', methods=['GET'])
def get_available_commands():
    """Get available AutoCAD commands"""
    try:
        agent = get_agent()
        commands = agent.get_available_commands()
        
        return jsonify({
            "success": True,
            "commands": commands,
            "timestamp": datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"Error getting commands: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/lighting-systems', methods=['GET'])
def get_lighting_systems():
    """Get available lighting systems"""
    try:
        agent = get_agent()
        systems = agent.get_lighting_systems()
        
        return jsonify({
            "success": True,
            "lighting_systems": systems,
            "timestamp": datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"Error getting lighting systems: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/config', methods=['GET'])
def get_configuration():
    """Get current configuration"""
    try:
        config_data = {
            "openai_model": config.OPENAI_MODEL,
            "openai_temperature": config.OPENAI_TEMPERATURE,
            "openai_max_tokens": config.OPENAI_MAX_TOKENS,
            "autocad_timeout": config.AUTOCAD_TIMEOUT,
            "autocad_command_delay": config.AUTOCAD_COMMAND_DELAY,
            "default_units": config.DEFAULT_UNITS,
            "command_map": config.COMMAND_MAP,
            "lighting_systems": config.LIGHTING_SYSTEMS,
            "color_temperatures": config.COLOR_TEMPERATURES,
            "lens_options": config.LENS_OPTIONS,
            "mounting_options": config.MOUNTING_OPTIONS
        }
        
        return jsonify({
            "success": True,
            "configuration": config_data,
            "timestamp": datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/validate', methods=['POST'])
def validate_specifications():
    """Validate drawing specifications without executing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'specifications' not in data:
            return jsonify({"error": "Missing 'specifications' field"}), 400
        
        specs = data['specifications']
        
        # Get agent
        agent = get_agent()
        
        # Validate specifications
        is_valid = agent._validate_specifications(specs)
        
        if is_valid:
            return jsonify({
                "success": True,
                "valid": True,
                "message": "Specifications are valid",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "success": False,
                "valid": False,
                "error": "Invalid specifications",
                "timestamp": datetime.now().isoformat()
            }), 400
            
    except Exception as e:
        logger.error(f"Error validating specifications: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/export', methods=['POST'])
def export_drawing():
    """Export drawing to file format"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        if 'specifications' not in data:
            return jsonify({"error": "Missing 'specifications' field"}), 400
        
        specs = data['specifications']
        export_format = data.get('format', 'dwg')  # Default to DWG
        
        # Get agent
        agent = get_agent()
        
        # Create drawing
        result = agent.create_complete_drawing(specs)
        
        if not result.get("success"):
            return jsonify({
                "success": False,
                "error": result.get("error", "Failed to create drawing"),
                "timestamp": datetime.now().isoformat()
            }), 400
        
        # For now, return success message
        # In a real implementation, you would export the drawing file
        return jsonify({
            "success": True,
            "message": f"Drawing created and ready for {export_format.upper()} export",
            "format": export_format,
            "timestamp": datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"Error exporting drawing: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/status', methods=['GET'])
def get_status():
    """Get current system status"""
    try:
        # Check AutoCAD connection
        autocad_ok = validate_autocad_connection()
        
        # Check OpenAI API key
        openai_ok = bool(os.getenv('OPENAI_API_KEY'))
        
        # Get agent status
        agent_status = "initialized" if agent is not None else "not_initialized"
        
        return jsonify({
            "success": True,
            "status": {
                "autocad_connection": autocad_ok,
                "openai_api_key": openai_ok,
                "agent_status": agent_status,
                "server_time": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }), 200
            
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("OPENAI_API_KEY environment variable is required")
        exit(1)
    
    # Check AutoCAD connection
    if not validate_autocad_connection():
        logger.warning("AutoCAD connection failed. Some features may not work.")
    
    # Run the Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AutoDraw API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 