# CIn Event Hub — Auditoria de Identidade Visual (US 7.1)

**Projeto:** CIn Event Hub — IESI 2026.2 / UFPE  
**Data da inspeção inicial:** 26/11/2026  
**Branch da correção:** `fix/us71-identidade-visual`  
**Fonte analisada:** versão final recebida em `cin-event-hub(2).zip`  
**Referência:** Backlog v4.0 (US 7.1), template de design system da equipe e `frontend/src/styles/global.css`  
**Método:** inspeção estática do ZIP e do patch, análise de duas capturas administrativas e validação local relatada pelo desenvolvedor, complementadas pelos resultados de lint, build e Git enviados na conversa. Não houve acesso independente ao navegador local nem auditoria automatizada completa de acessibilidade.

## 1. Objetivo e critérios de aceite

Confrontar as telas da SPA com os padrões de **paleta, tipografia, espaçamento, componentes e tema claro/escuro**. Registrar desvios e indicar correções. Os dois cenários do backlog exigem (a) auditoria de listagem, detalhes, painel administrativo e favoritos e (b) nenhum uso não justificado de cor, fonte ou componente fora do padrão.

**Fonte de verdade técnica:** `frontend/src/styles/global.css`, com tokens de fundo (`--page`, `--surface`), texto (`--ink`, `--muted`), destaques (`--red`, `--accent-text`), bordas (`--line`, `--border`), estados (`--success-*`, `--danger-*`), foco e tipos de eventos (`--t-*`). O tema escuro é controlado por `html[data-theme='dark']`.

## 2. Resultado por tela — inspeção e validação local

| Tela / elemento | Evidências no código | Resultado da inspeção | Validação no navegador |
|---|---|---|---|
| **Listagem/Home** | `home.css`, `Home.jsx`, `EventCard.jsx`, `SiteHeader.jsx` | Fundo, cartões, filtros e cabeçalho utilizam tokens; família monoespaçada declarada localmente | Conferência geral relatada; sem captura específica |
| **Detalhes** | `details.css`, `EventDetails.jsx` | Cores por tokens; fonte monoespaçada repetida em três regras | Conferência geral relatada; sem captura específica |
| **Favoritos** | `favorites.css`, `FavoritesPage.jsx` | Cores funcionais por tokens semânticos | Conferência geral relatada; sem captura específica |
| **Login** | `login.css`, `Login.jsx` | Campos, alertas e botão por tokens; sombra `rgba()` direta | Login realizado segundo o desenvolvedor; estados não documentados |
| **Admin / Eventos** | `admin.css`, `admin-layout.css`, `AdminEventsPage.jsx`, formulário e modal | Tabela, formulário, alertas e ações usam tokens | Captura em estado de erro no tema escuro; acesso autenticado relatado como normal |
| **Admin / Extração** | `extraction-status.css`, `ExtractionStatusPage.jsx` | **Divergência confirmada:** dez declarações de cores hexadecimais em CSS local; cabeçalho com hierarquia visual distinta | Captura em estado de erro no tema escuro; funcionamento após login relatado como normal |
| **Alternador de tema** | `ThemeToggle.jsx`, `ThemeProvider.jsx`, `global.css` | Controle e tokens presentes, com seletores para ambos os temas | Conferência geral relatada; persistência e foco sem evidência específica |

O relato geral do desenvolvedor (“tudo ok”) complementa a inspeção do código, mas não comprova individualmente todos os estados ou os dois temas de cada tela.

## 3. Divergências registradas

