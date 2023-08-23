# Get the config file.
import os
config_dir = os.path.dirname( __file__ )
config_fn = 'config.yml'

# Ensure the repository is added to the path
# This should typically be accessible post pip-installation
# But we add it to the path because when hosted on the web that doesn't work necessarily.
import sys
root_dir = os.path.dirname( os.path.dirname( __file__ ) )
if root_dir not in sys.path:
    sys.path.append( root_dir )

# Process any user arguments
import argparse
parser = argparse.ArgumentParser(description="Dashboard script.")
parser.add_argument( '--pagetype', type=str, default='blank_page', help='The type of page to display.' )
args = parser.parse_args()
page_type = args.pagetype

# Call the main function.
import importlib
import root_dash_lib.pages
page_module = getattr( root_dash_lib.pages, page_type )
importlib.reload( page_module )
page_module.main( os.path.join( config_dir, config_fn ) )
