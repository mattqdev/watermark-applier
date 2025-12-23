# Watermark Applier
A Python script that intelligently applies watermarks to images. It doesn't just paste an image; it analyzes the background to find the best placement and automatically adjusts the watermark color (white/black) and opacity based on the image's brightness and complexity.

## ✨ Features

- **Smart Positioning**: Analyzes the "chaos" (standard deviation) of the bottom-right corner. If it's too busy, it tries the bottom-center to find a "calmer" area.

- **Auto-Inversion**: Automatically detects if the background is too light and inverts the watermark to a dark version for better visibility.

- **Dynamic Opacity**: Adjusts transparency based on the background brightness to ensure the watermark is readable but not intrusive.

- **Recursive Processing**: Can scan through entire folder structures, maintaining the original directory hierarchy in the output.

- **Customizable Padding**: Set a specific pixel distance from the bottom for precise alignment.

## 🚀 Getting Started
### Prerequisites
You will need Python 3.x and the Pillow library.

```Bash
pip install Pillow
```
### Installation

Clone this repository:

```Bash
git clone https://github.com/mattqdev/watermark-applier.git
```

Place your images in an inputs folder.

Place your watermark (preferably a white PNG with transparency) in the root folder.

🛠 Usage
Modify the parameters in the apply_watermark function call at the bottom of the script:

```Python

apply_watermark(
    input_folder="inputs",      # Path to your source images
    output_folder="output",    # Where saved images will go
    watermark_path="wm.png",   # Your watermark file
    recursive=True,            # Check for images also in subfolders
    width_percent=25,          # Size of watermark relative to image width
    bottom_padding=40,         # Fixed pixel distance from bottom
    auto_invert=True,          # If background brightness > inversion_threshold then invert the image
    inversion_threshold=180,   # Thresold for inverting watermark (white -> black)
    check_empty_space=True,    # Looks for "calm" space
    chaos_threshold=30         # Sensitivity to "busy" backgrounds
)
```
Run the script:

```Bash
python main.py
```

## ⚙️ How it Works
- **Luminance Analysis**: The script converts the area under the watermark to grayscale to calculate the average brightness.

- **Chaos Detection**: It calculates the standard deviation of pixels. A high value means the area has high contrast/detail (like text or foliage), making a watermark hard to read.

- **Fallback Logic**: If the default corner is too "chaotic," the script compares it to the center position and chooses the clearest one.

## 📄 License
This project is open-source and available under the MIT License.