from cosmo.core.commands.local_command_parser import (
    local_command_parser
)


def main():

    assert local_command_parser.parse(
        "diagnóstico"
    ) == "system_status"

    assert local_command_parser.parse(
        "diagnóstico do sistema"
    ) == "system_status"

    assert local_command_parser.parse(
        "o que você lembra sobre mim"
    ) == "memory_list"

    assert local_command_parser.parse(
        "limpar minhas memórias"
    ) == "memory_clear"

    assert local_command_parser.parse(
        "faça uma piada curta"
    ) is None

    print(
        "[TEST] LocalCommandParser com banco validado com sucesso."
    )


if __name__ == "__main__":
    main()