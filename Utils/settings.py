import logging
from os import path

from Utils.custom_exceptions import ApplicationError


class Settings:
    def __init__(self, path_to_settings):
        self.file_name = path_to_settings
        self.files_with_path = []

        # [ main ]
        self.save_mode = None
        self.paths_to_save = None
        self.server_ip_address = None
        self.archiving_mode = None
        self.archiving_max = None

        # [ ftp ]
        self.username = None
        self.password = None
        self.port = None
        self.directory_to_save_in = None

    def read_parameters(self):
        try:
            import configparser as cp
        except ImportError:
            # TODO understand this
            import ConfigParser as cp

        config = cp.ConfigParser()
        try:
            # verify if settings.ini exists
            if not path.exists(self.file_name):
                raise ApplicationError("Setting file not found")

            config.read(self.file_name)

            self.paths_to_save = config.get('main', 'paths_to_save').splitlines()
            self.save_mode = config.get('main', 'save_mode')
            self.server_ip_address = config.get('main', 'server_ip_address')  # TODO verify
            self.archiving_mode = config.get('main', 'archiving_mode')
            self.archiving_max = config.get('main', 'archiving_max')

            # ================================= main =================================
            if self.save_mode == "FTP":
                self.username = config.get('ftp', 'username')
                self.password = config.get('ftp', 'password')
                self.port = config.get('ftp', 'port')
                self.directory_to_save_in = config.get('ftp', 'directory_to_save_in')
            elif self.save_mode == "SFTP":
                print()
            elif self.save_mode == "FTPS":
                print()
            elif self.save_mode == "RSYNC":
                print()
            elif self.save_mode == "RSYNC":
                print()
            elif self.save_mode == "LOCAL":
                print()
            else:
                raise ApplicationError("Save method is not valid, please verify your settings.ini")

            # verify archiving mode
            self.archiving_mode = config.get('main', 'archiving_mode')
            if self.archiving_mode not in {"date", "version"}:
                raise ApplicationError("Archiving mode mode is not valid, please verify your settings.ini")

        except cp.Error as e:
            raise ApplicationError("Unable to read settings file : " + e.message)
