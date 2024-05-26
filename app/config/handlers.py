from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def request_validation_exception_handler(_: Request, exc: RequestValidationError):
    """This function handles request validation errors raised by pydantic"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "status": "error",
                "data": {"message": exc.body},
            }
        ),
    )


async def http_exception_handler(_: Request, exc: HTTPException):
    """This function handles HTTP exceptions raised by the application"""
    if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        # send email to the developers
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                {
                    "status": "error",
                    "data": {"message": "Internal Server Error Contact Support"},
                }
            ),
        )
    elif exc.status_code == status.HTTP_502_BAD_GATEWAY:
        # send email to the developers
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(
                {"status": "error", "data": {"message": "Bad Gateway Contact Support"}}
            ),
        )
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder({"status": "error", "data": {"message": exc.detail}}),
    )


async def uncaptured_exception_handler(_: Request, exc: Exception):
    """This function handles uncaptured exceptions raised by the application"""
    # send email to the developers
    print(exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "status": "error",
                "data": {"message": "Internal Server Error Contact Support"},
            }
        ),
    )
