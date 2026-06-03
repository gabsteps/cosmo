from cosmo.cognition.personality.personality_command_parser import (
    personality_command_parser
)


def main():

    result = personality_command_parser.parse(
        "ajuste humor para noventa"
    )

    assert result.is_personality_command is True
    assert result.is_complete is True
    assert result.command.param == "humor"
    assert result.command.value == 90

    result = personality_command_parser.parse(
        "reduza honestidade para vinte por cento"
    )

    assert result.is_personality_command is True
    assert result.is_complete is True
    assert result.command.param == "honesty"
    assert result.command.value == 20

    result = personality_command_parser.parse(
        "aumente estabilidade emocional para oitenta e cinco"
    )

    assert result.is_personality_command is True
    assert result.is_complete is True
    assert result.command.param == "emotional_stability"
    assert result.command.value == 85

    result = personality_command_parser.parse(
        "reduza honestidade para"
    )

    assert result.is_personality_command is True
    assert result.is_complete is False
    assert result.missing_value is True

    result = personality_command_parser.parse(
        "faça uma piada curta"
    )

    assert result.is_personality_command is False

    print(
        "[TEST] PersonalityCommandParser com banco validado com sucesso."
    )


if __name__ == "__main__":
    main()