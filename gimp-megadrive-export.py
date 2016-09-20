#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2016 Alexei Kireev

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
### Installation

 - Copy **gimp-megadrive-export.py** to your Gimp plugins folder, e.g. 
~/.gimp-2.8/plug-ins/

 - Change file permissions by adding executable bit: ``chmod +x gimp-megadrive-export.py``

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
"""

from gimpfu import *
import platform


def export_to_asm(image, drawable, filename, rawfilename, dummy1, use_palette_macro):
    gimp_tile_width = gimp.tile_width()
    if gimp_tile_width % 8 != 0 or gimp_tile_width <= 0:
        gimp.pdb.gimp_message("GIMP reports tile width = {}, which is not a multiple of 8.\n"
                              "Sorry, but export plugin can't work in this environment.".format(gimp_tile_width))
        gimp.quit()
    gimp_tile_height = gimp.tile_height()
    if gimp_tile_height % 8 != 0 or gimp_tile_height <= 0:
        gimp.pdb.gimp_message("GIMP reports tile height = {}, which is not a multiple of 8.\n"
                              "Sorry, but export plugin can't work in this environment.".format(gimp_tile_height))
        gimp.quit()

    if pdb.gimp_drawable_type(drawable) not in (INDEXED_IMAGE, INDEXEDA_IMAGE):
        gimp.pdb.gimp_message("This image is not in indexed mode, use Image > Mode > Indexed..")
        gimp.quit()

    colmap = pdb.gimp_image_get_colormap(image)
    if colmap[0] > 15 * 3:  # No more than 15 colors
        gimp.pdb.gimp_message("Too many colors, must have 15 + transparency or less")
        gimp.quit()

    message = ""
    if drawable.width % 8 != 0:
        message = "Image width ({}) is not a multiple of 8. " \
                  "Because of that, {} pixel columns weren't exported.".format(drawable.width, drawable.width % 8)
    if drawable.height % 8 != 0:
        if message != "":
            message += "\n"
        message += "Image height ({}) is not a multiple of 8. " \
                   "Because of that, {} pixel rows weren't exported.".format(drawable.height, drawable.height % 8)

    # Platform-specific EOL bytes (<CR><LF> for Windows, <LF> for others, like Linux or OS X)
    if platform.system().upper().startswith("WINDOWS"):
        newline = "\r\n"
    else:
        newline = "\n"

    # -----------------------------------------

    out_file = open(filename, "w")
    export_palette(out_file, colmap, use_palette_macro, newline)
    out_file.write(newline + newline)

    sega_tile_cols = int(drawable.width / 8)  # We have already made sure that image width is a multipe of 8
    sega_tile_rows = int(drawable.height / 8)  # We have made already sure that image height is a multipe of 8
    out_file.write("	; --- Tiles ---" + newline)
    #
    for sega_tile_col_idx in range(sega_tile_cols):
        start_x = sega_tile_col_idx * 8
        gimp_tile_col = start_x / gimp_tile_width
        for sega_tile_row_idx in range(sega_tile_rows):
            start_y = sega_tile_row_idx * 8
            gimp_tile_row = start_y / gimp_tile_height
            export_sega_tile(out_file, drawable.get_tile(shadow=False, row=gimp_tile_row, col=gimp_tile_col),
                             start_x - gimp_tile_col * gimp_tile_width, start_y - gimp_tile_row * gimp_tile_height,
                             drawable.has_alpha, "(col {}, row {})".format(sega_tile_col_idx, sega_tile_row_idx), newline)
            out_file.write(newline)
    out_file.close()

    # -----------------------------------------

    if message != "":
        gimp.pdb.gimp_message(message)


def export_palette(out_file, colmap, use_palette_macro, newline):
    def rgb_elem_to_sega(col_elem):
        # Map 8-bit range of a color element (R, G or B) to 3-bit Sega range (values = 0..7)
        return int(round(float(col_elem) / 255.0 * 7.0))

    if use_palette_macro:
        export_macro(out_file, newline)
        out_file.write(newline + newline)

    out_file.write("	; --- Palette ---" + newline)
    colors = colmap[1]
    out_file.write("	dc.w	$0000	;	Color 0 is transparent (so actual value doesn't matter)" + newline)
    for i in range(0, colmap[0] - 2, 3):
        if use_palette_macro:
            out_file.write("	COLRW	{},{},{}	;	Color {}".format(rgb_elem_to_sega(colors[i]),
                                                                          rgb_elem_to_sega(colors[i + 1]),
                                                                          rgb_elem_to_sega(colors[i + 2]),
                                                                          hex((i + 3) / 3)[2:]))
        else:
            palette_entry = (rgb_elem_to_sega(colors[i]) << 1) | (rgb_elem_to_sega(colors[i + 1]) << 5) | \
                (rgb_elem_to_sega(colors[i + 2]) << 9)  # ----bbb-ggg-rrr-
            out_file.write("	dc.w	${}	;	Color {}".format(hex(palette_entry)[2:].zfill(4),
                                                                 hex((i + 3) / 3)[2:]))
        if i < colmap[0] - 3:
            out_file.write(newline)


def export_macro(out_file, newline):
    out_file.write("* macro definition" + newline)
    out_file.write("* narg = number of arguments in macro call" + newline)
    out_file.write("* \\1,\\2,\\3 = macro arguments" + newline)
    out_file.write("* \\Label\\@ = label that will be expanded with a number to make" + newline)
    out_file.write("*            it unique in each macro expansion" + newline)
    out_file.write("* ifne 	  ; print error message" + newline + newline)

    out_file.write("; Pack RGB data like so: ----bbb-ggg-rrr-" + newline)
    out_file.write("COLRW	MACRO       ; Define word constant, representing a palette color entry (R, G, B must be within 0-7 range)" + newline)
    out_file.write("	IFNE narg-3	; narg minus 3 != 0" + newline)
    out_file.write("	FAIL COLRW needs three arguments:  COLRW R,G,B" + newline)
    out_file.write("	ENDC" + newline)
    out_file.write("	; Spaces between expression elements ruin everything" + newline)
    out_file.write("	dc.w	(\\1<<1)|(\\2<<5)|(\\3<<9)" + newline)
    out_file.write("	ENDM" + newline + newline)

    out_file.write("; ---------- Example of use --------" + newline)
    out_file.write(";	dc.w	(2<<1)|(3<<5)|4<<9)	; R, G, B" + newline)
    out_file.write(";	is the same as" + newline)
    out_file.write(";	COLRW	2,3,4")


def export_sega_tile(out_file, tile, start_x, start_y, has_alpha, tile_name, newline):
    """
    Export one Sega Genesis tile (8x8 pixels), NOT Gimp tile (64x64 pixels).
    Note that
        tile parameter is Gimp tile,
        start_x and start_y indicate the top left corner of 8x8 area to be exported.
    """
    for y in range(start_y, start_y + 8):
        shift_left_by = 28
        long_word = 0
        for x in range(start_x, start_x + 8):
            if has_alpha:
                # Images with alpha channel return two bytes per pixel - #0 is color index, #1 is opacity
                color_bytes = tile[x, y]
                color_idx = color_bytes[0]
                is_opaque = (color_bytes[1] == '\xff')
            else:
                # Images w/o alpha channel give you just one byte per pixel - color index
                color_idx = tile[x, y]
                is_opaque = True
            if is_opaque:  # Transparent pixel?
                long_word |= (ord(color_idx) + 1) << shift_left_by  # + 1 because color 0 is always transparent
            # If the pixel IS transparent, do nothing, as transparent color in all Sega palettes is color 0
            shift_left_by -= 4
        #
        out_file.write("	dc.l	${}".format(hex(long_word)[2:].zfill(8)))  # Because hex() can't add leading 0's
        if y == start_y:
            out_file.write("	;	Tile {}".format(tile_name))
        if y < start_y + 7:
            out_file.write(newline)


def register_save():
    gimp.register_save_handler("file-asm-save", "asm", "")


register("file-asm-save",
         "Asm68k Sega Genesis/Megadrive tile exporter",
         "This script exports 8x8 tiles for Sega Genesis/Megadrive.\n"
         "Your image must be in indexed format and have not more than 15 colors (may have transparency).",
         "Alexei Kireev",
         "Copyright 2016 Alexei Kireev",
         "2016-09-19",
         "<Save>/Asm68k files",
         "*",  # All image types, including RGB and grayscale - we tell the user what they have to do to convert the image to indexed
         [
             (PF_BOOL, "use_palette_macro", "Export and use COLRW macro:", True),  # I don't know why, but the first parameter is ignored
             (PF_BOOL, "use_palette_macro", "Export and use COLRW macro:", True),  # So I have added the first parameter to actually be able to use this one
         ],
         [],
         export_to_asm,
         on_query=register_save)

main()