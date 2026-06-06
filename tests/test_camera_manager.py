from cosmo.vision.camera.camera_manager import (
    camera_manager
)


def main():

    print(
        "[TEST] Iniciando teste da câmera"
    )

    started = camera_manager.start()

    print(
        f"[TEST] Camera started: {started}"
    )

    snapshot_before = camera_manager.snapshot()

    print(
        f"[TEST] Snapshot inicial: {snapshot_before}"
    )

    frame = camera_manager.capture_frame()

    if frame is None:

        print(
            "[TEST] Nenhum frame capturado"
        )

        print(
            f"[TEST] Erro: {camera_manager.last_error}"
        )

        camera_manager.stop()

        return

    print(
        f"[TEST] Frame capturado com shape: {frame.shape}"
    )

    snapshot_path = camera_manager.save_snapshot()

    print(
        f"[TEST] Snapshot salvo em: {snapshot_path}"
    )

    snapshot_after = camera_manager.snapshot()

    print(
        f"[TEST] Snapshot final: {snapshot_after}"
    )

    camera_manager.stop()

    print(
        "[TEST] Teste de câmera finalizado"
    )


if __name__ == "__main__":
    main()