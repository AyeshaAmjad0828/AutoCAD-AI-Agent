#!/usr/bin/env python3
"""
Test script for AutoDraw Flask API
Tests various endpoints and functionality
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   AutoCAD connection: {data['autocad_connection']}")
            print(f"   OpenAI API key: {data['openai_api_key']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_get_commands():
    """Test getting available commands"""
    print("\nTesting get commands...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/commands", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                commands = data.get('commands', {})
                print(f"✅ Commands retrieved successfully: {len(commands)} commands")
                for cmd, autocad_cmd in list(commands.items())[:5]:  # Show first 5
                    print(f"   {cmd}: {autocad_cmd}")
                return True
            else:
                print(f"❌ Commands request failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Commands request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Commands request error: {e}")
        return False

def test_get_lighting_systems():
    """Test getting lighting systems"""
    print("\nTesting get lighting systems...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/lighting-systems", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                systems = data.get('lighting_systems', {})
                print(f"✅ Lighting systems retrieved successfully: {len(systems)} systems")
                for system_id, system_info in systems.items():
                    print(f"   {system_id}: {system_info.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Lighting systems request failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Lighting systems request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Lighting systems request error: {e}")
        return False

def test_get_config():
    """Test getting configuration"""
    print("\nTesting get configuration...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/config", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                config = data.get('configuration', {})
                print(f"✅ Configuration retrieved successfully")
                print(f"   OpenAI model: {config.get('openai_model')}")
                print(f"   AutoCAD timeout: {config.get('autocad_timeout')}s")
                print(f"   Color temperatures: {config.get('color_temperatures', [])}")
                return True
            else:
                print(f"❌ Configuration request failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Configuration request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Configuration request error: {e}")
        return False

def test_validate_specifications():
    """Test validating specifications"""
    print("\nTesting validate specifications...")
    try:
        specs = {
            "command": "linear_light",
            "dimensions": {
                "length": 10,
                "width": 4
            },
            "position": {
                "start_point": [5, 5, 0],
                "end_point": [15, 5, 0]
            },
            "specifications": {
                "wattage": 50,
                "color_temperature": "4000k"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            json={"specifications": specs},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('valid'):
                print("✅ Specifications validation passed")
                return True
            else:
                print(f"❌ Specifications validation failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Specifications validation request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Specifications validation error: {e}")
        return False

def test_process_natural_language():
    """Test natural language processing"""
    print("\nTesting natural language processing...")
    try:
        text = "Draw a 10-foot linear light with 50W power and 4000K color temperature"
        
        response = requests.post(
            f"{BASE_URL}/api/v1/natural",
            json={"text": text},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                specs = data.get('specifications', {})
                print("✅ Natural language processing successful")
                print(f"   Command: {specs.get('command')}")
                print(f"   Dimensions: {specs.get('dimensions', {})}")
                return True
            else:
                print(f"❌ Natural language processing failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Natural language processing request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Natural language processing error: {e}")
        return False

def test_batch_processing():
    """Test batch processing"""
    print("\nTesting batch processing...")
    try:
        requests_list = [
            "Draw a 4-foot linear light at position 0,0",
            "Create a circle with radius 3 at center 10,10"
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/v1/batch",
            json={"requests": requests_list},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                total = data.get('total_requests', 0)
                successful = data.get('successful', 0)
                print(f"✅ Batch processing completed: {successful}/{total} successful")
                return True
            else:
                print(f"❌ Batch processing failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Batch processing request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
        return False

def test_get_status():
    """Test getting status"""
    print("\nTesting get status...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/status", timeout=TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                status = data.get('status', {})
                print("✅ Status retrieved successfully")
                print(f"   AutoCAD connection: {status.get('autocad_connection')}")
                print(f"   OpenAI API key: {status.get('openai_api_key')}")
                print(f"   Agent status: {status.get('agent_status')}")
                return True
            else:
                print(f"❌ Status request failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Status request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status request error: {e}")
        return False

def test_drawing_creation():
    """Test drawing creation (without AutoCAD)"""
    print("\nTesting drawing creation...")
    try:
        specs = {
            "command": "linear_light",
            "dimensions": {
                "length": 10,
                "width": 4
            },
            "position": {
                "start_point": [5, 5, 0],
                "end_point": [15, 5, 0]
            },
            "specifications": {
                "wattage": 50,
                "color_temperature": "4000k"
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/draw",
            json={"specifications": specs},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Drawing creation request successful")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"❌ Drawing creation failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Drawing creation request failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Drawing creation error: {e}")
        return False

def main():
    """Run all tests"""
    print("AutoDraw API Test Suite")
    print("=" * 50)
    
    # Check if API is running
    print("Checking if API is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ API is not responding properly: {response.status_code}")
            print("Please ensure the API is running with: python app.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API")
        print("Please ensure the API is running with: python app.py")
        sys.exit(1)
    
    print("✅ API is running")
    
    # Run tests
    tests = [
        test_health_check,
        test_get_commands,
        test_get_lighting_systems,
        test_get_config,
        test_validate_specifications,
        test_process_natural_language,
        test_batch_processing,
        test_get_status,
        test_drawing_creation
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
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 