# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class ApplicationError(Error):
    """Raised when could not save, we have to stop application
    """

    def __init__(self, message):
        self.message = message

    pass
