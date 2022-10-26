# Name: Philipp Plamper
# Date: 26. october 2022

import os 
import sys
abs_path = os.path.split(os.path.dirname(os.path.abspath(__file__))) # get system path to files
path_prefix = str(abs_path[0])
sys.path.insert(0, path_prefix)