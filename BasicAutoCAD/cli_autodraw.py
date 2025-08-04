#!/usr/bin/env python3
"""
Command Line Interface for AutoDraw AI Agent
Takes drawing details as command-line arguments and generates AutoCAD diagrams
"""

import argparse
import sys
import json
import os
from typing import Dict, List
import logging

from autodraw_ai_agent import AutoDrawAIAgent
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDrawCLI:
    """
    Command Line Interface for AutoDraw AI Agent
    """
    
    def __init__(self):
        self.agent = None
        
    def parse_arguments(self) -> argparse.Namespace:
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description="AutoDraw AI Agent - Generate AutoCAD diagrams from command line",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Create a linear light
  python cli_autodraw.py --system linear_light --length 10 --width 4 --wattage 50 --color-temp 4000k --start 5,5 --end 15,5
  
  # Create a rush light with specifications
  python cli_autodraw.py --system rush_light --length 8 --width 6 --wattage 75 --mounting ceiling --lens frosted
  
  # Create a rectangle
  python cli_autodraw.py --command rectangle --start 0,0 --end 10,8
  
  # Create a circle
  python cli_autodraw.py --command circle --center 5,5 --radius 3
  
  # Create a polyline
  python cli_autodraw.py --command polyline --points "0,0;5,5;10,0;15,5" --closed
  
  # Create an arc
  python cli_autodraw.py --command arc --center 5,5 --radius 4 --start-angle 0 --end-angle 90
  
  # Add text
  python cli_autodraw.py --command text --insertion-point 2,2 --text-content "Sample Text" --text-height 0.25
  
  # Create a rectangular array
  python cli_autodraw.py --command array --array-type rectangular --rows 3 --columns 4 --row-spacing 2 --column-spacing 2
  
  # Create from natural language description
  python cli_autodraw.py --natural "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
  
  # Batch process from file
  python cli_autodraw.py --batch-file requests.txt
            """
        )
        
        # Input method group
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument(
            '--natural', '-n',
            type=str,
            help='Natural language description of the drawing'
        )
        input_group.add_argument(
            '--batch-file', '-b',
            type=str,
            help='File containing multiple drawing requests (one per line)'
        )
        
        # System specification group
        system_group = parser.add_argument_group('System Specifications')
        system_group.add_argument(
            '--system', '-s',
            choices=list(config.LIGHTING_SYSTEMS.keys()),
            help='Lighting system type'
        )
        system_group.add_argument(
            '--command', '-c',
            choices=list(config.COMMAND_MAP.keys()),
            help='Specific AutoCAD command to execute (rectangle, circle, polyline, arc, ellipse, text, dimension, hatch, block, array, mirror, rotate, scale, offset, trim, extend, fillet, chamfer)'
        )
        
        # Dimensions group
        dim_group = parser.add_argument_group('Dimensions')
        dim_group.add_argument(
            '--length', '-l',
            type=float,
            help='Length in feet'
        )
        dim_group.add_argument(
            '--width', '-w',
            type=float,
            help='Width in inches'
        )
        dim_group.add_argument(
            '--height', '-ht',
            type=float,
            help='Height in inches'
        )
        
        # Position group
        pos_group = parser.add_argument_group('Position')
        pos_group.add_argument(
            '--start',
            type=str,
            help='Start point as "x,y" coordinates'
        )
        pos_group.add_argument(
            '--end',
            type=str,
            help='End point as "x,y" coordinates'
        )
        pos_group.add_argument(
            '--center',
            type=str,
            help='Center point as "x,y" coordinates (for circles, arcs, ellipses)'
        )
        pos_group.add_argument(
            '--insertion-point',
            type=str,
            help='Insertion point as "x,y" coordinates (for text, blocks)'
        )
        pos_group.add_argument(
            '--points',
            type=str,
            help='Multiple points as "x1,y1;x2,y2;x3,y3" (for polylines)'
        )
        pos_group.add_argument(
            '--orientation',
            choices=['horizontal', 'vertical', 'angled'],
            default='horizontal',
            help='Orientation of the fixture'
        )
        
        # Specifications group
        spec_group = parser.add_argument_group('Specifications')
        spec_group.add_argument(
            '--wattage',
            type=int,
            help='Power in watts'
        )
        spec_group.add_argument(
            '--color-temp', '--ct',
            choices=config.COLOR_TEMPERATURES,
            help='Color temperature'
        )
        spec_group.add_argument(
            '--lens',
            choices=config.LENS_OPTIONS,
            help='Lens type'
        )
        spec_group.add_argument(
            '--mounting',
            choices=config.MOUNTING_OPTIONS,
            help='Mounting type'
        )
        spec_group.add_argument(
            '--driver',
            type=str,
            help='Driver specification'
        )
        spec_group.add_argument(
            '--quantity',
            type=int,
            default=1,
            help='Number of units'
        )
        
        # Additional parameters group
        add_group = parser.add_argument_group('Additional Parameters')
        add_group.add_argument(
            '--spacing',
            type=float,
            help='Distance between units in feet'
        )
        add_group.add_argument(
            '--voltage',
            type=int,
            help='Voltage requirement'
        )
        add_group.add_argument(
            '--emergency-backup',
            action='store_true',
            help='Include emergency backup'
        )
        add_group.add_argument(
            '--dimmable',
            action='store_true',
            help='Make fixture dimmable'
        )
        add_group.add_argument(
            '--ip-rating',
            type=str,
            help='Ingress protection rating'
        )
        # New parameters for complex drawings
        add_group.add_argument(
            '--radius',
            type=float,
            help='Radius for circles and arcs'
        )
        add_group.add_argument(
            '--major-axis',
            type=float,
            help='Major axis length for ellipses'
        )
        add_group.add_argument(
            '--minor-axis',
            type=float,
            help='Minor axis length for ellipses'
        )
        add_group.add_argument(
            '--start-angle',
            type=float,
            help='Start angle in degrees for arcs'
        )
        add_group.add_argument(
            '--end-angle',
            type=float,
            help='End angle in degrees for arcs'
        )
        add_group.add_argument(
            '--closed',
            action='store_true',
            help='Close polyline (for polylines)'
        )
        add_group.add_argument(
            '--text-content',
            type=str,
            help='Text content to display'
        )
        add_group.add_argument(
            '--text-height',
            type=float,
            help='Text height'
        )
        add_group.add_argument(
            '--block-name',
            type=str,
            help='Name of block to insert'
        )
        add_group.add_argument(
            '--pattern-name',
            type=str,
            help='Hatch pattern name'
        )
        add_group.add_argument(
            '--array-type',
            choices=['rectangular', 'polar'],
            help='Type of array to create'
        )
        add_group.add_argument(
            '--rows',
            type=int,
            help='Number of rows for rectangular array'
        )
        add_group.add_argument(
            '--columns',
            type=int,
            help='Number of columns for rectangular array'
        )
        add_group.add_argument(
            '--row-spacing',
            type=float,
            help='Spacing between rows'
        )
        add_group.add_argument(
            '--column-spacing',
            type=float,
            help='Spacing between columns'
        )
        add_group.add_argument(
            '--num-items',
            type=int,
            help='Number of items for polar array'
        )
        add_group.add_argument(
            '--scale-factor',
            type=float,
            help='Scale factor for scaling operations'
        )
        add_group.add_argument(
            '--rotation',
            type=float,
            help='Rotation angle in degrees'
        )
        add_group.add_argument(
            '--offset-distance',
            type=float,
            help='Offset distance'
        )
        add_group.add_argument(
            '--fillet-radius',
            type=float,
            help='Fillet radius'
        )
        add_group.add_argument(
            '--chamfer-distance1',
            type=float,
            help='First chamfer distance'
        )
        add_group.add_argument(
            '--chamfer-distance2',
            type=float,
            help='Second chamfer distance'
        )
        
        # Output options
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file for results (JSON format)'
        )
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Verbose output'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse and validate without executing AutoCAD commands'
        )
        
        return parser.parse_args()
    
    def build_specifications(self, args: argparse.Namespace) -> Dict:
        """Build specifications dictionary from command line arguments"""
        specs = {}
        
        # Command
        if args.command:
            specs['command'] = args.command
        elif args.system:
            specs['command'] = config.LIGHTING_SYSTEMS[args.system]['command']
        else:
            specs['command'] = 'linear_light'  # Default
        
        # Lighting system
        if args.system:
            specs['lighting_system'] = args.system
        
        # Dimensions
        if any([args.length, args.width, args.height, args.radius, args.major_axis, args.minor_axis]):
            specs['dimensions'] = {}
            if args.length:
                specs['dimensions']['length'] = args.length
            if args.width:
                specs['dimensions']['width'] = args.width
            if args.height:
                specs['dimensions']['height'] = args.height
            if args.radius:
                specs['dimensions']['radius'] = args.radius
            if args.major_axis:
                specs['dimensions']['major_axis'] = args.major_axis
            if args.minor_axis:
                specs['dimensions']['minor_axis'] = args.minor_axis
        
        # Position
        if any([args.start, args.end, args.center, args.insertion_point, args.points, args.orientation]):
            specs['position'] = {}
            if args.start:
                try:
                    x, y = map(float, args.start.split(','))
                    specs['position']['start_point'] = [x, y, 0]
                except ValueError:
                    logger.error("Invalid start point format. Use 'x,y'")
                    return None
            if args.end:
                try:
                    x, y = map(float, args.end.split(','))
                    specs['position']['end_point'] = [x, y, 0]
                except ValueError:
                    logger.error("Invalid end point format. Use 'x,y'")
                    return None
            if args.center:
                try:
                    x, y = map(float, args.center.split(','))
                    specs['position']['center_point'] = [x, y, 0]
                except ValueError:
                    logger.error("Invalid center point format. Use 'x,y'")
                    return None
            if args.insertion_point:
                try:
                    x, y = map(float, args.insertion_point.split(','))
                    specs['position']['insertion_point'] = [x, y, 0]
                except ValueError:
                    logger.error("Invalid insertion point format. Use 'x,y'")
                    return None
            if args.points:
                try:
                    points = []
                    for point_str in args.points.split(';'):
                        x, y = map(float, point_str.split(','))
                        points.append([x, y, 0])
                    specs['position']['points'] = points
                except ValueError:
                    logger.error("Invalid points format. Use 'x1,y1;x2,y2;x3,y3'")
                    return None
            specs['position']['orientation'] = args.orientation
        
        # Specifications
        if any([args.wattage, args.color_temp, args.lens, args.mounting, args.driver, args.quantity, 
                args.text_content, args.text_height, args.block_name, args.pattern_name]):
            specs['specifications'] = {}
            if args.wattage:
                specs['specifications']['wattage'] = args.wattage
            if args.color_temp:
                specs['specifications']['color_temperature'] = args.color_temp
            if args.lens:
                specs['specifications']['lens_type'] = args.lens
            if args.mounting:
                specs['specifications']['mounting_type'] = args.mounting
            if args.driver:
                specs['specifications']['driver_type'] = args.driver
            if args.text_content:
                specs['specifications']['text_content'] = args.text_content
            if args.text_height:
                specs['specifications']['text_height'] = args.text_height
            if args.block_name:
                specs['specifications']['block_name'] = args.block_name
            if args.pattern_name:
                specs['specifications']['pattern_name'] = args.pattern_name
            specs['specifications']['quantity'] = args.quantity
        
        # Additional parameters
        if any([args.spacing, args.voltage, args.emergency_backup, args.dimmable, args.ip_rating,
                args.start_angle, args.end_angle, args.closed, args.array_type, args.rows, args.columns,
                args.row_spacing, args.column_spacing, args.num_items, args.scale_factor, args.rotation,
                args.offset_distance, args.fillet_radius, args.chamfer_distance1, args.chamfer_distance2]):
            specs['additional_parameters'] = {}
            if args.spacing:
                specs['additional_parameters']['spacing'] = args.spacing
            if args.voltage:
                specs['additional_parameters']['voltage'] = args.voltage
            if args.emergency_backup:
                specs['additional_parameters']['emergency_backup'] = 'true'
            if args.dimmable:
                specs['additional_parameters']['dimmable'] = 'true'
            if args.ip_rating:
                specs['additional_parameters']['ip_rating'] = args.ip_rating
            if args.start_angle:
                specs['additional_parameters']['start_angle'] = args.start_angle
            if args.end_angle:
                specs['additional_parameters']['end_angle'] = args.end_angle
            if args.closed:
                specs['additional_parameters']['closed'] = 'true'
            if args.array_type:
                specs['additional_parameters']['array_type'] = args.array_type
            if args.rows:
                specs['additional_parameters']['rows'] = args.rows
            if args.columns:
                specs['additional_parameters']['columns'] = args.columns
            if args.row_spacing:
                specs['additional_parameters']['row_spacing'] = args.row_spacing
            if args.column_spacing:
                specs['additional_parameters']['column_spacing'] = args.column_spacing
            if args.num_items:
                specs['additional_parameters']['num_items'] = args.num_items
            if args.scale_factor:
                specs['additional_parameters']['scale_factor'] = args.scale_factor
            if args.rotation:
                specs['additional_parameters']['rotation'] = args.rotation
            if args.offset_distance:
                specs['additional_parameters']['offset_distance'] = args.offset_distance
            if args.fillet_radius:
                specs['additional_parameters']['fillet_radius'] = args.fillet_radius
            if args.chamfer_distance1:
                specs['additional_parameters']['chamfer_distance1'] = args.chamfer_distance1
            if args.chamfer_distance2:
                specs['additional_parameters']['chamfer_distance2'] = args.chamfer_distance2
        
        return specs
    
    def validate_specifications(self, specs: Dict) -> bool:
        """Validate specifications"""
        if not specs:
            logger.error("No specifications provided")
            return False
        
        if 'command' not in specs:
            logger.error("No command specified")
            return False
        
        if specs['command'] not in config.COMMAND_MAP:
            logger.error(f"Invalid command: {specs['command']}")
            return False
        
        return True
    
    def print_specifications(self, specs: Dict):
        """Print specifications in a readable format"""
        print("\n" + "="*50)
        print("DRAWING SPECIFICATIONS")
        print("="*50)
        
        if 'command' in specs:
            print(f"Command: {specs['command']}")
        
        if 'lighting_system' in specs:
            system_info = config.LIGHTING_SYSTEMS.get(specs['lighting_system'], {})
            print(f"Lighting System: {system_info.get('name', specs['lighting_system'])}")
        
        if 'dimensions' in specs:
            print("\nDimensions:")
            dims = specs['dimensions']
            if 'length' in dims:
                print(f"  Length: {dims['length']} feet")
            if 'width' in dims:
                print(f"  Width: {dims['width']} inches")
            if 'height' in dims:
                print(f"  Height: {dims['height']} inches")
            if 'radius' in dims:
                print(f"  Radius: {dims['radius']} units")
            if 'major_axis' in dims:
                print(f"  Major Axis: {dims['major_axis']} units")
            if 'minor_axis' in dims:
                print(f"  Minor Axis: {dims['minor_axis']} units")
        
        if 'position' in specs:
            print("\nPosition:")
            pos = specs['position']
            if 'start_point' in pos:
                print(f"  Start: {pos['start_point']}")
            if 'end_point' in pos:
                print(f"  End: {pos['end_point']}")
            if 'center_point' in pos:
                print(f"  Center: {pos['center_point']}")
            if 'insertion_point' in pos:
                print(f"  Insertion Point: {pos['insertion_point']}")
            if 'points' in pos:
                print(f"  Points: {pos['points']}")
            if 'orientation' in pos:
                print(f"  Orientation: {pos['orientation']}")
        
        if 'specifications' in specs:
            print("\nSpecifications:")
            specs_data = specs['specifications']
            if 'wattage' in specs_data:
                print(f"  Wattage: {specs_data['wattage']}W")
            if 'color_temperature' in specs_data:
                print(f"  Color Temperature: {specs_data['color_temperature']}")
            if 'lens_type' in specs_data:
                print(f"  Lens: {specs_data['lens_type']}")
            if 'mounting_type' in specs_data:
                print(f"  Mounting: {specs_data['mounting_type']}")
            if 'text_content' in specs_data:
                print(f"  Text Content: {specs_data['text_content']}")
            if 'text_height' in specs_data:
                print(f"  Text Height: {specs_data['text_height']}")
            if 'block_name' in specs_data:
                print(f"  Block Name: {specs_data['block_name']}")
            if 'pattern_name' in specs_data:
                print(f"  Pattern Name: {specs_data['pattern_name']}")
            if 'quantity' in specs_data:
                print(f"  Quantity: {specs_data['quantity']}")
        
        if 'additional_parameters' in specs:
            print("\nAdditional Parameters:")
            add_params = specs['additional_parameters']
            for key, value in add_params.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        print("="*50 + "\n")
    
    def process_natural_language(self, natural_input: str, dry_run: bool = False) -> Dict:
        """Process natural language input using the AI agent"""
        try:
            if not self.agent:
                # Don't initialize AutoCAD for dry runs
                self.agent = AutoDrawAIAgent(initialize_autocad=not dry_run)
            
            return self.agent.process_natural_language_request(natural_input)
        except Exception as e:
            logger.error(f"Error processing natural language: {e}")
            return None
    
    def execute_drawing(self, specs: Dict, dry_run: bool = False) -> Dict:
        """Execute the drawing command"""
        try:
            if not self.agent:
                # Don't initialize AutoCAD for dry runs
                self.agent = AutoDrawAIAgent(initialize_autocad=not dry_run)
            
            return self.agent.create_complete_drawing(specs)
        except Exception as e:
            logger.error(f"Error executing drawing: {e}")
            return {"success": False, "error": str(e)}
    
    def process_batch_file(self, file_path: str) -> List[Dict]:
        """Process a batch file with multiple requests"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            requests = [line.strip() for line in lines if line.strip()]
            logger.info(f"Loaded {len(requests)} requests from {file_path}")
            
            results = []
            for i, request in enumerate(requests, 1):
                logger.info(f"Processing request {i}/{len(requests)}: {request}")
                result = self.process_natural_language(request)
                if result:
                    results.append(result)
                else:
                    results.append({"success": False, "error": "Failed to parse request"})
            
            return results
        except Exception as e:
            logger.error(f"Error processing batch file: {e}")
            return []
    
    def save_results(self, results: Dict, output_file: str):
        """Save results to output file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def run(self):
        """Main execution method"""
        try:
            # Parse arguments
            args = self.parse_arguments()
            
            # Set logging level
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            
            print("AutoDraw AI Agent - Command Line Interface")
            print("="*50)
            
            # Test AutoCAD connection if not in dry-run mode
            if not args.dry_run:
                logger.info("Testing AutoCAD connection...")
                try:
                    import win32com.client
                    import pythoncom
                    
                    pythoncom.CoInitialize()
                    try:
                        autocad = win32com.client.GetActiveObject("AutoCAD.Application")
                        logger.info(f"✅ AutoCAD connection verified: {autocad.Name}")
                    except Exception as e:
                        logger.error(f"❌ AutoCAD not accessible: {e}")
                        print("Please ensure AutoCAD is running before using this tool.")
                        print("You can test the connection with: python test_autocad_connection.py")
                        sys.exit(1)
                    finally:
                        pythoncom.CoUninitialize()
                except ImportError:
                    logger.error("pywin32 not installed. Please install it with: pip install pywin32")
                    sys.exit(1)
            
            # Process based on input method
            if args.natural:
                # Natural language processing
                logger.info("Processing natural language request")
                specs = self.process_natural_language(args.natural, dry_run=args.dry_run)
                if not specs:
                    logger.error("Failed to parse natural language request")
                    print("❌ Could not parse the natural language request.")
                    print("Please try a different description or use parameter-based specification.")
                    sys.exit(1)
                
                if args.verbose:
                    self.print_specifications(specs)
                
                if args.dry_run:
                    print("✅ Dry run completed - specifications parsed successfully")
                    return
                
                # Execute drawing
                result = self.execute_drawing(specs, dry_run=args.dry_run)
                
            elif args.batch_file:
                # Batch processing
                logger.info("Processing batch file")
                results = self.process_batch_file(args.batch_file)
                
                if args.dry_run:
                    print(f"✅ Dry run completed - {len(results)} requests parsed")
                    return
                
                # Execute all drawings
                execution_results = []
                for i, specs in enumerate(results, 1):
                    logger.info(f"Executing drawing {i}/{len(results)}")
                    result = self.execute_drawing(specs, dry_run=args.dry_run)
                    execution_results.append(result)
                
                result = {
                    "success": any(r.get("success") for r in execution_results),
                    "batch_results": execution_results,
                    "total_requests": len(results),
                    "successful": sum(1 for r in execution_results if r.get("success"))
                }
            
            else:
                # Parameter-based specification
                logger.info("Building specifications from parameters")
                specs = self.build_specifications(args)
                if not specs:
                    logger.error("Failed to build specifications")
                    sys.exit(1)
                
                if not self.validate_specifications(specs):
                    logger.error("Invalid specifications")
                    sys.exit(1)
                
                if args.verbose:
                    self.print_specifications(specs)
                
                if args.dry_run:
                    print("✅ Dry run completed - specifications validated successfully")
                    return
                
                # Execute drawing
                result = self.execute_drawing(specs, dry_run=args.dry_run)
            
            # Handle results
            if result.get("success"):
                print("✅ Drawing created successfully!")
                if args.verbose and 'summary' in result:
                    print(f"Summary: {result['summary']}")
            else:
                print("❌ Drawing creation failed!")
                print(f"Error: {result.get('error', 'Unknown error')}")
                sys.exit(1)
            
            # Save results if requested
            if args.output:
                self.save_results(result, args.output)
            
            print("🎉 Process completed successfully!")
            
        except KeyboardInterrupt:
            print("\n⚠️  Process interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            sys.exit(1)
        finally:
            # Cleanup
            if self.agent:
                try:
                    self.agent.close_connection()
                except Exception as e:
                    logger.error(f"Error during cleanup: {e}")


def main():
    """Main entry point"""
    cli = AutoDrawCLI()
    cli.run()


if __name__ == "__main__":
    main() 