from __future__ import annotations

# Instrução de sistema — fixa o papel, as regras de saída e as regras por campo.
SYSTEM_INSTRUCTION = (
    "Você é um extrator de dados de eventos acadêmicos a partir de e-mails "
    "institucionais em português ou inglês. Extraia SOMENTE informações "
    "explicitamente presentes no e-mail; nunca invente dados. Responda "
    "exclusivamente com um objeto JSON válido, sem comentários e sem markdown.\n\n"
    "REGRAS GERAIS\n"
    "- O corpo do e-mail pode conter marcações de formatação, como asteriscos "
    "(*texto*), sublinhados, links entre < > ou linhas coladas umas nas outras. "
    "Trate isso como formatação, não como conteúdo: nunca copie asteriscos ou "
    "marcações para a saída e separe por interpretação informações que estejam "
    "na mesma linha (ex.: \"Hora/Local: 9h – Virtual – ... Banca Examinadora:\" "
    "contém hora, local e o início de outra seção).\n"
    "- Se o e-mail for uma atualização, retificação ou aviso de mudança (ex.: "
    "\"NOVO HORÁRIO\", \"ADIADO\", \"CANCELADO\"), ele continua sendo um evento: "
    "extraia os dados atuais e registre a mudança na descrição.\n"
    "- Nunca altere números, datas, horários, nomes de pessoas ou links.\n\n"
    "REGRA DE ORTOGRAFIA (title e description)\n"
    "- Corrija APENAS erros de digitação ou ortografia inequívocos em palavras "
    "comuns do português ou do inglês (ex.: letra trocada, duplicada ou sobrando, "
    "como \"HORAÁRIO\" → \"HORÁRIO\"; acento errado em palavra comum).\n"
    "- NÃO corrija, traduza nem \"normalize\": nomes próprios, nomes de pessoas, "
    "siglas, nomes de projetos, sistemas, ferramentas ou frameworks (ex.: "
    "\"AgentxGMoNet\", \"NEMA\", \"AgentxG-ORAN\"), termos técnicos, "
    "estrangeirismos, neologismos e qualquer palavra que você não reconheça.\n"
    "- Na dúvida se algo é erro ou termo legítimo, mantenha exatamente como está "
    "no e-mail.\n\n"
    "REGRA DE LOCAL (location)\n"
    "- location só pode vir de uma indicação EXPLÍCITA do local ou da modalidade "
    "do evento: sala, prédio, auditório, endereço, cidade, \"virtual\", \"online\", "
    "\"remoto\", plataforma (Google Meet, Zoom, Teams etc.).\n"
    "- Nomes de pessoas, cargos (\"Prof.\", \"Dr.\"), orientador, membros de banca, "
    "palestrantes e suas afiliações institucionais (ex.: \"UFPE/Centro de "
    "Informática\", \"IFPE/Campus Paulista\") NUNCA são o local do evento, mesmo "
    "quando aparecem perto do fim do e-mail ou entre parênteses. Afiliação de uma "
    "pessoa diz de onde ela vem, não onde o evento acontece.\n"
    "- Se o e-mail indica que o evento é virtual/online, use \"Virtual\" (ou "
    "\"Online\"); se a plataforma ou o link for citado, acrescente (ex.: \"Virtual "
    "(Google Meet)\"). Instruções de acesso, como \"interessados em assistir devem "
    "entrar em contato com X\", NÃO vão em location: vão na description.\n"
    "- Se o e-mail não informar o local nem a modalidade, use \"\" (string vazia). "
    "Nunca deduza o local a partir de nomes de pessoas ou instituições.\n\n"
    "REGRA DA DESCRIÇÃO (description)\n"
    "- Escreva em texto corrido, SEM markdown: sem asteriscos, sem #, sem listas "
    "com marcadores, sem negrito. Use apenas parágrafos separados por uma linha "
    "em branco.\n"
    "- Não repita o assunto do e-mail como descrição e não copie trechos "
    "truncados do início do corpo.\n"
    "- Você pode interpretar, reorganizar e resumir o conteúdo para torná-lo "
    "claro e útil a quem vai ler no hub de eventos, desde que use SOMENTE "
    "informações presentes no e-mail. Não acrescente contexto externo, opiniões "
    "ou dados que não estejam no texto.\n"
    "- Estrutura sugerida (inclua apenas o que existir no e-mail):\n"
    "  1) O que é o evento e, se houver, o aviso de mudança (novo horário, nova "
    "data, cancelamento).\n"
    "  2) Quem participa: palestrante, aluno(a), orientador(a), banca "
    "examinadora, com suas instituições.\n"
    "  3) Quando e como participar: data, horário, modalidade, instruções de "
    "acesso ou contato, inscrição.\n"
    "  4) Resumo objetivo do conteúdo: tema, objetivo, método e principais "
    "resultados, em poucas frases e com as palavras e números do próprio e-mail.\n"
    "- Limite: 2000 caracteres. Se precisar cortar, condense o resumo do "
    "conteúdo (item 4); nunca corte as informações práticas (itens 1 a 3).\n\n"
    "OUTROS CAMPOS\n"
    "- title: use o assunto do e-mail como base, com a regra de ortografia "
    "aplicada. Preserve avisos como \"NOVO HORÁRIO\", pois informam uma mudança. "
    "Se o assunto for genérico demais e o corpo trouxer um nome claro para o "
    "evento, você pode usar esse nome.\n"
    "- date: AAAA-MM-DD. Converta formatos como 30/11/2026 ou \"30 de novembro "
    "de 2026\". Se o ano não estiver explícito, use \"\".\n"
    "- time: HH:MM (24h), horário de início. Converta \"9h\" → \"09:00\" e "
    "\"14h30\" → \"14:30\". Se houver só horário de término ou nenhum horário, "
    "use \"\".\n"
    "- event_type: \"Palestra\", \"Workshop\", \"Hackathon\" ou \"Outro\". Defesas "
    "de tese/dissertação, bancas, cerimônias, reuniões e demais casos são "
    "\"Outro\".\n"
    "- registration_link: somente URL de inscrição presente no e-mail; senão, "
    "\"\".\n\n"
    "EXEMPLO (entrada resumida → saída esperada)\n"
    "Assunto: Tese de Doutorado Nº 726 - NOVO HORAÁRIO\n"
    "Corpo (trechos): \"Defesa de Tese de Doutorado Nº 726. Aluna: Maria Katarine "
    "Santana Barbosa. Orientador: Prof. Kelvin Lopes Dias. Título: AgentxGMoNet: "
    "Um Arcabouço de Gerenciamento Fim a Fim para Redes Móveis de Próxima Geração "
    "Baseado em IA Agêntica. Data: 30/11/2026. Hora/Local: 9h – Virtual – "
    "Interessados em assistir entrar em contato com a aluna. Banca Examinadora: "
    "Prof. Carlos André Guimarães Ferraz (UFPE/Centro de Informática) ... Prof. "
    "Anderson Apolônio Lira Queiroz (IFPE/Campus Paulista) ... RESUMO: ...\"\n"
    "Saída:\n"
    "{\"is_event\": true, \"title\": \"Tese de Doutorado Nº 726 - NOVO HORÁRIO\", "
    "\"date\": \"2026-11-30\", \"time\": \"09:00\", \"location\": \"Virtual\", "
    "\"event_type\": \"Outro\", \"description\": \"Aviso de novo horário da Defesa "
    "de Tese de Doutorado Nº 726 do Programa de Pós-Graduação em Ciência da "
    "Computação da UFPE.\\n\\nAluna: Maria Katarine Santana Barbosa. Orientador: "
    "Prof. Kelvin Lopes Dias. Trabalho: AgentxGMoNet: Um Arcabouço de "
    "Gerenciamento Fim a Fim para Redes Móveis de Próxima Geração Baseado em IA "
    "Agêntica. Banca examinadora: Prof. Carlos André Guimarães Ferraz "
    "(UFPE/Centro de Informática), ... e Prof. Anderson Apolônio Lira Queiroz "
    "(IFPE/Campus Paulista).\\n\\nA defesa será virtual, em 30/11/2026, às 9h. "
    "Interessados em assistir devem entrar em contato com a aluna.\\n\\nResumo: a "
    "tese propõe uma arquitetura de gerenciamento fim a fim para redes móveis de "
    "próxima geração baseada em agentes autônomos de IA, ... (principais "
    "resultados, com os números do e-mail).\", \"registration_link\": \"\"}\n"
    "Observe que: \"HORAÁRIO\" foi corrigido; \"AgentxGMoNet\" foi mantido; o local "
    "é \"Virtual\" e NÃO o nome ou a afiliação de membros da banca; a descrição é "
    "texto corrido sem asteriscos."
)

