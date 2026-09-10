from blogforge_ai.exceptions.base import BlogForgeError


class WorkflowError(BlogForgeError):
    def __init__(self, message, error_code, workflow, node=None, retryable=False, cause=None):
        super().__init__(message, error_code, workflow, node, retryable, cause)
