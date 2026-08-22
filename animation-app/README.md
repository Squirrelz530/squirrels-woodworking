# AI Animation Studio

A PySide6 desktop application for generating animation frames using cloud AI image generation.

## Features

- **Image Generation**: Generate images from text prompts using Pollinations.ai (free, no authentication required)
- **Asset Management**: Save, organize, and preview generated images
- **Timeline Controls**: Play/pause/stop controls with MM:SS formatting
- **Responsive UI**: Threaded generation keeps the UI responsive during network operations
- **Preview**: View generated images with smooth scaling and aspect ratio preservation

## Screenshots

The application features:
- Left sidebar with prompt input and asset list
- Central preview area with image display
- Bottom timeline with playback controls

## Requirements

- Python 3.9 or higher
- PySide6 >= 6.4.0
- requests >= 2.28.0

## Installation

### Using pip (Recommended)

```bash
# Clone or navigate to the animation-app directory
cd animation-app

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
cd animation-app
python main.py
```

Or with the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

## Usage

### Generating Images

1. Enter a text prompt in the "Generate Image" section (e.g., "a beautiful sunset over mountains")
2. Click the "Generate" button
3. Wait for the image to be generated (progress will be shown)
4. The generated image will appear in the Assets list and be displayed in the Preview area

### Managing Assets

- **View Assets**: Generated images appear in the Assets list with thumbnails
- **Select Asset**: Click on an asset to preview it
- **Double-click Asset**: Open the asset in your default image viewer
- **Delete Asset**: Select an asset and click "Delete" to remove it
- **Refresh**: Click "Refresh" to reload the asset list
- **Import**: Use File > Open Asset to import existing images

### Timeline Controls

- Drag the slider to scrub through the timeline
- Click "Play" to start playback (toggles to "Pause")
- Click "Stop" to reset to the beginning
- Time is displayed in MM:SS format
- Frame counter shows current/total frames

## Project Structure

```
animation-app/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Data models (Asset, GenerationRequest, etc.)
│   ├── api.py               # API client for image generation
│   ├── storage.py           # Asset storage and persistence
│   ├── worker.py            # Background worker for generation
│   └── main_window.py       # Main application window
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
└── README.md               # This file

# Created on first run:
├── assets/                 # Generated image files
└── assets.json             # Asset metadata
```

## Configuration

### Image Generation Provider

The application uses **Pollinations.ai** by default:
- URL: `https://image.pollinations.ai/prompt`
- No authentication required
- Free to use (rate limited)
- Supports various parameters: prompt, width, height, seed, nolog

### Custom Provider

To use a different provider, modify the `ImageGenerationAPI` class in `app/api.py`:
- Update `POLLINATIONS_BASE_URL`
- Modify `generate_image()` method to use the new API
- Add authentication if required

### Generation Parameters

Default generation parameters:
- Width: 512px
- Height: 512px
- Format: PNG

You can modify these in the `GenerationRequest` creation in `main_window.py`.

## Testing

Install pytest and pytest-qt:
```bash
pip install pytest pytest-qt
```

Run tests:
```bash
pytest tests/
```

## Troubleshooting

### PySide6 not found

Make sure you've installed the requirements:
```bash
pip install -r requirements.txt
```

### Application hangs during generation

The application uses threaded generation, so the UI should remain responsive. If it hangs:
- Check your internet connection
- Try a shorter/simpler prompt
- The default timeout is 60 seconds

### Images not displaying

- Make sure the assets directory exists
- Check that the image files were created successfully
- The application supports PNG format by default

### Error: "No module named 'PySide6'"

Install PySide6:
```bash
pip install PySide6
```

## Known Limitations

1. Pollinations.ai has rate limits (approximately 1-2 requests per second)
2. Generated images are limited to 512x512 by default (can be increased)
3. No authentication/authorization system
4. Assets are stored locally only (no cloud sync)
5. Timeline playback is a basic implementation (for single images, it loops)

## Future Enhancements

- [ ] Multiple image generation (batches)
- [ ] Animation frame sequences
- [ ] Custom resolution settings
- [ ] Seed control for reproducible results
- [ ] Asset tags and categories
- [ ] Export animations as video files
- [ ] Drag-and-drop import
- [ ] Theme support (dark/light mode)
- [ ] Keyboard shortcuts
- [ ] Recent prompts history

## License

MIT License - Feel free to use, modify, and distribute.

## Credits

- **Pollinations.ai**: Free AI image generation API
- **PySide6**: Qt for Python bindings
- **Qt**: Cross-platform application framework
