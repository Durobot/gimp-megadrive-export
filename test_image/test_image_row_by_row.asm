* macro definition
* narg = number of arguments in macro call
* \1,\2,\3 = macro arguments
* \Label\@ = label that will be expanded with a number to make
*            it unique in each macro expansion
* ifne 	  ; print error message

; Pack RGB data like so: ----bbb-ggg-rrr-
COLRW	MACRO		; Define word constant, representing a palette color entry (R, G, B must be within 0-7 range)
	IFNE narg-3		; narg minus 3 != 0
	FAIL COLRW needs three arguments:  COLRW R,G,B
	ENDC
	; Spaces between expression elements ruin everything
	dc.w	(\1<<1)|(\2<<5)|(\3<<9)
	ENDM

; ---------- Example of use --------
;	dc.w	(2<<1)|(3<<5)|4<<9)	; R, G, B
;	is the same as
;	COLRW	2,3,4

	; --- Palette ---
	dc.w	$0000	;	Color 0 is transparent (so actual value doesn't matter)
	COLRW	0,0,7	;	Color 1
	COLRW	0,7,0	;	Color 2
	COLRW	7,7,0	;	Color 3
	COLRW	7,0,0	;	Color 4

	; --- Tiles ---
	dc.l	$11111111	;	Tile (col 0, row 0)
	dc.l	$11111111
	dc.l	$11111111
	dc.l	$11111111
	dc.l	$11111111
	dc.l	$11111111
	dc.l	$11111111
	dc.l	$11111111
	dc.l	$22222222	;	Tile (col 1, row 0)
	dc.l	$22222222
	dc.l	$22222222
	dc.l	$22222222
	dc.l	$22222222
	dc.l	$22222222
	dc.l	$22222222
	dc.l	$22222222
	dc.l	$33333333	;	Tile (col 0, row 1)
	dc.l	$33333333
	dc.l	$33333333
	dc.l	$33333333
	dc.l	$33333333
	dc.l	$33333333
	dc.l	$33333333
	dc.l	$33333333
	dc.l	$44444444	;	Tile (col 1, row 1)
	dc.l	$44444444
	dc.l	$44444444
	dc.l	$44444444
	dc.l	$44444444
	dc.l	$44444444
	dc.l	$44444444
	dc.l	$44444444
