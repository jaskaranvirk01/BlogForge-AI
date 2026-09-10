from blogforge_ai.exceptions.base import BlogForgeError


class AnalysisError(BlogForgeError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class AnalysisRetrievalError(AnalysisError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class AnalysisGenerationError(AnalysisError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class AnalysisPersistenceError(AnalysisError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)
