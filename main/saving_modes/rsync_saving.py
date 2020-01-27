import logging
import shlex
import subprocess
import sys

from main.utils import logging_subprocess
from main.utils.custom_exceptions import ApplicationError


class RSyncSave:
    """
    Class for RSync saving. Uses rsync shell command.
    This method is not guaranteed to work on a non Linux system.
    Necessity of rsync and sshpass installed.
    """

    def __init__(self, settings, infos):
        """
        Constructor.
        :param settings: Object that contains the information about server, path to save, usernames...
        :param infos: Object that contains the information about what happens.
        """
        self.rsync_connection = None
        self.settings = settings
        self.server_ip_address = self.settings.server_ip_address
        self.infos = infos

    def connect_rsync(self):
        # require Python interpreter > v.3.5
        assert sys.version_info >= (3, 5)

        # Don't run if not under a Unix-type environment
        # this could potentially happen e.g. if system default Python is Anaconda
        # but Cygwin is also installed
        if sys.platform == 'win32':
            raise ApplicationError("This script is incompatible with the Windows native"
                                   "environment.\nIt should be run under a Unix-like"
                                   "environment such as Linux or Cygwin.\n.")

        try:
            for path in self.settings.paths_to_save:
                args = '-avzrh' + ' -d' + ' --update --stats -e'
                """
                    -a : archive mode which makes it retain file attributes such as permissions and ownership.
                    -v : verbose mode, this will make rsync output status of the copy.
                    -z : compress files during the copy, this will save time for slow network connections.
                    -r : recursively copy files and directories.
                    -h : outputs in a human readable format. 
                    -e : specify the type of protocol to be used
                    --update :  If we want to copy files over the remote-host that have been updated more recently on 
                        the local filesystem. Files that do not exist on the remote-host are copied.
                    Files that exist on both local and remote but have a newer timestamp on the local-host are copied 
                        to remote-host. 
                """

                command = 'rsync --rsync-path="/usr/bin/sudo /usr/bin/rsync" {0} ' \
                          '"sshpass -p "{1}" ' \
                          'ssh -p {2} -o StrictHostKeyChecking=no" ' \
                          '{3} {4}@{5}:/{6}'.format(args,
                                                    self.settings.password,
                                                    self.settings.port,
                                                    path,
                                                    self.settings.username,
                                                    self.settings.server_ip_address,
                                                    self.settings.directory_to_save_in)

                logging_subprocess.call(shlex.split(command), self.infos)

        except (OSError, subprocess.CalledProcessError) as exception:
            logging.info('Subprocess failed')
            raise ApplicationError(str(exception))
        # no exception was raised
        logging.info('Subprocess finished')
