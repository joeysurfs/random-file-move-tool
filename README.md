# Random File Move Tool

## Overview
A Python GUI application that helps you randomly select and move/copy files between folders. Perfect for organizing files, creating random sample sets, or managing media collections.

## Features
- Select source and destination folders
- Choose number of files to process
- Filter by file types (Pictures, Videos, Documents, Music, etc.)
- Move or copy files
- Preview images when moving picture files
- Undo last operation
- Dark theme interface
- Progress tracking
- Operation logging

## Requirements
- Python 3.7+
- Pillow (PIL)
- tkinter (usually comes with Python)

## Installation
1. Clone this repository
2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage
1. Run the application:
```bash
python app.py
```
2. Select your source folder (where files are located)
3. Select your destination folder (where files will go)
4. Configure options:
   - Number of files to process
   - File type filter
   - Move or Copy operation
5. Click "Process Files" to begin
6. Use "Undo Last" if needed to reverse the last operation

## Notes
- The image preview works for common image formats (jpg, png, gif, etc.)
- Operations are logged in 'file_mover.log'
- The application maintains aspect ratios when displaying image previews

## Contributing
Feel free to submit issues or pull requests for improvements or bug fixes. 

## License
This project is licensed under the MIT License.