# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class ApplicationError(Error):
    """Raised when could not save, we have to stop application
        Attributes:
            previous -- state at beginning of transition
            next -- attempted new state
            message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, message):
        self.message = message

    pass
