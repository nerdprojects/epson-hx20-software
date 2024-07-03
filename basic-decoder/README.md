# Epson Binary Decoder

This script converts the binary Epson Basic format to the human-readable format.

## Instructions
Provide your binary Basic file as argument to the script, then the converted output will be printed to stdout.

    ./basic-decoder INPUT.BIN.BAS > OUTPUT.BAS 

Note that the script also prints Basic, that it can decode after the defined file size. However, this goes into stderr along with the status messages.
Therefore you can redirect stdout into a file and will only have the relevant data in it.

## Thanks 
The majority of reverse engineering I could borrow from https://hxtape.sourceforge.net/, thank you 😊!
