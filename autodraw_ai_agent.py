import openai
import win32com.client
import json
import re
import os
import sys
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDrawAIAgent:
    """
    AI Agent for AutoCAD drawing automation using natural language processing.
    Leverages existing AutoLISP functions for lighting design automation.
    """
    
    def __init__(self, openai_api_key: str = None):
        """
        Initialize the AutoDraw AI Agent.
        
        Args:
            openai_api_key: OpenAI API key for natural language processing
        """
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to constructor.")
        
        openai.api_key = self.openai_api_key
        
        # Initialize AutoCAD COM connection
        try:
            print("I am here P1")
            self.autocad = win32com.client.Dispatch("AutoCAD.Application")
            self.doc = self.autocad.ActiveDocument
            self.modelspace = self.doc.ModelSpace
            logger.info("Successfully connected to AutoCAD")
        except Exception as e:
            logger.error(f"Failed to connect to AutoCAD: {e}")
            raise
        
        # Command mapping for existing AutoLISP functions
        self.command_map = {
            "linear_light": "_LSAUTO",
            "linear_light_reflector": "_LSRAUTO", 
            "rush_light": "_RushAuto",
            "rush_recessed": "_RushRecAuto",
            "pg_light": "_PGAuto",
            "magneto_track": "_MagTrkAuto",
            "repeat_last": "_LSREP",
            "details": "_Details",
            "add_empck": "_ADDEM",
            "output_modifier": "_CustomLumenCalculator",
            "driver_calculator": "_DriverCalculator",
            "driver_update": "_DriverUpdater",
            "runid_update": "_RunID",
            "susp_kit_count": "_SuspCnt",
            "ww_toggle": "_ArrowToggle",
            "import_assets": "_ImportAssets",
            "redefine_blocks": "_BlockRedefine",
            "purge_all": "_PALL"
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
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AutoCAD lighting design assistant. Parse user requests into structured specifications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse the response
            parsed_specs = json.loads(response.choices[0].message.content)
            logger.info(f"Parsed specifications: {parsed_specs}")
            
            return parsed_specs
            
        except Exception as e:
            logger.error(f"Error processing natural language request: {e}")
            raise
    
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

            # Get the actual AutoCAD command
            autocad_command = self.command_map[command]

            # Prepare and sanitize command parameters
            params = self._prepare_command_parameters(specifications)
            if params is None:
                logger.error(f"Missing or invalid parameters for command: {autocad_command}")
                return False
            
            # Sanitize: replace None with "0" or some default fallback
            sanitized_params = [str(p) if p is not None else "0" for p in params]

           # Form the complete command string
            command_string = f"{autocad_command} {' '.join(sanitized_params)}\n"
            logger.info(f"Executing AutoCAD command: {command_string.strip()}")

            # Abort if all parameters are "0", "", or "None"
            if all(str(p).strip() in ["0", "", "None"] for p in sanitized_params):
                logger.error("All command parameters are missing or zero — aborting to avoid AutoCAD crash.")
                return False

            # Check AutoCAD COM connection before sending
            try:
                doc = self.autocad.ActiveDocument
            except Exception as e:
                logger.error(f"AutoCAD COM session is broken: {e}")
                return False

            # Send command to AutoCAD
            doc.SendCommand(command_string)

            # Wait for command completion
            self._wait_for_command_completion()

            logger.info(f"Successfully executed command: {autocad_command}")
            return True

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
                # Check if command is still running
                if not self.autocad.ActiveDocument.CommandInProgress:
                    return
                time.sleep(0.1)
            except:
                time.sleep(0.1)
        
        logger.warning("Command execution timeout")
    
    def create_complete_drawing(self, user_input: str) -> Dict:
        """
        Create a complete AutoCAD drawing from natural language input.
        
        Args:
            user_input: Natural language description of the drawing requirements
            
        Returns:
            Dictionary with execution results
        """
        try:
            logger.info(f"Processing drawing request: {user_input}")
            
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
            # Apply emergency backup if specified
            if additional_params.get('emergency_backup') == 'true':
                self.autocad.ActiveDocument.SendCommand("_ADDEM ")
            
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
            if hasattr(self, 'autocad'):
                self.autocad = None
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