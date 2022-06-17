import uvicorn

from nux.app import create_app


def run_app():
    import nux.config
    uvicorn.run(
        create_app(),  # type: ignore
        port=nux.config.PORT,
        host="0.0.0.0"
    )
