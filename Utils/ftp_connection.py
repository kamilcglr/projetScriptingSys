from ftplib import FTP


class FtpConnection:

    def __init__(self, settings):
        self.server_ip_address = settings.server_ip_address
        self.ftp_connection = None
        self.user_name = settings.username
        self.password = settings.password

    def connect_ftp(self):
        with FTP(self.server_ip_address) as self.ftp_connection:
            try:
                print(self.ftp_connection.getwelcome())
                self.ftp_connection.login(user=self.user_name, passwd=self.password)
                self.ftp_connection.cwd('sauvegardes')
                self.ftp_connection.dir()
                print(self.ftp_connection.pwd())
                self.ftp_connection.quit()

            except FTP.all_errors as msg:
                print("[-] An error occurred: " + msg)  # log
                pass
