from blogforge_ai.exceptions.base import BlogForgeError


class FactCheckError (BlogForgeError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class FactCheckRetrievalError(FactCheckError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class FactCheckGenerationError(FactCheckError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class FactCheckPersistenceError(FactCheckError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)
