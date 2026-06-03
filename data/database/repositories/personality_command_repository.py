from cosmo.data.database.database import (
    db
)


class PersonalityCommandRepository:

    def get_active_parameter_aliases(self):

        return db.fetchall(
            """
            SELECT alias, parameter
            FROM personality_parameter_aliases
            WHERE active = 1
            ORDER BY length(alias) DESC
            """
        )

    def get_active_number_words(self):

        return db.fetchall(
            """
            SELECT word, value
            FROM number_words
            WHERE active = 1
            """
        )

    def get_active_command_words(self):

        return db.fetchall(
            """
            SELECT word
            FROM personality_command_words
            WHERE active = 1
            """
        )


personality_command_repository = PersonalityCommandRepository()