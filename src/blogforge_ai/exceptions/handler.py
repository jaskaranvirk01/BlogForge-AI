from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from blogforge_ai.exceptions.base import BlogForgeError
from blogforge_ai.exceptions.error_codes import ErrorCodes
from blogforge_ai.exceptions.workflow import WorkflowNotFoundError


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(BlogForgeError)
    async def blogforge_error_handler(
        request: Request,
        exc: BlogForgeError,
    ):
        if isinstance(exc, WorkflowNotFoundError):
            status_code = 404
        else:
            status_code = 500

        error_code = (
            exc.error_code.value
            if isinstance(exc.error_code, ErrorCodes)
            else exc.error_code
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error_code": error_code,
                "message": exc.message,
            },
        )
