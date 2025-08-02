#!/usr/bin/env python3
"""
Test script for AutoDraw CLI
Demonstrates CLI functionality and validates argument parsing
"""

import sys
import json
import tempfile
import os
from cli_autodraw import AutoDrawCLI

def test_argument_parsing():
    """Test command line argument parsing"""
    print("Testing argument parsing...")
    
    # Test 1: Natural language input
    sys.argv = ['cli_autodraw.py', '--natural', 'Draw a 10-foot linear light']
    cli = AutoDrawCLI()
    args = cli.parse_arguments()
    assert args.natural == 'Draw a 10-foot linear light'
    print("✅ Natural language argument parsing: PASS")
    
    # Test 2: Parameter-based specification
    sys.argv = [
        'cli_autodraw.py',
        '--system', 'linear_light',
        '--length', '10',
        '--width', '4',
        '--wattage', '50',
        '--color-temp', '4000k'
    ]
    cli = AutoDrawCLI()
    args = cli.parse_arguments()
    assert args.system == 'linear_light'
    assert args.length == 10.0
    assert args.width == 4.0
    assert args.wattage == 50
    assert args.color_temp == '4000k'
    print("✅ Parameter-based argument parsing: PASS")
    
    # Test 3: Batch file input
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Draw a linear light\nCreate a rush light\n")
        batch_file = f.name
    
    sys.argv = ['cli_autodraw.py', '--batch-file', batch_file]
    cli = AutoDrawCLI()
    args = cli.parse_arguments()
    assert args.batch_file == batch_file
    print("✅ Batch file argument parsing: PASS")
    
    # Cleanup
    os.unlink(batch_file)

def test_specification_building():
    """Test specification building from arguments"""
    print("\nTesting specification building...")
    
    # Test 1: Basic specification
    sys.argv = [
        'cli_autodraw.py',
        '--system', 'linear_light',
        '--length', '10',
        '--wattage', '50'
    ]
    cli = AutoDrawCLI()
    args = cli.parse_arguments()
    specs = cli.build_specifications(args)
    
    assert specs['command'] == 'linear_light'
    assert specs['lighting_system'] == 'linear_light'
    assert specs['dimensions']['length'] == 10.0
    assert specs['specifications']['wattage'] == 50
    print("✅ Basic specification building: PASS")
    
    # Test 2: Complex specification with position
    sys.argv = [
        'cli_autodraw.py',
        '--system', 'rush_light',
        '--length', '8',
        '--width', '6',
        '--start', '5,5',
        '--end', '13,5',
        '--wattage', '75',
        '--mounting', 'ceiling_mount',
        '--emergency-backup',
        '--dimmable'
    ]
    cli = AutoDrawCLI()
    args = cli.parse_arguments()
    specs = cli.build_specifications(args)
    
    assert specs['command'] == 'rush_light'
    assert specs['position']['start_point'] == [5.0, 5.0, 0]
    assert specs['position']['end_point'] == [13.0, 5.0, 0]
    assert specs['specifications']['mounting_type'] == 'ceiling_mount'
    assert specs['additional_parameters']['emergency_backup'] == 'true'
    assert specs['additional_parameters']['dimmable'] == 'true'
    print("✅ Complex specification building: PASS")

def test_validation():
    """Test specification validation"""
    print("\nTesting specification validation...")
    
    cli = AutoDrawCLI()
    
    # Test 1: Valid specification
    valid_specs = {
        'command': 'linear_light',
        'lighting_system': 'linear_light',
        'dimensions': {'length': 10.0}
    }
    assert cli.validate_specifications(valid_specs) == True
    print("✅ Valid specification validation: PASS")
    
    # Test 2: Invalid command
    invalid_specs = {
        'command': 'invalid_command',
        'lighting_system': 'linear_light'
    }
    assert cli.validate_specifications(invalid_specs) == False
    print("✅ Invalid command validation: PASS")
    
    # Test 3: Missing command
    missing_specs = {
        'lighting_system': 'linear_light'
    }
    assert cli.validate_specifications(missing_specs) == False
    print("✅ Missing command validation: PASS")

def test_batch_file_processing():
    """Test batch file processing"""
    print("\nTesting batch file processing...")
    
    # Create temporary batch file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("""Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature
Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens
Design a magneto track system 12 feet long with 75W fixtures every 2 feet""")
        batch_file = f.name
    
    cli = AutoDrawCLI()
    
    # Test batch file loading
    requests = cli.process_batch_file(batch_file)
    assert len(requests) == 3
    print("✅ Batch file processing: PASS")
    
    # Cleanup
    os.unlink(batch_file)

def test_specification_display():
    """Test specification display functionality"""
    print("\nTesting specification display...")
    
    specs = {
        'command': 'linear_light',
        'lighting_system': 'linear_light',
        'dimensions': {
            'length': 10.0,
            'width': 4.0,
            'height': 4.0
        },
        'position': {
            'start_point': [5.0, 5.0, 0],
            'end_point': [15.0, 5.0, 0],
            'orientation': 'horizontal'
        },
        'specifications': {
            'wattage': 50,
            'color_temperature': '4000k',
            'lens_type': 'clear',
            'mounting_type': 'ceiling_mount',
            'quantity': 1
        },
        'additional_parameters': {
            'emergency_backup': 'true',
            'dimmable': 'true',
            'voltage': 120
        }
    }
    
    cli = AutoDrawCLI()
    cli.print_specifications(specs)
    print("✅ Specification display: PASS")

def run_all_tests():
    """Run all tests"""
    print("AutoDraw CLI Test Suite")
    print("=" * 50)
    
    try:
        test_argument_parsing()
        test_specification_building()
        test_validation()
        test_batch_file_processing()
        test_specification_display()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests() 