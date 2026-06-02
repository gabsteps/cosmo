# cosmo/cognition/personality/persona_manager.py

from pathlib import Path
import yaml

from cosmo.cognition.personality.persona import Persona


class PersonaManager:
    def __init__(self, profiles_path: str, active_profile: str):
        self.profiles_path = Path(profiles_path)
        self.active_profile = active_profile
        self._persona: Persona | None = None

    def load(self) -> Persona:
        profile_path = self.profiles_path / f"{self.active_profile}.yaml"

        if not profile_path.exists():
            raise FileNotFoundError(f"Persona profile not found: {profile_path}")

        with profile_path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        self._persona = Persona(
            id=data.get("id", self.active_profile),
            name=data.get("name", data.get("char_name", "COSMO")),
            version=str(data.get("version", "1.0")),

            char_name=data.get("char_name", "COSMO"),
            char_persona=data.get("char_persona", ""),
            world_scenario=data.get("world_scenario", ""),
            char_greeting=data.get("char_greeting", ""),
            example_dialogue=data.get("example_dialogue", ""),

            description=data.get("description", ""),
            personality=data.get("personality", ""),
            scenario=data.get("scenario", ""),
            first_mes=data.get("first_mes", ""),
            mes_example=data.get("example_dialogue", ""),

            parameters=data.get("parameters", {}),
            metadata=data.get("metadata", {}),
        )

        return self._persona

    @property
    def persona(self) -> Persona:
        if self._persona is None:
            return self.load()

        return self._persona