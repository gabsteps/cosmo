import uvicorn

from cosmo.core.config.settings_manager import (
    config
)

from cosmo.core.logger.logger_manager import (
    logger
)


class WebUIServer:

    def __init__(self):

        self.host = (
            config.get("webui", "host")
            or "127.0.0.1"
        )

        self.port = (
            config.get("webui", "port")
            or 8765
        )

        self.server = None

    async def start(self):

        logger.info(
            f"WebUI iniciando em http://{self.host}:{self.port}"
        )

        uvicorn_config = uvicorn.Config(
            "cosmo.interfaces.webui.webui_app:app",
            host=self.host,
            port=int(self.port),
            reload=False,
            log_level="warning"
        )

        self.server = uvicorn.Server(
            uvicorn_config
        )

        await self.server.serve()

    async def shutdown(self):

        if self.server:

            logger.info(
                "Encerrando WebUI"
            )

            self.server.should_exit = True


webui_server = WebUIServer()


def main():

    uvicorn.run(
        "cosmo.interfaces.webui.webui_app:app",
        host=(
            config.get("webui", "host")
            or "127.0.0.1"
        ),
        port=int(
            config.get("webui", "port")
            or 8765
        ),
        reload=False
    )


if __name__ == "__main__":
    main()