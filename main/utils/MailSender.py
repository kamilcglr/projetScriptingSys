import logging
import smtplib
import ssl
from copy import deepcopy
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailSender:
    def __init__(self, settings, infos):
        self.settings = settings
        self.infos = infos

    def send_mail(self):
        message = MIMEMultipart()
        message["From"] = self.settings.sender_email

        # Add body to email
        body = ""

        if not self.infos.result:
            message["Subject"] = self.settings.title + " FAILED"
            body += "Backup started at {} has failed because : {}.\n" \
                    "Please look at the attached error.log and application.log".format(self.infos.start_time,
                                                                                       self.infos.fail_reason)
        else:
            message["Subject"] = self.settings.title + " SUCCESS"

            if get_nb_lines(self.infos.script_path + '/' + "warning.log") > 0:
                body += "\nBUT there are some warnings, please look at warning.log !"

            directories_saved = '\n'.join(self.settings.paths_to_save)
            body = "Backup started at {} has succeeded. \n" \
                   "These directories/files have been saved : \n{}\nFor a total of {} files.".format(
                    self.infos.start_time,
                    directories_saved,
                    self.infos.nb_file_copied)

            # Add deleted directories to mail
            if len(self.infos.deleted_directories) > 0:
                body += "\n{} have been deleted.".format('\n'.join(self.infos.deleted_directories))

            if self.infos.new_directory_name != "":
                body += "\nNew directory {} have been created.".format(self.infos.new_directory_name)

        message.attach(MIMEText(body, "plain"))

        files = ["application.log", "error.log", "warning.log"]
        for filename in files:
            try:
                # We assume that the file is in the directory where you run your Python script from
                with open(self.infos.script_path + '/' + filename, "rb") as attachment:
                    # The content type "application/octet-stream" means that a MIME attachment is a binary file
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode to base64
                encoders.encode_base64(part)

                # Add header
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )

                # Add attachment to your message and convert it to string
                message.attach(part)

            except Exception as e:
                logging.warning("{} can't be attached".format(filename))

        server = None
        try:
            # Send email with TLS or not
            if self.settings.use_tls == 'YES':
                # Create a secure SSL context
                context = ssl.create_default_context()
                server = smtplib.SMTP(self.settings.smtp_server, self.settings.email_port)
                server.ehlo()  # Can be omitted
                server.starttls(context=context)  # Secure the connection
                server.ehlo()  # Can be omitted
                server.login(self.settings.sender_login, self.settings.sender_password)
            else:
                server = smtplib.SMTP(self.settings.smtp_server, self.settings.email_port)
                server.login(self.settings.sender_login, self.settings.sender_password)

            for recipient in self.settings.email_recipients:
                temp_message = deepcopy(message)
                temp_message["To"] = recipient
                text = temp_message.as_string()
                server.sendmail(self.settings.sender_email, recipient, text)
                logging.info("Email sent to {}".format(recipient))

        except Exception as e:
            # Print any error messages to stdout
            print(e)
        finally:
            server.quit()


def get_nb_lines(path):
    """
    Get the number of lines in a file.
    :param path: of the file
    :return: int number of file.
    """
    i = 0
    with open(path) as f:
        for i, l in enumerate(f, 1):
            pass
    return i
