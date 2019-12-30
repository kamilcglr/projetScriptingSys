import logging
from os import path

from main.utils.custom_exceptions import ApplicationError


class Settings:
    def __init__(self, path_to_settings):
        self.file_name = path_to_settings
        self.files_with_path = []

        # [ main ]
        self.save_mode = None
        self.paths_to_save = None
        self.archiving_mode = None
        self.archiving_max = None
        self.server_ip_address = None

        # [ ftp ] and [ ftps ]
        self.username = None
        self.password = None
        self.port = None
        self.directory_to_save_in = None

        # [ sftp ]
        self.identification_mode = None
        self.full_path_of_rsa_key = None

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
            self.archiving_mode = config.get('main', 'archiving_mode')
            self.archiving_max = config.get('main', 'archiving_max')

            # ================================= main =================================
            if self.save_mode == "FTP" or self.save_mode == "FTPS":
                if self.save_mode == "FTPS":
                    logging.info("FTPS mode chosen")
                    self.server_ip_address = config.get('ftps', 'server_ip_address')
                else:
                    logging.info("FTP mode chosen")
                    self.server_ip_address = config.get('ftp', 'server_ip_address')
                self.username = config.get('ftp', 'username')
                self.password = config.get('ftp', 'password')
                self.port = config.get('ftp', 'port')
                self.directory_to_save_in = config.get('ftp', 'directory_to_save_in')

            elif self.save_mode == "SFTP":
                logging.info("SFTP mode chosen")
                self.identification_mode = config.get('sftp', 'identification_mode')
                if self.identification_mode == "longinandkey":
                    self.full_path_of_rsa_key = config.get('sftp', 'full_path_of_rsa_key')

                    # verify if settings.ini exists
                    if not path.exists(self.full_path_of_rsa_key):
                        raise ApplicationError("RSA key file not found")
                self.username = config.get('sftp', 'username')
                self.password = config.get('sftp', 'password')
                self.directory_to_save_in = config.get('sftp', 'directory_to_save_in')
                self.server_ip_address = config.get('sftp', 'server_ip_address')

            elif self.save_mode == "RSYNC":
                logging.info("RSYNC mode chosen")
                self.identification_mode = config.get('rsync', 'identification_mode')
                if self.identification_mode == "longinandkey":
                    self.full_path_of_rsa_key = config.get('rsync', 'full_path_of_rsa_key')

                    # verify if settings.ini exists
                    if not path.exists(self.full_path_of_rsa_key):
                        raise ApplicationError("RSA key file not found")
                self.username = config.get('rsync', 'username')
                self.password = config.get('rsync', 'password')
                self.directory_to_save_in = config.get('rsync', 'directory_to_save_in')
                self.server_ip_address = config.get('rsync', 'server_ip_address')
                self.port = config.get('rsync', 'port')

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
