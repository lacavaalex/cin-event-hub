# Roteiro do pitch — Hub de Eventos CIn (IESI)

Apoio para a fala. Não é texto para decorar. Slides ≈ 7 min · demo ≈ 5–6 min · Q&A à parte. Total de fala ≈ 12–13 min (limite do professor: 10–15).

Sugestão de quem apresenta: divida por **frente de trabalho** (a equipe define os nomes). Ex.: problema e stakeholders → quem conduz o produto; decisões técnicas → quem atua no back-end e no banco; demo → quem atua no front e no back; fechamento → quem facilitou o projeto.

| # | Slide | Tempo | Objetivo | Fala (ideias, não frases prontas) | Transição |
|---|-------|-------|----------|-----------------------------------|-----------|
| 1 | Abertura | 0:30 | Dizer o que é e por que prestar atenção | Todo aluno do CIn já perdeu uma palestra ou um hackathon no meio de dezenas de e-mails. O Hub de Eventos existe para isso não acontecer. | "Vamos ver o problema." |
| 2 | O problema | 0:50 | Concretizar a dor | O CIn divulga eventos por e-mail em massa para as contas @cin.ufpe.br. No mesmo lugar chegam vendas de usados, achados e perdidos e avisos de turma. O evento vira ruído e ninguém enxerga o que vem pela frente. (Fonte: Entrega 1 e 2.) | "Quem sente isso?" |
| 3 | Quem é afetado | 0:50 | Conectar com alunos, ASCOM e CIn | Alunos perdem oportunidades. O CIn tem um ecossistema ativo, com networking e aprendizado, que fica invisível. **Sobre a ASCOM:** dizer que é a hipótese de quem divulga institucionalmente e que as necessidades dela ainda vão ser validadas (selo "A validar"). | "Qual é a resposta?" |
| 4 | A solução | 1:00 | Mostrar o fluxo e o valor | Lemos a caixa institucional pela Gmail API, extraímos título, data, hora e local (parser primeiro, Gemini quando o texto é livre), validamos e publicamos. Nenhum evento vencido fica no ar: a limpeza roda todo dia às 3h. Do remetente guardamos só o domínio. | "O que já está de pé?" |
| 5 | O que funciona | 1:00 | Separar entregue, parcial e planejado | Ler as três colunas com calma. Assumir o parcial (favoritos sem a ★ na tela, status da extração sem tela, Home com 100 eventos) e o planejado (US 4.5, 4.6, Docker). | "Por que construímos assim?" |
| 6 | Decisões | 1:15 | Defender 3–4 decisões | Escolha as que a plateia mais valoriza: três camadas e monólito (sem excesso); Python/FastAPI (Gmail e Gemini nativos); PostgreSQL (integridade); LGPD (só o que é do evento). As outras ficam para o Q&A. | "Vamos ver funcionando." |
| 7 | Evidências | 0:45 | Provar que existe MVP e preparar a demo | 291 testes de backend, 106 verificações do banco, 83 casos de jornada rodados na `develop`, 12 defeitos já registrados. A captura usa dados de demonstração. | **→ IR PARA O SISTEMA AO VIVO** |
| — | **Demo** | 5–6 min | Provar o valor com o fluxo principal | Ver "Roteiro da demonstração" abaixo. | Voltar ao slide 8 |
| 8 | Fechamento | 0:45 | Retomar valor e próximos passos | Valor por stakeholder, próximos passos realistas, frase final: "Nenhum evento do CIn deveria passar batido." | Abrir para perguntas |

## Roteiro da demonstração (5–6 min)

Preparação (antes de entrar na sala): banco com seed, back-end em `:8000`, front em `:5173`, usuário admin criado, aba do navegador já aberta na Home. Teste tudo no mesmo computador que vai apresentar.

1. **Home (1 min).** Mostrar "Esta semana", a ordem cronológica, o contador de eventos.
2. **Buscar e filtrar (1 min).** Digitar um termo (ex.: "git") e clicar em um tipo (ex.: Workshop).
3. **Detalhes e agenda (1 min).** Abrir um evento e baixar o `.ics`.
4. **Curador (2 min).** Login pela "Área do curador", abrir a listagem administrativa, criar um evento novo, voltar à Home e mostrar que ele aparece.
5. **Extração (opcional, só se testado antes com credenciais reais).** Mostrar o resultado de um ciclo ou os registros. Se não houver credenciais, **não simule ao vivo**: mostre o código do fluxo e os testes, e diga que a extração foi validada com Gmail e Gemini simulados.

### O que não demonstrar
- A estrela de favoritos (não aparece na tela) e a página "Meus Favoritos" (placeholder).
- A tela "Status de Extração" (placeholder).
- Docker (PR ainda em revisão) e banco na nuvem.
- Eventos além do 100º na Home (limitação conhecida).

### Se algo der errado
- Back-end fora do ar: a Home mostra a mensagem "Não foi possível carregar os eventos" com botão "Tentar novamente". Suba a API e clique; não precisa reiniciar o front.
- Sem internet: tudo roda local; só a extração real depende de rede.
