"""
AutoDraw AI Agent - AutoCAD Drawing Automation
Integrates with AutoLISP functions for lighting fixture design automation.

Version: 2.0
Author: Hira - Rewritten for LISP integration
"""

import win32com.client
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import threading
import pythoncom
import traceback
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AutoDrawAIAgent:
    """
    AI Agent for AutoCAD drawing automation.
    Integrates with AutoLISP functions for lighting fixture design.
    
    Supports fixture types: PG, LS, LSR, Rush, Magneto, and more.
    """
    
    def __init__(self, initialize_autocad: bool = True):
        """
        Initialize the AutoDraw AI Agent.
        
        Args:
            lisp_base_path: Base path to LISP files directory
            initialize_autocad: Whether to initialize AutoCAD connection on startup
        """

        self.lisp_base_path = r"C:\Users\coronetastera\Documents\Lisp and Dialogue files\Lisp"

        self._thread_local = threading.local()
        
        # LISP file configuration
        # self.lisp_base_path = lisp_base_path or self._get_default_lisp_path()
        self._setup_lisp_files()
        
        # Track loaded LISP files
        self._loaded_lisp = set()
        
        # Initialize AutoCAD connection
        if initialize_autocad:
            self._initialize_autocad_connection()
        
        logger.info("AutoDraw AI Agent initialized successfully")
    
    def _get_default_lisp_path(self) -> str:
        """Get default LISP files path based on script location."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "LISP")
    
    def _setup_lisp_files(self):
        """Setup LISP file paths and fixture configurations."""
        
        # LISP file paths - UPDATE THESE PATHS FOR YOUR SYSTEM
        self.lisp_files = {
            "universal": os.path.join(self.lisp_base_path, "Autodraw_UnivFunctions.lsp"),
            "PG": os.path.join(self.lisp_base_path, "PG_AutoDraw_API.lsp"),
            "LS": os.path.join(self.lisp_base_path, "LS_AutoDraw.lsp"),
            "LSR": os.path.join(self.lisp_base_path, "LSR_AutoDraw.lsp"),
            "Rush": os.path.join(self.lisp_base_path, "Rush_AutoDraw.lsp"),
            "Rush-Rec": os.path.join(self.lisp_base_path, "Rush_AutoDraw.lsp"),  # Same file, different mode
            "Magneto": os.path.join(self.lisp_base_path, "Magneto_AutoDraw.lsp"),
        }
        
        # Fixture type to LISP API function mapping
        self.fixture_api_map = {
            "PG": "c:PGAutoAPI",
            "LS": "c:LSAutoAPI",
            "LSR": "c:LSRAutoAPI",
            "Rush": "c:RushAutoAPI",
            "Rush-Rec": "c:RushRecAutoAPI",
            "Magneto": "c:MagAutoAPI",
        }
        
        # Supported fixture types with their valid options
        self.fixture_configs = {
            "PG": {
                "series": ["PG2", "PG4", "FLAWLESS.2", "FLAWLESS.4", "PF2", "PF4"],
                "mounting": ["F", "NT", "T", "T15", "MW"],
                "output": ["LOW", "MED", "HIGH", "LMFT", "WFT"],
                "regress": [0, 1, 2, 3, 4],
                "finish": ["White", "Black", "Silver", "CC"],
            },
            "LS": {
                "series": ["LS1", "LS2", "LS3", "LS4"],
                "mounting": ["AC", "SM", "WM", "F", "NT", "T", "T15"],
                "output": ["LOW", "MED", "HIGH", "LMFT", "WFT"],
                "config": ["DN", "UP", "UPDN"],
                "finish": ["White", "Black", "Silver", "CC"],
            },
            "LSR": {
                "series": ["LSR1", "LSR2", "LSR3", "LSR4"],
                "mounting": ["F", "NT", "T", "T15", "PMF", "PMNT"],
                "output": ["LOW", "MED", "HIGH", "LMFT", "WFT"],
                "finish": ["White", "Black", "Silver", "CC"],
            },
            "Rush": {
                "series": ["Rush"],
                "mounting": ["AC", "SM", "WM"],
                "output": ["LOW", "MED", "HIGH"],
                "finish": ["White", "Black", "Silver", "CC"],
            },
            "Magneto": {
                "series": ["Magneto"],
                "mounting": ["Surface", "Recessed"],
                "output": ["LOW", "MED", "HIGH"],
            },
        }
        
        # Finish code mapping (input format -> LISP format)
        self.finish_map = {
            'WH': 'White', 'WHITE': 'White', 'W': 'White',
            'BK': 'Black', 'BLACK': 'Black', 'BLK': 'Black',
            'SL': 'Silver', 'SILVER': 'Silver', 'SV': 'Silver', 'SLV': 'Silver',
            'CC': 'CC', 'CUSTOM': 'CC'
        }

    # =========================================================================
    # AUTOCAD CONNECTION MANAGEMENT
    # =========================================================================
    
    def _initialize_autocad_connection(self):
        """Initialize AutoCAD COM connection for the current thread."""
        try:
            pythoncom.CoInitialize()
            
            # Try to get existing AutoCAD instance first
            try:
                self._thread_local.autocad = win32com.client.GetActiveObject("AutoCAD.Application")
                logger.info("Connected to existing AutoCAD instance")
            except:
                self._thread_local.autocad = win32com.client.Dispatch("AutoCAD.Application")
                logger.info("Created new AutoCAD instance")
            
            # Wait for AutoCAD to initialize
            import time
            time.sleep(1.0)
            
            # Verify connection
            try:
                app_name = self._thread_local.autocad.Name
                logger.info(f"Connected to AutoCAD: {app_name}")
            except Exception as e:
                logger.error(f"AutoCAD application not accessible: {e}")
                raise
            
            # Get or create document
            try:
                documents = self._thread_local.autocad.Documents
                doc_count = documents.Count
                logger.info(f"Found {doc_count} existing documents")
                
                if doc_count == 0:
                    logger.info("Creating new document")
                    self._thread_local.doc = documents.Add()
                else:
                    logger.info("Using active document")
                    self._thread_local.doc = self._thread_local.autocad.ActiveDocument
                    
            except Exception as e:
                logger.error(f"Error accessing documents: {e}")
                try:
                    self._thread_local.doc = self._thread_local.autocad.Documents.Add()
                except Exception as e2:
                    logger.error(f"Failed to create new document: {e2}")
                    raise
            
            # Get ModelSpace
            self._thread_local.modelspace = self._thread_local.doc.ModelSpace
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
            if not hasattr(self._thread_local, 'autocad') or self._thread_local.autocad is None:
                self._initialize_autocad_connection()
            
            # Test the connection
            try:
                doc = self._thread_local.autocad.ActiveDocument
                return self._thread_local.autocad, doc, self._thread_local.modelspace
            except Exception as e:
                logger.info(f"AutoCAD connection broken, reconnecting... Error: {e}")
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

    # =========================================================================
    # LISP FILE MANAGEMENT
    # =========================================================================
    
    def _load_lisp_file(self, file_key: str) -> bool:
        """
        Load a LISP file if not already loaded.
        
        Args:
            file_key: Key from self.lisp_files dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if file_key in self._loaded_lisp:
            logger.debug(f"LISP file already loaded: {file_key}")
            return True
        
        if file_key not in self.lisp_files:
            logger.error(f"Unknown LISP file key: {file_key}")
            return False
        
        file_path = self.lisp_files[file_key]
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"LISP file not found: {file_path}")
            return False
        
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            
            # Normalize path for LISP (use forward slashes)
            lisp_path = file_path.replace('\\', '/')
            
            # Load the LISP file
            load_cmd = f'(load "{lisp_path}")\n'
            doc.SendCommand(load_cmd)
            
            self._loaded_lisp.add(file_key)
            logger.info(f"Loaded LISP file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load LISP file {file_key}: {e}")
            return False
    
    def _ensure_lisp_loaded(self, fixture_type: str) -> bool:
        """
        Ensure required LISP files are loaded.
        Always reloads to handle new drawings.
        """
        # Always load universal functions (safe to reload)
        if not self._load_lisp_file_always("universal"):
            logger.error("Failed to load universal LISP functions")
            return False
        
        # Load fixture-specific LISP
        if fixture_type not in self.lisp_files:
            logger.error(f"No LISP file configured for fixture type: {fixture_type}")
            return False
        
        if not self._load_lisp_file_always(fixture_type):
            logger.error(f"Failed to load LISP file for fixture type: {fixture_type}")
            return False
        
        return True
    
    def _load_lisp_file_always(self, file_key: str) -> bool:
        """Load a LISP file (always reloads, doesn't check cache)."""
        if file_key not in self.lisp_files:
            logger.error(f"Unknown LISP file key: {file_key}")
            return False
        
        file_path = self.lisp_files[file_key]
        
        if not os.path.exists(file_path):
            logger.error(f"LISP file not found: {file_path}")
            return False
        
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            lisp_path = file_path.replace('\\', '/')
            load_cmd = f'(load "{lisp_path}")\n'
            doc.SendCommand(load_cmd)
            logger.info(f"Loaded LISP file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load LISP file {file_key}: {e}")
            return False
    
    def set_lisp_path(self, fixture_type: str, path: str):
        """
        Set or update the path for a LISP file.
        
        Args:
            fixture_type: Type of fixture or "universal"
            path: Full path to the LISP file
        """
        self.lisp_files[fixture_type] = path
        # Remove from loaded set so it gets reloaded with new path
        self._loaded_lisp.discard(fixture_type)
        logger.info(f"Updated LISP path for {fixture_type}: {path}")

    # =========================================================================
    # MAIN DRAWING INTERFACE
    # =========================================================================
    
    def draw_fixture(self, fixture_type: str, specs: Dict) -> Dict:
        """
        Main entry point for drawing any fixture type.
        Routes to the appropriate fixture-specific method.
        
        Args:
            fixture_type: "PG", "LS", "LSR", "Rush", "Magneto", etc.
            specs: Dictionary with fixture specifications
        
        Returns:
            Dictionary with success status and details
        """
        try:
            # Normalize fixture type
            fixture_type = fixture_type.upper() if fixture_type.upper() in ["PG", "LS", "LSR"] else fixture_type
            
            # Validate fixture type
            if fixture_type not in self.fixture_api_map:
                return {
                    "success": False,
                    "error": f"Unknown fixture type: {fixture_type}. "
                             f"Supported types: {list(self.fixture_api_map.keys())}"
                }
            
            # Ensure LISP files are loaded
            if not self._ensure_lisp_loaded(fixture_type):
                return {"success": False, "error": f"Failed to load LISP files for {fixture_type}"}
            
            # Route to fixture-specific method
            draw_methods = {
                "PG": self._draw_pg_fixture,
                "LS": self._draw_ls_fixture,
                "LSR": self._draw_lsr_fixture,
                "Rush": self._draw_rush_fixture,
                "Rush-Rec": self._draw_rush_rec_fixture,
                "Magneto": self._draw_magneto_fixture,
            }
            
            if fixture_type in draw_methods:
                return draw_methods[fixture_type](specs)
            else:
                return {"success": False, "error": f"No handler implemented for: {fixture_type}"}
                
        except Exception as e:
            logger.error(f"Error drawing {fixture_type} fixture: {e}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
    
    def get_supported_fixtures(self) -> List[str]:
        """Get list of supported fixture types."""
        return list(self.fixture_api_map.keys())
    
    def get_fixture_options(self, fixture_type: str) -> Dict:
        """Get valid options for a fixture type."""
        return self.fixture_configs.get(fixture_type, {})

    # =========================================================================
    # UTILITY FUNCTIONS
    # =========================================================================
    
    def _to_lisp_value(self, val, is_string: bool = False) -> str:
        """
        Convert Python value to LISP representation.
        
        Args:
            val: Value to convert
            is_string: Whether to wrap in quotes
            
        Returns:
            LISP-compatible string representation
        """
        if val is None:
            return 'nil'
        elif is_string:
            return f'"{val}"'
        elif isinstance(val, bool):
            return '1' if val else '0'
        else:
            return str(val)
    
    def _map_finish(self, finish_input: str) -> str:
        """Map various finish input formats to LISP-expected format."""
        if finish_input is None:
            return 'White'
        raw = str(finish_input).upper()
        return self.finish_map.get(raw, 'White')
    
    def _validate_required_fields(self, specs: Dict, required: List[str]) -> Optional[str]:
        """
        Validate that required fields are present in specs.
        
        Args:
            specs: Specifications dictionary
            required: List of required field names
            
        Returns:
            Error message if validation fails, None if valid
        """
        for field in required:
            if field not in specs:
                return f"Missing required field: {field}"
        return None

    # =========================================================================
    # PG FIXTURE DRAWING
    # =========================================================================
    
    def _draw_pg_fixture(self, specs: Dict) -> Dict:
        """
        Draw PG fixture using LISP API.
        
        Required specs:
            - series: "PG2", "PG4", "FLAWLESS.2", "FLAWLESS.4", "PF2", "PF4"
            - mounting: "F", "NT", "T", "T15", "MW"
            - output: "LOW", "MED", "HIGH", "LMFT", "WFT"
            - regress: 0, 1, 2, 3, 4
            - length_ft: Run length in feet
            
        Optional specs:
            - length_in: Additional inches (default: 0)
            - flush_ceiling: Boolean (default: False)
            - wall_to_wall: Boolean (default: False)
            - custom_output: Number for LMFT/WFT modes
            - finish: "WH", "BK", "SL", "CC" (default: "WH")
            - oa_option: "Exact" or "Nom" (default: "Exact")
            - breakdown: "EqualLength" or "MaxSection" (default: "EqualLength")
            - max_section: Max section length in feet
            - fixture_num: e.g., "F1" (default: "F1")
            - quantity: Number of fixtures (default: 1)
            - fixture_type: Description string
            - run_id: Run identifier string
            - start_x, start_y: Starting coordinates (default: 0, 0)
        """
        try:

            # Handle if specs is passed as JSON string
            if isinstance(specs, str):
                specs = json.loads(specs)

            # Validate required fields
            required = ['series', 'mounting', 'output', 'regress', 'length_ft']
            error = self._validate_required_fields(specs, required)
            if error:
                return {"success": False, "error": error}
            
            # Map specifications to LISP parameters
            params = self._map_pg_params(specs)
            
            # Build and execute LISP command
            lisp_cmd = self._build_pg_lisp_command(params)
            
            autocad, doc, modelspace = self._get_autocad_objects()
            logger.info(f"Executing PG LISP command")
            logger.debug(f"Command: {lisp_cmd}")
            
            doc.SendCommand(lisp_cmd)

            # Wait for command to complete
            self.wait_for_autocad(doc)

            
            return {
                "success": True,
                "message": "PG fixture drawn successfully",
                "fixture_type": "PG",
                "params": params,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to draw PG fixture: {e}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}
        

    def _wait_for_autocad(self, doc, timeout: int = 30):
        """Wait for AutoCAD to finish processing commands."""
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check if command is still active
                cmd_active = doc.GetVariable("CMDACTIVE")
                if cmd_active == 0:
                    # Command finished, wait a tiny bit more for safety
                    time.sleep(0.3)
                    return True
            except:
                # If we can't check, just wait
                pass
            time.sleep(0.2)
        
        logger.warning("AutoCAD command may not have completed within timeout")
        return False
        

    
    def _map_pg_params(self, specs: Dict) -> Dict:
        """Map input specs to PG LISP parameters."""
        breakdown = specs.get('breakdown', 'EqualLength')
        max_tog = 1 if breakdown == 'MaxSection' else 0
        
        return {
            'series': specs['series'],
            'mounting': specs['mounting'],
            'output': specs['output'],
            'regress': int(specs['regress']),
            'rft': float(specs['length_ft']),
            'rin': float(specs.get('length_in', 0)),
            'fc_tog': 1 if specs.get('flush_ceiling') else 0,
            'wtw_tog': 1 if specs.get('wall_to_wall') else 0,
            'dout_mod': specs.get('custom_output'),
            'finish': self._map_finish(specs.get('finish', 'White')),
            'ex_nom': specs.get('oa_option', 'Exact'),
            'breakdown': breakdown,
            'max_tog': max_tog,
            'max_section': specs.get('max_section'),
            'fix_num': specs.get('fixture_num', 'F1'),
            'fix_qty': int(specs.get('quantity', 1)),
            'fix_type': specs.get('fixture_type', ''),
            'run_ident': specs.get('run_id', ''),
            'start_x': float(specs.get('start_x', 0)),
            'start_y': float(specs.get('start_y', 0)),
        }
    
    def _build_pg_lisp_command(self, params: Dict) -> str:
        """Build LISP command string for PG fixture."""
        cmd = (
            f'(c:PGAutoAPI '
            f'"{params["series"]}" '
            f'"{params["mounting"]}" '
            f'"{params["output"]}" '
            f'{params["regress"]} '
            f'{params["rft"]} '
            f'{params["rin"]} '
            f'{params["fc_tog"]} '
            f'{params["wtw_tog"]} '
            f'{self._to_lisp_value(params["dout_mod"])} '
            f'"{params["finish"]}" '
            f'"{params["ex_nom"]}" '
            f'"{params["breakdown"]}" '
            f'{params["max_tog"]} '
            f'{self._to_lisp_value(params["max_section"])} '
            f'"{params["fix_num"]}" '
            f'{params["fix_qty"]} '
            f'{self._to_lisp_value(params["fix_type"], True)} '
            f'{self._to_lisp_value(params["run_ident"], True)} '
            f'{params["start_x"]} '
            f'{params["start_y"]}'
            f')\n'
        )

        print("=" * 70)
        print("LISP COMMAND BEING SENT:")
        print(cmd)
        print("=" * 70) 
    
        return cmd

    # =========================================================================
    # LS FIXTURE DRAWING (Template - implement when LISP is ready)
    # =========================================================================
    
    def _draw_ls_fixture(self, specs: Dict) -> Dict:
        """
        Draw LS fixture using LISP API.
        
        TODO: Implement when LS_AutoDraw.lsp API function is created.
        Required specs will include: series, mounting, output, config, length_ft, etc.
        """
        # Validate required fields
        required = ['series', 'mounting', 'output', 'config', 'length_ft']
        error = self._validate_required_fields(specs, required)
        if error:
            return {"success": False, "error": error}
        
        # TODO: Implement parameter mapping and LISP command building
        # Similar pattern to PG fixture
        
        return {
            "success": False,
            "error": "LS fixture API not yet implemented. "
                     "Please share LS_AutoDraw.lsp and its DCL file to implement."
        }

    # =========================================================================
    # LSR FIXTURE DRAWING (Template)
    # =========================================================================
    
    def _draw_lsr_fixture(self, specs: Dict) -> Dict:
        """
        Draw LSR (Linear Light with Reflector) fixture using LISP API.
        
        TODO: Implement when LSR_AutoDraw.lsp API function is created.
        """
        required = ['series', 'mounting', 'output', 'length_ft']
        error = self._validate_required_fields(specs, required)
        if error:
            return {"success": False, "error": error}
        
        return {
            "success": False,
            "error": "LSR fixture API not yet implemented. "
                     "Please share LSR_AutoDraw.lsp and its DCL file to implement."
        }

    # =========================================================================
    # RUSH FIXTURE DRAWING (Template)
    # =========================================================================
    
    def _draw_rush_fixture(self, specs: Dict) -> Dict:
        """
        Draw Rush fixture using LISP API.
        
        TODO: Implement when Rush_AutoDraw.lsp API function is created.
        """
        required = ['series', 'mounting', 'output', 'length_ft']
        error = self._validate_required_fields(specs, required)
        if error:
            return {"success": False, "error": error}
        
        return {
            "success": False,
            "error": "Rush fixture API not yet implemented. "
                     "Please share Rush_AutoDraw.lsp and its DCL file to implement."
        }
    
    def _draw_rush_rec_fixture(self, specs: Dict) -> Dict:
        """
        Draw Rush Recessed fixture using LISP API.
        
        TODO: Implement when Rush_AutoDraw.lsp API function is created.
        """
        required = ['series', 'mounting', 'output', 'length_ft']
        error = self._validate_required_fields(specs, required)
        if error:
            return {"success": False, "error": error}
        
        return {
            "success": False,
            "error": "Rush-Rec fixture API not yet implemented. "
                     "Please share Rush_AutoDraw.lsp and its DCL file to implement."
        }

    # =========================================================================
    # MAGNETO FIXTURE DRAWING (Template)
    # =========================================================================
    
    def _draw_magneto_fixture(self, specs: Dict) -> Dict:
        """
        Draw Magneto track fixture using LISP API.
        
        TODO: Implement when Magneto_AutoDraw.lsp API function is created.
        """
        required = ['series', 'mounting', 'output', 'length_ft']
        error = self._validate_required_fields(specs, required)
        if error:
            return {"success": False, "error": error}
        
        return {
            "success": False,
            "error": "Magneto fixture API not yet implemented. "
                     "Please share Magneto_AutoDraw.lsp and its DCL file to implement."
        }

    # =========================================================================
    # BATCH PROCESSING
    # =========================================================================
    
    def batch_draw_fixtures(self, fixture_list: List[Dict]) -> List[Dict]:
        """
        Process multiple fixture drawing requests.
        
        Args:
            fixture_list: List of dictionaries, each containing:
                         - fixture_type: Type of fixture
                         - specifications: Dict of fixture specs
        
        Returns:
            List of result dictionaries
        """
        results = []
        
        for i, item in enumerate(fixture_list):
            logger.info(f"Processing fixture {i+1}/{len(fixture_list)}")
            
            fixture_type = item.get('fixture_type')
            specs = item.get('specifications', {})
            
            if not fixture_type:
                results.append({
                    "success": False,
                    "error": "Missing fixture_type",
                    "index": i
                })
                continue
            
            result = self.draw_fixture(fixture_type, specs)
            result['index'] = i
            results.append(result)
            
            # Small delay between drawings to prevent AutoCAD overload
            import time
            time.sleep(0.5)
        
        # Summary
        successful = sum(1 for r in results if r.get('success'))
        logger.info(f"Batch complete: {successful}/{len(fixture_list)} successful")
        
        return results

    # =========================================================================
    # UTILITY COMMANDS
    # =========================================================================
    
    def save_drawing(self, filepath: str = None) -> Dict:
        """
        Save the current AutoCAD drawing.
        
        Args:
            filepath: Optional path to save as (if None, saves current file)
            
        Returns:
            Dictionary with success status
        """
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            
            if filepath:
                doc.SaveAs(filepath)
                logger.info(f"Drawing saved as: {filepath}")
            else:
                doc.Save()
                logger.info("Drawing saved")
            
            return {"success": True, "message": "Drawing saved"}
            
        except Exception as e:
            logger.error(f"Failed to save drawing: {e}")
            return {"success": False, "error": str(e)}
    
    def new_drawing(self) -> Dict:
        """
        Create a new AutoCAD drawing.
        
        Returns:
            Dictionary with success status
        """
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            
            new_doc = autocad.Documents.Add()
            self._thread_local.doc = new_doc
            self._thread_local.modelspace = new_doc.ModelSpace
            
            logger.info("New drawing created")
            return {"success": True, "message": "New drawing created"}
            
        except Exception as e:
            logger.error(f"Failed to create new drawing: {e}")
            return {"success": False, "error": str(e)}
    
    def zoom_extents(self) -> Dict:
        """Zoom to show all objects in the drawing."""
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            doc.SendCommand("_ZOOM _E ")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def purge_drawing(self) -> Dict:
        """Purge unused objects from the drawing."""
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            doc.SendCommand("_PURGE _ALL * _N ")
            logger.info("Drawing purged")
            return {"success": True, "message": "Drawing purged"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # CONNECTION MANAGEMENT
    # =========================================================================
    
    def close_connection(self):
        """Close AutoCAD connection."""
        try:
            self._cleanup_autocad_connection()
            logger.info("AutoCAD connection closed")
        except Exception as e:
            logger.error(f"Error closing AutoCAD connection: {e}")
    
    def reconnect(self) -> Dict:
        """Reconnect to AutoCAD."""
        try:
            self._cleanup_autocad_connection()
            self._loaded_lisp.clear()  # Clear loaded LISP tracking
            self._initialize_autocad_connection()
            return {"success": True, "message": "Reconnected to AutoCAD"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict:
        """Get current connection status."""
        try:
            autocad, doc, modelspace = self._get_autocad_objects()
            return {
                "connected": True,
                "autocad_name": autocad.Name,
                "document_name": doc.Name,
                "loaded_lisp_files": list(self._loaded_lisp),
                "supported_fixtures": self.get_supported_fixtures()
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e)
            }


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """Example usage of the AutoDraw AI Agent."""
    
    print("=" * 60)
    print("AutoDraw AI Agent - Test")
    print("=" * 60)
    
    try:
        # Initialize agent
        # Update this path to your LISP files location
        agent = AutoDrawAIAgent(
            lisp_base_path="C:/AutoCAD/LISP",
            initialize_autocad=True
        )
        
        # Check status
        status = agent.get_status()
        print(f"\nStatus: {json.dumps(status, indent=2)}")
        
        # Example: Draw a PG fixture
        pg_specs = {
            "series": "PG4",
            "mounting": "NT",
            "output": "HIGH",
            "regress": 2,
            "length_ft": 12,
            "length_in": 6,
            "flush_ceiling": True,
            "wall_to_wall": False,
            "finish": "WH",
            "oa_option": "Exact",
            "breakdown": "EqualLength",
            "fixture_num": "F1",
            "quantity": 2,
            "fixture_type": "Linear Pendant",
            "run_id": "R1",
            "start_x": 0,
            "start_y": 0
        }
        
        print("\nDrawing PG fixture...")
        result = agent.draw_fixture("PG", pg_specs)
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Zoom to see result
        agent.zoom_extents()
        
        # Close connection
        agent.close_connection()
        print("\nTest complete!")
        
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()