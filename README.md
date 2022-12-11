README for Gits: First Assault Online Upscaler v0.0.2
=====================================================
![Comparison](https://user-images.githubusercontent.com/5176531/206932845-f1a72f4d-1e27-4094-82a0-978de743ca8b.png)

What is this?
=============

This is a simple upscaler for Gits: First Assault Online. It uses the
ESRGAN model or waifu2x to upscale the game's textures. It is not perfect, 
but it does a decent job.

How to use
==========
1. Download the latest release from the releases page on github (https://github.com/hrkrx/GITSU/releases)
2. Ensure you have Python 3.9 or 3.10 installed (3.11 is not working yet)
3. Install ImageMagick (https://imagemagick.org/script/download.php)
4. Run the upscaler by double clicking the "start.bat" file
5. Click "Start"
6. Choose the model you want to use (ESRGAN or waifu2x)
```
If you choose ESRGAN be sure you don't need your computer for anything else while it's running as it will use all your CPU cores (it takes a long time)

If you choose waifu2x you can choose the noise reduction level (1-3) and the scale factor (2, 3, 4) and the model (cunet, anime_style_art_rgb, photo)
```
7. Choose the texture group you want to upscale (you can upscale multiple groups at once)
8. Choose the max resolution of the final upscaled images (2048 -> performance | 4096 -> more details | 8192 -> max quality)
9. Enter the path to the game's directory (the one that contains the "Data" folder)
10. Optionally enter the path to the quickbms executable, if you don't a python script will be used to extract the textures, which is way slower (https://aluigi.altervista.org/quickbms.htm#:~:text=Compiled%20versions%20of%20QuickBMS%3A)
11. Click "OK"
12. Wait for the upscaling to finish

Additional notes
================
- The upscaler can resume if it crashes or you close it (since version 0.0.2)
- The upscaler will create a backup of the original dat files named .dat.bak
- The upscaler will use a temporary folder in the same directory as the upscaler
