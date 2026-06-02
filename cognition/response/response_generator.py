from cosmo.core.config.settings_manager import config
from cosmo.core.logger.logger_manager import logger

from cosmo.cognition.conversation.conversation_manager import (
    conversation_manager
)

from cosmo.cognition.personality.persona_manager import (
    PersonaManager
)

from cosmo.cognition.personality.prompt_builder import (
    PromptBuilder
)

from cosmo.cognition.personality.personality_state import (
    personality_state
)

from cosmo.cognition.personality.personality_command_parser import (
    personality_command_parser
)


class ResponseGenerator:

    def __init__(self):

        self.persona_manager = PersonaManager(
            profiles_path=config.get(
                "personality",
                "profiles_path"
            ),
            active_profile=config.get(
                "personality",
                "active_profile"
            )
        )

        self.prompt_builder = PromptBuilder()

        # Carrega a persona uma única vez na inicialização.
        self.persona = self.persona_manager.persona

        # Copia os parâmetros padrão do YAML para o estado runtime.
        # Não coloque isso dentro de build_messages(), senão todo ajuste
        # feito durante a execução será perdido.
        personality_state.load_from_persona(
            self.persona.parameters
        )

    def build_messages(
        self,
        user_text: str
    ) -> list[dict[str, str]]:

        system_prompt = (
            self.prompt_builder
            .build_system_prompt(
                self.persona
            )
        )

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(
            conversation_manager.get_history()
        )

        messages.append(
            {
                "role": "user",
                "content": user_text
            }
        )

        return messages

    def build_personality_confirmation_messages(
        self,
        spoken_param: str,
        param: str,
        value: int
    ) -> list[dict[str, str]]:

        system_prompt = (
            self.prompt_builder
            .build_personality_confirmation_prompt(
                self.persona
            )
        )

        current_parameters = personality_state.all()

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": (
                    f"Parâmetro alterado: {spoken_param}\n"
                    f"Nome interno: {param}\n"
                    f"Valor novo: {value}%"
                )
            }
        ]

        return messages

    async def generate_personality_confirmation(
        self,
        spoken_param: str,
        param: str,
        value: int,
        llm_provider
    ) -> str:

        messages = self.build_personality_confirmation_messages(
            spoken_param=spoken_param,
            param=param,
            value=value
        )

        response_text = await llm_provider.generate(
            messages
        )

        return response_text.strip()

    async def generate(
        self,
        user_text: str,
        llm_provider
    ) -> str:

        user_text = user_text.strip()

        if not user_text:
            return (
                "Entrada vazia. Sem dados, sem milagre operacional."
            )

        try:

            command = personality_command_parser.parse(
                user_text
            )

            if command:

                personality_state.set(
                    command.param,
                    command.value
                )

                final_value = personality_state.get(
                    command.param
                )

                response_text = await self.generate_personality_confirmation(
                    spoken_param=command.spoken_param,
                    param=command.param,
                    value=final_value,
                    llm_provider=llm_provider
                )

                conversation_manager.add_user_message(
                    user_text
                )

                conversation_manager.add_assistant_message(
                    response_text
                )

                return response_text

            messages = self.build_messages(
                user_text
            )

            response_text = await llm_provider.generate(
                messages
            )

            conversation_manager.add_user_message(
                user_text
            )

            conversation_manager.add_assistant_message(
                response_text
            )

            return response_text

        except Exception as error:

            logger.exception(
                f"Erro ao gerar resposta: {error}"
            )

            return (
                "Falha ao gerar resposta. O módulo cognitivo "
                "não concluiu a operação."
            )


response_generator = ResponseGenerator()