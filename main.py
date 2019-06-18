# ====================================================================================================================
# This is the script implemented to validate csv file and to check information about billing information and the
# central platform of AXESS.
#
# version: 1.0.0
# author : ppacheco
# date   : 17.06.2019
#
# ====================================================================================================================
import os
import re
import sys
from json import loads
from datetime import datetime
from shutil import move

sys.path.append("./opt/production_axess")


def __get_time__():
    time_now = datetime.utcnow()
    time_str = time_now.strftime("%Y%m%d")
    return time_str


def __get_config__():
    config = loads(open("./config/config.json").read())
    config = config.get("config")
    return config


def __get_dir_name__(action="delete"):
    dir_name = sys.path.__getitem__(len(sys.path) - 1)
    if action == "read":
        dir_name += "/daily_csv/"
    elif action == "archive":
        dir_name += "/archive_csv/"
    else:
        dir_name += "/deleted_csv/"
    return dir_name


def __get_pattern__():
    name = ""
    config = __get_config__()
    name += config.get("country_code")
    name += "_"
    name += __get_time__()
    return name


def __get_file_name__():
    file = ""
    try:
        dir_name = __get_dir_name__(action="read")
        pattern = re.compile(__get_pattern__())
        files = os.listdir(dir_name)
        for file in files:
            matcher = re.search(pattern, file)
            if matcher:
                return file
    except Exception as expt:
        raise BaseException(expt)
    return file


def get_csv_file(action):
    dir_name = __get_dir_name__(action)
    file_name = __get_file_name__()
    file = dir_name + "/" + file_name
    return file


def check_file_name():
    status = "NOK"
    try:
        config = __get_config__()
        file = get_csv_file(action="reader")
        file_name = __get_file_name__()
        country_code = config.get("country_code")
        if country_code in str(file_name[0:2]):
            pattern = re.compile(datetime.strftime(datetime.utcnow(), "%Y%m%d"))
            matcher = re.search(pattern, file_name[3:11])
            print(matcher)
            if matcher:
                status = "OK"
                return status
            else:
                source = __get_dir_name__(action="read")
                source += file
                move(source, __get_dir_name__())
                # generates inconsistence
                return status
        else:
            # generates inconsistence
            move(file, __get_dir_name__())
            return status
    except Exception as expt:
        raise BaseException(expt)


def check_file_age():
    status = "NOK"
    try:
        file = get_csv_file(action="read")
        file_name = __get_file_name__()
        datetime_obj = datetime.strptime(file_name[3:14], '%Y%m%d%H%M%S')
        delta = datetime.date(datetime.utcnow()) - datetime.date(datetime_obj)
        if delta.days < 30:
            status = "OK"
            return status
        else:
            # generates inconsistence
            move(file, __get_dir_name__())
            return status
    except Exception as expt:
        raise BaseException(expt)


def check_file_header():
    status = "NOK"
    try:
        config = __get_config__()
        file = get_csv_file(action="read")
        headers = config.get("csv_file").get("headers")
        for line in open(file, "r", encoding="utf8").readlines():
            elements = line.strip("\n").split(";")
            for index in range(0, len(elements)):
                if str(elements[index]) != str(headers[index]):
                    # generate inconsistences
                    move(file, __get_dir_name__())
                    return status
            break
        status = "OK"
        return status
    except Exception as expt:
        raise BaseException(expt)


print("check_file_header -> {}".format(check_file_header()))
