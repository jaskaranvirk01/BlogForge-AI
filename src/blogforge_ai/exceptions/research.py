from blogforge_ai.exceptions.base import BlogForgeError


class ResearchError(BlogForgeError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class ResearchSearchError(ResearchError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class ResearchExtractionError(ResearchError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class ResearchPersistenceError(ResearchError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)


class ResearchGenerationError(ResearchError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)
