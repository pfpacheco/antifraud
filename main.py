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


sys.path.append("./opt/production_axess")


def __get_time__():
    time_now = datetime.utcnow()
    time_str = time_now.strftime("%Y%m%d")
    return time_str


def __get_config__():
    config = loads(open("./config/config.json").read())
    config = config.get("config")
    return config


def __get_dir_name__(action="read"):
    dir_name = sys.path.__getitem__(len(sys.path) - 1)
    if action == "read":
        dir_name += "/daily_csv/"
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
        # generates inconsistence
        raise BaseException(expt)
    return file


def __get_csv_file__():
    dir_name = __get_dir_name__(action="read")
    file_name = __get_file_name__()
    file = dir_name + "/" + file_name
    return file


def __check_file_name__():
    status = "NOK"
    try:
        config = __get_config__()
        file = __get_csv_file__()
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
                # generates inconsistence
                os.remove(file)
                return status
        else:
            # generates inconsistence
            os.remove(file)
            return status
    except Exception as expt:
        # generates inconsistence
        raise BaseException(expt)


def __check_file_age_():
    status = "NOK"
    try:
        file = __get_csv_file__()
        file_name = __get_file_name__()
        datetime_obj = datetime.strptime(file_name[3:14], '%Y%m%d%H%M%S')
        delta = datetime.date(datetime.utcnow()) - datetime.date(datetime_obj)
        if delta.days < 30:
            status = "OK"
            return status
        else:
            # generates inconsistence
            os.remove(file)
            return status
    except Exception as expt:
        # generates inconsistence
        raise BaseException(expt)


def __check_file_header__():
    status = "NOK"
    try:
        config = __get_config__()
        file = __get_csv_file__()
        headers = config.get("csv_file").get("headers")
        for line in open(file, "r", encoding="utf8").readlines():
            elements = line.strip("\n").split(";")
            for index in range(0, len(elements)):
                if str(elements[index]) != str(headers[index]):
                    # generate inconsistences
                    os.remove(file)
                    return status
            break
        status = "OK"
        return status
    except Exception as expt:
        # generates inconsistence
        raise BaseException(expt)


def __get_customers__():
    customers = dict()
    try:
        file = __get_csv_file__()
        for index in range(0, len(open(file, "r", encoding="utf8").readlines())):
            if index > 0:
                line = open(file, "r", encoding="utf8").readlines()[index]
                elements = line.strip("\n").split(";")
                customers.update(
                    {
                        "customer{}".format(str(index)):
                        {
                            "customerid": elements[0],
                            "serviceid": elements[1],
                            "cpeid": elements[2],
                            "value1": elements[3],
                            "value2": elements[4],
                            "value3": elements[5],
                            "kbps": elements[6],
                            "spgt": elements[7],
                            "lineauno": elements[8],
                            "lineados": elements[9],
                            "macmta": elements[10],
                            "idsuspension": elements[11],
                            "nombrecli": elements[12]
                        }
                    }
                )
        return customers
    except Exception as expt:
        # generates inconsistence
        raise BaseException(expt)


def __check_duplicate_customers__():
    results = dict()
    try:
        normalized = dict()
        customers = __get_customers__()
        for customer in customers.values():
            service_id = customer.get("serviceid")
            for comparable in customers.values():
                if service_id == comparable.get("serviceid"):
                    normalized.update(
                        {
                            "customer_{}".format(comparable.get("customerid")):
                            {
                                "customerid": comparable.get("customerid"),
                                "serviceid": comparable.get("serviceid"),
                                "cpeid": comparable.get("cpeid"),
                                "value1": comparable.get("value1"),
                                "value2": comparable.get("value2"),
                                "value3": comparable.get("value3"),
                                "kbps": comparable.get("kbps"),
                                "spgt": comparable.get("spgt"),
                                "lineauno": comparable.get("lineauno"),
                                "lineados": comparable.get("lineados"),
                                "macmta": comparable.get("macmta"),
                                "idsuspension": comparable.get("idsuspension"),
                                "nombrecli": comparable.get("nombrecli")
                            }
                        }
                    )
        results.update(
            {
                "normalized": normalized
            }
        )
        return results
    except Exception as expt:
        # generates inconsistence
        raise BaseException(expt)


print("check_duplicate_customsers -> {}".format(__check_duplicate_customers__()))
