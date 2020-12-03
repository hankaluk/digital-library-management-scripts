# searching for duplicates and getting info about them in the file tree of a digital library
# run on web server using docker-compose.yml

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
    for roots, dirs, files in os.walk(path, topdown=False):
        for file in files:
            roots_dict[roots] = file
            if file not in uuid_dict.keys():
                uuid_dict[file] = 1
            else:
                uuid_dict[file] += 1
    with open("/app/duplicates-list.txt", "w", encoding="utf-8") as f:
        for key, value in uuid_dict.items():
            if value > 1:
                for root, filename in roots_dict.items():
                    if key == filename:
                        f.write(f"{root}@@{filename}")


def get_duplicate_info():
    for key, value in roots_dict.items():
        duplicate_path = os.path.join(key, value)
        duplicate_size = os.path.getsize(duplicate_path)
        if duplicate_size > 0:
            with open(duplicate_path, "r") as d_file, open("/app/duplicates-info.csv", "w") as r_file:
                file_content = d_file.read()
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
                r_file.write(f"{key}@@{value}@@{pid}@@{model}@@{imageserver}")


def find_match_image():
    for roots, dirs, files in os.walk(path, topdown=False):
        for file in files:
            file_path = os.path.join(roots, file)
            if file_path not in imageserver_dict.keys():
                with open(file_path, "r") as fp, open("/app/duplicates-new-file.txt", "w") as nf:
                    file_contents = fp.read()
                    match_image = re.search(image_pattern, file_contents)
                    if match_image is not None:
                        if match_image.group(1) in imageserver_dict.values():
                            nf.write(f"{file}@@{match_image.group(1)}")


find_duplicate()
get_duplicate_info()
find_match_image()