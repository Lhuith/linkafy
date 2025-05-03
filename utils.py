# what titles and artists will be split by cause
# this industry can't make up its mind
import datetime
import glob
import os

fileSeperator = '*'
dicSeperator = '>>>'
extSeperator = '::'


# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
# thanks joeld, Peter Mortensen (E)
class bcolors:
    OKMEG = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_p(message):
    print(bcolors.OKMEG + message)


def print_c(message):
    print(bcolors.OKCYAN + message)


def print_w(message):
    print(bcolors.ENDC + message)


def print_y(message):
    print(bcolors.WARNING + message)


def print_r(message):
    print(bcolors.FAIL + message)


def print_b(message):
    print(bcolors.OKBLUE + message)


def print_g(message):
    print(bcolors.OKGREEN + message)


def file_exists(file_path):
    return os.path.exists(file_path)


def file_to_dict(file_path):
    output = dict()
    if not file_exists(file_path):
        print_r(f"file {file_path} does not exist")
        return output

    file = open(file_path, encoding="utf-8")
    for line in file.readlines():
        songSplit = line.rstrip('\n').split(dicSeperator)
        if len(songSplit) != 2:
            print_r(f"file is not properly formatted for dictionary parsing")
            break
        output[songSplit[0].strip()] = songSplit[1].strip()
    file.close()
    return output


def file_to_array(file_path):
    output = []

    if not file_exists(file_path):
        print_r(f"file {file_path} does not exist")
        return output

    file = open(file_path, encoding="utf-8")
    for line in file.readlines():
        output.append(line.rstrip('\n').strip())
    file.close()
    return output


def time_pretty():
    return datetime.datetime.now()


def get_files_by_ext(folder_path, extensions):
    return [g for ext in extensions for g in glob.glob(folder_path + f'/*.{ext}')]
