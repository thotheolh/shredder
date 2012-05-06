#!/usr/bin/env python

import os

## Utility class.
class util():

    ## Get the relative working path of the current files
    def get_resource(self, rel_path):
        dir_of_py_file = os.path.dirname(__file__)
        rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
        abs_path_to_resource = os.path.abspath(rel_path_to_resource)
        return abs_path_to_resource

    def str2bool(self, var):
        return var.lower() in ("yes", "true", "t", "1")
