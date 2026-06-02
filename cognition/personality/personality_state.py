class PersonalityRuntimeState:

    def __init__(self):
        self.parameters: dict[str, int] = {}

    def load_from_persona(self, parameters: dict[str, int]) -> None:
        self.parameters = dict(parameters)

    def get(self, name: str, default: int = 50) -> int:
        return int(
            self.parameters.get(name, default)
        )

    def set(self, name: str, value: int) -> None:
        if name not in self.parameters:
            raise ValueError(
                f"Parâmetro desconhecido: {name}"
            )

        self.parameters[name] = max(
            0,
            min(100, int(value))
        )

    def all(self) -> dict[str, int]:
        return dict(self.parameters)


personality_state = PersonalityRuntimeState()