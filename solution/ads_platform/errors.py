class ConflictMailError(Exception): ...


class AuthenticationError(Exception):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.message = message


class ForbiddenError(Exception): ...
