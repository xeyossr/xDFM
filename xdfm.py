#!/usr/bin/env python3
from modules import dfmargs, dfm

home_dir = dfm.home_dir
dot_config_dir = dfm.dot_config_dir
config_dir = dfm.config_dir
config_file = dfmargs.config_file

if __name__ == "__main__":
    dfm.read_config(config_file);
    dfmargs.xdfm()
