class BlogForgeError(Exception):
    def __init__(self, message: str, error_code: str, workflow: str, node: str = None, retryable: bool = False, cause: Exception = None):
        self.message = message
        self.error_code = error_code
        self.workflow = workflow
        self.node = node
        self.retryable = retryable
        self.cause = cause

        super().__init__(message)
