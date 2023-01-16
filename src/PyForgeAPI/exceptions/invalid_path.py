class Invalid_path(Exception):
    def __init__(self, msg):
        self.msg = msg