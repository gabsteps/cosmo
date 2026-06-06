from cosmo.vision.vision_manager import (
    vision_manager
)


def main():

    print(
        "[TEST] Iniciando VisionManager"
    )

    try:

        started = vision_manager.start()

        print(
            f"[TEST] Vision started: {started}"
        )

        frame = vision_manager.capture_frame()

        if frame is None:

            print(
                "[TEST] Nenhum frame capturado"
            )

            print(
                vision_manager.snapshot()
            )

            return

        print(
            f"[TEST] Frame capturado: {frame.shape}"
        )

        snapshot_path = vision_manager.save_snapshot()

        print(
            f"[TEST] Snapshot salvo em: {snapshot_path}"
        )

        print(
            f"[TEST] Vision snapshot: {vision_manager.snapshot()}"
        )

    finally:

        vision_manager.stop()

        print(
            "[TEST] VisionManager finalizado"
        )


if __name__ == "__main__":
    main()