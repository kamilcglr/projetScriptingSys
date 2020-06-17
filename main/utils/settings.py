import logging
from os import path

import configparser as configparser

from main.utils.custom_exceptions import ApplicationError


class Settings:
    """
    Class that contains all information necessary to
    """

    def __init__(self, path_to_settings):
        self.file_name = path_to_settings

        # [ main ]
        self.save_mode = None
        self.paths_to_save = None
        self.archiving_mode = None
        self.archiving_max = None
        self.directory_to_save_in = None

        # [remote]
        self.username = None
        self.password = None
        self.port = None
        self.server_ip_address = None

        # [email]
        self.email_recipients = []
        self.title = None
        self.smtp_server = None
        self.use_tls = None
        self.email_port = None
        self.sender_email = None
        self.sender_password = None
        self.sender_login = None

    def read_parameters(self):
        """
        Parse the setting file in this object.
        Verify as possible if arguments in settings.ini are correct
        """
        config = configparser.ConfigParser()
        try:
            # verify if settings.ini exists
            if not path.exists(self.file_name):
                raise ApplicationError("Setting file not found")

            config.read(self.file_name)

            self.paths_to_save = config.get('main', 'paths_to_save').splitlines()
            self.save_mode = config.get('main', 'save_mode')
            self.archiving_mode = config.get('main', 'archiving_mode')
            self.archiving_max = config.get('main', 'archiving_max')
            self.directory_to_save_in = config.get('main', 'directory_to_save_in')

            # Verify archiving mode
            self.archiving_mode = config.get('main', 'archiving_mode')
            if self.archiving_mode not in {"date", "version"}:
                raise ApplicationError("Archiving mode mode is not valid, please verify your settings.ini")

            remote_modes = ["FTP", "FTPS", "SFTP", "RSYNC"]
            # Verify if save mode is a remote method
            if self.save_mode in remote_modes:
                logging.info("{} mode chosen".format(self.save_mode))
                self.server_ip_address = config.get('remote', 'server_ip_address')
                self.username = config.get('remote', 'username')
                self.password = config.get('remote', 'password')
                self.port = int(config.get('remote', 'port'))

            # Else, verify if it is local
            elif self.save_mode == "LOCAL":
                logging.info("{} mode chosen".format(self.save_mode))

            # Raise an exception if precedent tests failed
            else:
                raise ApplicationError("Save method is not valid, please verify your settings.ini")

            self.email_recipients = config.get('email', 'email_recipients').splitlines()
            self.title = config.get('email', 'title')
            self.smtp_server = config.get('email', 'smtp_server')
            self.email_port = config.get('email', 'email_port')
            self.use_tls = config.get('email', 'use_tls')
            self.sender_email = config.get('email', 'sender_email')
            self.sender_login = config.get('email', 'sender_login')
            self.sender_password = config.get('email', 'sender_password')

        except configparser.Error as e:
            raise ApplicationError("Unable to read settings file : " + e.message)
