# searching for duplicates and getting info about them in the file tree of a digital library
# run on web server using docker-compose.yml

# duplicates-list.txt = list of all duplicates
# duplicates-info.csv = a file to be opened in a table, contains root, file, pid, model, imageserver link
# duplicates-empty.txt = list of duplicates that are empty
# duplicates-new-file.txt = info, if there's a same imageserver link in another uuid

import os
import re

path = "/data"
uuid_dict = {}
roots_dict = {}
imageserver_dict = {}

image_pattern = re.compile(r'(http://imageserver.mzk.cz/[0-9a-zA-Z-_/]+)/big.jpg')
pid_pattern = re.compile(r'PID="(uuid:([a-z0-9-]+))"')
model_pattern = re.compile(r'model:[a-z]+')


def find_duplicate():
    for roots, dirs, files in os.walk(path):
        for file in files:
            roots_dict[roots] = file
            if file not in uuid_dict.keys():
                uuid_dict[file] = 1
            else:
                uuid_dict[file] += 1
    with open("/app/duplicates-list.txt", "w", encoding="utf-8") as dl:
        for k1, v1 in uuid_dict.items():
            if v1 > 1:
                for k2, v2 in roots_dict.items():
                    if k1 == v2:
                        dl.write(f"{k2}@@{v2}\n")


def get_duplicate_info():
    for key, value in roots_dict.items():
        duplicate_path = os.path.join(key, value)
        duplicate_size = os.path.getsize(duplicate_path)
        if duplicate_size > 0:
            with open(duplicate_path, "r") as dfile, open("/app/duplicates-info.csv", "w") as rfile:
                file_content = dfile.read()
                pid = ""
                match_pid = re.search(pid_pattern, file_content)
                model = ""
                match_model = re.search(model_pattern, file_content)
                imageserver = ""
                match_imageserver = re.search(image_pattern, file_content)
                if match_pid is None:
                    pid = "no PID in file"
                else:
                    pid = match_pid.group(0)
                if match_model is None:
                    model = "model not included"
                else:
                    model = match_model.group(0)
                if match_imageserver is None:
                    imageserver = "no imageserver link"
                else:
                    imageserver = match_imageserver.group(1)
                    imageserver_dict[duplicate_path] = imageserver
                rfile.write(f"{key}@@{value}@@{pid}@@{model}@@{imageserver}\n")
        else:
            with open("/app/duplicates-empty.txt", "a") as empty:
                empty.write(f"{key}@@{value}@@The file is empty.\n")


def find_match_image():
    for roots, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(roots, file)
            if file_path not in imageserver_dict.keys():
                with open(file_path, "r") as fp, open("/app/duplicates-new-file.txt", "a") as nf:
                    file_contents = fp.read()
                    match_image = re.search(image_pattern, file_contents)
                    if match_image is not None:
                        if match_image.group(1) in imageserver_dict.values():
                            nf.write(f"{file}@@{match_image.group(1)}\n")


find_duplicate()
get_duplicate_info()
find_match_image()
uuid_dict.clear()
roots_dict.clear()
imageserver_dict.clear()
