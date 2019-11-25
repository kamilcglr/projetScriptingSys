from ftplib import FTP

with FTP('161.3.36.255') as ftp:
    try:
        print(ftp.getwelcome())  # log
        ftp.login(user='kamil', passwd='test')
        ftp.sendcmd('CWD sauvegardes')
        ftp.dir()
        print(ftp.pwd())
        ftp.quit()

    except (FTP.all_errors) as msg:
        print("[-] An error occurred: " + msg) # log
        pass
