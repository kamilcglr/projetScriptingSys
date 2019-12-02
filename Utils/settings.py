class Settings:
    def __init__(self, path_to_settings):
        self.file_name = path_to_settings

        self.mode = None
        self.ip = None
        self.username = None
        self.password = None

        self.server_ip_address = None

        self.paths_to_save = []

    def read_parameters(self):
        try:
            import configparser as cp
        except ImportError:
            # TODO understand this
            import ConfigParser as cp

        config = cp.ConfigParser()

        config.read(self.file_name)

        # read the parameters
        self.mode = config.get('main', 'save_mode')
        self.server_ip_address = config.get('main', 'server_ip_address')

        self.username = config.get('ftp', 'username')
        self.password = config.get('ftp', 'password')

        self.paths_to_save = config.get('main', 'paths_to_save').splitlines()
