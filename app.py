import logging.config
import os
from os import path

from connection_modes.sftp_saving import SftpSave
from utils.custom_exceptions import ApplicationError
from connection_modes.ftp_ftps_saving import FtpFtpsSave
from utils.settings import Settings


def save_with_ftp(settings):
    ftp_connection = FtpFtpsSave(settings)
    ftp_connection.connect_ftp()

def save_with_sftp(settings):
    sftp_connection = SftpSave(settings)
    sftp_connection.connect_sftp()

def switch_mode(settings):
    if settings.save_mode == 'FTP' or settings.save_mode == 'FTPS':
        save_with_ftp(settings)
    elif settings.save_mode == 'SFTP':
        save_with_sftp(settings)
    else:
        logging.critical("Save method is not valid, please verify your settings.ini")
        raise ApplicationError


def get_files(paths_to_save):
    logging.info("Scanning files...")

    # Will contain verified paths/files
    paths_to_save_ok = []

    # All the files with their path e.g. : /etc/test.txt or test.txt
    list_files_to_save = list()

    # Verify if files or paths exist
    for path_or_file in paths_to_save:
        if path.exists(path_or_file):
            if path.isfile(path_or_file):
                logging.info("File: " + path_or_file + " exists")
                paths_to_save_ok.append(path_or_file) # TODO delete if using oswalk
            else:
                logging.info("Directory: " + path_or_file + " exists")
                paths_to_save_ok.append(path_or_file)
        else:
            logging.error("File or directory NOT FOUND: " + path_or_file)

    # Get all the path of files recursively in paths to save
    for path_to_save in paths_to_save_ok:
        logging.info("Analysing: " + path_to_save)
        # Get the list of all files in directory tree at given path
        for (dirpath, dirnames, filenames) in os.walk(path_to_save):
            complete_path = [os.path.join(dirpath, file) for file in filenames]
            list_files_to_save += complete_path

    logging.info("Analyse terminated " + str(len(list_files_to_save)) + " files analysed")
    #return list_files_to_save
    return paths_to_save_ok

if __name__ == '__main__':

    try:
        # Initialize logging
        logging.config.fileConfig('settings/logging.ini')
        logging.info("Application started")

        # Read settings file
        settings = Settings("settings/settings.ini")
        settings.read_parameters()

        # Verify files
        settings.paths_to_save = get_files(settings.paths_to_save)

        # Save
        switch_mode(settings)
        logging.info("save successfully terminated")

    except ApplicationError as e:
        logging.critical("UNSUCCESSFULLY terminated because: " + e.message)
    except Exception as e:
        logging.exception("UNSUCCESSFULLY terminated because: ")

    logging.info("Application terminated")
