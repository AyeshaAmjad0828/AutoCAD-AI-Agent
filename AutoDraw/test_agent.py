"""
Test script for AutoDraw AI Agent
Tests the functionality without requiring AutoCAD connection
"""

import json
import sys
import os
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autodraw_ai_agent import AutoDrawAIAgent
import config

def test_parsing_prompt():
    """Test the parsing prompt creation"""
    print("Testing parsing prompt creation...")
    
    agent = AutoDrawAIAgent.__new__(AutoDrawAIAgent)
    agent.command_map = config.COMMAND_MAP
    agent.lighting_systems = config.LIGHTING_SYSTEMS
    agent.mounting_options = config.MOUNTING_OPTIONS
    agent.lens_options = config.LENS_OPTIONS
    agent.color_temps = config.COLOR_TEMPERATURES
    
    user_input = "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
    prompt = agent._create_parsing_prompt(user_input)
    
    print("✅ Parsing prompt created successfully")
    print(f"Prompt length: {len(prompt)} characters")
    print("Prompt includes all required elements:")
    print(f"- Available commands: {'linear_light' in prompt}")
    print(f"- Lighting systems: {'ls' in prompt}")
    print(f"- Mounting options: {'ceiling_mount' in prompt}")
    print(f"- Lens options: {'clear' in prompt}")
    print(f"- Color temperatures: {'4000k' in prompt}")
    
    return True

def test_specification_validation():
    """Test specification validation"""
    print("\nTesting specification validation...")
    
    agent = AutoDrawAIAgent.__new__(AutoDrawAIAgent)
    agent.command_map = config.COMMAND_MAP
    
    # Valid specifications
    valid_specs = {
        "command": "linear_light",
        "lighting_system": "ls",
        "dimensions": {"length": 10, "width": 4},
        "specifications": {"wattage": 50, "color_temperature": "4000k"}
    }
    
    # Invalid specifications (missing command)
    invalid_specs = {
        "lighting_system": "ls",
        "dimensions": {"length": 10}
    }
    
    # Invalid specifications (invalid command)
    invalid_command_specs = {
        "command": "invalid_command",
        "lighting_system": "ls"
    }
    
    # Test valid specs
    result1 = agent._validate_specifications(valid_specs)
    print(f"✅ Valid specifications: {result1}")
    
    # Test invalid specs
    result2 = agent._validate_specifications(invalid_specs)
    print(f"✅ Invalid specifications (missing command): {not result2}")
    
    # Test invalid command
    result3 = agent._validate_specifications(invalid_command_specs)
    print(f"✅ Invalid command: {not result3}")
    
    return result1 and not result2 and not result3

def test_command_parameter_preparation():
    """Test command parameter preparation"""
    print("\nTesting command parameter preparation...")
    
    agent = AutoDrawAIAgent.__new__(AutoDrawAIAgent)
    
    specifications = {
        "command": "linear_light",
        "position": {
            "start_point": [5, 5, 0],
            "end_point": [15, 5, 0]
        },
        "dimensions": {
            "length": 10,
            "width": 4,
            "height": 2
        },
        "specifications": {
            "wattage": 50,
            "color_temperature": "4000k",
            "quantity": 1
        }
    }
    
    params = agent._prepare_command_parameters(specifications)
    print(f"✅ Prepared parameters: {params}")
    
    # Check that parameters are properly formatted
    param_list = params.split()
    print(f"Number of parameters: {len(param_list)}")
    print(f"Parameters: {param_list}")
    
    return len(param_list) > 0

