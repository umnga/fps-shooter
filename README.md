# FPS Training Simulation

A Computer Graphics project implementing a first-person shooter training simulation using Python, pygame, and PyOpenGL.

## Phase 1: 3D Camera and Environment Setup

This foundational phase establishes the core rendering pipeline and camera controls.

### Features

- **OpenGL Perspective Projection**: 45° FOV, 0.1 to 100.0 clipping planes
- **First-Person Camera**: Full 3D movement with mouse-look controls
  - Yaw (horizontal) and Pitch (vertical) rotation
  - Pitch constrained to ±89° to prevent screen flipping
  - WASD movement on the XZ plane
  - Space/Shift for vertical movement
- **Ground Plane**: Grid-based floor for spatial reference
- **Coordinate Axes**: RGB visualization (X=Red, Y=Green, Z=Blue)
- **2D Crosshair**: Fixed center-screen overlay

### Controls

| Key | Action |
|-----|--------|
| W | Move forward |
| S | Move backward |
| A | Strafe left |
| D | Strafe right |
| Space | Move up |
| Left Shift | Move down |
| Mouse | Look around |
| ESC | Exit |

### Installation

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running

```bash
python main.py
```

### Project Structure

```
fps-shooter/
├── main.py          # Entry point, main loop, OpenGL setup
├── camera.py        # Camera class with position/rotation management
├── renderer.py      # 3D and 2D rendering functions
├── requirements.txt # Python dependencies
└── README.md        # This file
```

### Technical Details

#### View Matrix Calculation

The camera provides two methods for view transformation:
1. `apply_view_matrix()` - Uses `gluLookAt` for OpenGL-native transformation
2. `get_view_matrix()` - Returns a NumPy 4x4 matrix for custom calculations

#### Coordinate System

- **X-axis**: Right (positive) / Left (negative)
- **Y-axis**: Up (positive) / Down (negative)  
- **Z-axis**: Backward (positive) / Forward (negative)

This follows the standard OpenGL right-handed coordinate system.

### Future Phases

- **Phase 2**: Target system and shooting mechanics
- **Phase 3**: Scoring and feedback
- **Phase 4**: Advanced rendering (textures, lighting)
- **Phase 5**: Training scenarios and statistics
