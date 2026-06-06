from pathlib import Path
from datetime import datetime, timezone

import cv2


class FrameStore:

    def __init__(
        self
    ):

        self.last_frame = None
        self.last_frame_at = None
        self.last_snapshot_path = None

    def set_frame(
        self,
        frame
    ) -> None:

        self.last_frame = frame
        self.last_frame_at = datetime.now(
            timezone.utc
        ).isoformat()

    def get_frame(
        self
    ):

        return self.last_frame

    def save_snapshot(
        self,
        path: str
    ) -> str | None:

        if self.last_frame is None:
            return None

        snapshot_path = Path(
            path
        )

        snapshot_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        ok = cv2.imwrite(
            str(snapshot_path),
            self.last_frame
        )

        if not ok:
            return None

        self.last_snapshot_path = str(
            snapshot_path
        )

        return self.last_snapshot_path

    def snapshot(
        self
    ) -> dict:

        return {
            "last_frame_at": self.last_frame_at,
            "last_snapshot_path": self.last_snapshot_path,
            "has_frame": self.last_frame is not None,
        }


frame_store = FrameStore()