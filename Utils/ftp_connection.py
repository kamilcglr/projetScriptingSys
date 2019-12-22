import ftplib
import logging
import os
from ftplib import FTP
from pathlib import Path

from Utils.custom_exceptions import ApplicationError
from Utils.historisation import get_new_name_by_date


class FtpConnection:

    def __init__(self, settings):
        self.server_ip_address = settings.server_ip_address
        self.ftp_connection = None
        self.settings = settings

    def connect_ftp(self):
        try:
            logging.info("Connection to FTP server at " + self.server_ip_address)
            with FTP(self.server_ip_address, timeout=5) as self.ftp_connection:
                self.ftp_connection.encoding = 'utf-8'
                logging.info(self.ftp_connection.getwelcome())
                self.ftp_connection.login(user=self.settings.username, passwd=self.settings.password)

                self.ftp_connection.cwd(self.settings.directory_to_save_in)
                logging.info("Positioned in: " + self.ftp_connection.pwd())

                self.save_files()

                self.ftp_connection.quit()
                logging.info("Quiting from FTP server at " + self.server_ip_address)

        except ftplib.all_errors as e:
            raise ApplicationError(str(e))

    def save_files(self):
        self.cleaning()
        new_directory_name = None

        if self.settings.archiving_mode == "date":
            new_directory_name = get_new_name_by_date()

        # create new directory to store files
        self.ftp_connection.mkd(new_directory_name)
        logging.info("New backup directory created: " + new_directory_name)
        self.ftp_connection.cwd(new_directory_name)
        logging.info("Positioned in: " + self.ftp_connection.pwd())

        for path in self.settings.paths_to_save:
            logging.info(self.ftp_connection.pwd())

            if os.path.isfile(path):
                file_name = Path(path).name
                self.send_file(path, file_name)

            elif os.path.isdir(path):
                path_name = Path(path).name
                try:
                    self.ftp_connection.mkd(path_name)
                    logging.info("New directory created: " + path_name)

                # ignore "directory already exists"
                except ftplib.error_perm as e:
                    raise ApplicationError(e.__traceback__)

                self.ftp_connection.cwd(path_name)
                self.send_files(path)
                self.ftp_connection.cwd('..')

    def cleaning(self):
        """ Counts the number of backups in directory. If it is greater than limit, it delete old versions.

        """
        entries = self.get_directories_in_path(self.ftp_connection.pwd())
        if len(entries) >= int(self.settings.archiving_max):
            logging.info("Maximum backup (" + str(self.settings.archiving_max) + ") is reached: " + str(len(entries)))

            while len(entries) >= int(self.settings.archiving_max):
                # sort files by date from oldest to newest
                entries.sort(key=lambda entry: entry[1]['modify'], reverse=False)
                oldest_name = entries[0][0]
                logging.info("Deleting: " + oldest_name)
                self.remove_directories(oldest_name)
                entries = self.get_directories_in_path(self.ftp_connection.pwd())

    def remove_directories(self, path):
        for (name, properties) in self.get_directories_in_path(path=path):
            if properties['type'] == 'file':
                self.ftp_connection.delete(f"{path}/{name}")
            elif properties['type'] == 'dir':
                self.remove_directories(f"{path}/{name}")
        self.ftp_connection.rmd(path)

    def get_directories_in_path(self, path):
        entries = list(self.ftp_connection.mlsd(path=path))
        entries = list(filter(lambda entry: entry[0] not in ['.', '..'], entries))
        return entries

    def send_files(self, path):
        try:
            for name in os.listdir(path):
                local_path = os.path.join(path, name)
                if os.path.isfile(local_path):
                    self.send_file(local_path, name)
                elif os.path.isdir(local_path):
                    try:
                        self.ftp_connection.mkd(name)
                        logging.info("New directory created" + local_path + name)

                    # ignore "directory already exists"
                    except ftplib.error_perm as e:
                        if not e.args[0].startswith('550'):
                            raise

                    self.ftp_connection.cwd(name)
                    self.send_files(local_path)
                    self.ftp_connection.cwd("..")

        except PermissionError:
            logging.warning("Cannot copy: " + path + " PERMISSION DENIED")

    def send_file(self, path, file_name):
        try:
            logging.info("Sending " + path)
            self.ftp_connection.storbinary('STOR ' + file_name, open(path, 'rb'))
        except PermissionError:
            logging.warning("Cannot copy: " + path + " PERMISSION DENIED")
