#!/usr/bin/env python3
"""
Test script for complex drawing capabilities of AutoDraw AI Agent
"""

import sys
import os
import subprocess

def test_complex_drawings():
    """Test various complex drawing commands"""
    
    print("Testing Complex Drawing Capabilities")
    print("=" * 50)
    
    # Test cases for different drawing commands
    test_cases = [
        {
            "name": "Rectangle",
            "command": [
                "python", "cli_autodraw.py",
                "--command", "rectangle",
                "--start", "0,0",
                "--end", "10,8",
                "--dry-run"
            ]
        },
        {
            "name": "Circle",
            "command": [
                "python", "cli_autodraw.py",
                "--command", "circle",
                "--center", "5,5",
                "--radius", "3",
                "--dry-run"
            ]
        },
        {
            "name": "Polyline",
            "command": [
                "python", "cli_autodraw.py",
                "--command", "polyline",
                "--points", "0,0;5,5;10,0;15,5",
                "--closed",
                "--dry-run"
            ]
        },
        {
            "name": "Arc",
            "command": [
                "python", "cli_autodraw.py",
                "--command", "arc",
                "--center", "5,5",
                "--radius", "4",
                "--start-angle", "0",
                "--end-angle", "90",
                "--dry-run"
            ]
        },
        {
            "name": "Text",
            "command": [
                "python", "cli_autodraw.py",
                "--command", "text",
                "--insertion-point", "2,2",
                "--text-content", "Sample Text",
                "--text-height", "0.25",
                "--dry-run"
            ]
        },
        {
            "name": "Ellipse",
            "command": [
                "python", "cli_autodraw.py",
                "--command", "ellipse",
                "--center", "5,5",
                "--major-axis", "6",
                "--minor-axis", "3",
                "--dry-run"
            ]
        },
        {
            "name": "Natural Language - Rectangle",
            "command": [
                "python", "cli_autodraw.py",
                "--natural", "Draw a rectangle from point 0,0 to 10,8",
                "--dry-run"
            ]
        },
        {
            "name": "Natural Language - Circle",
            "command": [
                "python", "cli_autodraw.py",
                "--natural", "Create a circle with center at 5,5 and radius 3",
                "--dry-run"
            ]
        },
        {
            "name": "Natural Language - Complex Shape",
            "command": [
                "python", "cli_autodraw.py",
                "--natural", "Draw a polyline through points 0,0; 5,5; 10,0; 15,5 and close it",
                "--dry-run"
            ]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print("-" * 30)
        
        try:
            result = subprocess.run(
                test_case['command'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            if result.returncode == 0:
                print("PASSED")
                print(f"Output: {result.stdout.strip()}")
                results.append({"name": test_case['name'], "status": "PASSED"})
            else:
                print("FAILED")
                print(f"Error: {result.stderr.strip()}")
                results.append({"name": test_case['name'], "status": "FAILED", "error": result.stderr.strip()})
                
        except Exception as e:
            print(f"ERROR: {e}")
            results.append({"name": test_case['name'], "status": "ERROR", "error": str(e)})
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    
    if failed > 0 or errors > 0:
        print("\nFailed Tests:")
        for result in results:
            if result['status'] != 'PASSED':
                print(f"  - {result['name']}: {result['status']}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
    
    return passed == len(results)

def test_help():
    """Test that help shows new commands"""
    print("\nTesting Help Documentation")
    print("=" * 30)
    
    try:
        result = subprocess.run(
            ["python", "cli_autodraw.py", "--help"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            help_text = result.stdout
            new_commands = ["rectangle", "circle", "polyline", "arc", "ellipse", "text", "array"]
            
            print("Checking for new commands in help:")
            for cmd in new_commands:
                if cmd in help_text:
                    print(f"  {cmd} found in help")
                else:
                    print(f"  {cmd} not found in help")
        else:
            print(f"Help command failed: {result.stderr}")
            
    except Exception as e:
        print(f"Error testing help: {e}")

if __name__ == "__main__":
    print("AutoDraw AI Agent - Complex Drawing Test")
    print("=" * 50)
    
    # Test help documentation
    test_help()
    
    # Test complex drawings
    success = test_complex_drawings()
    
    if success:
        print("\nAll tests passed! Complex drawing capabilities are working.")
        sys.exit(0)
    else:
        print("\nSome tests failed. Please check the output above.")
        sys.exit(1) 