#!/usr/bin/env python3
"""
Test script for AutoDraw AI Agent with complex drawing commands
Tests all AutoDraw palette functionality
"""

import sys
import os
import logging
import json
from typing import List, Dict

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autodraw_ai_agent import AutoDrawAIAgent
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDrawTester:
    """Test class for AutoDraw AI Agent functionality"""
    
    def __init__(self):
        self.agent = None
        self.test_results = []
    
    def initialize_agent(self, initialize_autocad: bool = True):
        """Initialize the AutoDraw AI Agent"""
        try:
            self.agent = AutoDrawAIAgent(initialize_autocad=initialize_autocad)
            logger.info("✅ AutoDraw AI Agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize AutoDraw AI Agent: {e}")
            return False
    
    def test_command_mapping(self):
        """Test that all AutoDraw commands are properly mapped"""
        print("\n" + "="*60)
        print("TESTING COMMAND MAPPING")
        print("="*60)
        
        expected_commands = {
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
        
        success = True
        for command, expected in expected_commands.items():
            actual = self.agent.command_map.get(command)
            if actual == expected:
                print(f"✅ {command} -> {actual}")
            else:
                print(f"❌ {command} -> {actual} (expected: {expected})")
                success = False
        
        return success
    
    def test_lighting_systems(self):
        """Test that all lighting systems are properly configured"""
        print("\n" + "="*60)
        print("TESTING LIGHTING SYSTEMS")
        print("="*60)
        
        expected_systems = ["ls", "lsr", "rush", "rush_rec", "pg", "magneto"]
        
        success = True
        for system in expected_systems:
            if system in self.agent.lighting_systems:
                system_info = self.agent.lighting_systems[system]
                print(f"✅ {system}: {system_info.get('name', 'Unknown')}")
            else:
                print(f"❌ Missing lighting system: {system}")
                success = False
        
        return success
    
    def test_natural_language_parsing(self):
        """Test natural language parsing with complex requests"""
        print("\n" + "="*60)
        print("TESTING NATURAL LANGUAGE PARSING")
        print("="*60)
        
        test_requests = [
            "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature",
            "Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens",
            "Design a magneto track system 12 feet long with 75W fixtures every 2 feet",
            "Generate a PG light 6 feet long with 40W power and 3000K color temperature",
            "Create a linear light with reflector 15 feet long, 6 inches wide, with emergency backup",
            "Add emergency pack to the current drawing",
            "Calculate driver specifications for 60W linear light",
            "Update driver brand for existing fixtures",
            "Add suspension kit count for ceiling mounted fixtures",
            "Import all lighting assets and blocks",
            "Redefine all blocks in the drawing",
            "Purge all unused elements from the drawing"
        ]
        
        success_count = 0
        for i, request in enumerate(test_requests, 1):
            try:
                print(f"\n{i}. Testing: {request}")
                specs = self.agent.process_natural_language_request(request)
                if specs and 'command' in specs:
                    print(f"   ✅ Parsed successfully: {specs['command']}")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to parse")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n📊 Natural language parsing: {success_count}/{len(test_requests)} successful")
        return success_count >= len(test_requests) * 0.8  # 80% success rate
    
    def test_specification_validation(self):
        """Test specification validation"""
        print("\n" + "="*60)
        print("TESTING SPECIFICATION VALIDATION")
        print("="*60)
        
        test_specs = [
            {
                "command": "linear_light",
                "lighting_system": "ls",
                "dimensions": {"length": 10, "width": 4},
                "specifications": {"wattage": 50, "color_temperature": "4000k"}
            },
            {
                "command": "rush_light",
                "lighting_system": "rush",
                "dimensions": {"length": 8, "width": 6},
                "specifications": {"wattage": 75, "lens_type": "frosted"}
            },
            {
                "command": "add_empck",
                "specifications": {"quantity": 1}
            }
        ]
        
        success = True
        for i, specs in enumerate(test_specs, 1):
            try:
                is_valid = self.agent._validate_specifications(specs)
                if is_valid:
                    print(f"✅ Test {i}: Valid specifications")
                else:
                    print(f"❌ Test {i}: Invalid specifications")
                    success = False
            except Exception as e:
                print(f"❌ Test {i}: Error - {e}")
                success = False
        
        return success
    
    def test_autodraw_command_execution(self, dry_run: bool = True):
        """Test AutoDraw command execution (with dry run option)"""
        print("\n" + "="*60)
        print("TESTING AUTODRAW COMMAND EXECUTION")
        print("="*60)
        
        if dry_run:
            print("🔍 DRY RUN MODE - No actual AutoCAD commands will be executed")
        
        test_specs = [
            {
                "command": "linear_light",
                "dimensions": {"length": 10, "width": 4},
                "specifications": {"wattage": 50, "color_temperature": "4000k"},
                "position": {"start_point": [5, 5, 0], "end_point": [15, 5, 0]}
            },
            {
                "command": "add_empck",
                "specifications": {"quantity": 1}
            },
            {
                "command": "details",
                "specifications": {"text": "Lighting System Details"}
            }
        ]
        
        success_count = 0
        for i, specs in enumerate(test_specs, 1):
            try:
                print(f"\n{i}. Testing command: {specs['command']}")
                if dry_run:
                    # Just test the parameter preparation
                    params = self.agent._prepare_autodraw_parameters(specs)
                    print(f"   ✅ Parameters prepared: {params}")
                    success_count += 1
                else:
                    # Actually execute the command
                    result = self.agent.execute_drawing_command(specs)
                    if result:
                        print(f"   ✅ Command executed successfully")
                        success_count += 1
                    else:
                        print(f"   ❌ Command execution failed")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print(f"\n📊 Command execution: {success_count}/{len(test_specs)} successful")
        return success_count >= len(test_specs) * 0.8  # 80% success rate
    
    def test_batch_processing(self):
        """Test batch processing functionality"""
        print("\n" + "="*60)
        print("TESTING BATCH PROCESSING")
        print("="*60)
        
        batch_requests = [
            "Draw a 5-foot linear light with 50W power",
            "Create a rush light 6 feet long",
            "Add emergency pack"
        ]
        
        try:
            results = self.agent.batch_process_requests(batch_requests)
            success_count = sum(1 for r in results if r.get('success'))
            print(f"📊 Batch processing: {success_count}/{len(batch_requests)} successful")
            return success_count >= len(batch_requests) * 0.8
        except Exception as e:
            print(f"❌ Batch processing error: {e}")
            return False
    
    def run_all_tests(self, test_autocad: bool = False):
        """Run all tests"""
        print("🚀 AUTODRAW AI AGENT COMPREHENSIVE TEST SUITE")
        print("="*60)
        
        # Initialize agent
        if not self.initialize_agent(initialize_autocad=test_autocad):
            print("❌ Cannot proceed without agent initialization")
            return False
        
        # Run tests
        tests = [
            ("Command Mapping", self.test_command_mapping),
            ("Lighting Systems", self.test_lighting_systems),
            ("Natural Language Parsing", self.test_natural_language_parsing),
            ("Specification Validation", self.test_specification_validation),
            ("AutoDraw Command Execution", lambda: self.test_autodraw_command_execution(dry_run=not test_autocad)),
            ("Batch Processing", self.test_batch_processing)
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                status = "✅ PASSED" if result else "❌ FAILED"
                print(f"\n{status}: {test_name}")
            except Exception as e:
                results.append((test_name, False))
                print(f"\n❌ FAILED: {test_name} - Error: {e}")
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print(f"\n📊 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! AutoDraw AI Agent is ready for complex drawing tasks.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        return passed == total
    
    def cleanup(self):
        """Clean up resources"""
        if self.agent:
            try:
                self.agent.close_connection()
                logger.info("✅ Cleanup completed")
            except Exception as e:
                logger.error(f"❌ Cleanup error: {e}")


def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AutoDraw AI Agent functionality")
    parser.add_argument(
        '--test-autocad',
        action='store_true',
        help='Test with actual AutoCAD commands (requires AutoCAD to be running)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    tester = AutoDrawTester()
    
    try:
        success = tester.run_all_tests(test_autocad=args.test_autocad)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        tester.cleanup()


if __name__ == "__main__":
    main() 