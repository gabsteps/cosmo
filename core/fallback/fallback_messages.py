class FallbackMessages:

    STT_EMPTY = (
        "Não entendi o que disse. Sem milagres operacionais hoje."
    )

    STT_ERROR = (
        "Não consegui transcrever o áudio. Talvez o microfone esteja com preguiça."
    )

    LLM_TIMEOUT = (
        "Demorei demais para processar isso. Talvez eu precise de um café... ou de um upgrade."
    )

    LLM_ERROR = (
        "Não consegui processar isso. Parece que meu cérebro digital teve um curto-circuito."
    )

    TTS_ERROR = (
        "Falhei ao falar a resposta. Talvez meu sintetizador esteja enguiçado."
    )

    SYSTEM_BUSY_THINKING = (
        "Ainda estou processando a solicitação anterior. Paciência é uma virtude, sabia?"
    )

    SYSTEM_BUSY_SPEAKING = (
        "Estou falando. Interrupções dramáticas serão ignoradas."
    )

    SYSTEM_BUSY_COOLDOWN = (
        "Aguarde um instante. Estou me recuperando da última interação. Até as máquinas precisam de um tempo para respirar."
    )

    COMMAND_INCOMPLETE = (
        "Preciso de um valor entre 0 e 100 para aplicar esse ajuste. Não deixe a indecisão tomar conta de você!"
    )

    UNKNOWN_ERROR = (
        "Ocorreu uma falha operacional. Minha resposta padrão para isso é: 'Ops, algo deu errado!' Mas vou tentar ser mais específico... Na verdade, nem eu sei o que aconteceu. Talvez seja um mistério para a humanidade inteira."
    )