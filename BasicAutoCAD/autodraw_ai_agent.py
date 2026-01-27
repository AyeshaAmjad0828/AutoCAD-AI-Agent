from urllib import response
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
import os
import httpx
from openai import OpenAI


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDrawAIAgent:
    """
    AI Agent for AutoCAD drawing automation using natural language processing.
    Leverages existing AutoLISP functions for lighting design automation.
    """
    
    def __init__(self, openai_api_key: str = None, initialize_autocad: bool = True):

        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")

        http_client = httpx.Client(timeout=httpx.Timeout(60.0),trust_env=False)

        self.openai_client = OpenAI(api_key=self.openai_api_key,http_client=http_client)

        self._thread_local = threading.local()

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
            "purge_all": "_PURGE",
            # New drawing commands for complex shapes
            "rectangle": "_RECTANGLE",
            "circle": "_CIRCLE",
            "polyline": "_PLINE",
            "arc": "_ARC",
            "ellipse": "_ELLIPSE",
            "text": "_TEXT",
            "dimension": "_DIMENSION",
            "hatch": "_HATCH",
            "block": "_INSERT",
            "array": "_ARRAY",
            "mirror": "_MIRROR",
            "rotate": "_ROTATE",
            "scale": "_SCALE",
            "offset": "_OFFSET",
            "trim": "_TRIM",
            "extend": "_EXTEND",
            "fillet": "_FILLET",
            "chamfer": "_CHAMFER"
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
            prompt = self._create_parsing_prompt(user_input)


            response = self.openai_client.chat.completions.create(model="gpt-4.1-mini",messages=[{"role": "system", "content": "You are an expert AutoCAD lighting design assistant. Parse user requests into structured specifications."},{"role": "user", "content": prompt}],temperature=0.1,max_tokens=1000)
            
            return json.loads(response.choices[0].message.content)

        except Exception as e:
           logger.error(f"NLP parsing failed: {e}")
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
        Parse this AutoCAD drawing request into JSON format:
        
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
                "height": "value_in_inches_or_mm",
                "radius": "value_for_circles_arcs",
                "major_axis": "value_for_ellipses",
                "minor_axis": "value_for_ellipses"
            }},
            "position": {{
                "start_point": [x, y, z],
                "end_point": [x, y, z],
                "center_point": [x, y, z],
                "insertion_point": [x, y, z],
                "text_position": [x, y, z],
                "mirror_line_start": [x, y, z],
                "mirror_line_end": [x, y, z],
                "base_point": [x, y, z],
                "points": [[x1, y1, z1], [x2, y2, z2], ...],
                "orientation": "horizontal/vertical/angled"
            }},
            "specifications": {{
                "wattage": "value_in_watts",
                "color_temperature": "value_in_kelvin",
                "lens_type": "lens_option",
                "mounting_type": "mounting_option",
                "driver_type": "driver_specification",
                "quantity": "number_of_units",
                "text_content": "text_to_display",
                "text_height": "text_height_value",
                "block_name": "name_of_block_to_insert",
                "pattern_name": "hatch_pattern_name"
            }},
            "additional_parameters": {{
                "spacing": "distance_between_units",
                "voltage": "voltage_requirement",
                "emergency_backup": "true/false",
                "dimmable": "true/false",
                "ip_rating": "ingress_protection_rating",
                "closed": "true/false_for_polylines",
                "start_angle": "angle_in_degrees",
                "end_angle": "angle_in_degrees",
                "scale": "scale_factor",
                "rotation": "rotation_angle",
                "array_type": "rectangular/polar",
                "rows": "number_of_rows",
                "columns": "number_of_columns",
                "row_spacing": "distance_between_rows",
                "column_spacing": "distance_between_columns",
                "num_items": "number_of_items_for_polar_array",
                "angle": "total_angle_for_polar_array",
                "scale_factor": "scale_factor_for_scale_command",
                "offset_distance": "distance_for_offset",
                "fillet_radius": "radius_for_fillet",
                "chamfer_distance1": "first_chamfer_distance",
                "chamfer_distance2": "second_chamfer_distance"
            }}
        }}
        
        Extract all relevant information from the user request. If a value is not specified, use null.
        Use standard units (feet for length, inches for width/height, watts for power, etc.).
        
        Examples of commands:
        - "rectangle": Use start_point and end_point
        - "circle": Use center_point and radius
        - "polyline": Use points array and closed parameter
        - "arc": Use center_point, radius, start_angle, end_angle
        - "ellipse": Use center_point, major_axis, minor_axis
        - "text": Use insertion_point and text_content
        - "array": Use array_type, rows, columns, row_spacing, column_spacing
        - "mirror": Use mirror_line_start and mirror_line_end
        - "rotate": Use base_point and angle
        - "scale": Use base_point and scale_factor
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

    def _draw_lighting_fixture(self, specs, modelspace):
        print("Running as:", os.getlogin())
        """
        Draw a linear light fixture in AutoCAD using start/end points.
        """
        try:

            # Validate required fields
            if "position" not in specs or "start_point" not in specs["position"] or "end_point" not in specs["position"]:
                logger.error("Missing required position information")
                return False
                
            if "dimensions" not in specs or "length" not in specs["dimensions"]:
                logger.error("Missing required dimension information")
                return False
                
            if "specifications" not in specs or "wattage" not in specs["specifications"]:
                logger.error("Missing required specification information")
                return False

            start = specs["position"]["start_point"]
            end = specs["position"]["end_point"]
            length = specs["dimensions"]["length"]
            width = specs["dimensions"]["width"]
            wattage = specs["specifications"]["wattage"]

            logger.info(f"Drawing linear light from {start} to {end} "
                            f"with length={length}, width={width}, wattage={wattage}")

            # Basic polyline between start and end points
            start_point = self._convert_to_3d_point(start)
            end_point = self._convert_to_3d_point(end)
            logger.debug(f"Converted start_point: {start_point}, end_point: {end_point}")
            
            # Ensure start and end points are valid
            if not isinstance(start_point, tuple) or not isinstance(end_point, tuple):
                raise ValueError("Invalid start or end point format. Must be a list or tuple of numbers.")

            # Example: create a simple line between start and end
            try:
                modelspace.AddLine(self._to_variant_3d_point(start_point), self._to_variant_3d_point(end_point))
            except Exception as e:
                print("Drawing creation failed!")
                traceback.print_exc()
                return False  # ✅ Explicit failure

            # You can expand this to draw a rectangle, block, or more
            logger.info("Successfully drew linear light fixture.")
            return True  # ✅ Explicit success
        except Exception as e:
            logger.error(f"Failed to draw linear light: {str(e)}")
            raise

    def _draw_rectangle(self, specs, modelspace):
        """Draw a rectangle in AutoCAD."""
        try:
            start = specs["position"]["start_point"]
            end = specs["position"]["end_point"]
            
            start_point = self._convert_to_3d_point(start)
            end_point = self._convert_to_3d_point(end)
            
            logger.info(f"Drawing rectangle from {start_point} to {end_point}")
            
            # Create rectangle using polyline with 4 points
            x1, y1, z1 = start_point
            x2, y2, z2 = end_point
            
            # Define the 4 corners of the rectangle
            points = [
                (x1, y1, z1),  # Bottom-left
                (x2, y1, z1),  # Bottom-right
                (x2, y2, z1),  # Top-right
                (x1, y2, z1),  # Top-left
                (x1, y1, z1)   # Back to start to close
            ]
            
            # Convert points to variant array
            point_array = []
            for point in points:
                point_array.extend(point)
            
            # Create closed polyline for rectangle
            polyline = modelspace.AddPolyline(win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point_array))
            polyline.Closed = True
            
            logger.info("Successfully drew rectangle.")
            return True
        except Exception as e:
            logger.error(f"Failed to draw rectangle: {str(e)}")
            return False

    def _draw_circle(self, specs, modelspace):
        """Draw a circle in AutoCAD."""
        try:
            center = specs["position"]["center_point"]
            radius = specs["dimensions"].get("radius", 1.0)
            
            center_point = self._convert_to_3d_point(center)
            
            logger.info(f"Drawing circle at {center_point} with radius {radius}")
            
            # Create circle using AddCircle method
            # Convert center point to variant array
            center_array = list(center_point)
            circle = modelspace.AddCircle(win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, center_array), radius)
            
            logger.info("Successfully drew circle.")
            return True
        except Exception as e:
            logger.error(f"Failed to draw circle: {str(e)}")
            return False

    def _draw_polyline(self, specs, modelspace):
        """Draw a polyline in AutoCAD."""
        try:
            points = specs["position"]["points"]
            closed = specs.get("closed", False)
            
            # Convert all points to 3D format and flatten to array
            point_array = []
            for point in points:
                converted_point = self._convert_to_3d_point(point)
                point_array.extend(converted_point)
            
            logger.info(f"Drawing polyline with {len(points)} points")
            
            # Create polyline using AddPolyline method
            polyline = modelspace.AddPolyline(win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point_array))
            
            # Close the polyline if specified
            if closed:
                polyline.Closed = True
            
            logger.info("Successfully drew polyline.")
            return True
        except Exception as e:
            logger.error(f"Failed to draw polyline: {str(e)}")
            return False

    def _draw_arc(self, specs, modelspace):
        """Draw an arc in AutoCAD."""
        try:
            center = specs["position"]["center_point"]
            radius = specs["dimensions"].get("radius", 1.0)
            start_angle = specs.get("start_angle", 0.0)
            end_angle = specs.get("end_angle", 90.0)
            
            center_point = self._convert_to_3d_point(center)
            
            logger.info(f"Drawing arc at {center_point} with radius {radius}")
            
            # Create arc using AddArc method
            # Convert center point to variant array
            center_array = list(center_point)
            arc = modelspace.AddArc(win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, center_array), radius, start_angle, end_angle)
            
            logger.info("Successfully drew arc.")
            return True
        except Exception as e:
            logger.error(f"Failed to draw arc: {str(e)}")
            return False

    def _draw_ellipse(self, specs, modelspace):
        """Draw an ellipse in AutoCAD."""
        try:
            center = specs["position"]["center_point"]
            major_axis = specs["dimensions"].get("major_axis", 2.0)
            minor_axis = specs["dimensions"].get("minor_axis", 1.0)
            
            center_point = self._convert_to_3d_point(center)
            
            logger.info(f"Drawing ellipse at {center_point}")
            
            # Create ellipse using AddEllipse method
            # Convert center point to variant array
            center_array = list(center_point)
            # For ellipse, we need to specify the major axis endpoint
            major_axis_end = (center_point[0] + major_axis, center_point[1], center_point[2])
            major_axis_array = list(major_axis_end)
            
            ellipse = modelspace.AddEllipse(win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, center_array), 
                                          win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, major_axis_array), 
                                          minor_axis / major_axis)
            
            logger.info("Successfully drew ellipse.")
            return True
        except Exception as e:
            logger.error(f"Failed to draw ellipse: {str(e)}")
            return False

    def _add_text(self, specs, modelspace):
        """Add text to AutoCAD drawing."""
        try:
            position = specs["position"]["insertion_point"]
            text_content = specs.get("text_content", "Sample Text")
            height = specs.get("text_height", 0.125)
            
            insertion_point = self._convert_to_3d_point(position)
            
            logger.info(f"Adding text '{text_content}' at {insertion_point}")
            
            # Create text using AddText method
            # Convert insertion point to variant array
            insertion_array = list(insertion_point)
            text = modelspace.AddText(text_content, win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, insertion_array), height)
            
            logger.info("Successfully added text.")
            return True
        except Exception as e:
            logger.error(f"Failed to add text: {str(e)}")
            return False

    def _add_dimension(self, specs, modelspace):
        """Add dimension to AutoCAD drawing."""
        try:
            start_point = specs["position"]["start_point"]
            end_point = specs["position"]["end_point"]
            text_position = specs["position"]["text_position"]
            
            start_pt = self._convert_to_3d_point(start_point)
            end_pt = self._convert_to_3d_point(end_point)
            text_pt = self._convert_to_3d_point(text_position)
            
            logger.info(f"Adding dimension from {start_pt} to {end_pt}")
            
            # Create dimension using AddDimAligned method
            modelspace.AddDimAligned(start_pt, end_pt, text_pt)
            
            logger.info("Successfully added dimension.")
            return True
        except Exception as e:
            logger.error(f"Failed to add dimension: {str(e)}")
            return False

    def _add_hatch(self, specs, modelspace):
        """Add hatch pattern to AutoCAD drawing."""
        try:
            pattern_name = specs.get("pattern_name", "SOLID")
            scale = specs.get("scale", 1.0)
            angle = specs.get("angle", 0.0)
            
            # Get the last created object to hatch
            last_object = modelspace.Item(modelspace.Count - 1)
            
            logger.info(f"Adding hatch pattern '{pattern_name}'")
            
            # Create hatch using AddHatch method
            hatch = modelspace.AddHatch(0, pattern_name, True)
            hatch.AppendOuterLoop([last_object])
            hatch.Evaluate()
            
            logger.info("Successfully added hatch.")
            return True
        except Exception as e:
            logger.error(f"Failed to add hatch: {str(e)}")
            return False

    def import_assets_as_blocks(self, assets_folder: str = None) -> Dict:
        """
        Import AutoCAD drawing files from assets folder as blocks.
        
        Args:
            assets_folder: Path to assets folder (default: AD App&Assets)
            
        Returns:
            Dictionary of imported block names and their file paths
        """
        try:
            if assets_folder is None:
                # Use default assets folder
                current_dir = os.path.dirname(os.path.abspath(__file__))
                assets_folder = os.path.join(os.path.dirname(current_dir), "AD App&Assets")
            
            if not os.path.exists(assets_folder):
                logger.error(f"Assets folder not found: {assets_folder}")
                return {}
            
            # Get AutoCAD objects
            autocad, doc, modelspace = self._get_autocad_objects()
            
            imported_blocks = {}
            
            # Find all .dwg files in the assets folder
            for filename in os.listdir(assets_folder):
                if filename.lower().endswith('.dwg'):
                    file_path = os.path.join(assets_folder, filename)
                    block_name = os.path.splitext(filename)[0]  # Remove .dwg extension
                    
                    try:
                        # Import the drawing as a block
                        logger.info(f"Importing {filename} as block '{block_name}'")
                        
                        # Use AutoCAD's InsertBlock method to import the drawing
                        # This creates a block definition from the external drawing
                        doc.InsertBlock(
                            win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, [0, 0, 0]),  # Insertion point
                            file_path,  # File path
                            1.0, 1.0, 1.0,  # Scale factors
                            0.0  # Rotation
                        )
                        
                        imported_blocks[block_name] = file_path
                        logger.info(f"Successfully imported block: {block_name}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to import {filename}: {e}")
                        continue
            
            logger.info(f"Imported {len(imported_blocks)} blocks from assets folder")
            return imported_blocks
            
        except Exception as e:
            logger.error(f"Error importing assets: {e}")
            return {}
    
    def list_available_blocks(self) -> List[str]:
        """
        List all available blocks in the current drawing.
        
        Returns:
            List of block names
        """
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            
            blocks = []
            for i in range(doc.Blocks.Count):
                block = doc.Blocks.Item(i)
                if not block.IsLayout:  # Skip layout blocks
                    blocks.append(block.Name)
            
            return blocks
            
        except Exception as e:
            logger.error(f"Error listing blocks: {e}")
            return []

    def _insert_block(self, specs, modelspace):
        """Insert a block in AutoCAD drawing."""
        try:
            insertion_point = specs["position"]["insertion_point"]
            block_name = specs.get("block_name", "test_block")
            scale = specs.get("scale", 1.0)
            rotation = specs.get("rotation", 0.0)
            
            insert_pt = self._convert_to_3d_point(insertion_point)
            
            logger.info(f"Inserting block '{block_name}' at {insert_pt}")
            
            # Get AutoCAD objects for current thread
            autocad, doc, modelspace = self._get_autocad_objects()
            
            # Check if the block exists in the drawing
            try:
                # Try to get the block definition
                block_def = doc.Blocks.Item(block_name)
                logger.info(f"Found existing block: {block_name}")
            except Exception as e:
                logger.warning(f"Block '{block_name}' not found in drawing. Creating a simple rectangle as placeholder.")
                
                # Create a simple rectangle as a placeholder block
                # Define rectangle points (1x1 unit)
                x, y, z = insert_pt
                rect_points = [
                    (x, y, z),           # Bottom-left
                    (x + 1, y, z),       # Bottom-right
                    (x + 1, y + 1, z),   # Top-right
                    (x, y + 1, z),       # Top-left
                    (x, y, z)            # Back to start to close
                ]
                
                # Convert points to variant array
                point_array = []
                for point in rect_points:
                    point_array.extend(point)
                
                # Create closed polyline for rectangle
                polyline = modelspace.AddPolyline(win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, point_array))
                polyline.Closed = True
                
                # Add text label
                text_point = (x + 0.5, y + 0.5, z)
                text = modelspace.AddText(block_name, win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(text_point)), 0.1)
                
                logger.info(f"Created placeholder block '{block_name}' as rectangle with label")
                return True
            
            # If block exists, try to insert it
            try:
                # Create block reference using AddBlockReference method
                block_ref = modelspace.AddBlockReference(insert_pt, block_name, scale, scale, scale, rotation)
                
                # Apply rotation if specified
                if rotation != 0.0:
                    block_ref.Rotation = rotation * (3.14159 / 180.0)  # Convert degrees to radians
                
                logger.info("Successfully inserted block.")
                return True
                
            except Exception as e:
                logger.error(f"Failed to insert block '{block_name}': {str(e)}")
                logger.info("This might be due to the block not being properly defined or accessible.")
                return False
                
        except Exception as e:
            logger.error(f"Failed to insert block: {str(e)}")
            return False

    def _create_array(self, specs, modelspace):
        """Create an array of objects in AutoCAD."""
        try:
            array_type = specs.get("array_type", "rectangular")  # rectangular or polar
            rows = specs.get("rows", 2)
            columns = specs.get("columns", 2)
            row_spacing = specs.get("row_spacing", 2.0)
            column_spacing = specs.get("column_spacing", 2.0)
            
            # Get the last created object to array
            last_object = modelspace.Item(modelspace.Count - 1)
            
            logger.info(f"Creating {array_type} array with {rows}x{columns} objects")
            
            if array_type == "rectangular":
                # Create rectangular array
                modelspace.AddRectangularArray(last_object, rows, columns, row_spacing, column_spacing)
            else:
                # Create polar array
                center_point = specs["position"]["center_point"]
                center_pt = self._convert_to_3d_point(center_point)
                num_items = specs.get("num_items", 8)
                angle = specs.get("angle", 360.0)
                
                modelspace.AddPolarArray(last_object, center_pt, num_items, angle)
            
            logger.info("Successfully created array.")
            return True
        except Exception as e:
            logger.error(f"Failed to create array: {str(e)}")
            return False

    def _mirror_objects(self, specs, modelspace):
        """Mirror objects in AutoCAD."""
        try:
            mirror_line_start = specs["position"]["mirror_line_start"]
            mirror_line_end = specs["position"]["mirror_line_end"]
            
            start_pt = self._convert_to_3d_point(mirror_line_start)
            end_pt = self._convert_to_3d_point(mirror_line_end)
            
            logger.info(f"Mirroring objects along line from {start_pt} to {end_pt}")
            
            # Get all objects in modelspace
            objects = []
            for i in range(modelspace.Count):
                objects.append(modelspace.Item(i))
            
            # Mirror each object
            for obj in objects:
                modelspace.AddMirror(obj, start_pt, end_pt)
            
            logger.info("Successfully mirrored objects.")
            return True
        except Exception as e:
            logger.error(f"Failed to mirror objects: {str(e)}")
            return False

    def _rotate_objects(self, specs, modelspace):
        """Rotate objects in AutoCAD."""
        try:
            base_point = specs["position"]["base_point"]
            angle = specs.get("angle", 90.0)
            
            base_pt = self._convert_to_3d_point(base_point)
            
            logger.info(f"Rotating objects around {base_pt} by {angle} degrees")
            
            # Get all objects in modelspace
            objects = []
            for i in range(modelspace.Count):
                objects.append(modelspace.Item(i))
            
            # Rotate each object
            for obj in objects:
                modelspace.AddRotate(obj, base_pt, angle)
            
            logger.info("Successfully rotated objects.")
            return True
        except Exception as e:
            logger.error(f"Failed to rotate objects: {str(e)}")
            return False

    def _scale_objects(self, specs, modelspace):
        """Scale objects in AutoCAD."""
        try:
            base_point = specs["position"]["base_point"]
            scale_factor = specs.get("scale_factor", 2.0)
            
            base_pt = self._convert_to_3d_point(base_point)
            
            logger.info(f"Scaling objects from {base_pt} by factor {scale_factor}")
            
            # Get all objects in modelspace
            objects = []
            for i in range(modelspace.Count):
                objects.append(modelspace.Item(i))
            
            # Scale each object
            for obj in objects:
                modelspace.AddScale(obj, base_pt, scale_factor)
            
            logger.info("Successfully scaled objects.")
            return True
        except Exception as e:
            logger.error(f"Failed to scale objects: {str(e)}")
            return False

    def _modify_objects(self, specs, modelspace, command):
        """Modify existing objects in AutoCAD."""
        try:
            if command == "offset":
                distance = specs.get("offset_distance", 1.0)
                # Get the last created object to offset
                last_object = modelspace.Item(modelspace.Count - 1)
                modelspace.AddOffset(last_object, distance)
                logger.info(f"Successfully offset object by {distance}")
                
            elif command == "trim":
                # Trim objects using cutting edges
                cutting_edges = specs.get("cutting_edges", [])
                if cutting_edges:
                    # Get objects to trim (last created object)
                    last_object = modelspace.Item(modelspace.Count - 1)
                    modelspace.AddTrim(last_object, cutting_edges)
                    logger.info("Successfully trimmed object")
                    
            elif command == "extend":
                # Extend objects to boundary
                boundary = specs.get("boundary", [])
                if boundary:
                    # Get objects to extend (last created object)
                    last_object = modelspace.Item(modelspace.Count - 1)
                    modelspace.AddExtend(last_object, boundary)
                    logger.info("Successfully extended object")
                    
            elif command == "fillet":
                radius = specs.get("fillet_radius", 0.5)
                # Get the last two created objects to fillet
                if modelspace.Count >= 2:
                    obj1 = modelspace.Item(modelspace.Count - 2)
                    obj2 = modelspace.Item(modelspace.Count - 1)
                    modelspace.AddFillet(obj1, obj2, radius)
                    logger.info(f"Successfully created fillet with radius {radius}")
                    
            elif command == "chamfer":
                distance1 = specs.get("chamfer_distance1", 0.5)
                distance2 = specs.get("chamfer_distance2", 0.5)
                # Get the last two created objects to chamfer
                if modelspace.Count >= 2:
                    obj1 = modelspace.Item(modelspace.Count - 2)
                    obj2 = modelspace.Item(modelspace.Count - 1)
                    modelspace.AddChamfer(obj1, obj2, distance1, distance2)
                    logger.info(f"Successfully created chamfer with distances {distance1}, {distance2}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to modify objects with {command}: {str(e)}")
            return False

    def _repeat_last_command(self, specs, modelspace):
        """Repeat the last command executed."""
        try:
            # This would typically repeat the last command with new parameters
            # For now, we'll just log that it was called
            logger.info("Repeat last command called")
            return True
        except Exception as e:
            logger.error(f"Failed to repeat last command: {str(e)}")
            return False

    def _add_text_annotation(self, specs, modelspace):
        """Add text annotation to the drawing."""
        try:
            # Use the existing _add_text method
            return self._add_text(specs, modelspace)
        except Exception as e:
            logger.error(f"Failed to add text annotation: {str(e)}")
            return False

    def _purge_drawing(self, doc):
        """Purge unused objects from the drawing."""
        try:
            # Execute purge command
            doc.SendCommand("_PURGE ")
            logger.info("Successfully purged drawing")
            return True
        except Exception as e:
            logger.error(f"Failed to purge drawing: {str(e)}")
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
            # New complex drawing commands
            elif command == "rectangle":
                return self._draw_rectangle(specifications, modelspace)
            elif command == "circle":
                return self._draw_circle(specifications, modelspace)
            elif command == "polyline":
                return self._draw_polyline(specifications, modelspace)
            elif command == "arc":
                return self._draw_arc(specifications, modelspace)
            elif command == "ellipse":
                return self._draw_ellipse(specifications, modelspace)
            elif command == "text":
                return self._add_text(specifications, modelspace)
            elif command == "dimension":
                return self._add_dimension(specifications, modelspace)
            elif command == "hatch":
                return self._add_hatch(specifications, modelspace)
            elif command == "block":
                return self._insert_block(specifications, modelspace)
            elif command == "array":
                return self._create_array(specifications, modelspace)
            elif command == "mirror":
                return self._mirror_objects(specifications, modelspace)
            elif command == "rotate":
                return self._rotate_objects(specifications, modelspace)
            elif command == "scale":
                return self._scale_objects(specifications, modelspace)
            elif command in ["offset", "trim", "extend", "fillet", "chamfer"]:
                # These are modification commands that work on existing objects
                return self._modify_objects(specifications, modelspace, command)
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
        # Command is always required
        if 'command' not in specifications:
            logger.error("Missing required field: command")
            return False
        
        if specifications['command'] not in self.command_map:
            logger.error(f"Invalid command: {specifications['command']}")
            return False
        
        # Lighting system is only required for lighting-related commands
        lighting_commands = ["linear_light", "linear_light_reflector", "rush_light", "rush_recessed", "pg_light", "magneto_track"]
        if specifications['command'] in lighting_commands:
            if 'lighting_system' not in specifications:
                logger.error(f"Missing required field: lighting_system for command {specifications['command']}")
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