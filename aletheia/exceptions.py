class AletheiaException(Exception):

    def __init__(self, message=None, *args):
        super().__init__(message or self.get_default_message(), *args)

    def get_default_message(self):
        return "An unknown error occurred.  Sorry about that."


class UnknownFileTypeError(AletheiaException):
    def get_default_message(self):
        return "Aletheia doesn't recognise that file type"


class PublicKeyNotExistsError(AletheiaException):
    def get_default_message(self):
        return (
            "The public key location contained in the file header either "
            "can't be accessed, or does not contain a public key",
        )


class UnparseableFileError(AletheiaException):
    def get_default_message(self):
        return "Aletheia can't find a signature in that file"


class DependencyMissingError(AletheiaException):
    def get_default_message(self):
        return (
            "A software dependency appears to be missing, but this should "
            "never happen.  Please report an issue at "
            "https://github.com/danielquinn/pyletheia/issues"
        )


class UnacceptableLocationError(AletheiaException):
    def get_default_message(self):
        return "The domain name provided does not appear to be valid"


class UnrecognisedKey(AletheiaException):
    def get_default_message(self):
        return (
            "The key data provided could not be recognised as one formatted "
            "for Aletheia"
        )
