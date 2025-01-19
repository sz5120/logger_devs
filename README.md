# EXCITING NEWS:

This should now be able to run without installing python. You should **only** need the .exe file found in the \dist folder, but just in case, you may need the \dist and \build folders. 

Please consider this a 'proof of concept' at this point. Background files will be saved as temporary files however (I believe), so export your csv each time. Eventually, you will be able to select a folder to save background files.

Running it via python (see below) will still create a Data folder in the same directory it's run in, and also a src.json in the same directory.


"# logger_dev" 
INCREDIBLY BUGGY
currently you can search a work ID, hit 'add row' which will write it to a csv in a folder called 'data', and include a date to add with it.

The following non-standard packages are needed:
nicegui
beautifulsoup
unidecode

may possibly also need to install
requests
json
argparse

Honestly, run this in a docker container.

To run: python log_gui.py 


The only two required files are:
log_gui.py
ao3_logger.py

all other files will be created by the program.

src.json includes any fics you have already scraped and exists for testing purposes, so that if a fic has been scraped once, it uses the saved soup. this will not be there in general because fics can and will be updated.
