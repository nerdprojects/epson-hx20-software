# Image Viewer Programs
With these programs, I checked how fast I can display images on the HX-20.

## Programs
- viewer.asm -> Final program I came up with, can be used to display images and fluid animations.
- convert-png-to-asm.py -> Converts a png image to assembly data definitions.
- convert-png-to-bas.py -> Converts a png image to a BASIC script that displays the image.
- speed-test-dispit.asm -> Test to check the speed of the ASM subroutine DISPIT.
- speed-test-print -> Test to check the speed of the BASIC command PRINT.
- speed-test-pset.bas -> Test to check the speed of the BASIC command PSET.
- examples/carlton.b -> Compiled animation of Carlton from Fresh Prince. Original GIF created by Gustavo Viselner.
- examples/geometry.b -> Compiled animation of 3 spinning geometric shapes.
- examples/tunnel.b -> Compiled endless tunnel animation.

## Notes
The viewer program can be used to display single images or multiple images as animation on the HX-20 internal display.
Because the onboard BASIC command PSET and the ASM subroutine DISPIT are quire slow,
the program accesses the rather low level ASM subroutines WRTP26, LCDMOD and DATAMOD to fill the screen with data. I put this together by looking at the code listings of the firmwares LCD driver routines in the Software Manual on page 3-8. The Python script convert-png-to-asm.py

## Instructions
You can create your own animations, by:
1. Create all animation frames as 120x32 sized 8 bit grayscale PNG files.
3. Generate the assembly FCB definitions of all the frames with the convert-png-to-asm.py script and append them to viewer.asm at the label "IMGSTA" after line 128.
4. If you want to adjust the delay between the frames, you can changed the code from line 108 to 113
5. Assemble the adjusted viewer.asm and load it to the EPSON with the loader scripts and execute it.


 