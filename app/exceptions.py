from app.core.logger import CustomLogger


class CustomError(Exception):
    def __init__(self, message: str = "Something went wrong", logger: CustomLogger | None = None, name="Internal Server Error", code: int | None = None):
        self.message = message
        self.name = name
        self.code = code
        self.logger = logger
        super().__init__(self.message, self.name)

class WrongFileTypeError(CustomError):
    def __init__(self, message: str = "Wrong file uploaded", logger: CustomLogger | None = None, name: str = "Wrong File Error", code: int | None = None):
        super().__init__(message, logger, name, code)
