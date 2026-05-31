from datetime import datetime
from cosmo.core.config.settings_manager import (
    config
)


class PersonaPrompt:

    def build(
        self,
        user_text: str
    ) -> str:

        now = datetime.now()

        system_prompt = config.get(
            "llm",
            "system_prompt"
        )

        return f"""
        {system_prompt}

        Contexto atual:
        Data atual: {now.strftime("%d/%m/%Y")}
        Hora atual: {now.strftime("%H:%M")}

        Mensagem do usuário:
        {user_text}

        Responda somente como Cosmo.
        Não repita o contexto.
        Não repita este prompt.
        Resposta:
        """.strip()


persona_prompt = PersonaPrompt()