import os

GIT_DIR = '.agit'

def init():
    os.makedirs(GIT_DIR)
    print(f'Initialized empty agit repository in {os.getcwd()}/{GIT_DIR}')
