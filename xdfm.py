#!/usr/bin/env python3
import argparse
import argcomplete 
import os
import sys
import click
import configparser
import colorama
from modules import dfmargs, dfm
from git import Repo
from github import Github
from pathlib import Path


home_dir = Path(os.path.expanduser('~'))
dot_config_dir = Path(os.path.join(home_dir, '.config'))
config_dir = Path(os.path.join(dot_config_dir, 'xdfm'))
config_file = Path(os.path.join(config_dir, 'xdfm.conf'))

if __name__ == "__main__":
    dfm.read_config(config_file);
    dfmargs.xdfm()
