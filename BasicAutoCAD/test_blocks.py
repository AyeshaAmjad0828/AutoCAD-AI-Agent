#!/usr/bin/env python3
"""
Test script for AutoCAD block operations
Demonstrates creating and inserting blocks
"""

import sys
import os
import logging
from autodraw_ai_agent import AutoDrawAIAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_create_simple_block():
    """Test creating a simple block"""
    print("Testing simple block creation...")
    try:
        agent = AutoDrawAIAgent()
        
        # Create a simple rectangle as a block
        specs = {
            "command": "rectangle",
            "position": {
                "start_point": [0, 0, 0],
                "end_point": [2, 1, 0]
            },
            "specifications": {
                "block_name": "simple_rect"
            }
        }
        
        result = agent.create_complete_drawing(specs)
        if result.get("success"):
            print("✅ Simple rectangle created successfully")
        else:
            print(f"❌ Failed to create rectangle: {result.get('error')}")
            return False
        
        # Now try to insert the block
        insert_specs = {
            "command": "block",
            "position": {
                "insertion_point": [5, 5, 0]
            },
            "specifications": {
                "block_name": "simple_rect"
            },
            "additional_parameters": {
                "scale_factor": 1.0,
                "rotation": 0.0
            }
        }
        
        result = agent.create_complete_drawing(insert_specs)
        if result.get("success"):
            print("✅ Block insertion successful")
            return True
        else:
            print(f"❌ Block insertion failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in block test: {e}")
        return False
    finally:
        if 'agent' in locals():
            agent.close_connection()

def test_insert_nonexistent_block():
    """Test inserting a block that doesn't exist (should create placeholder)"""
    print("\nTesting insertion of nonexistent block...")
    try:
        agent = AutoDrawAIAgent()
        
        specs = {
            "command": "block",
            "position": {
                "insertion_point": [10, 10, 0]
            },
            "specifications": {
                "block_name": "nonexistent_block"
            },
            "additional_parameters": {
                "scale_factor": 2.0,
                "rotation": 45.0
            }
        }
        
        result = agent.create_complete_drawing(specs)
        if result.get("success"):
            print("✅ Placeholder block created successfully")
            return True
        else:
            print(f"❌ Placeholder block creation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in nonexistent block test: {e}")
        return False
    finally:
        if 'agent' in locals():
            agent.close_connection()

def test_multiple_block_insertions():
    """Test inserting multiple blocks"""
    print("\nTesting multiple block insertions...")
    try:
        agent = AutoDrawAIAgent()
        
        # Create multiple blocks at different positions
        positions = [
            [0, 0, 0],
            [5, 0, 0],
            [0, 5, 0],
            [5, 5, 0]
        ]
        
        success_count = 0
        for i, pos in enumerate(positions):
            specs = {
                "command": "block",
                "position": {
                    "insertion_point": pos
                },
                "specifications": {
                    "block_name": f"test_block_{i+1}"
                },
                "additional_parameters": {
                    "scale_factor": 1.0,
                    "rotation": i * 90.0  # Rotate each block differently
                }
            }
            
            result = agent.create_complete_drawing(specs)
            if result.get("success"):
                success_count += 1
                print(f"✅ Block {i+1} created at {pos}")
            else:
                print(f"❌ Block {i+1} failed: {result.get('error')}")
        
        print(f"Successfully created {success_count}/{len(positions)} blocks")
        return success_count == len(positions)
        
    except Exception as e:
        print(f"❌ Error in multiple block test: {e}")
        return False
    finally:
        if 'agent' in locals():
            agent.close_connection()

def test_block_with_text():
    """Test creating a block with text annotation"""
    print("\nTesting block with text annotation...")
    try:
        agent = AutoDrawAIAgent()
        
        # First create a rectangle
        rect_specs = {
            "command": "rectangle",
            "position": {
                "start_point": [15, 15, 0],
                "end_point": [18, 17, 0]
            }
        }
        
        result = agent.create_complete_drawing(rect_specs)
        if not result.get("success"):
            print(f"❌ Failed to create rectangle: {result.get('error')}")
            return False
        
        # Add text annotation
        text_specs = {
            "command": "text",
            "position": {
                "insertion_point": [16.5, 16, 0]
            },
            "specifications": {
                "text_content": "BLOCK TEST",
                "text_height": 0.2
            }
        }
        
        result = agent.create_complete_drawing(text_specs)
        if result.get("success"):
            print("✅ Block with text created successfully")
            return True
        else:
            print(f"❌ Text addition failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in block with text test: {e}")
        return False
    finally:
        if 'agent' in locals():
            agent.close_connection()

def main():
    """Run all block tests"""
    print("AutoCAD Block Operations Test Suite")
    print("=" * 50)
    
    tests = [
        test_create_simple_block,
        test_insert_nonexistent_block,
        test_multiple_block_insertions,
        test_block_with_text
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Block Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All block tests passed!")
    else:
        print("⚠️  Some block tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 