# OCT Image Processing Tool

This tool processes new experimental HoloOCT `.raw` image files from a specified folder according to user-configurable parameters, such as image size, normalization, and averaging settings.
Then outputs the results in a specified directory.

## How to Use
1. Edit the `config.yaml` file to adjust the settings for your specific dataset and requirements.
2. Run the script using the command:
   ```bash
   python main.py
   ```
3. The processed images will be saved in the folder specified in the configuration file.
