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

from cosmo.core.fallback.fallback_manager import (
    fallback_manager
)

from cosmo.cognition.personality.personality_persistence import (
    personality_persistence
)

from cosmo.core.commands.local_command_parser import (
    local_command_parser
)

from cosmo.core.commands.local_command_handler import (
    local_command_handler
)

from cosmo.cognition.memory.memory_manager import (
    memory_manager
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

        saved_parameters = personality_persistence.load(
            active_profile=self.persona.id
        )

        if saved_parameters:
            personality_state.replace(
                saved_parameters
            )

            logger.info(
                "Parâmetros de personalidade carregados do estado persistido"
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

        memory_context = memory_manager.build_memory_context(
            user_text=user_text
        )

        if memory_context:

            messages.append(
                {
                    "role": "system",
                    "content": (
                        "MEMÓRIAS RELEVANTES:\n"
                        f"{memory_context}\n\n"
                        "Use essas memórias apenas quando forem úteis para responder. "
                        "Não mencione que está usando memória."
                    )
                }
            )

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
            return fallback_manager.stt_empty()

        try:

            local_command = local_command_parser.parse(
                user_text
            )

            if local_command:

                response_text = local_command_handler.handle(
                    local_command
                )

                if response_text:

                    conversation_manager.add_user_message(
                        user_text
                    )

                    conversation_manager.add_assistant_message(
                        response_text
                    )

                    memory_manager.process_interaction(
                        user_text=user_text,
                        assistant_text=response_text,
                        extract_memories=False
                    )

                    return response_text

            parse_result = personality_command_parser.parse(
                user_text
            )

            if (
                parse_result.is_personality_command
                and not parse_result.is_complete
            ):

                response_text = fallback_manager.command_incomplete()

                conversation_manager.add_user_message(
                    user_text
                )

                conversation_manager.add_assistant_message(
                    response_text
                )

                return response_text

            if parse_result.is_complete and parse_result.command:

                command = parse_result.command

                personality_state.set(
                    command.param,
                    command.value
                )

                personality_persistence.save(
                    active_profile=self.persona.id,
                    parameters=personality_state.all()
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

                memory_manager.process_interaction(
                    user_text=user_text,
                    assistant_text=response_text,
                    extract_memories=False
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

            memory_manager.process_interaction(
                user_text=user_text,
                assistant_text=response_text,
                extract_memories=True
            )

            return response_text

        except Exception as error:

            logger.exception(
                f"Erro ao gerar resposta: {error}"
            )

            return fallback_manager.llm_error()


response_generator = ResponseGenerator()