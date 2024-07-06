
# Tape Recover Software

Scripts that can be used to extract Epson HX-20 files from tape recordings.

## Scripts
- tape-recover.py -> Extracts raw block information from a tape recording (step 1)
- merge-blocks.py -> Merges the recovered blocks together into the original file (step 2)
- decode_functions.py -> Contains different algorithms for signal decoding (not intended to be directly invoked)
- extract_functions.py -> Contains the block extract algorithm (not intended to be directly invoked)

## Instructions
### Create a Tape Recording
I use a Microcasette recorder / player for this:
<img src="https://raw.githubusercontent.com/nerdprojects/epson-hx20-software/main/tape-recover/microcasette-dictaphone.jpg"/>

I connect the headphone output of the player to the input jack of my laptop and record it with Audacity.
Make sure you setup a mono channel recording. 

The script should be able to handle different sample rates and bit-depths. I normally use CD quality: 44.1 khz / 16 bit. But 22.05 khz / 8 bit also work.

### Recover Block Information
To recover block data from a .wav file, the tape-recover.py script can be run.

I make a folder with the same name as the .wav file, for the blocks files:

    mkdir test_recording
    cd test_recording

There are different algorithms that I came up with, which recover data differently. Zerocross works best most of the time:

    ../tape-recover.py zerocross test_recording.wav

For every identified block, a file is created:

    test_recording_0116319_H_0_0_OK.block
    test_recording_0134416_H_0_1_OK.block
    test_recording_0219248_D_1_1_OK.block
    test_recording_0262681_D_2_0_OK.block
    test_recording_0306436_D_2_1_OK.block
    test_recording_0350233_D_3_0_OK.block
    test_recording_0393935_D_3_1_OK.block
    test_recording_0437627_D_4_0_ERROR.block
    test_recording_0481476_D_4_1_OK.block
    ...
    test_recording_1585841_D_17_0_OK.block
    test_recording_1629923_D_17_1_OK.block
    test_recording_1693650_E_18_0_OK.block
    test_recording_1711803_E_18_1_OK.block

There are header (H), data (D) and end (E) blocks. On failed extraction, the block is flagged with ERROR.
Becasue the HX-20 stores every block twice for reliability, there are two files for every block.

If desired, the block files can be inspected with a hex editor. For example the header blocks contain the original file name, file type and the creation date:

    xxd test_recording_0116319_H_0_0_OK.block
    00000000: 4844 5231 5441 5045 5f52 4543 2020 2000  HDR1TAPE_REC   .
    00000010: 0000 0000 3253 2020 3235 3620 2020 2020  ....2S  256     
    00000020: 3037 3036 3234 3137 3030 3134 2020 2020  070624170014    
    00000030: 2020 2020 4858 2d32 3020 2020 0000 0000      HX-20   ....
    00000040: 0000 0000 0000 0000 0000 0000 0000 0000  ................
    
The strings command can also be used to look for interesting data, also in bad blocks.

### Merge Good Blocks
The merge-block.py script can be run to merge all blocks and recreate the original file.
Provide the file prefix as parameter to the script. Most of the time, this will be the .wav file name without the .wav ending:

    ../merge-blocks.py test_recording

If the script finds a valid block file for every block, it will recover the original file. Depending on the file type it will create a .BAS, .DATA or .ASM file.

### Failed Recoveries
Fixing bad recordings is currently manual labor.

You can try to use the peak algorithm instead of the zerocross:

    ../tape-recover.py peak test_recording.wav

Or try to detect issues with the plot functionality:

    ../tape-recover.py zerocross test_recording.wav 0.0 plot
   
<img src="https://raw.githubusercontent.com/nerdprojects/epson-hx20-software/main/tape-recover/zerocross-plot.png"/>

For long recordings, it makes sense to create a trimmed .wav file only containing the defective audio section. Otherwise, the plot functionality is very slow, as all samples are plotted. It is not optimized in any way.

Playing around with the dc-offset or peak-threshold values might also be an option and also try to fix things in Audacity.

But to debug issues efficiently, some knowledge of the Epson HX-20 recording scheme and the zerocross / peak algorithms is needed.

I hope I have time for (and feel like doing) an in depth blog article about this at some point 😬...

