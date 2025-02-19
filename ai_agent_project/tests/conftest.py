"""

This Python script modifies the system path by adding the parent directory of the current script file to the start of the system path. This allows the script to import modules and files from the parent directory. 

"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
