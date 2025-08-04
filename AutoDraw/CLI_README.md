# AutoDraw AI Agent - Command Line Interface

A command-line tool for generating AutoCAD diagrams using natural language processing and AI. This tool takes drawing details as command-line arguments and automatically creates AutoCAD diagrams.

## Features

- **Natural Language Processing**: Describe drawings in plain English
- **Parameter-based Specification**: Use command-line arguments for precise control
- **Batch Processing**: Process multiple drawing requests from a file
- **Multiple Lighting Systems**: Support for various lighting fixture types
- **Validation**: Built-in specification validation
- **Dry Run Mode**: Test specifications without executing AutoCAD commands
- **Verbose Output**: Detailed logging and specification display

## Prerequisites

1. **Python 3.7+**
2. **AutoCAD** (must be installed and running)
3. **OpenAI API Key** (set as environment variable `OPENAI_API_KEY`)
4. **Required Python packages** (install via `pip install -r requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AutoCAD-AI-Agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your OpenAI API key:
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# Linux/Mac
export OPENAI_API_KEY=your_api_key_here
```

4. Ensure AutoCAD is running and accessible

## Usage

### Basic Usage

```bash
python cli_autodraw.py [OPTIONS]
```

### Input Methods

The CLI supports three input methods (mutually exclusive):

#### 1. Natural Language Description

```bash
python cli_autodraw.py --natural "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
```

#### 2. Parameter-based Specification

```bash
python cli_autodraw.py --system linear_light --length 10 --width 4 --wattage 50 --color-temp 4000k --start 5,5 --end 15,5
```

#### 3. Batch Processing

```bash
python cli_autodraw.py --batch-file requests.txt
```

## Command Line Options

### Input Options
- `--natural, -n TEXT`: Natural language description of the drawing
- `--batch-file, -b FILE`: File containing multiple drawing requests (one per line)

### System Specifications
- `--system, -s {ls,lsr,rush,rush_rec,pg,magneto}`: Lighting system type
- `--command, -c COMMAND`: Specific AutoCAD command to execute

### Dimensions
- `--length, -l FLOAT`: Length in feet
- `--width, -w FLOAT`: Width in inches
- `--height, -ht FLOAT`: Height in inches

### Position
- `--start TEXT`: Start point as "x,y" coordinates
- `--end TEXT`: End point as "x,y" coordinates
- `--orientation {horizontal,vertical,angled}`: Orientation of the fixture

### Specifications
- `--wattage INT`: Power in watts
- `--color-temp, --ct {2700k,3000k,3500k,4000k,5000k,6500k}`: Color temperature
- `--lens {clear,frosted,prismatic,louvered,reflector,diffuser,lens_cover}`: Lens type
- `--mounting {wall_mount,ceiling_mount,suspension,track_mount,recessed,surface_mount,pendant}`: Mounting type
- `--driver TEXT`: Driver specification
- `--quantity INT`: Number of units (default: 1)

### Additional Parameters
- `--spacing FLOAT`: Distance between units in feet
- `--voltage INT`: Voltage requirement
- `--emergency-backup`: Include emergency backup
- `--dimmable`: Make fixture dimmable
- `--ip-rating TEXT`: Ingress protection rating

### Output Options
- `--output, -o FILE`: Output file for results (JSON format)
- `--verbose, -v`: Verbose output
- `--dry-run`: Parse and validate without executing AutoCAD commands

## Examples

### Example 1: Simple Linear Light
```bash
python cli_autodraw.py --system linear_light --length 10 --width 4 --wattage 50 --color-temp 4000k --start 5,5 --end 15,5
```

### Example 2: Rush Light with Specifications
```bash
python cli_autodraw.py --system rush_light --length 8 --width 6 --wattage 75 --mounting ceiling_mount --lens frosted --quantity 2
```

### Example 3: Natural Language Request
```bash
python cli_autodraw.py --natural "Create a magneto track system 12 feet long with 75W fixtures every 2 feet, mounted on ceiling with clear lens"
```

### Example 4: Batch Processing
```bash
python cli_autodraw.py --batch-file example_requests.txt --output results.json
```

### Example 5: Dry Run (Validation Only)
```bash
python cli_autodraw.py --system linear_light --length 10 --wattage 50 --dry-run --verbose
```

### Example 6: Complex Specification
```bash
python cli_autodraw.py \
  --system linear_light \
  --length 15 \
  --width 6 \
  --wattage 60 \
  --color-temp 3500k \
  --mounting ceiling_mount \
  --lens prismatic \
  --emergency-backup \
  --dimmable \
  --voltage 277 \
  --ip-rating 65 \
  --start 0,0 \
  --end 15,0 \
  --verbose
```

## Available Lighting Systems

| System | Description | Default Wattage | Default Length | Default Width |
|--------|-------------|----------------|----------------|---------------|
| `ls` | Linear Light | 50W | 4ft | 4in |
| `lsr` | Linear Light with Reflector | 60W | 4ft | 4in |
| `rush` | Rush Light | 75W | 4ft | 6in |
| `rush_rec` | Rush Recessed | 75W | 4ft | 6in |
| `pg` | PG Light | 40W | 4ft | 4in |
| `magneto` | Magneto Track | 50W | 4ft | 4in |

## Available Commands

- `linear_light`: Create linear lighting fixtures
- `linear_light_reflector`: Create linear lighting with reflector
- `rush_light`: Create rush lighting fixtures
- `rush_recessed`: Create recessed rush lighting
- `pg_light`: Create PG series lighting
- `magneto_track`: Create magneto track system
- `repeat_last`: Repeat the last command
- `details`: Add text annotations
- `add_empck`: Insert emergency pack
- `purge_all`: Purge drawing elements

## Batch File Format

Create a text file with one drawing request per line:

```
Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature
Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens
Design a magneto track system 12 feet long with 75W fixtures every 2 feet
```

## Output

The tool provides:
- Console output with status messages
- Optional JSON output file with detailed results
- Verbose mode for detailed specification display
- Error messages for failed operations

### Example Output
```
AutoDraw AI Agent - Command Line Interface
==================================================
2024-01-15 10:30:15 - INFO - Processing natural language request
2024-01-15 10:30:16 - INFO - Parsed specifications: {...}
2024-01-15 10:30:17 - INFO - Successfully connected to AutoCAD
2024-01-15 10:30:18 - INFO - Drawing created successfully
✅ Drawing created successfully!
Summary: Created linear light drawing:
- Dimensions: 10.0 x 4.0 x 4.0
- Wattage: 50W
- Color Temperature: 4000k
- Quantity: 1
🎉 Process completed successfully!
```

## Error Handling

The tool includes comprehensive error handling:
- Invalid specifications
- AutoCAD connection issues
- API errors
- File I/O errors
- Validation failures

## Troubleshooting

### Common Issues

1. **AutoCAD not accessible**
   - Ensure AutoCAD is running
   - Check if AutoCAD is properly installed
   - Verify COM access permissions

2. **OpenAI API errors**
   - Verify API key is set correctly
   - Check API key permissions
   - Ensure sufficient API credits

3. **Invalid specifications**
   - Use `--dry-run` to validate specifications
   - Check parameter formats (coordinates as "x,y")
   - Verify lighting system names

4. **Batch processing errors**
   - Check file format (one request per line)
   - Verify file encoding (UTF-8 recommended)
   - Ensure file is readable

### Debug Mode

Use `--verbose` for detailed logging:
```bash
python cli_autodraw.py --natural "your request" --verbose
```

## Advanced Usage

### Custom Commands
```bash
python cli_autodraw.py --command details --specifications "Custom annotation text"
```

### Emergency Backup Systems
```bash
python cli_autodraw.py --system linear_light --emergency-backup --voltage 277
```

### IP-Rated Fixtures
```bash
python cli_autodraw.py --system rush_light --ip-rating 65 --mounting recessed
```

## Integration

The CLI can be integrated into:
- Build scripts
- CI/CD pipelines
- Automated workflows
- Batch processing systems

Example integration:
```bash
#!/bin/bash
# Process multiple drawing requests
for request in "request1" "request2" "request3"; do
    python cli_autodraw.py --natural "$request" --output "result_${request}.json"
done
```

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error messages carefully
3. Use `--verbose` for detailed debugging
4. Ensure all prerequisites are met 