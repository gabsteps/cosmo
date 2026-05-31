class TranscriptNormalizer:

    def __init__(self):

        self.wake_words = {
            "cosmo",
            "cosmos",
            "cosme",
            "zenith",
            "zênite"
        }

    def normalize(self, text: str) -> str:

        if not text:
            return ""

        return text.strip().lower()

    def should_ignore(self, text: str) -> bool:

        normalized = self.normalize(text)

        if not normalized:
            return True

        if normalized in self.wake_words:
            return True

        if len(normalized) < 3:
            return True

        return False


transcript_normalizer = TranscriptNormalizer()