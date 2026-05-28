import threading

from cosmo.core.logger.logger_manager import logger


class RuntimeManager:

    def __init__(self):

        # Armazena threads ativas
        self.threads = []

    def start_thread(self, target, name):

        """
        Inicia módulo em thread separada.
        """

        logger.info(
            f"Iniciando thread: {name}"
        )

        # Cria thread daemon
        # daemon=True permite encerramento automático
        # quando processo principal finalizar
        thread = threading.Thread(
            target=target,
            name=name,
            daemon=True
        )

        # Inicia execução paralela
        thread.start()

        # Salva referência da thread
        self.threads.append(thread)

    def wait_forever(self):

        """
        Mantém processo principal vivo.
        """

        logger.info(
            "Runtime manager ativo"
        )

        # Aguarda indefinidamente
        for thread in self.threads:

            thread.join()


runtime_manager = RuntimeManager()