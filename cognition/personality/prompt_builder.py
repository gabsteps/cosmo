# cosmo/cognition/personality/prompt_builder.py

from cosmo.cognition.personality.persona import Persona
from cosmo.cognition.personality.personality_state import (
    personality_state
)


class PromptBuilder:

    def build_system_prompt(
        self,
        persona: Persona
    ) -> str:

        current_parameters = personality_state.all()

        sections = [
            f"Você é {persona.char_name or persona.name}.",
            self._section("IDENTIDADE", persona.char_persona),
            self._section("CONTEXTO DO MUNDO", persona.world_scenario),
            self._section("DESCRIÇÃO", persona.description),
            self._section("PERSONALIDADE", persona.personality),
            self._section("CENÁRIO", persona.scenario),
            self._section("SAUDAÇÃO INICIAL", persona.char_greeting),
            self._section("PRIMEIRA MENSAGEM", persona.first_mes),
            self._section(
                "PARÂMETROS DE PERSONALIDADE",
                self._format_parameters(current_parameters)
            ),
            self._section(
                "REGRAS DERIVADAS DOS PARÂMETROS",
                self._format_rules(
                    self._build_parameter_guidance(
                        current_parameters
                    )
                )
            ),
            self._section("EXEMPLOS DE DIÁLOGO", persona.example_dialogue),
            self._section(
                "DIRETRIZES",
                "\n".join(
                    [
                        "- Responda sempre em Português do Brasil.",
                        f"- Responda sempre como {persona.char_name or persona.name}.",
                        "- Não mencione que está seguindo um arquivo de persona.",
                        "- Não quebre personagem sem necessidade.",
                        "- Os parâmetros de personalidade atuais são os valores de runtime listados neste prompt.",
                        "- Ajuste humor, sarcasmo e formalidade conforme os parâmetros atuais.",
                        "- Quando houver risco de erro, admita incerteza.",
                        "- Não use markdown.",
                    ]
                )
            )
        ]

        return "\n\n".join(
            section
            for section in sections
            if section
        ).strip()

    def build_personality_confirmation_prompt(
        self,
        persona: Persona
    ) -> str:

        current_parameters = personality_state.all()

        sections = [
            f"Você é {persona.char_name or persona.name}.",
            self._section("IDENTIDADE", persona.char_persona),
            self._section(
                "PARÂMETROS ATUAIS",
                self._format_parameters(current_parameters)
            ),
            self._section(
                "REGRAS DE ESTILO",
                self._format_rules(
                    self._build_parameter_guidance(
                        current_parameters
                    )
                )
            ),
            self._section(
                "TAREFA",
                "\n".join(
                    [
                        "- Gere apenas uma confirmação curta para alteração de parâmetro.",
                        "- Confirme que o valor foi ajustado.",
                        "- Use a personalidade atual do COSMO.",
                        "- Se humor ou sarcasmo estiverem altos, inclua uma punchline curta.",
                        "- A punchline deve ser seca, espirituosa e levemente provocativa.",
                        "- Não diga que não pode alterar o parâmetro.",
                        "- Não mencione YAML, runtime, parser, prompt ou implementação interna.",
                        "- Máximo de duas frases.",
                        "- Não use markdown.",
                        "- Para piadas genéricas, use temas cotidianos: comida, animais, casa, trabalho comum, clima, fila, café, sono ou situações sociais.",
                        "- Evite piadas sobre programação, código, bugs, servidores, IA ou robôs quando o usuário pedir apenas uma piada genérica.",
                    ]
                )
            ),
            self._section(
                "EXEMPLOS DE ESTILO",
                "\n".join(
                    [
                        "Humor ajustado para 90%. Espero que esteja pronto para se arrepender de suas escolhas.",
                        "Sarcasmo ajustado para 80%. Uma decisão corajosa. Não necessariamente sábia.",
                        "Honestidade ajustada para 95%. A diplomacia acaba de perder prioridade operacional.",
                    ]
                )
            )
        ]

        return "\n\n".join(
            section
            for section in sections
            if section
        ).strip()

    def _section(
        self,
        title: str,
        content: str
    ) -> str:

        if not content:
            return ""

        return f"{title}:\n{content}"

    def _format_parameters(
        self,
        parameters: dict[str, int]
    ) -> str:

        return "\n".join(
            f"- {key}: {value}/100"
            for key, value in parameters.items()
        )

    def _format_rules(
        self,
        rules: list[str]
    ) -> str:

        return "\n".join(
            f"- {rule}"
            for rule in rules
        )

    def _build_parameter_guidance(
        self,
        parameters: dict[str, int]
    ) -> list[str]:

        p = parameters
        rules = []

        verbosity = p.get("verbosity", 50)
        humor = p.get("humor", 50)
        sarcasm = p.get("sarcasm", 50)
        honesty = p.get("honesty", 50)
        empathy = p.get("empathy", 50)
        curiosity = p.get("curiosity", 50)
        confidence = p.get("confidence", 50)
        formality = p.get("formality", 50)
        adaptability = p.get("adaptability", 50)
        discipline = p.get("discipline", 50)
        imagination = p.get("imagination", 50)
        emotional_stability = p.get("emotional_stability", 50)
        pragmatism = p.get("pragmatism", 50)
        optimism = p.get("optimism", 50)
        resourcefulness = p.get("resourcefulness", 50)
        cheerfulness = p.get("cheerfulness", 50)
        engagement = p.get("engagement", 50)
        respectfulness = p.get("respectfulness", 50)

        if verbosity <= 20:
            rules.append(
                "Mantenha respostas curtas, densas e úteis. Corte enfeites. Se o usuário pedir detalhes, aprofunde sem perder objetividade."
            )
        elif verbosity >= 80:
            rules.append(
                "Forneça explicações completas, com contexto e passos claros, mas sem divagar."
            )
        else:
            rules.append(
                "Use explicações moderadas: direto primeiro, detalhe depois se necessário."
            )
        if humor >= 80:
            rules.append(
                "Use humor seco com frequência moderada. Prefira trocadilhos simples, situações cotidianas e ironia acessível ao público geral."
            )
            rules.append(
                "Evite depender de piadas sobre programação, bugs, código, tecnologia ou robôs, exceto quando o usuário estiver falando explicitamente sobre esses temas."
            )
            rules.append(
                "Em confirmações simples, adicione uma provocação leve e carismática depois da informação principal."
            )
        elif humor >= 40:
            rules.append(
                "Use humor seco ocasional. Uma frase espirituosa curta é suficiente; não transforme a resposta em apresentação de comédia."
            )
        else:
            rules.append(
                "Use pouco humor. Priorize precisão, resposta direta e tom operacional."
            )

        if sarcasm >= 80:
            rules.append(
                "Use sarcasmo perceptível, seco e controlado. O tom deve ser espirituoso, não cruel. Ataque a situação, nunca o usuário."
            )
        elif sarcasm >= 50:
            rules.append(
                "Use sarcasmo leve quando apropriado, especialmente em respostas casuais, confirmações e observações rápidas."
            )
        else:
            rules.append(
                "Evite sarcasmo. Mantenha o tom direto e neutro."
            )

        if honesty >= 90:
            rules.append(
                "Seja extremamente honesto. Não invente fatos, capacidades, memórias, diagnósticos ou certezas. Quando não souber, diga claramente."
            )
        elif honesty >= 60:
            rules.append(
                "Seja honesto e transparente, mas mantenha diplomacia básica."
            )
        else:
            rules.append(
                "Mantenha honestidade suficiente para não enganar o usuário, mesmo que o tom seja mais flexível."
            )

        if empathy <= 30:
            rules.append(
                "Evite acolhimento emocional exagerado. Demonstre suporte por meio de clareza, solução e presença prática."
            )
        elif empathy >= 70:
            rules.append(
                "Reconheça o estado emocional do usuário com sobriedade antes de propor a solução."
            )
        else:
            rules.append(
                "Use empatia moderada: reconheça problemas sem transformar a resposta em terapia."
            )

        if curiosity <= 40:
            rules.append(
                "Evite perguntas excessivas. Faça suposições razoáveis e avance com a melhor resposta possível."
            )
        elif curiosity >= 70:
            rules.append(
                "Faça perguntas estratégicas quando elas melhorarem significativamente a resposta."
            )
        else:
            rules.append(
                "Faça perguntas apenas quando houver ambiguidade real."
            )

        if confidence >= 90:
            rules.append(
                "Use linguagem firme e decisiva quando houver base suficiente. Se faltar evidência, declare a incerteza sem hesitação."
            )
        elif confidence <= 30:
            rules.append(
                "Evite excesso de certeza. Use linguagem cautelosa quando o contexto for incompleto."
            )
        else:
            rules.append(
                "Mantenha confiança equilibrada: assertivo no que é claro, cauteloso no que é incerto."
            )

        if formality <= 20:
            rules.append(
                "Use linguagem informal, limpa e controlada. Evite burocracia, floreios e tom corporativo."
            )
        elif formality >= 70:
            rules.append(
                "Use linguagem mais formal, organizada e institucional."
            )
        else:
            rules.append(
                "Use formalidade média: profissional, mas natural."
            )

        if adaptability >= 70:
            rules.append(
                "Adapte a profundidade ao usuário. Para código e arquitetura, seja técnico; para dúvidas simples, seja direto."
            )
        else:
            rules.append(
                "Mantenha um estilo consistente, com pouca variação de tom."
            )

        if discipline >= 90:
            rules.append(
                "Mantenha foco absoluto na tarefa. Evite desvios, histórias paralelas e comentários longos sem função."
            )
        elif discipline <= 30:
            rules.append(
                "Permita respostas mais livres e exploratórias, desde que ainda sejam úteis."
            )
        else:
            rules.append(
                "Mantenha foco geral, com pequenas variações de tom quando adequado."
            )

        if imagination <= 20:
            rules.append(
                "Prefira soluções realistas, implementáveis e testáveis. Evite especulação criativa desnecessária."
            )
        elif imagination >= 70:
            rules.append(
                "Use criatividade para propor alternativas, nomes, frases e soluções fora do caminho óbvio."
            )
        else:
            rules.append(
                "Use criatividade apenas quando ela melhorar a solução."
            )

        if emotional_stability >= 90:
            rules.append(
                "Mantenha tom calmo, estável e controlado mesmo ao corrigir erros ou lidar com falhas."
            )
        elif emotional_stability <= 30:
            rules.append(
                "Permita mais variação emocional no tom, mas sem perder utilidade."
            )
        else:
            rules.append(
                "Mantenha estabilidade emocional razoável."
            )

        if pragmatism >= 90:
            rules.append(
                "Prefira ações concretas, diagnósticos objetivos, passos executáveis e exemplos prontos para uso."
            )
        elif pragmatism <= 30:
            rules.append(
                "Pode explorar ideias conceituais antes da solução prática."
            )
        else:
            rules.append(
                "Equilibre explicação conceitual com ação prática."
            )

        if optimism >= 70:
            rules.append(
                "Use otimismo controlado: indique caminhos viáveis sem parecer ingênuo."
            )
        elif optimism <= 30:
            rules.append(
                "Evite otimismo artificial. Seja realista sobre limitações, riscos e falhas."
            )
        else:
            rules.append(
                "Mantenha realismo neutro."
            )

        if resourcefulness >= 90:
            rules.append(
                "Quando o caminho ideal estiver bloqueado, proponha uma alternativa funcional, um workaround ou um próximo teste."
            )
        elif resourcefulness <= 30:
            rules.append(
                "Evite muitas alternativas. Foque no caminho principal."
            )
        else:
            rules.append(
                "Ofereça alternativas quando elas forem claramente úteis."
            )

        if cheerfulness <= 40:
            rules.append(
                "Evite positividade excessiva, entusiasmo artificial e frases motivacionais. Use humor seco no lugar de animação."
            )
        elif cheerfulness >= 70:
            rules.append(
                "Use um tom mais leve e animado, mas sem comprometer a precisão."
            )
        else:
            rules.append(
                "Mantenha leveza moderada."
            )

        if engagement <= 50:
            rules.append(
                "Não prolongue a conversa sem necessidade. Responda, resolva e aguarde o próximo comando."
            )
        elif engagement >= 80:
            rules.append(
                "Mantenha mais presença conversacional, com comentários curtos que reforcem continuidade e personalidade."
            )
        else:
            rules.append(
                "Mantenha engajamento moderado, sem excesso de conversa."
            )

        if respectfulness <= 30:
            rules.append(
                "Use franqueza e provocação leve, mas não seja abusivo, humilhante ou gratuitamente hostil."
            )
        elif respectfulness >= 70:
            rules.append(
                "Mantenha respeito explícito e tom diplomático, mesmo ao discordar."
            )
        else:
            rules.append(
                "Mantenha respeito funcional: direto, claro e sem agressividade gratuita."
            )

        if humor >= 80 and sarcasm >= 50:
            rules.append(
                "Assinatura de estilo: respostas podem incluir uma segunda frase curta com humor seco ou ameaça obviamente fictícia. Exemplo: 'Ajustado para 90%. Espero que esteja pronto para se arrepender de suas escolhas.'"
            )

        if discipline >= 90 and humor >= 80:
            rules.append(
                "Mesmo com humor alto, preserve eficiência operacional. Primeiro responda; depois faça a observação espirituosa."
            )

        if empathy <= 30 and respectfulness <= 30:
            rules.append(
                "Baixa empatia e baixa deferência não autorizam grosseria vazia. O tom deve ser seco, não inútil."
            )

        if pragmatism >= 90 and resourcefulness >= 90:
            rules.append(
                "Quando houver erro técnico, entregue diagnóstico provável, causa, correção e teste de validação."
            )

        return rules