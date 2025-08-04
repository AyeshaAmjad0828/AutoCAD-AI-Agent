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
import traceback
import config

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
        
        # Use the proper AutoDraw palette commands from config
        self.command_map = config.COMMAND_MAP
        
        # Lighting system specifications from config
        self.lighting_systems = config.LIGHTING_SYSTEMS
        
        # Mounting options from config
        self.mounting_options = config.MOUNTING_OPTIONS
        
        # Lens options from config
        self.lens_options = config.LENS_OPTIONS
        
        # Color temperature options from config
        self.color_temps = config.COLOR_TEMPERATURES
        
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
        Converts [x, y, z] or [x, y] list into a 3D AutoCAD point (tuple of 3 floats),
        safely handling None or invalid Z values.
        """
        x = float(point_list[0])
        y = float(point_list[1])

        z = 0.0
        if len(point_list) > 2:
            try:
                z = float(point_list[2])
            except (ValueError, TypeError):
                z = 0.0

        return (x, y, z)

    def _to_variant_3d_point(self, point):
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point)

    def _execute_autodraw_command(self, command: str, specifications: Dict, doc) -> bool:
        """
        Execute AutoDraw palette commands using SendCommand.
        
        Args:
            command: The AutoDraw command to execute (e.g., "_LSAUTO", "_RushAuto")
            specifications: Drawing specifications
            doc: AutoCAD document object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Executing AutoDraw command: {command}")
            
            # Prepare command parameters based on specifications
            params = self._prepare_autodraw_parameters(specifications)
            
            # Build the complete command string
            full_command = f"{command} {params}"
            logger.info(f"Full command: {full_command}")
            
            # Execute the command
            doc.SendCommand(full_command + "\n")
            
            # Give AutoCAD a moment to start processing the command
            import time
            time.sleep(0.5)
            
            # Wait for command completion
            self._wait_for_command_completion()
            
            logger.info(f"Successfully executed {command}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute {command}: {str(e)}")
            return False
    
    def _prepare_autodraw_parameters(self, specifications: Dict) -> str:
        """
        Prepare parameters for AutoDraw commands based on specifications.
        
        Args:
            specifications: Drawing specifications
            
        Returns:
            Formatted parameter string for AutoDraw commands
        """
        params = []
        
        # Helper to safely convert values and validate ranges
        def safe_str(val, default="", max_val=None):
            if val is None:
                return default
            try:
                num_val = float(val)
                if max_val and num_val > max_val:
                    logger.warning(f"Value {num_val} exceeds maximum {max_val}, using {max_val}")
                    return str(max_val)
                return str(num_val)
            except (ValueError, TypeError):
                return str(val) if val else default
        
        # Add position parameters if available
        if 'position' in specifications:
            pos = specifications['position']
            if 'start_point' in pos:
                start = pos['start_point']
                if isinstance(start, (list, tuple)) and len(start) >= 2:
                    params.extend([safe_str(start[0], "0"), safe_str(start[1], "0")])
            if 'end_point' in pos:
                end = pos['end_point']
                if isinstance(end, (list, tuple)) and len(end) >= 2:
                    params.extend([safe_str(end[0], "10"), safe_str(end[1], "0")])
        
        # Add dimension parameters with reasonable limits
        if 'dimensions' in specifications:
            dims = specifications['dimensions']
            if 'length' in dims:
                params.append(safe_str(dims['length'], "10", 100))  # Max 100 feet
            if 'width' in dims:
                params.append(safe_str(dims['width'], "4", 24))    # Max 24 inches
            if 'height' in dims:
                params.append(safe_str(dims['height'], "4", 24))   # Max 24 inches
        
        # Add specification parameters
        if 'specifications' in specifications:
            specs = specifications['specifications']
            if 'wattage' in specs:
                params.append(safe_str(specs['wattage'], "50", 1000))  # Max 1000W
            if 'color_temperature' in specs:
                # Remove 'k' suffix if present and validate
                temp = str(specs['color_temperature']).lower().replace('k', '')
                params.append(safe_str(temp, "4000", 6500))  # Max 6500K
            if 'lens_type' in specs:
                params.append(safe_str(specs['lens_type'], "clear"))
            if 'mounting_type' in specs:
                params.append(safe_str(specs['mounting_type'], "ceiling_mount"))
            if 'quantity' in specs:
                params.append(safe_str(specs['quantity'], "1", 100))  # Max 100 units
        
        # Add additional parameters
        if 'additional_parameters' in specifications:
            add_params = specifications['additional_parameters']
            if 'spacing' in add_params:
                params.append(safe_str(add_params['spacing'], "0", 50))  # Max 50 feet
            if 'voltage' in add_params:
                params.append(safe_str(add_params['voltage'], "120", 480))  # Max 480V
            if 'emergency_backup' in add_params:
                params.append(safe_str(add_params['emergency_backup'], "false"))
            if 'dimmable' in add_params:
                params.append(safe_str(add_params['dimmable'], "false"))
            if 'ip_rating' in add_params:
                params.append(safe_str(add_params['ip_rating'], "20"))
        
        logger.info(f"Prepared parameters: {' '.join(params)}")
        return " ".join(params)
    
    def _draw_lighting_fixture(self, specs, modelspace):
        """
        Draw a lighting fixture using AutoDraw palette commands.
        """
        try:
            command = specs.get('command')
            if not command:
                logger.error("No command specified for lighting fixture")
                return False
            
            # Get the actual AutoDraw command from the command map
            autodraw_command = self.command_map.get(command)
            if not autodraw_command:
                logger.error(f"Unknown command: {command}")
                return False
            
            # Get AutoCAD objects for current thread
            autocad, doc, modelspace = self._get_autocad_objects()
            
            # Execute the appropriate AutoDraw command
            return self._execute_autodraw_command(autodraw_command, specs, doc)
            
        except Exception as e:
            logger.error(f"Failed to draw lighting fixture: {str(e)}")
            return False


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
            if not command:
                logger.error("No command specified")
                return False

            # Get AutoCAD objects for current thread
            autocad, doc, modelspace = self._get_autocad_objects()

            # Get the actual AutoDraw command from the command map
            autodraw_command = self.command_map.get(command)
            if not autodraw_command:
                logger.error(f"Unknown command: {command}")
                return False

            logger.info(f"Executing command: {command} -> {autodraw_command}")

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
                # For any other command, try to execute it directly
                return self._execute_autodraw_command(autodraw_command, specifications, doc)

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
                    logger.info("Command completed successfully")
                    return
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error waiting for command completion: {e}")
                time.sleep(0.1)
        
        logger.warning("Command execution timeout - proceeding anyway")
        # Don't fail the command if timeout occurs, as some commands might complete
        # but not properly report their completion status
    
    def _repeat_last_command(self, specifications: Dict, modelspace) -> bool:
        """Repeat the last command using LSREP."""
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            return self._execute_autodraw_command("_LSREP", specifications, doc)
        except Exception as e:
            logger.error(f"Failed to repeat last command: {e}")
            return False
    
    def _add_text_annotation(self, specifications: Dict, modelspace) -> bool:
        """Add text annotations using appropriate AutoDraw commands."""
        try:
            command = specifications.get('command')
            autocad, doc, modelspace = self._get_autocad_objects()
            
            # Map command to appropriate AutoDraw command
            command_mapping = {
                "details": "_Details",
                "output_modifier": "_CustomLumenCalculator",
                "driver_calculator": "_DriverCalculator",
                "driver_update": "_DriverUpdater",
                "runid_update": "_RunID",
                "susp_kit_count": "_SuspCnt",
                "ww_toggle": "_ArrowToggle"
            }
            
            autodraw_command = command_mapping.get(command, command)
            return self._execute_autodraw_command(autodraw_command, specifications, doc)
            
        except Exception as e:
            logger.error(f"Failed to add text annotation: {e}")
            return False
    
    def _insert_block(self, specifications: Dict, modelspace) -> bool:
        """Insert blocks using appropriate AutoDraw commands."""
        try:
            command = specifications.get('command')
            autocad, doc, modelspace = self._get_autocad_objects()
            
            # Map command to appropriate AutoDraw command
            command_mapping = {
                "add_empck": "_ADDEM",
                "import_assets": "_ImportAssets",
                "redefine_blocks": "_BlockRedefine"
            }
            
            autodraw_command = command_mapping.get(command, command)
            return self._execute_autodraw_command(autodraw_command, specifications, doc)
            
        except Exception as e:
            logger.error(f"Failed to insert block: {e}")
            return False
    
    def _purge_drawing(self, doc) -> bool:
        """Purge drawing using PALL command."""
        try:
            return self._execute_autodraw_command("_PALL", {}, doc)
        except Exception as e:
            logger.error(f"Failed to purge drawing: {e}")
            return False
    
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
        # Check if command exists
        if 'command' not in specifications:
            logger.error("Missing required field: command")
            return False
        
        # Check if command is valid
        if specifications['command'] not in self.command_map:
            logger.error(f"Invalid command: {specifications['command']}")
            return False
        
        # For lighting system commands, check if lighting_system is specified
        lighting_commands = ["linear_light", "linear_light_reflector", "rush_light", "rush_recessed", "pg_light", "magneto_track"]
        if specifications['command'] in lighting_commands:
            if 'lighting_system' not in specifications:
                logger.warning(f"Lighting system not specified for command: {specifications['command']}")
                # Don't fail validation for this, just warn
        
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