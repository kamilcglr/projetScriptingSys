#!/usr/bin/env python
import logging.config
import os
from datetime import datetime
from os import path

from main.saving_modes.ftp_ftps_saving import FtpFtpsSave
from main.saving_modes.local_saving import LocalSave
from main.saving_modes.rsync_saving import RSyncSave
from main.saving_modes.sftp_saving import SftpSave
from main.utils.MailSender import MailSender
from main.utils.custom_exceptions import ApplicationError
from main.utils.infos import Infos
from main.utils.settings import Settings


def run():
    """
    Main function of the app.
    First reads the settings, then get all the files to save and finally save them with the chosen method in settings.
    """

    # Create object containing infos during save
    infos = Infos()
    settings = None
    try:
        # Initialize logging
        logging.config.fileConfig('main/settings/logging.ini')
        logging.info("Application started")

        # Read settings file
        settings = Settings("main/settings/settings.ini")
        settings.read_parameters()

        # Verify files to save
        settings.paths_to_save = get_files_to_save(settings.paths_to_save)

        # Save
        infos.start_time = datetime.now()
        switch_mode(settings, infos)
        logging.info("save successfully terminated")
        infos.result = True

    except ApplicationError as e:
        infos.result = False
        logging.critical("UNSUCCESSFULLY terminated because: " + e.message)
        infos.fail_reason = e.message
    except Exception as e:
        infos.result = False
        logging.exception("UNSUCCESSFULLY terminated because: ")

    mail_sender = MailSender(settings, infos)
    mail_sender.send_mail()

    logging.info("Application terminated")


def switch_mode(settings, infos):
    """
    Choose the saving mode
    :param infos:
    :param settings:
    :return:
    """
    if settings.save_mode == 'FTP' or settings.save_mode == 'FTPS':
        save_with_ftp(settings, infos)
    elif settings.save_mode == 'SFTP':
        save_with_sftp(settings, infos)
    elif settings.save_mode == 'RSYNC':
        save_with_rsync(settings, infos)
    elif settings.save_mode == 'LOCAL':
        save_local(settings, infos)
    else:
        logging.critical("Save method is not valid, please verify your settings.ini")
        raise ApplicationError


def get_files_to_save(paths_to_save):
    """
    For each file or path to save, verify their existence.
    :param paths_to_save: List of strings that contains paths or files.
    :return: List of string that contains all the paths of files.
    """
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
                paths_to_save_ok.append(path_or_file)
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
    return paths_to_save_ok


def save_with_ftp(settings, infos):
    """
    Calls the FTP or FTPS saving mode.
    :param infos:
    :param settings: Settings object.
    """
    ftp_connection = FtpFtpsSave(settings, infos)
    ftp_connection.connect_ftp()


def save_with_sftp(settings, infos):
    """
    Calls the SFTP saving mode.
    :param infos:
    :param settings: Settings object.
    """
    sftp_connection = SftpSave(settings, infos)
    sftp_connection.connect_sftp()


def save_with_rsync(settings, infos):
    """
    Calls the rsync saving mode.
    :param infos:
    :param settings: Settings object.
    """
    rsync_connection = RSyncSave(settings, infos)
    rsync_connection.connect_rsync()


def save_local(settings, infos):
    """
    Calls the local saving mode.
    :param infos:
    :param settings: Settings object.
    """
    local = LocalSave(settings, infos)
    local.save()
