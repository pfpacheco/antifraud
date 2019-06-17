# ====================================================================================================================
#
#
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


def get_csv_file():
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


def check_file_name():
    status = "NOK"
    try:
        config = __get_config__()
        file_name = get_csv_file()
        dir_name = __get_dir_name__(action="read")
        file = dir_name + "/" + get_csv_file()
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
        dir_name = __get_dir_name__(action="read")
        file = dir_name + "/" + get_csv_file()
        file_name = get_csv_file()
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
        dir_name = __get_dir_name__(action="read")
        file = dir_name + "/" + get_csv_file()
        header = config.get("csv_file").get("headers")
        for line in open(file, "r", encoding="utf8").readlines():
            elements = line.split(";")
            for index in range(len(elements)):
                if header[index] != elements[index]:
                    # generate inconsistences
                    move(file, __get_dir_name__())
                    return status
                else:
                    status = "OK"
        return status
    except Exception as expt:
        raise BaseException(expt)
    return status
    

print("check_file_header -> {}".format(check_file_header()))
