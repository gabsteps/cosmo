# cosmo/cognition/pipeline/conversation_pipeline.py

from cosmo.core.logger.logger_manager import logger

from cosmo.cognition.response.response_generator import (
    response_generator
)

from cosmo.cognition.llm.openrouter_provider import (
    llm_provider
)

from cosmo.core.events.async_event_bus import (
    async_event_bus
)


class ConversationPipeline:

    async def process_text(
        self,
        text: str
    ) -> None:

        text = text.strip()

        if not text:
            await self._emit_response(
                "Não entendi o que disse."
            )
            return

        try:
            response_text = await response_generator.generate(
                user_text=text,
                llm_provider=llm_provider
            )

            await self._emit_response(
                response_text
            )

        except Exception as error:
            logger.exception(
                f"Erro no ConversationPipeline: {error}"
            )

            await self._emit_response(
                "Não consegui processar isso. Falha controlada, pelo menos."
            )

    async def _emit_response(
        self,
        text: str
    ) -> None:

        await async_event_bus.emit(
            "response_generated",
            {
                "text": text
            },
            priority=3
        )


conversation_pipeline = ConversationPipeline()