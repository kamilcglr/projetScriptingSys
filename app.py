import logging
from os import path

from Utils.ftp_connection import FtpConnection
from Utils.settings import Settings


def init_logging():
    # create logger
    # logger = logging.getLogger('application.log')
    # logger.setLevel(logging.DEBUG)
    # TODO generate a .log each time
    # TODO erase and rotate
    logging.basicConfig(filename='application.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')

    # create console handler and set level to debug
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)

    # create formatter
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')

    logging.info("Application started")


def save_with_ftp(settings):
    ftp_connection = FtpConnection(settings)
    ftp_connection.connect_ftp()


def switch_mode(settings):
    switcher = {
        "FTP": save_with_ftp(settings)
        # 2: "FT",
        # 3: "March",
        # 4: "April",
        # 5: "May",
        # 6: "June",
        # 7: "July",
        # 8: "August",
        # 9: "September",
        # 10: "October",
        # 11: "November",
        # 12: "December"
    }
    switcher.get(settings.mode, logging.CRITICAL("Save method is not valid, please verify your settings.ini"))


def analyse_files(paths_to_save):
    logging.info("Scanning files...")
    for path_or_file in paths_to_save:
        # TODO separate path and file
        # TODO throw an exception ?
        if path.exists(path_or_file):
            logging.info("File or directory " + path_or_file + " exists")
        else:
            logging.error("File or directory " + path_or_file + " not found")


if __name__ == '__main__':
    init_logging()
    # read settings file
    settings = Settings("settings.ini")
    settings.read_parameters()
    analyse_files(settings.paths_to_save)
    switch_mode(settings)
    logging.info("Application terminated")
