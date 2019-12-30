import logging
import os
from pathlib import Path

import paramiko

from main.utils.custom_exceptions import ApplicationError
from main.utils.historisation import get_new_name_by_date, get_new_names_by_version


class SftpSave:
    def __init__(self, settings):
        self.server_ip_address = settings.server_ip_address
        self.sftp_connection = None
        self.transport = None
        self.settings = settings

    def connect_sftp(self):
        try:
            # Open a transport
            self.transport = paramiko.Transport(self.settings.server_ip_address, 22)
            logging.info("Creating transport " + self.server_ip_address + " on port " + str(22))

            # Auth
            self.transport.connect(None, self.settings.username, self.settings.password)
            logging.info("Connecting to " + self.server_ip_address)

            # Go!
            self.sftp_connection = paramiko.SFTPClient.from_transport(self.transport)

            self.sftp_connection.chdir(self.settings.directory_to_save_in)
            logging.info("Positioned in: " + self.sftp_connection.getcwd())

            self.save_files()

            # Close
            if self.sftp_connection:
                self.sftp_connection.close()
            if self.transport:
                logging.info("Quiting from SFTP server at " + self.server_ip_address)
            self.transport.close()


        except paramiko.SSHException as e:
            # except Exception as e:
            raise ApplicationError(str(e) + str(e.args) + str(e.with_traceback(e.__traceback__)))

    def save_files(self):
        self.cleaning()

        if self.settings.archiving_mode == "date":
            new_directory_name = get_new_name_by_date()
        else:
            directories_in_path = self.get_directories_in_path(self.sftp_connection.getcwd())
            directories_in_path.sort(key=lambda f: f.st_mtime)
            old_names = [entry.filename for entry in directories_in_path]
            new_names = get_new_names_by_version(old_names)
            new_directory_name = new_names[len(new_names) - 1]
            for directory_index in range(0, len(new_names) - 1):
                logging.info(
                    "Renaming directory: " + old_names[directory_index] + " to: " + new_names[directory_index]);
                self.sftp_connection.posix_rename(old_names[directory_index], new_names[directory_index])

        # create new directory to store files
        self.sftp_connection.mkdir(new_directory_name)
        logging.info("New backup directory created: " + new_directory_name)
        self.sftp_connection.chdir(new_directory_name)
        logging.info("Positioned in: " + self.sftp_connection.getcwd())

        for path in self.settings.paths_to_save:

            if os.path.isfile(path):
                file_name = Path(path).name
                self.send_file(path, file_name)

            elif os.path.isdir(path):
                path_name = Path(path).name
                try:
                    self.sftp_connection.mkdir(path_name)
                    logging.info("New directory created: " + path_name)
                except Exception as e:
                    raise ApplicationError(e)

                self.sftp_connection.chdir(path_name)
                self.send_files(path)
                self.sftp_connection.chdir('..')

    def cleaning(self):
        """ Counts the number of backups in directory. If it is greater than limit, it delete old versions.

        """
        entries = self.get_directories_in_path(self.sftp_connection.getcwd())
        if len(entries) >= int(self.settings.archiving_max):
            logging.info("Maximum backup (" + str(self.settings.archiving_max) + ") is reached: " + str(len(entries)))

            while len(entries) >= int(self.settings.archiving_max):
                # sort files by date from oldest to newest
                entries.sort(key=lambda f: f.st_mtime)
                oldest_name = entries[0].filename
                logging.info("Deleting directory: " + oldest_name)
                self.remove_directories(oldest_name)
                entries = self.get_directories_in_path(self.sftp_connection.getcwd())

    def remove_directories(self, path):
        files = self.sftp_connection.listdir(path)

        for f in files:
            filepath = os.path.join(path, f)
            try:
                self.sftp_connection.remove(filepath)
            except IOError:
                self.remove_directories(filepath)
        self.sftp_connection.rmdir(path)

    def get_directories_in_path(self, path):
        directories_in_path = self.sftp_connection.listdir_attr(path=path)
        return directories_in_path

    def send_files(self, path):
        try:
            for name in os.listdir(path):
                local_path = os.path.join(path, name)
                if os.path.isfile(local_path):
                    self.send_file(local_path, name)
                elif os.path.isdir(local_path):
                    try:
                        self.sftp_connection.mkdir(name)
                        logging.info("New directory created" + local_path + name)

                    # ignore "directory already exists"
                    except paramiko.__all__ as e:
                        raise ApplicationError(e)

                    self.sftp_connection.chdir(name)
                    self.send_files(local_path)
                    self.sftp_connection.chdir("..")
        except PermissionError:
            logging.warning("Cannot copy: " + path + " PERMISSION DENIED")

    def send_file(self, path, file_name):
        try:
            logging.info("Sending " + path)
            self.sftp_connection.putfo(open(path, 'rb'), file_name)
        except PermissionError:
            logging.warning("Cannot copy: " + path + " PERMISSION DENIED")
