class FallbackMessages:

    STT_EMPTY = (
        "Não entendi o que disse."
    )

    STT_ERROR = (
        "Não consegui transcrever o áudio."
    )

    LLM_TIMEOUT = (
        "Demorei demais para processar isso."
    )

    LLM_ERROR = (
        "Não consegui processar isso."
    )

    TTS_ERROR = (
        "Falhei ao falar a resposta."
    )

    SYSTEM_BUSY_THINKING = (
        "Ainda estou processando a solicitação anterior."
    )

    SYSTEM_BUSY_SPEAKING = (
        "Estou falando. Interrupções dramáticas serão ignoradas."
    )

    SYSTEM_BUSY_COOLDOWN = (
        "Aguarde um instante."
    )

    COMMAND_INCOMPLETE = (
        "Preciso de um valor entre 0 e 100 para aplicar esse ajuste."
    )

    UNKNOWN_ERROR = (
        "Ocorreu uma falha operacional."
    )