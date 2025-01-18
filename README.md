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