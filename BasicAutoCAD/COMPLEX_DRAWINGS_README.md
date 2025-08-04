# Complex Drawing Capabilities

The AutoDraw AI Agent has been enhanced to support complex AutoCAD drawing commands beyond simple lines. This document describes the new capabilities and how to use them.

## New Drawing Commands

### Basic Shapes

#### Rectangle
```bash
python cli_autodraw.py --command rectangle --start 0,0 --end 10,8
```

#### Circle
```bash
python cli_autodraw.py --command circle --center 5,5 --radius 3
```

#### Ellipse
```bash
python cli_autodraw.py --command ellipse --center 5,5 --major-axis 6 --minor-axis 3
```

#### Arc
```bash
python cli_autodraw.py --command arc --center 5,5 --radius 4 --start-angle 0 --end-angle 90
```

### Complex Shapes

#### Polyline
```bash
# Open polyline
python cli_autodraw.py --command polyline --points "0,0;5,5;10,0;15,5"

# Closed polyline
python cli_autodraw.py --command polyline --points "0,0;5,5;10,0;15,5" --closed
```

### Text and Annotations

#### Text
```bash
python cli_autodraw.py --command text --insertion-point 2,2 --text-content "Sample Text" --text-height 0.25
```

#### Dimension
```bash
python cli_autodraw.py --command dimension --start 0,0 --end 10,0 --text-position 5,1
```

### Patterns and Blocks

#### Hatch
```bash
python cli_autodraw.py --command hatch --pattern-name "SOLID"
```

#### Block Insertion
```bash
python cli_autodraw.py --command block --insertion-point 5,5 --block-name "test_block" --scale 1.0 --rotation 45
```

### Transformations

#### Array (Rectangular)
```bash
python cli_autodraw.py --command array --array-type rectangular --rows 3 --columns 4 --row-spacing 2 --column-spacing 2
```

#### Array (Polar)
```bash
python cli_autodraw.py --command array --array-type polar --center 5,5 --num-items 8 --angle 360
```

#### Mirror
```bash
python cli_autodraw.py --command mirror --mirror-line-start 0,0 --mirror-line-end 0,10
```

#### Rotate
```bash
python cli_autodraw.py --command rotate --base-point 5,5 --angle 90
```

#### Scale
```bash
python cli_autodraw.py --command scale --base-point 0,0 --scale-factor 2.0
```

### Modifications

#### Offset
```bash
python cli_autodraw.py --command offset --offset-distance 1.0
```

#### Fillet
```bash
python cli_autodraw.py --command fillet --fillet-radius 0.5
```

#### Chamfer
```bash
python cli_autodraw.py --command chamfer --chamfer-distance1 0.5 --chamfer-distance2 0.5
```

## Natural Language Support

The AI agent can now understand natural language descriptions for complex shapes:

```bash
# Rectangle
python cli_autodraw.py --natural "Draw a rectangle from point 0,0 to 10,8"

# Circle
python cli_autodraw.py --natural "Create a circle with center at 5,5 and radius 3"

# Complex shape
python cli_autodraw.py --natural "Draw a polyline through points 0,0; 5,5; 10,0; 15,5 and close it"

# Text
python cli_autodraw.py --natural "Add text 'Sample Text' at position 2,2 with height 0.25"

# Array
python cli_autodraw.py --natural "Create a 3x4 rectangular array with 2 unit spacing"
```

## Command Line Parameters

### Position Parameters
- `--start`: Start point as "x,y" coordinates
- `--end`: End point as "x,y" coordinates  
- `--center`: Center point as "x,y" coordinates (for circles, arcs, ellipses)
- `--insertion-point`: Insertion point as "x,y" coordinates (for text, blocks)
- `--points`: Multiple points as "x1,y1;x2,y2;x3,y3" (for polylines)

### Dimension Parameters
- `--length`: Length in feet
- `--width`: Width in inches
- `--height`: Height in inches
- `--radius`: Radius for circles and arcs
- `--major-axis`: Major axis length for ellipses
- `--minor-axis`: Minor axis length for ellipses

### Additional Parameters
- `--start-angle`: Start angle in degrees for arcs
- `--end-angle`: End angle in degrees for arcs
- `--closed`: Close polyline (for polylines)
- `--text-content`: Text content to display
- `--text-height`: Text height
- `--block-name`: Name of block to insert
- `--pattern-name`: Hatch pattern name
- `--array-type`: Type of array to create (rectangular/polar)
- `--rows`: Number of rows for rectangular array
- `--columns`: Number of columns for rectangular array
- `--row-spacing`: Spacing between rows
- `--column-spacing`: Spacing between columns
- `--num-items`: Number of items for polar array
- `--scale-factor`: Scale factor for scaling operations
- `--rotation`: Rotation angle in degrees
- `--offset-distance`: Offset distance
- `--fillet-radius`: Fillet radius
- `--chamfer-distance1`: First chamfer distance
- `--chamfer-distance2`: Second chamfer distance

## Testing

Run the test script to verify all capabilities:

```bash
python test_complex_drawings.py
```

This will test all the new drawing commands and provide a summary of results.

## Examples

### Creating a Simple Floor Plan
```bash
# Create room outline
python cli_autodraw.py --command rectangle --start 0,0 --end 20,15

# Add door
python cli_autodraw.py --command rectangle --start 0,6 --end 2,9

# Add window
python cli_autodraw.py --command rectangle --start 8,14 --end 12,15

# Add room label
python cli_autodraw.py --command text --insertion-point 10,7.5 --text-content "LIVING ROOM" --text-height 0.5
```

### Creating a Mechanical Part
```bash
# Create base rectangle
python cli_autodraw.py --command rectangle --start 0,0 --end 10,8

# Add holes
python cli_autodraw.py --command circle --center 2,2 --radius 0.5
python cli_autodraw.py --command circle --center 8,2 --radius 0.5
python cli_autodraw.py --command circle --center 5,6 --radius 1

# Add dimensions
python cli_autodraw.py --command dimension --start 0,0 --end 10,0 --text-position 5,-1
python cli_autodraw.py --command dimension --start 0,0 --end 0,8 --text-position -1,4
```

### Creating a Lighting Layout
```bash
# Create room
python cli_autodraw.py --command rectangle --start 0,0 --end 30,20

# Add lighting fixtures in grid
python cli_autodraw.py --command array --array-type rectangular --rows 4 --columns 6 --row-spacing 5 --column-spacing 5

# Add control panel
python cli_autodraw.py --command rectangle --start 25,0 --end 30,5

# Add labels
python cli_autodraw.py --command text --insertion-point 15,10 --text-content "LIGHTING LAYOUT" --text-height 0.75
```

## Notes

- All coordinates are in the current AutoCAD units
- The `--dry-run` flag can be used to test commands without actually executing them in AutoCAD
- Natural language processing works best with clear, descriptive requests
- Some commands (like array, mirror, rotate, scale) work on the last created object
- Make sure AutoCAD is running before executing commands that create actual drawings

## Troubleshooting

1. **Command not recognized**: Make sure you're using the correct command name from the list above
2. **Invalid coordinates**: Use the format "x,y" for coordinates
3. **Missing parameters**: Check that all required parameters for the command are provided
4. **AutoCAD not responding**: Ensure AutoCAD is running and accessible
5. **Natural language parsing fails**: Try using parameter-based commands instead

For more help, run:
```bash
python cli_autodraw.py --help
``` 