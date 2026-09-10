from blogforge_ai.exceptions.base import BlogForgeError


class WriterError(BlogForgeError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class WriterInputError(WriterError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class WriterGenerationError(WriterError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class WriterPersistenceError(WriterError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)
