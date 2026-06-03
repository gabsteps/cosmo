from cosmo.cognition.personality.personality_command_parser import (
    personality_command_parser
)


def main():

    result = personality_command_parser.parse(
        "reduza o nível de honestidade para"
    )

    assert result.is_personality_command is True
    assert result.is_complete is False
    assert result.missing_value is True
    assert result.param == "honesty"

    result = personality_command_parser.parse(
        "abaixe honestidade para vinte por cento"
    )

    assert result.is_personality_command is True
    assert result.is_complete is True
    assert result.command.param == "honesty"
    assert result.command.value == 20

    result = personality_command_parser.parse(
        "faça uma piada curta"
    )

    assert result.is_personality_command is False

    print(
        "[TEST] PersonalityCommandParser validado com sucesso."
    )


if __name__ == "__main__":
    main()