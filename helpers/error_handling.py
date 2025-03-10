class FailedLoginError(Exception):
    def __init__(self, msg="Failed to log in"):
        self.msg=msg
        super().__init__(self.msg)