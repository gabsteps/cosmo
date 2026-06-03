from cosmo.cognition.personality.personality_persistence import (
    personality_persistence,
    STATE_FILE
)

from cosmo.cognition.personality.personality_state import (
    personality_state
)


def main():

    if STATE_FILE.exists():
        STATE_FILE.unlink()

    personality_state.replace(
        {
            "humor": 90,
            "honesty": 20,
            "sarcasm": 70
        }
    )

    personality_persistence.save(
        active_profile="cosmo",
        parameters=personality_state.all()
    )

    loaded = personality_persistence.load(
        active_profile="cosmo"
    )

    assert loaded is not None
    assert loaded["humor"] == 90
    assert loaded["honesty"] == 20
    assert loaded["sarcasm"] == 70

    wrong_profile = personality_persistence.load(
        active_profile="outro"
    )

    assert wrong_profile is None

    print(
        "[TEST] Persistência de personalidade validada com sucesso."
    )


if __name__ == "__main__":
    main()