from datetime import datetime


def get_new_name_by_date():
    """ Get a string formatted with the date at the moment it is called
    Format : 20191224_105021 -> YEAR MONTH DAY _ HOURS MINUTES SECONDS
    :return: time as string
    """
    now = datetime.now()
    return now.strftime("%Y%m%d_%H:%M:%S")


def get_new_names_by_version(file_names):
    return 0
