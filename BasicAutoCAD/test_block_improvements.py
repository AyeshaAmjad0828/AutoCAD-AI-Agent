#!/usr/bin/env python3
"""
Test script for improved block functionality
Demonstrates the enhanced block insertion with placeholder creation
"""

import sys
import os
import logging
from autodraw_ai_agent import AutoDrawAIAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_improved_block_insertion():
    """Test the improved block insertion with placeholder creation"""
    print("Testing improved block insertion...")
    try:
        agent = AutoDrawAIAgent()
        
        # Test 1: Insert a block that doesn't exist (should create placeholder)
        print("\n1. Testing insertion of nonexistent block...")
        specs = {
            "command": "block",
            "position": {
                "insertion_point": [0, 0, 0]
            },
            "specifications": {
                "block_name": "nonexistent_block"
            },
            "additional_parameters": {
                "scale_factor": 1.0,
                "rotation": 0.0
            }
        }
        
        result = agent.create_complete_drawing(specs)
        if result.get("success"):
            print("✅ Placeholder block created successfully")
        else:
            print(f"❌ Placeholder block creation failed: {result.get('error')}")
            return False
        
        # Test 2: Insert another block with different parameters
        print("\n2. Testing insertion with rotation and scale...")
        specs = {
            "command": "block",
            "position": {
                "insertion_point": [5, 5, 0]
            },
            "specifications": {
                "block_name": "rotated_block"
            },
            "additional_parameters": {
                "scale_factor": 2.0,
                "rotation": 45.0
            }
        }
        
        result = agent.create_complete_drawing(specs)
        if result.get("success"):
            print("✅ Rotated and scaled block created successfully")
        else:
            print(f"❌ Rotated block creation failed: {result.get('error')}")
            return False
        
        # Test 3: List available blocks
        print("\n3. Testing block listing...")
        blocks = agent.list_available_blocks()
        if blocks:
            print(f"✅ Found {len(blocks)} blocks in drawing:")
            for block_name in sorted(blocks):
                print(f"   - {block_name}")
        else:
            print("No blocks found in drawing")
        
        # Test 4: Try to import assets (if available)
        print("\n4. Testing asset import...")
        imported_blocks = agent.import_assets_as_blocks()
        if imported_blocks:
            print(f"✅ Successfully imported {len(imported_blocks)} blocks from assets")
            for block_name, file_path in list(imported_blocks.items())[:5]:  # Show first 5
                print(f"   - {block_name}: {os.path.basename(file_path)}")
        else:
            print("No assets imported (this is normal if assets folder is not accessible)")
        
        print("\n✅ All block tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in block test: {e}")
        return False
    finally:
        if 'agent' in locals():
            agent.close_connection()

def test_block_with_real_assets():
    """Test block insertion with real assets (if available)"""
    print("\nTesting block insertion with real assets...")
    try:
        agent = AutoDrawAIAgent()
        
        # First, try to import some assets
        imported_blocks = agent.import_assets_as_blocks()
        
        if not imported_blocks:
            print("No assets available for testing")
            return True
        
        # Try to insert one of the imported blocks
        block_name = list(imported_blocks.keys())[0]  # Use the first imported block
        
        print(f"Testing insertion of imported block: {block_name}")
        
        specs = {
            "command": "block",
            "position": {
                "insertion_point": [10, 10, 0]
            },
            "specifications": {
                "block_name": block_name
            },
            "additional_parameters": {
                "scale_factor": 1.0,
                "rotation": 0.0
            }
        }
        
        result = agent.create_complete_drawing(specs)
        if result.get("success"):
            print(f"✅ Successfully inserted real block: {block_name}")
            return True
        else:
            print(f"❌ Failed to insert real block: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error in real asset test: {e}")
        return False
    finally:
        if 'agent' in locals():
            agent.close_connection()

def main():
    """Run all block improvement tests"""
    print("AutoCAD Block Improvements Test Suite")
    print("=" * 50)
    
    tests = [
        test_improved_block_insertion,
        test_block_with_real_assets
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
    print(f"Block Improvement Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All block improvement tests passed!")
    else:
        print("⚠️  Some block improvement tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 