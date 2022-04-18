class ApiError(Exception):
    pass


class TrainError(ApiError):
    pass


class MysqlError(ApiError):
    pass


class HandlingError(ApiError):
    def __init__(self, msg, code=500):
        super().__init__()
        self.handling_code = code
        self.handling_msg = msg
