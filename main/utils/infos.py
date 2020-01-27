import os


class Infos:
    """
    Contains some information about saving process.
    """
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.nb_file_copied = 0
        self.new_directory_name = ""
        self.deleted_directories = []
        self.fail_reason = ""
        self.result = False  # indicates if success or fail
        self.script_path = os.getcwd()
