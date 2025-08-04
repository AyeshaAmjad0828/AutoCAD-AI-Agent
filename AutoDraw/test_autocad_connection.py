#!/usr/bin/env python3
"""
Simple test script to verify AutoCAD connection
"""

import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_autocad_connection():
    """Test if AutoCAD is accessible"""
    try:
        import win32com.client
        import pythoncom
        
        print("Testing AutoCAD connection...")
        
        # Initialize COM
        pythoncom.CoInitialize()
        
        try:
            # Try to get existing AutoCAD instance
            print("Attempting to connect to existing AutoCAD instance...")
            autocad = win32com.client.GetActiveObject("AutoCAD.Application")
            print(f"✅ Connected to existing AutoCAD: {autocad.Name}")
            
            # Test document access
            try:
                doc_count = autocad.Documents.Count
                print(f"✅ Found {doc_count} documents")
                
                if doc_count > 0:
                    doc = autocad.ActiveDocument
                    print(f"✅ Active document: {doc.Name}")
                else:
                    print("ℹ️  No documents open, will create new one when needed")
                    
            except Exception as e:
                print(f"⚠️  Warning: Could not access documents: {e}")
                
        except Exception as e:
            print(f"❌ Could not connect to existing AutoCAD: {e}")
            print("Make sure AutoCAD is running before using the CLI")
            return False
            
        finally:
            pythoncom.CoUninitialize()
            
        return True
        
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        print("Please install pywin32: pip install pywin32")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_autocad_connection()
    if success:
        print("\n🎉 AutoCAD connection test passed!")
        print("You can now run the CLI script.")
    else:
        print("\n❌ AutoCAD connection test failed!")
        print("Please ensure AutoCAD is running and try again.")
        sys.exit(1) 