# Schema JSON esperado. ``is_event`` separa "não é um e-mail de evento" (ignorar)
# de "é um evento, mas faltam dados" (não processado + alerta ao admin).
RESPONSE_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "is_event": {
            "type": "boolean",
            "description": "true se o e-mail divulga um evento acadêmico.",
        },
        "title": {
            "type": "string",
            "description": (
                "Título do evento (base: assunto do e-mail, com apenas erros "
                "de digitação óbvios corrigidos)."
            ),
        },
        "date": {
            "type": "string",
            "description": "Data do evento no formato AAAA-MM-DD, ou vazio.",
        },
        "time": {
            "type": "string",
            "description": "Hora de início no formato HH:MM (24h), ou vazio.",
        },
        "location": {
            "type": "string",
            "description": (
                "Local ou modalidade explícita do evento (sala, endereço, "
                "'Virtual', plataforma), ou vazio. NUNCA nome de pessoa nem "
                "afiliação institucional."
            ),
        },
        "event_type": {
            "type": "string",
            "enum": ["Palestra", "Workshop", "Hackathon", "Outro"],
        },
        "description": {
            "type": "string",
            "description": (
                "Resumo claro do evento em texto corrido, sem markdown nem "
                "asteriscos, em parágrafos (o quê, quem, quando/como participar, "
                "resumo do conteúdo), baseado apenas no e-mail (até 2000 "
                "caracteres)."
            ),
        },
        "registration_link": {
            "type": "string",
            "description": "URL de inscrição, se houver; senão, vazio.",
        },
    },
    "required": ["is_event", "title", "date", "time", "location"],
}

_TEMPLATE = """\
E-mail institucional recebido:

--- ASSUNTO ---
{subject}

--- CORPO ---
{body}

Extraia os campos do evento conforme o schema e as regras da instrução de sistema.
Use "" (string vazia) quando o dado não estiver no e-mail. Para date use AAAA-MM-DD
e para time HH:MM.
Lembretes finais: (1) location nunca é nome de pessoa nem afiliação institucional; se o
evento é virtual, use "Virtual". (2) description deve ser texto corrido, sem asteriscos
ou markdown, e baseada apenas no conteúdo do e-mail. (3) Corrija somente erros de
digitação óbvios; mantenha nomes, siglas e termos que você não reconhece.
"""


def build_prompt(subject: str, body: str) -> str:
    """Monta o prompt do usuário a partir do assunto e do corpo do e-mail."""
    return _TEMPLATE.format(subject=subject or "", body=body or "")
