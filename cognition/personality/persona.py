# cosmo/cognition/personality/persona.py

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Persona:
    id: str
    name: str
    version: str

    char_name: str
    char_persona: str
    world_scenario: str
    char_greeting: str
    example_dialogue: str

    description: str
    personality: str
    scenario: str
    first_mes: str
    mes_example: str

    parameters: dict[str, int] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def get_parameter(self, name: str, default: int = 50) -> int:
        return int(self.parameters.get(name, default))