def test_configuration_loading():
    """Test configuration loading"""
    print("\nTesting configuration loading...")
    
    # Test command map
    print(f"✅ Command map loaded: {len(config.COMMAND_MAP)} commands")
    
    # Test lighting systems
    print(f"✅ Lighting systems loaded: {len(config.LIGHTING_SYSTEMS)} systems")
    
    # Test mounting options
    print(f"✅ Mounting options loaded: {len(config.MOUNTING_OPTIONS)} options")
    
    # Test lens options
    print(f"✅ Lens options loaded: {len(config.LENS_OPTIONS)} options")
    
    # Test color temperatures
    print(f"✅ Color temperatures loaded: {len(config.COLOR_TEMPERATURES)} options")
    
    # Verify specific values
    assert "linear_light" in config.COMMAND_MAP
    assert "ls" in config.LIGHTING_SYSTEMS
    assert "ceiling_mount" in config.MOUNTING_OPTIONS
    assert "clear" in config.LENS_OPTIONS
    assert "4000k" in config.COLOR_TEMPERATURES
    
    return True

def test_summary_generation():
    """Test drawing summary generation"""
    print("\nTesting drawing summary generation...")
    
    agent = AutoDrawAIAgent.__new__(AutoDrawAIAgent)
    
    specifications = {
        "lighting_system": "ls",
        "dimensions": {
            "length": 10,
            "width": 4,
            "height": 2
        },
        "specifications": {
            "wattage": 50,
            "color_temperature": "4000k",
            "quantity": 2
        }
    }
    
    summary = agent._generate_drawing_summary(specifications)
    print(f"✅ Generated summary: {summary}")
    
    # Check summary content
    assert "Created" in summary
    assert "10" in summary
    assert "50W" in summary
    assert "4000k" in summary
    assert "2" in summary
    
    return True

@patch('autodraw_ai_agent.openai')
@patch('autodraw_ai_agent.win32com.client')
def test_mock_agent_initialization(mock_win32com, mock_openai):
    """Test agent initialization with mocked dependencies"""
    print("\nTesting agent initialization (mocked)...")
    
    # Mock OpenAI
    mock_openai.api_key = "test_key"
    
    # Mock AutoCAD
    mock_autocad = Mock()
    mock_doc = Mock()
    mock_modelspace = Mock()
    mock_autocad.ActiveDocument = mock_doc
    mock_doc.ModelSpace = mock_modelspace
    mock_win32com.client.Dispatch.return_value = mock_autocad
    
    try:
        agent = AutoDrawAIAgent(openai_api_key="test_key")
        print("✅ Agent initialized successfully with mocked dependencies")
        
        # Test command map
        assert len(agent.command_map) > 0
        print(f"✅ Command map loaded: {len(agent.command_map)} commands")
        
        # Test lighting systems
        assert len(agent.lighting_systems) > 0
        print(f"✅ Lighting systems loaded: {len(agent.lighting_systems)} systems")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        return False

def test_batch_file_parsing():
    """Test batch file parsing"""
    print("\nTesting batch file parsing...")
    
    # Read the example batch file
    try:
        with open('batch_example.txt', 'r') as f:
            content = f.read()
        
        # Parse as text file with one request per line
        requests = [line.strip() for line in content.split('\n') if line.strip()]
        
        print(f"✅ Batch file loaded: {len(requests)} requests")
        
        # Check content
        for i, request in enumerate(requests):
            print(f"  Request {i+1}: {request[:50]}...")
        
        # Verify we have the expected requests
        assert len(requests) >= 6
        assert "linear light" in requests[0].lower()
        assert "rush light" in requests[1].lower()
        assert "magneto track" in requests[2].lower()
        
        return True
        
    except FileNotFoundError:
        print("❌ Batch example file not found")
        return False
    except Exception as e:
        print(f"❌ Error reading batch file: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running AutoDraw AI Agent Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Parsing Prompt Creation", test_parsing_prompt),
        ("Specification Validation", test_specification_validation),
        ("Command Parameter Preparation", test_command_parameter_preparation),
        ("Summary Generation", test_summary_generation),
        ("Mock Agent Initialization", test_mock_agent_initialization),
        ("Batch File Parsing", test_batch_file_parsing)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The AI agent is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 