gimp-megadrive-export
---------------------

Export Sega Megadrive/Genesis tiles from Gimp

This is a plug-in for [Gimp](http://www.gimp.org/) for exporting images
as 8x8 tiles for Sega Genesis/Megadrive as asm68k source files.

### Installation

 - Copy **gimp-megadrive-export.py** to your Gimp plugins folder, e.g. 
~/.gimp-2.8/plug-ins/

 - (Skip if you're using Windows) Change file permissions by adding executable bit: ``chmod +x gimp-megadrive-export.py``

 - Restart Gimp

### Use

 - Make sure your image is indexed, with no more than 15 colors (may
   have transparency), use Image > Mode > Indexed.. to convert;

 - Go to File > Export As.., in "All export images" select "Asm68k
   files (*.asm)", click "Select File Type (By Extension)", then
   "Asm68k files";

 - Click "Export";

 - Click "Ok" in file-asm-save dialog box. You can choose whether to use
   COLRW macro (see below) or not;

 - Done. If one or both of your image's dimensions is not a multiple of
   8, the plugin will show a dialog box informing of unexported pixels.

COLRW is an asm68k macro that I use to improve readability of exported
palettes.
With it you can see palette RGB values (0 - 7) in the code, instead of
color components packed into hexadecimal words.

### To do

 - Palette optimization: combine repeating colors into one

 - Tile optimization: add an option to skip repeating tiles