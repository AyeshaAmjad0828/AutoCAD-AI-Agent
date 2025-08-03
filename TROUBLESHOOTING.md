# Troubleshooting Guide for AutoDraw CLI

## Common Issues and Solutions

### 1. AutoCAD Connection Errors

**Error**: `<unknown>.Count` or `<unknown>.Add`
**Solution**: 
- Make sure AutoCAD is running before using the CLI
- Test the connection: `python test_autocad_connection.py`
- Ensure you have pywin32 installed: `pip install pywin32`

**Error**: "AutoCAD not accessible"
**Solution**:
- Start AutoCAD manually
- Run as administrator if needed
- Check if AutoCAD is properly installed

### 2. OpenAI API Errors

**Error**: "OpenAI API key is required"
**Solution**:
- Set your OpenAI API key as environment variable:
  ```bash
  # Windows
  set OPENAI_API_KEY=your_api_key_here
  
  # Linux/Mac
  export OPENAI_API_KEY=your_api_key_here
  ```

**Error**: API rate limits or quota exceeded
**Solution**:
- Check your OpenAI account balance
- Wait before making more requests
- Use parameter-based specification instead of natural language

### 3. Natural Language Parsing Errors

**Error**: "Failed to parse natural language request"
**Solution**:
- Try a simpler, more specific description
- Use parameter-based specification instead
- Check your internet connection for API calls

### 4. Missing Dependencies

**Error**: "No module named 'win32com'"
**Solution**:
```bash
pip install pywin32
```

**Error**: "No module named 'openai'"
**Solution**:
```bash
pip install openai
```

## Testing Steps

### 1. Test AutoCAD Connection
```bash
python test_autocad_connection.py
```

### 2. Test CLI with Dry Run
```bash
python cli_autodraw.py --natural "Draw a linear light" --dry-run --verbose
```

### 3. Test Parameter-based Specification
```bash
python cli_autodraw.py --system linear_light --length 10 --wattage 50 --dry-run
```

## Debug Mode

Use `--verbose` flag for detailed logging:
```bash
python cli_autodraw.py --natural "your request" --verbose
```

## Alternative Approaches

If natural language processing fails:

1. **Use parameter-based specification**:
```bash
python cli_autodraw.py --system linear_light --length 10 --width 4 --wattage 50 --start 5,5 --end 15,5
```

2. **Use batch processing**:
```bash
python cli_autodraw.py --batch-file example_requests.txt
```

3. **Test with simple commands first**:
```bash
python cli_autodraw.py --system linear_light --length 5 --dry-run
```

## System Requirements

- Windows 10/11
- AutoCAD (any recent version)
- Python 3.7+
- pywin32
- openai
- Internet connection for API calls

## Getting Help

1. Check this troubleshooting guide
2. Run the test scripts
3. Use `--verbose` for detailed error messages
4. Ensure all prerequisites are met
5. Try simpler commands first 