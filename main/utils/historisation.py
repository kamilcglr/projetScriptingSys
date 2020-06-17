from datetime import datetime


def get_new_name_by_date():
    """ Get a string formatted with the date at the moment it is called
    Format : 20191224_105021 -> YEAR MONTH DAY _ HOURS MINUTES SECONDS
    :return: time as string
    """
    now = datetime.now()
    return now.strftime("%Y%m%d_%H:%M:%S")


def get_new_names_by_version(directories):
    """
    Get a list of directory names with number. e.g. ['1', '2', '3', '4', '5'] if there are 5 backups.
    :param directories list of old names.
    :return: directories: list of string.
    """
    new_directories_name = []
    for i in range(0, len(directories)+1):
        new_directories_name.append(str(i))
    return new_directories_name