| ID | Severidade | Local | Evidência concreta / problema | Ação | Estado |
|---|---|---|---|---|---|
| **VIS-01** | Alta | `extraction-status.css`, linhas 15, 33–35, 115 | Cores de sucesso e erro fixas em vez de `--success-text`, `--danger-bg`, `--danger-text`, `--danger-border` | Substituir por tokens | **Correção aplicada localmente** |
| **VIS-02** | Alta | `extraction-status.css`, linhas 41, 47, 57, 88, 99 | Bordas, divisores e legendas com cores fixas | Substituir por `--ink`, `--line` e `--muted` | **Correção aplicada localmente** |
| **VIS-03** | Média | `home.css` e `details.css` | Família `ui-monospace, 'JetBrains Mono', monospace` repetida | Centralizar em `--font-mono` | **Correção aplicada localmente** |
| **VIS-04** | Baixa | `login.css`, `.login-card` | Sombra definida como `rgba(0,0,0,.25)` fora dos tokens | Centralizar sombra em token semântico, inclusive no tema escuro | **Correção aplicada localmente** |
| **VIS-05** | Média | `global.css` e vários estilos locais | A escala de espaçamento é descrita no template, mas não existia como conjunto de tokens globais | Declarar escala e adotar progressivamente nos componentes | **Correção inicial aplicada**; adoção completa pendente |
| **VIS-06** | Média — decisão visual | `extraction-status.css` vs `admin.css` | Título da extração usa `3rem`, enquanto o título administrativo comum usa `2rem`; aparência editorial pode ser intencional | Comparar telas lado a lado; decidir se alinhar tipografia/cor ou documentar exceção | **Aberta:** diferença visível nas capturas; padronizar ou justificar |
| **VIS-07** | Baixa — decisão visual | `Dashboard.jsx` | Layout por `style={{...}}`, embora a cor do título use `var(--accent-text)` | Se a tela for mantida, converter apresentação para classes CSS | **Fora das rotas ativas** (confirmado em `App.jsx` do ZIP); revisão futura se reativado |
| **VIS-08** | Validação | Todas as telas | Estados hover/foco/desabilitado, modais, contraste e composição final não podem ser atestados apenas pelo CSS | Percorrer SPA nos dois temas; coletar capturas e, quando aplicável, medir contraste | **Validação geral relatada**; evidência detalhada pendente |

## 4. Correção técnica proposta

O patch **`US71_correcao_identidade_visual_final.patch`** foi gerado especificamente para a versão do ZIP auditado. Ele modifica apenas:

- `frontend/src/styles/global.css`: adiciona tokens de fonte, escala de espaçamento e sombra; usa token no `body`.
- `frontend/src/styles/home.css` e `details.css`: referenciam a mesma fonte técnica.
- `frontend/src/styles/login.css`: substitui a sombra fixa por token.
- `frontend/src/styles/extraction-status.css`: substitui as dez cores fixas e adota parte dos tokens de espaçamento.

**Verificação técnica realizada:** o patch passou em `git apply --check` e `git apply` contra uma cópia dos arquivos do ZIP. Uma busca estática após a correção não encontrou `#hex`, `rgb()`, `rgba()`, `hsl()` ou `hsla()` nas folhas CSS específicas; os valores de cor ficam em `global.css`. O desenvolvedor posteriormente confirmou a aplicação local, e os comandos de lint e build foram concluídos com sucesso (seção 6).

### Escopo da alteração preparada para commit

O resultado de `git diff --cached --stat` confirma cinco arquivos CSS no stage, com 36 inserções e 23 exclusões. O arquivo `backend/.env.example` e a pasta `.vscode/` permanecem fora do stage; não integram esta entrega. Não foram realizadas alterações de lógica no Back-end pelo patch.

## 5. Contraste — amostra de pares de tokens

Razões calculadas pelo método de luminância relativa da WCAG a partir dos valores no `global.css`. São exemplos isolados, **não auditoria completa**:

| Par de cores | Claro | Escuro | Leitura |
|---|---:|---:|---|
| `--ink` sobre `--page` | 15,92:1 | 15,96:1 | Acima de 4,5:1 |
| `--muted` sobre `--page` | 6,73:1 | 9,35:1 | Acima de 4,5:1 |
| `--on-color` sobre `--red` | 7,01:1 | 7,24:1 | Acima de 4,5:1 |
| `--danger-text` sobre `--danger-bg` | 8,31:1 | 10,86:1 | Acima de 4,5:1 |

