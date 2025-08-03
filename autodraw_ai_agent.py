import openai
import win32com.client
import json
import re
import os
import sys
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import threading
import pythoncom

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDrawAIAgent:
    """
    AI Agent for AutoCAD drawing automation using natural language processing.
    Leverages existing AutoLISP functions for lighting design automation.
    """
    
    def __init__(self, openai_api_key: str = None, initialize_autocad: bool = True):
        """
        Initialize the AutoDraw AI Agent.
        
        Args:
            openai_api_key: OpenAI API key for natural language processing
            initialize_autocad: Whether to initialize AutoCAD connection (default: True)
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to constructor.")
        
        # Thread-local storage for COM objects
        self._thread_local = threading.local()
        
        # Initialize AutoCAD COM connection in current thread if requested
        if initialize_autocad:
            self._initialize_autocad_connection()
        
        # Command mapping for direct AutoCAD drawing commands (non-interactive)
        self.command_map = {
            "linear_light": "_LINE",  # Use LINE command instead of popup-based LSAUTO
            "linear_light_reflector": "_LINE", 
            "rush_light": "_LINE",
            "rush_recessed": "_LINE",
            "pg_light": "_LINE",
            "magneto_track": "_LINE",
            "repeat_last": "_COPY",
            "details": "_TEXT",
            "add_empck": "_INSERT",
            "output_modifier": "_TEXT",
            "driver_calculator": "_TEXT",
            "driver_update": "_TEXT",
            "runid_update": "_TEXT",
            "susp_kit_count": "_TEXT",
            "ww_toggle": "_TEXT",
            "import_assets": "_INSERT",
            "redefine_blocks": "_INSERT",
            "purge_all": "_PURGE"
        }
        
        # Lighting system specifications
        self.lighting_systems = {
            "ls": {"name": "Linear Light", "command": "linear_light"},
            "lsr": {"name": "Linear Light with Reflector", "command": "linear_light_reflector"},
            "rush": {"name": "Rush Light", "command": "rush_light"},
            "rush_rec": {"name": "Rush Recessed", "command": "rush_recessed"},
            "pg": {"name": "PG Light", "command": "pg_light"},
            "magneto": {"name": "Magneto Track", "command": "magneto_track"}
        }
        
        # Mounting options
        self.mounting_options = [
            "wall_mount", "ceiling_mount", "suspension", "track_mount", 
            "recessed", "surface_mount", "pendant"
        ]
        
        # Lens options
        self.lens_options = [
            "clear", "frosted", "prismatic", "louvered", "reflector",
            "diffuser", "lens_cover"
        ]
        
        # Color temperature options
        self.color_temps = [
            "2700k", "3000k", "3500k", "4000k", "5000k", "6500k"
        ]
        
        logger.info("AutoDraw AI Agent initialized successfully")
    
    def _initialize_autocad_connection(self):
        """Initialize AutoCAD COM connection for the current thread."""
        try:
            # Initialize COM for this thread
            pythoncom.CoInitialize()
            
            print("I am here P1")
            
            # Try to get existing AutoCAD instance first
            try:
                self._thread_local.autocad = win32com.client.GetActiveObject("AutoCAD.Application")
                logger.info("Connected to existing AutoCAD instance")
            except:
                # If no existing instance, create a new one
                self._thread_local.autocad = win32com.client.Dispatch("AutoCAD.Application")
                logger.info("Created new AutoCAD instance")
            
            # Wait a moment for AutoCAD to fully initialize
            import time
            time.sleep(1.0)
            
            # Check if AutoCAD is properly connected
            try:
                # Try to access a simple property first
                app_name = self._thread_local.autocad.Name
                logger.info(f"Connected to AutoCAD: {app_name}")
            except Exception as e:
                logger.error(f"AutoCAD application not accessible: {e}")
                raise
            
            # Check if there's an active document
            try:
                # Get the Documents collection
                documents = self._thread_local.autocad.Documents
                doc_count = documents.Count
                logger.info(f"Found {doc_count} existing documents")
                
                if doc_count == 0:
                    # Create a new document if none exists
                    logger.info("Creating new document")
                    self._thread_local.doc = documents.Add()
                else:
                    # Use the active document
                    logger.info("Using active document")
                    self._thread_local.doc = self._thread_local.autocad.ActiveDocument
                    
            except Exception as e:
                logger.error(f"Error accessing documents: {e}")
                # Try to create a new document anyway
                try:
                    logger.info("Attempting to create new document after error")
                    self._thread_local.doc = self._thread_local.autocad.Documents.Add()
                except Exception as e2:
                    logger.error(f"Failed to create new document: {e2}")
                    raise
            
            # Get ModelSpace
            try:
                self._thread_local.modelspace = self._thread_local.doc.ModelSpace
                logger.info("Successfully accessed ModelSpace")
            except Exception as e:
                logger.error(f"Error accessing ModelSpace: {e}")
                raise
                
            logger.info("Successfully connected to AutoCAD")
        except Exception as e:
            logger.error(f"Failed to connect to AutoCAD: {e}")
            try:
                pythoncom.CoUninitialize()
            except:
                pass
            raise
    
    def _get_autocad_objects(self):
        """Get AutoCAD objects for the current thread, reconnecting if necessary."""
        try:
            # Check if we have valid COM objects for this thread
            if not hasattr(self._thread_local, 'autocad') or self._thread_local.autocad is None:
                self._initialize_autocad_connection()
            
            # Test the connection
            try:
                # Try to access the active document
                doc = self._thread_local.autocad.ActiveDocument
                # If we get here, the connection is working
                return self._thread_local.autocad, doc, self._thread_local.modelspace
            except Exception as e:
                logger.info(f"AutoCAD connection broken, reconnecting... Error: {e}")
                # Connection is broken, reinitialize
                self._cleanup_autocad_connection()
                self._initialize_autocad_connection()
                return self._thread_local.autocad, self._thread_local.doc, self._thread_local.modelspace
                
        except Exception as e:
            logger.error(f"Failed to get AutoCAD objects: {e}")
            raise
    
    def _cleanup_autocad_connection(self):
        """Clean up AutoCAD connection for the current thread."""
        try:
            if hasattr(self._thread_local, 'autocad'):
                self._thread_local.autocad = None
                self._thread_local.doc = None
                self._thread_local.modelspace = None
            pythoncom.CoUninitialize()
        except Exception as e:
            logger.error(f"Error cleaning up AutoCAD connection: {e}")
    
    def process_natural_language_request(self, user_input: str) -> Dict:
        """
        Process natural language input and extract drawing specifications.
        
        Args:
            user_input: Natural language description of the drawing requirements
            
        Returns:
            Dictionary containing parsed specifications
        """
        try:
            # Create a comprehensive prompt for the AI
            prompt = self._create_parsing_prompt(user_input)
            
            # Get AI response
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AutoCAD lighting design assistant. Parse user requests into structured specifications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse the response
            try:
                parsed_specs = json.loads(response.choices[0].message.content)
                logger.info(f"Parsed specifications: {parsed_specs}")
                return parsed_specs
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"AI Response: {response.choices[0].message.content}")
                # Return a default specification for linear light
                return self._create_default_specification(user_input)
            
        except Exception as e:
            logger.error(f"Error processing natural language request: {e}")
            # Return a default specification for linear light
            return self._create_default_specification(user_input)
    
    def _create_default_specification(self, user_input: str) -> Dict:
        """Create a default specification when AI parsing fails"""
        logger.info("Creating default specification for linear light")
        return {
            "command": "linear_light",
            "lighting_system": "ls",
            "dimensions": {
                "length": 10.0,
                "width": 4.0,
                "height": 4.0
            },
            "position": {
                "start_point": [0, 0, 0],
                "end_point": [10, 0, 0],
                "orientation": "horizontal"
            },
            "specifications": {
                "wattage": 50,
                "color_temperature": "4000k",
                "lens_type": "clear",
                "mounting_type": "ceiling_mount",
                "driver_type": "standard",
                "quantity": 1
            },
            "additional_parameters": {}
        }
    
    def _create_parsing_prompt(self, user_input: str) -> str:
        """Create a detailed prompt for parsing user input."""
        return f"""
        Parse this AutoCAD lighting design request into JSON format:
        
        User Request: "{user_input}"
        
        Available lighting systems: {list(self.lighting_systems.keys())}
        Available mounting options: {self.mounting_options}
        Available lens options: {self.lens_options}
        Available color temperatures: {self.color_temps}
        Available commands: {list(self.command_map.keys())}
        
        Return a JSON object with the following structure:
        {{
            "command": "command_name",
            "lighting_system": "system_type",
            "dimensions": {{
                "length": "value_in_feet_or_meters",
                "width": "value_in_inches_or_mm",
                "height": "value_in_inches_or_mm"
            }},
            "position": {{
                "start_point": [x, y, z],
                "end_point": [x, y, z],
                "orientation": "horizontal/vertical/angled"
            }},
            "specifications": {{
                "wattage": "value_in_watts",
                "color_temperature": "value_in_kelvin",
                "lens_type": "lens_option",
                "mounting_type": "mounting_option",
                "driver_type": "driver_specification",
                "quantity": "number_of_units"
            }},
            "additional_parameters": {{
                "spacing": "distance_between_units",
                "voltage": "voltage_requirement",
                "emergency_backup": "true/false",
                "dimmable": "true/false",
                "ip_rating": "ingress_protection_rating"
            }}
        }}
        
        Extract all relevant information from the user request. If a value is not specified, use null.
        Use standard units (feet for length, inches for width/height, watts for power, etc.).
        """
    
    def _convert_to_3d_point(self, point_list):
        """
        Converts [x, y, z] or [x, y] list into a 3D AutoCAD point (tuple of 3 floats).
        """
        x = float(point_list[0])
        y = float(point_list[1])
        z = float(point_list[2]) if len(point_list) > 2 and point_list[2] is not None else 0.0
        return (x, y, z)


    def _draw_linear_light(self, specs):
        """
        Draw a linear light fixture in AutoCAD using start/end points.
        """
        try:
            start = specs["position"]["start_point"]
            end = specs["position"]["end_point"]
            length = specs["dimensions"]["length"]
            width = specs["dimensions"]["width"]
            wattage = specs["specifications"]["wattage"]

            self.logger.info(f"Drawing linear light from {start} to {end} "
                            f"with length={length}, width={width}, wattage={wattage}")

            # Basic polyline between start and end points
            start_point = self._convert_to_3d_point(start)
            end_point = self._convert_to_3d_point(end)

            # Example: create a simple line between start and end
            self.model_space.AddLine(start_point, end_point)

            # You can expand this to draw a rectangle, block, or more
            self.logger.info("✅ Successfully drew linear light fixture.")
        except Exception as e:
            self.logger.error(f"Failed to draw linear light: {str(e)}")
            raise


    def execute_drawing_command(self, specifications: Dict) -> bool:
        """
        Execute the AutoCAD drawing command based on parsed specifications.

        Args:
            specifications: Parsed specifications from natural language input

        Returns:
            True if successful, False otherwise
        """
        try:
            command = specifications.get('command')
            if not command or command not in self.command_map:
                logger.error(f"Invalid command: {command}")
                return False

            # Get AutoCAD objects for current thread
            autocad, doc, modelspace = self._get_autocad_objects()

            # Execute based on command type
            if command in ["linear_light", "linear_light_reflector", "rush_light", "rush_recessed", "pg_light", "magneto_track"]:
                return self._draw_lighting_fixture(specifications, modelspace)
            elif command == "repeat_last":
                return self._repeat_last_command(specifications, modelspace)
            elif command in ["details", "output_modifier", "driver_calculator", "driver_update", "runid_update", "susp_kit_count", "ww_toggle"]:
                return self._add_text_annotation(specifications, modelspace)
            elif command in ["add_empck", "import_assets", "redefine_blocks"]:
                return self._insert_block(specifications, modelspace)
            elif command == "purge_all":
                return self._purge_drawing(doc)
            else:
                logger.error(f"Unknown command type: {command}")
                return False

        except Exception as e:
            logger.error(f"Error executing drawing command: {e}")
            return False
    
    def _prepare_command_parameters(self, specifications: Dict) -> str:
        """Prepare sanitized command parameters for AutoCAD execution."""
        params = []

        # Helper to safely convert values
        def safe_str(val, default="0"):
            return str(val) if val is not None else default

        # Add position parameters
        if 'position' in specifications:
            pos = specifications['position']
            if 'start_point' in pos:
                start = pos['start_point']
                if isinstance(start, (list, tuple)) and len(start) == 2:
                    params.extend([safe_str(start[0]), safe_str(start[1])])
            if 'end_point' in pos:
                end = pos['end_point']
                if isinstance(end, (list, tuple)) and len(end) == 2:
                    params.extend([safe_str(end[0]), safe_str(end[1])])

        # Add dimension parameters
        if 'dimensions' in specifications:
            dims = specifications['dimensions']
            params.append(safe_str(dims.get('length')))
            params.append(safe_str(dims.get('width')))

        # Add additional specification parameters
        if 'specifications' in specifications:
            specs = specifications['specifications']
            params.append(safe_str(specs.get('wattage')))
            params.append(safe_str(specs.get('color_temperature')))
            params.append(safe_str(specs.get('quantity')))

        return " ".join(params)
    
    def _wait_for_command_completion(self, timeout: int = 30):
        """Wait for AutoCAD command to complete."""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Get AutoCAD objects for current thread
                autocad, doc, modelspace = self._get_autocad_objects()
                
                # Check if command is still running
                if not doc.CommandInProgress:
                    return
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error waiting for command completion: {e}")
                time.sleep(0.1)
        
        logger.warning("Command execution timeout")
    
    def create_complete_drawing(self, user_input: str) -> Dict:
        """
        Create a complete AutoCAD drawing from natural language input.
        
        Args:
            user_input: Natural language description of the drawing requirements or specifications dict
            
        Returns:
            Dictionary with execution results
        """
        try:
            logger.info(f"Processing drawing request: {user_input}")
            
            # Check if user_input is already a dictionary (specifications)
            if isinstance(user_input, dict):
                specifications = user_input
                logger.info("Using provided specifications")
            else:
                # Step 1: Parse natural language input
                specifications = self.process_natural_language_request(user_input)
            
            # Step 2: Validate specifications
            if not self._validate_specifications(specifications):
                return {"success": False, "error": "Invalid specifications"}
            
            # Step 3: Execute drawing command
            success = self.execute_drawing_command(specifications)
            
            # Step 4: Apply additional modifications if needed
            if success and specifications.get('additional_parameters'):
                self._apply_additional_modifications(specifications['additional_parameters'])
            
            # Step 5: Generate summary
            summary = self._generate_drawing_summary(specifications)
            
            return {
                "success": success,
                "specifications": specifications,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating drawing: {e}")
            return {"success": False, "error": str(e)}
    
    def _validate_specifications(self, specifications: Dict) -> bool:
        """Validate parsed specifications."""
        required_fields = ['command', 'lighting_system']
        
        for field in required_fields:
            if field not in specifications:
                logger.error(f"Missing required field: {field}")
                return False
        
        if specifications['command'] not in self.command_map:
            logger.error(f"Invalid command: {specifications['command']}")
            return False
        
        return True
    
    def _apply_additional_modifications(self, additional_params: Dict):
        """Apply additional modifications to the drawing."""
        try:
            # Get AutoCAD objects for current thread
            autocad, doc, modelspace = self._get_autocad_objects()
            
            # Apply emergency backup if specified
            if additional_params.get('emergency_backup') == 'true':
                doc.SendCommand("_ADDEM ")
            
            # Apply dimming if specified
            if additional_params.get('dimmable') == 'true':
                # Add dimming controls
                pass
            
            # Apply IP rating modifications
            if 'ip_rating' in additional_params:
                # Modify for IP rating requirements
                pass
                
        except Exception as e:
            logger.error(f"Error applying additional modifications: {e}")
    
    def _generate_drawing_summary(self, specifications: Dict) -> str:
        """Generate a summary of the created drawing."""
        summary = f"Created {specifications.get('lighting_system', 'lighting')} drawing:\n"
        
        if 'dimensions' in specifications:
            dims = specifications['dimensions']
            summary += f"- Dimensions: {dims.get('length', 'N/A')} x {dims.get('width', 'N/A')} x {dims.get('height', 'N/A')}\n"
        
        if 'specifications' in specifications:
            specs = specifications['specifications']
            summary += f"- Wattage: {specs.get('wattage', 'N/A')}W\n"
            summary += f"- Color Temperature: {specs.get('color_temperature', 'N/A')}\n"
            summary += f"- Quantity: {specs.get('quantity', 'N/A')}\n"
        
        return summary
    
    def batch_process_requests(self, requests: List[str]) -> List[Dict]:
        """
        Process multiple drawing requests in batch.
        
        Args:
            requests: List of natural language drawing requests
            
        Returns:
            List of execution results
        """
        results = []
        
        for i, request in enumerate(requests):
            logger.info(f"Processing request {i+1}/{len(requests)}: {request}")
            result = self.create_complete_drawing(request)
            results.append(result)
            
            # Add delay between requests to prevent AutoCAD overload
            import time
            time.sleep(1)
        
        return results
    
    def get_available_commands(self) -> Dict:
        """Get list of available AutoCAD commands."""
        return self.command_map
    
    def get_lighting_systems(self) -> Dict:
        """Get list of available lighting systems."""
        return self.lighting_systems
    
    def close_connection(self):
        """Close AutoCAD connection."""
        try:
            self._cleanup_autocad_connection()
            logger.info("AutoCAD connection closed")
        except Exception as e:
            logger.error(f"Error closing AutoCAD connection: {e}")


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    try:
        # Initialize the AI agent
        agent = AutoDrawAIAgent()
        
        # Example drawing requests
        test_requests = [
            "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature",
            "Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens",
            "Design a magneto track system 12 feet long with 75W fixtures every 2 feet"
        ]
        
        # Process requests
        for request in test_requests:
            print(f"\nProcessing: {request}")
            result = agent.create_complete_drawing(request)
            print(f"Result: {result}")
        
        # Close connection
        agent.close_connection()
        
    except Exception as e:
        print(f"Error: {e}") 