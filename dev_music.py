#!/usr/bin/env python

"""dev_music

Use the /dev/audio device file to play musical notes on UNIX systems.

Created by Caoilte Guiry

License: BSD License

Sample Usage:
$ python dev_music.py  -i input_file.txt

Input File Format:
<note>, <duration>
<note>, <duration>
...

where <note> is a musical note in the range [A-G#] (flat notes, e.g. Bb, are
currently not supported), and duration is the length you wish to play that 
note.


Example Input File:
A, 0.2
B, 0.2
C, 0.1
B, 0.1
C, 0.1
A, 0.4
D, 0.4
A, 0.2
B, 0.2
C, 0.1
B, 0.1
C, 0.1
A, 0.4
D, 0.4


TODOs: 
* Allow specification of note delimiter in the input file (currently assumed as
  being the newline character).
* Allow specification of note/duration delimiter (currently assumed as being 
  comma).
* In fact, use a proper input file format (perhaps try to find something 
  standardised)
* Add --tempo option
* Add aliases for flat notes (e.g. Bb->A#)
* Set upper limit on duration?
* Implement REPL?
* Document how this works a bit better.

"""

from __future__ import with_statement
import os
import sys
from optparse import OptionParser

__author__ = "Caoilte Guiry"
__copyright__ = "Copyright (c) 2011 Caoilte Guiry."
__version__ = "0.0.1"
__license__ = "BSD License"


# The NOTES dict represents the notes and their associated number of 
# characters per line, e.g. for a D#, you would require a sequence of:
#     cccccccccccc
#     cccccccccccc
#     ...
# where c is an arbitrary character. 

NOTES = {
"E":23, 
"F":22, 
"F#":21, 
"G":20, 
"G#":19, 
"A":18, 
"A#":17, 
"B":16,
"C":15, 
"C#":14, 
"D":13, 
"D#":12,
}

# time playing a character consumes (imperical and very approximate)
CHAR_DURATION = 0.000125 


class DevMusicError(Exception):
    """Parent exception type for dev_music."""
    pass

class InvalidNoteError(DevMusicError):
    """An invalid note was specified."""
    def __init__(self, note):
        self.note = note
        self.value = "Invalid Note '%s'" % note
    def __str__(self):
        return repr(self.value)

class InvalidDurationError(DevMusicError):
    """An invalid note duration was specified."""
    def __init__(self, duration):
        self.duration = duration
        self.value = "Invalid Duration '%s'" % duration
    def __str__(self):
        return repr(self.value)



def get_text_stream(note, duration):
    """Return a text stream for a specified note and duration."""
    # normalise inputs
    note = note.upper()

    try:
        duration = float(duration)  
    except ValueError:
        raise InvalidDurationError(duration)

    try:
        chars_per_line = NOTES[note]
    except KeyError:
        raise InvalidNoteError(note)
    lines_required = int(duration/(CHAR_DURATION*chars_per_line))    
    
    # 'c' is an arbitrary character 
    return ("c"*chars_per_line+"\n")*lines_required


def main():
    """Parse args/options, read input file and write streams to /dev/audio."""
    # First, verify we have a /dev/audio
    if not os.path.exists("/dev/audio"):
        print "Sorry, your OS does not have a /dev/audio device file"
        sys.exit(1)

    parser = OptionParser()
    parser.add_option("-i", "--input-file", dest="input_file",
                      help="The name of the input file", 
                      metavar="<input_file>", default=None)
    options, args = parser.parse_args()

    if not options.input_file:
        print "You must specify an input file"
        parser.print_usage()
        sys.exit(1)

    try:
        with open(options.input_file) as input_fh:
            try:
                with open("/dev/audio", "w") as devaudio_fh:
                    for line in input_fh.readlines():
                        note, duration = line.rstrip().split(",")
                        data = get_text_stream(note, duration)
                        devaudio_fh.write(data)

            except IOError:
                print "Failed to open /dev/audio for writing"
                sys.exit(1) 
            except DevMusicError, error_msg:
                print error_msg
                sys.exit(1)
    except IOError:
        print "Error: Could not open input file '%s' for reading." % \
              (options.input_file)
        sys.exit(1)
    
if __name__ == "__main__":
    sys.exit(main())