Outras composições (cores com transparência, controles desabilitados, chips selecionados, imagens e bordas) precisam ser verificadas na página renderizada. Referências: WCAG AA — **4,5:1** para texto normal, **3:1** para texto grande e informação visual não textual essencial, quando aplicável.

## 6. Evidências da validação local

| Verificação | Resultado | Evidência |
|---|---|---|
| Back-end e Front-end | Funcionamento relatado | Desenvolvedor confirmou inicialização e exibição dos eventos. |
| Autenticação administrativa | Funcionamento relatado | Após identificar que não havia feito login, desenvolvedor informou que estava tudo OK. |
| `npm run lint` | Aprovado | Saída `eslint .`, sem erros ou avisos exibidos. |
| `npm run build` | Aprovado | Vite v8.3.8; 66 módulos transformados; build concluído em 133 ms. |
| Branch | Confirmada | `fix/us71-identidade-visual`. |
| Escopo do stage | Confirmado | 5 arquivos CSS, 36 inserções, 23 exclusões, antes da inclusão deste relatório. |
| Auditoria visual | Conferência geral relatada | Desenvolvedor informou “tudo ok”; não há capturas de todas as telas e estados. |
| Revisão cruzada e merge | Pendentes | Aguardar Pull Request e dupla espelho. |

### Evidência de terminal

```text
> frontend@0.0.0 lint
> eslint .

> frontend@0.0.0 build
> vite build
vite v8.3.8 building client environment for production...
✓ 66 modules transformed.
✓ built in 133ms
```

```text
frontend/src/styles/details.css           |  6 +++---
frontend/src/styles/extraction-status.css | 34 +++++++++++++++----------------
frontend/src/styles/global.css            | 15 +++++++++++++-
frontend/src/styles/home.css              |  2 +-
frontend/src/styles/login.css             |  2 +-
5 files changed, 36 insertions(+), 23 deletions(-)
```

### Observações das capturas administrativas

As duas capturas compartilhadas durante a auditoria mostram o tema escuro, menu lateral consistente, destaque vermelho da seção ativa e alertas de erro com fundo e borda semânticos. Mostram também diferença no título: “Eventos” aparece em cor de destaque, enquanto “Status de Extração” aparece maior e na cor de texto principal. A diferença corresponde às regras de `admin.css` e `extraction-status.css` (VIS-06). Recomenda-se alinhar a hierarquia dos títulos e o espaçamento externo ou aprovar formalmente a exceção. Os alertas de carregamento estavam associados ao acesso sem login, segundo o desenvolvedor; não são evidência de falha na extração autenticada. Não foram fornecidas novas capturas após o login.

### Checklist complementar para revisão cruzada

- [ ] Conferir individualmente Home, detalhes, favoritos, login, gestão de eventos, formulários, modais e extração nos dois temas.
- [ ] Conferir foco de teclado, contraste, estados vazios, de erro e desabilitados.
- [ ] Conferir responsividade em desktop e dispositivos móveis.
- [ ] Resolver ou justificar VIS-06 e avaliar adoção restante da escala de espaçamentos (VIS-05).
- [ ] Anexar capturas ou registrar evidências por tela no PR, se disponíveis.

## 7. Decisão de aceite

| Cenário Gherkin | Situação |
|---|---|
| Auditoria de identidade visual | Relatório produzido, com comparação por tela e divergências registradas. |
| Critérios de consistência | Correções de cores, fontes e sombra aplicadas; lint e build aprovados. Aceite integral depende da resolução ou justificativa da hierarquia administrativa e da verificação complementar. |

**Conclusão:** a revisão técnica e a primeira rodada de correções estão prontas para revisão cruzada. A auditoria identifica o que foi corrigido, o que foi confirmado localmente e o que ainda necessita de evidência. Não se declara conformidade integral da SPA nem certificação de acessibilidade. O status “Concluído” no Jira não substitui a validação dos critérios de aceite e a revisão pela dupla espelho.
