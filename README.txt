╔═══════════════════════════════════════════════════════╗
║ README for Gits: First Assault Online Upscaler v0.0.1 ║
╚═══════════════════════════════════════════════════════╝

What is this?
=============

This is a simple upscaler for Gits: First Assault Online. It uses the
ESRGAN model or waifu2x to upscale the game's textures. It is not perfect, 
but it does a decent job.

How to use
==========
1. Download the latest release from the releases page on github (If you read this you probably already did that)
2. Ensure you have Python 3.9 or 3.10 installed (3.11 is not working yet)
3. Install ImageMagick (https://imagemagick.org/script/download.php)
4. Run the upscaler by double clicking the "start.bat" file
5. Click "Start"
6. Choose the model you want to use (ESRGAN or waifu2x)
    6.1 If you choose ESRGAN be sure you don't need your computer for anything else while it's running as it will use all your CPU cores (it takes a long time)
    6.2 If you choose waifu2x you can choose the noise reduction level (1-3) and the scale factor (2, 3, 4) and the model (cunet, anime_style_art_rgb, photo)
7. Choose the texture group you want to upscale (you can upscale multiple groups at once)
8. Enter the path to the game's directory (the one that contains the "Data" folder)
9. Optionally enter the path to the quickbms executable, if you don't a python script will be used to extract the textures, which is way slower
10. Click "OK"
11. Wait for the upscaling to finish

Additional notes
================
- The upscaler can resume if it crashes or you close it (since version 0.0.2)
- The upscaler will create a backup of the original dat files named .dat.bak
- The upscaler will use a temporary folder in the same directory as the upscaler