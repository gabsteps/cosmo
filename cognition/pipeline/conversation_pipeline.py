# cosmo/cognition/pipeline/conversation_pipeline.py

import asyncio

from cosmo.core.logger.logger_manager import (
    logger
)

from cosmo.cognition.response.response_generator import (
    response_generator
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)

from cosmo.core.events.event_types import (
    RESPONSE_GENERATED
)


class ConversationPipeline:

    def __init__(
        self,
        llm_provider=None,
        timeout_seconds: float = 30.0
    ):
        self.llm_provider = llm_provider
        self.timeout_seconds = timeout_seconds

    def set_llm_provider(
        self,
        llm_provider
    ) -> None:

        self.llm_provider = llm_provider

    async def process_text(
        self,
        text: str
    ) -> None:

        logger.info(
            f"ConversationPipeline iniciado: {text}"
        )

        text = text.strip()

        if not text:
            await self._emit_response(
                response_text="Não entendi o que disse.",
                source_text=text
            )
            return

        try:

            if self.llm_provider is None:
                from cosmo.ai.llm.llm_provider import (
                    llm_provider
                )

                self.llm_provider = llm_provider

            response_text = await asyncio.wait_for(
                response_generator.generate(
                    user_text=text,
                    llm_provider=self.llm_provider
                ),
                timeout=self.timeout_seconds
            )

            logger.info(
                f"ConversationPipeline resposta: {response_text}"
            )

            logger.info(
                "ConversationPipeline emitindo RESPONSE_GENERATED"
            )

            await self._emit_response(
                response_text=response_text,
                source_text=text
            )

        except (asyncio.TimeoutError, TimeoutError):

            logger.warning(
                "ConversationPipeline timeout ao gerar resposta"
            )

            await self._emit_response(
                response_text="Demorei demais para processar isso.",
                source_text=text
            )

        except Exception as error:

            logger.exception(
                f"Erro no ConversationPipeline: {error}"
            )

            await self._emit_response(
                response_text=(
                    "Não consegui processar isso. "
                    "Falha controlada, pelo menos."
                ),
                source_text=text
            )

    async def _emit_response(
        self,
        response_text: str,
        source_text: str
    ) -> None:

        await async_event_bus.emit(
            RESPONSE_GENERATED,
            {
                "text": response_text,
                "source_text": source_text
            },
            priority=async_event_bus.PRIORITY_COGNITION
        )


conversation_pipeline = ConversationPipeline()