#!/usr/bin/env python3
import sys
import argparse
from time import time as gettime 
from os.path import dirname
from pathlib import Path

from parser.apache_parser import CLIParse
from reference import reference

# добавляем директорию с расположением скрипта в PATH
sys.path.append(dirname(Path(__file__).resolve()))

if __name__ == "__main__":
    parse = argparse.ArgumentParser(
        description="Скрипт для парсинга логов.", 
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    for item in reference:
        parse.add_argument(*item[0], **item[1])

    CLIParse(parse.parse_args())
