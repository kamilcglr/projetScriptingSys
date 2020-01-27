import logging
import os
import shutil
from pathlib import Path

from main.utils.custom_exceptions import ApplicationError
from main.utils.historisation import get_new_names_by_version, get_new_name_by_date


class LocalSave:
    """
    Class for LOCAL saving.
    """

    def __init__(self, settings, infos):
        """
        Constructor.
        :param settings: Object that contains the information about server, path to save, usernames...
        """
        self.settings = settings
        self.infos = infos

    def save(self):
        """Entry point of class.
        """
        try:
            os.chdir(self.settings.directory_to_save_in)
            logging.info("Positioned in: " + os.getcwd())

            self.save_files()

        except Exception as e:
            raise ApplicationError(str(e))

    def save_files(self):
        """
        Copy all files on locally.
        """

        # Clean the directory first.
        self.cleaning()

        # Get the directory name
        if self.settings.archiving_mode == "date":
            new_directory_name = get_new_name_by_date()
        else:
            # Change the names of older backups by doing a shift of index. (1->2, 2->3...)
            directories_in_path = self.get_directories_in_path(os.getcwd())
            directories_in_path.sort(key=os.path.getmtime)
            old_names = [entry for entry in directories_in_path]
            new_names = get_new_names_by_version(old_names)
            new_directory_name = new_names[len(new_names) - 1]
            for directory_index in range(0, len(new_names) - 1):
                logging.info(
                    "Renaming directory: " + old_names[directory_index] + " to: " + new_names[directory_index])
                os.rename(old_names[directory_index], new_names[directory_index])

        # Create new directory to store files
        self.infos.new_directory_name = new_directory_name
        os.mkdir(new_directory_name)
        logging.info("New backup directory created: " + new_directory_name)
        os.chdir(new_directory_name)
        logging.info("Positioned in: " + os.getcwd())
        new_path_name = os.getcwd()

        # Copy files and directory recursively.
        for path in self.settings.paths_to_save:
            if os.path.isfile(path):
                self.copy_file(path, new_path_name)

            elif os.path.isdir(path):
                self.copy_files(path, new_path_name)

    def cleaning(self):
        """
        Save Rotation.
        Counts the number of backups in directory. If it is greater than limit, it delete old versions.
        """
        entries = self.get_directories_in_path(os.getcwd())
        if len(entries) >= int(self.settings.archiving_max):
            logging.info("Maximum backup (" + str(self.settings.archiving_max) + ") is reached: " + str(len(entries)))

            while len(entries) >= int(self.settings.archiving_max):
                # sort files by date from oldest to newest
                entries.sort(key=os.path.getmtime)
                oldest_name = entries[0]
                logging.info("Deleting directory: " + oldest_name)
                self.remove_directories(oldest_name)
                self.infos.deleted_directories.append(oldest_name)
                entries = self.get_directories_in_path(os.getcwd())

    def remove_directories(self, path):
        """
        Delete a directory recursively.
        :param path: The path of directory to delete.
        """
        shutil.rmtree(path)

    def get_directories_in_path(self, path):
        """
        :param path: String current path
        :return: List of string that contains directories in path.
        """
        entries = list(os.listdir(path=path))
        return entries

    def copy_files(self, path, new_path):
        """
        Copy files recursively. Creates the subdirectories if necessary.
        :param new_path: Name of the new path
        :param path: path to save.
        """
        try:
            directory_name = '/' + Path(path).name
            logging.info("Copying " + path + " to " + new_path + directory_name)
            shutil.copytree(path, new_path + directory_name)

        except shutil.Error as e:
            logging.warning("Cannot copy: " + path + " PERMISSION DENIED")
            errors = e.args[0]
            for error in errors:
                src, dst, msg = error
                logging.warning("Cannot copy: " + src + " PERMISSION DENIED")

    def copy_file(self, path, new_path):
        """
        Copy one file.
        :param path: String path of the local file.
        :param new_path: path of the new file.
        """
        try:
            file_name = '/' + Path(path).name
            logging.info("Copying " + path + " to " + new_path + file_name)
            shutil.copy(path, new_path + file_name)
            self.infos.nb_file_copied += 1
        except PermissionError:
            logging.warning("Cannot copy: " + path + " PERMISSION DENIED")
