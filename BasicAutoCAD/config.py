"""
Configuration settings for AutoDraw AI Agent
"""

import os
from typing import Dict, List

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "gpt-4.1-mini"
OPENAI_TEMPERATURE = 0.1
OPENAI_MAX_TOKENS = 1000

# AutoCAD Configuration
AUTOCAD_TIMEOUT = 30  # seconds
AUTOCAD_COMMAND_DELAY = 0.1  # seconds

# Drawing Units
DEFAULT_UNITS = {
    "length": "feet",
    "width": "inches", 
    "height": "inches",
    "power": "watts",
    "temperature": "kelvin",
    "voltage": "volts"
}

# Command Mapping
COMMAND_MAP = {
    # Original lighting system commands
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
    "purge_all": "_PALL",
    
    # New complex drawing commands
    "rectangle": "rectangle",
    "circle": "circle",
    "polyline": "polyline",
    "arc": "arc",
    "ellipse": "ellipse",
    "text": "text",
    "dimension": "dimension",
    "hatch": "hatch",
    "block": "block",
    "array": "array",
    "mirror": "mirror",
    "rotate": "rotate",
    "scale": "scale",
    "offset": "offset",
    "trim": "trim",
    "extend": "extend",
    "fillet": "fillet",
    "chamfer": "chamfer"
}

# Lighting Systems
LIGHTING_SYSTEMS = {
    "ls": {
        "name": "Linear Light",
        "command": "linear_light",
        "description": "Standard linear lighting system",
        "default_wattage": 50,
        "default_length": 4,
        "default_width": 4
    },
    "lsr": {
        "name": "Linear Light with Reflector", 
        "command": "linear_light_reflector",
        "description": "Linear lighting with reflector for enhanced output",
        "default_wattage": 60,
        "default_length": 4,
        "default_width": 4
    },
    "rush": {
        "name": "Rush Light",
        "command": "rush_light", 
        "description": "High-output rush lighting system",
        "default_wattage": 75,
        "default_length": 4,
        "default_width": 6
    },
    "rush_rec": {
        "name": "Rush Recessed",
        "command": "rush_recessed",
        "description": "Recessed rush lighting system",
        "default_wattage": 75,
        "default_length": 4,
        "default_width": 6
    },
    "pg": {
        "name": "PG Light",
        "command": "pg_light",
        "description": "PG series lighting system",
        "default_wattage": 40,
        "default_length": 4,
        "default_width": 4
    },
    "magneto": {
        "name": "Magneto Track",
        "command": "magneto_track",
        "description": "Track-mounted magneto lighting system",
        "default_wattage": 50,
        "default_length": 4,
        "default_width": 4
    }
}

# Mounting Options
MOUNTING_OPTIONS = [
    "wall_mount",
    "ceiling_mount", 
    "suspension",
    "track_mount",
    "recessed",
    "surface_mount",
    "pendant"
]

# Lens Options
LENS_OPTIONS = [
    "clear",
    "frosted",
    "prismatic", 
    "louvered",
    "reflector",
    "diffuser",
    "lens_cover"
]

# Color Temperature Options
COLOR_TEMPERATURES = [
    "2700k",
    "3000k", 
    "3500k",
    "4000k",
    "5000k",
    "6500k"
]

# Default Specifications
DEFAULT_SPECIFICATIONS = {
    "wattage": 50,
    "color_temperature": "4000k",
    "lens_type": "clear",
    "mounting_type": "ceiling_mount",
    "quantity": 1,
    "spacing": 4,
    "voltage": 120,
    "emergency_backup": False,
    "dimmable": False,
    "ip_rating": "20"
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "autodraw_ai.log"
}

# Error Messages
ERROR_MESSAGES = {
    "no_autocad": "AutoCAD is not running or not accessible",
    "invalid_command": "Invalid command specified",
    "parsing_error": "Error parsing natural language input",
    "execution_error": "Error executing AutoCAD command",
    "timeout": "Command execution timed out",
    "no_api_key": "OpenAI API key is required"
}

# Success Messages
SUCCESS_MESSAGES = {
    "drawing_created": "Drawing created successfully",
    "command_executed": "Command executed successfully",
    "batch_completed": "Batch processing completed"
} 