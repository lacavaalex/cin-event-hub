# CIn Event Hub — Template de Padronização de Design e Identidade Visual

**História:** US 7.1 — Identidade visual coerente  
**Épico:** E7 — Revisão de Identidade Visual  
**Versão do documento:** 0.1 — proposta para revisão da equipe  
**Responsável:** a definir  
**Data da revisão:** a preencher  
**Status:** Em revisão; não constitui auditoria WCAG concluída

## 1. Objetivo e escopo

Definir uma referência comum para cores, tipografia, espaçamentos, componentes, estados e temas das telas públicas e administrativas do **CIn Event Hub**. O propósito é reduzir divergências e orientar novas implementações.

**Telas incluídas:** listagem/Home, detalhes de evento, login, favoritos, formulários de criação/edição, administração de eventos, painel de extração, mensagens de erro e modais.

**Regra de prioridade:** os tokens e as decisões documentados neste design system são a fonte de verdade. O protótipo do Lovable é **referência visual**, não substitui decisões documentadas nem autoriza incorporar botões e credenciais de demonstração.

## 2. Fonte técnica da verdade

- **Tokens e estilos globais:** `frontend/src/styles/global.css`.
- **Tema claro/escuro:** `frontend/src/contexts/ThemeProvider.jsx`, `frontend/src/components/ThemeToggle.jsx` e atributo `data-theme` no elemento `html`.
- **Estilos específicos:** `frontend/src/styles/home.css`, `details.css`, `favorites.css`, `login.css`, `admin.css`, `admin-layout.css`, `extraction-status.css` e `site-header.css`.
- **Revisão de interface:** registrar divergências neste documento e abrir correções conforme prioridade acordada pela equipe.

Os valores abaixo foram identificados na versão do projeto fornecida para análise. **Validar contra o `global.css` da branch de trabalho antes de aprovar este documento.**

## 3. Paleta e design tokens

### 3.1 Tokens semânticos essenciais

| Token CSS | Tema claro | Tema escuro | Uso esperado |
|---|---|---|---|
| `--page` | `#f4f0e8` | `#17191f` | Fundo principal da aplicação |
| `--surface` | `#ffffff` | `#252931` | Superfícies de cards, formulários e painéis |
| `--surface-soft` | `#f5f5f5` | `#30353f` | Hover, superfícies secundárias |
| `--ink` | `#161616` | `#f2f4f8` | Texto principal |
| `--muted` | `#57534b` | `#b9bdc8` | Texto secundário, legendas |
| `--border` | `#c5c5cc` | `#646873` | Bordas de controles |
| `--input-bg` | `#ffffff` | `#20242b` | Fundo de campos |
| `--accent-text` | `#a40828` | `#ff9ab0` | Títulos e destaques textuais |
| `--focus-ring` | `#a40828` | `#ffb8c7` | Indicador visual de foco |
| `--nav-bg` | `#ffffff` | `#21252d` | Navegação principal |
| `--red` | `#b20e2e` | `#ae0e2e` | Cor institucional de ações/destaques |
| `--red-dark` | `#8c0a22` | `#8f0a24` | Variante de interação |
| `--on-color` | `#ffffff` | `#ffffff` | Texto sobre superfícies coloridas, **após validar contraste** |

**Tokens complementares já disponíveis:** `--line`, `--shadow-color`, `--nav-hover`, `--sidebar-bg`, `--sidebar-heading`, `--sidebar-text`, `--sidebar-muted`, `--sidebar-hover`, `--success-bg`, `--success-border`, `--success-text`, `--danger-bg`, `--danger-border`, `--danger-text`, `--inactive-bg`, `--favorite-color` e `--modal-backdrop`.

### 3.2 Tipos de evento

Usar sempre os tokens `--t-palestra`, `--t-workshop`, `--t-hackathon`, `--t-minicurso`, `--t-outros` para superfícies indicativas; para texto, usar as variantes `--t-*-text` previstas no `global.css`.

A categoria deve ser identificada **também por texto**, não apenas pela cor. Não reutilizar uma cor de categoria para comunicar falha ou sucesso.

### 3.3 Mensagens de estado

| Situação | Tokens | Orientação |
|---|---|---|
| Sucesso | `--success-bg`, `--success-border`, `--success-text` | Mensagem legível, com texto explícito |
| Erro/falha | `--danger-bg`, `--danger-border`, `--danger-text` | Usar `role="alert"` quando pertinente |
| Neutro/inativo | `--surface-soft`, `--muted`, `--inactive-bg` | Não depender apenas de opacidade |

**Regra:** estilos de componentes não devem declarar novos valores `#hex`, `rgb()` ou `hsl()` para cores funcionais. Quando uma nova cor for necessária, primeiro acrescentá-la ao conjunto de tokens semânticos, documentar uso e validar ambos os temas. Sombras e transparências decorativas podem requerer exceções justificadas.

## 4. Tipografia

- **Fonte principal existente:** `system-ui, sans-serif` (definida no `body` em `global.css`).
- **Fonte técnica/metadados:** família monoespaçada quando fizer parte do componente; na Home aparece `ui-monospace, 'JetBrains Mono', monospace`.
- **Hierarquia:** apenas um `h1` por página; `h2` para seções; `h3` para subdivisões ou títulos de cards quando semanticamente apropriado.
- **Peso:** corpo 400; rótulos 600; botões e destaques 700; títulos principais conforme hierarquia, evitando variações arbitrárias.
- **Referência de escala (proposta a homologar):** corpo 16 px; legenda 12–14 px; rótulo 14–16 px; títulos de seção 20–24 px; título de página 32 px, com `clamp()` quando necessário.
- **Legibilidade:** evitar corpo muito pequeno, caixa alta em textos longos e espaçamento excessivo entre letras em parágrafos.

> A escala acima é uma **diretriz proposta**, não uma afirmação de que todas as telas já a seguem. Padronizá-la exige auditoria dos arquivos de estilo.

## 5. Espaçamento, bordas e responsividade

**Escala sugerida:** `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 px`. Preferir esses incrementos a valores isolados. O repositório ainda usa medidas locais; a equipe deve aprovar a escala antes de exigir conformidade total.

| Elemento | Referência de uso |
|---|---|
| Intervalo entre itens relacionados | 8–12 px |
| Preenchimento de campos e botões | 8–16 px |
| Preenchimento de cards | 16–32 px |
| Intervalo entre seções | 24–32 px |
| Foco de teclado | Contorno visível; implementação global usa 3 px |
| Bordas arredondadas | 4–8 px em controles/cards; 999 px para chips/pílulas; exceções documentadas |

**Larguras para verificação manual:** 360 px, 390 px, 768 px, 1280 px e 1920 px. Os estilos atuais possuem pontos de quebra conforme o componente (por exemplo, 640 px, 900 px e 1024 px), portanto **não presumir um único breakpoint global**.

Regras gerais: não cortar textos; permitir quebra de chips; evitar rolagem horizontal da página; usar rolagem dentro de tabelas largas quando necessário; respeitar `prefers-reduced-motion` em animações.

## 6. Componentes e estados obrigatórios

| Componente | Padrão a conferir | Estados a conferir |
|---|---|---|
| Cabeçalho e navegação | Tokens `--nav-*`, texto legível, indicação da rota ativa | normal, hover, foco, ativo |
| Botão principal | Fundo de ação, texto de contraste adequado, área clicável confortável | normal, hover, foco, desabilitado, carregando |
| Botão secundário | Superfície e borda por tokens | normal, hover, foco, desabilitado |
| Cards de eventos | Estrutura consistente, título e data legíveis, categoria com texto | normal, hover, foco do link |
| Filtros/chips | Seleção indicada por mais de cor; token de fundo e texto | selecionado, não selecionado, hover, foco |
| Formulários | `label` associado; mensagens próximas ao campo; foco visível | vazio, válido, inválido, desabilitado |
| Tabelas admin | Cabeçalhos distinguíveis, bordas e fundo por token | normal, hover, ações por teclado |
| Modais | Fundo, texto, borda e sobreposição consistentes | aberto, fechado, foco e confirmação |
| Alertas | Tokens semânticos e texto explícito | sucesso, erro, aviso, vazio |
| Favoritos | Estado marcado acessível por texto/nome acessível | marcado, desmarcado, desabilitado |
| Alternador de tema | Rótulo informa a ação (`Ativar tema claro/escuro`) | foco, claro, escuro |

## 7. Temas claro e escuro

1. **Primeiro acesso:** sem preferência gravada, seguir `prefers-color-scheme` do sistema operacional.
2. **Escolha manual:** alternar imediatamente; persistir a preferência no navegador usando a chave existente `cin-event-hub-theme`.
3. **Antes da renderização:** aplicar `data-theme` no `html` sem piscar no tema incorreto.
4. **Consistência:** manter a preferência ao navegar entre telas públicas e administrativas.
5. **Componentes:** consumir tokens semânticos; nunca corrigir o modo escuro apenas com texto branco sobre fundo desconhecido.
6. **Teste:** conferir estados normal, foco, hover, selecionado, erro e desabilitado em ambos os temas.

Exemplo de CSS **adequado**:

```css
.event-panel {
  background: var(--surface);
  color: var(--ink);
  border: 1px solid var(--border);
}
.event-panel__description {
  color: var(--muted);
}
```

Evitar CSS funcional com valores fixos:

```css
/* Evitar: não acompanha automaticamente o tema */
.event-panel { background: #ffffff; color: #161616; }
```

## 8. Critérios de acessibilidade

- **WCAG AA — texto comum:** contraste de pelo menos **4,5:1**.
- **WCAG AA — texto grande:** pelo menos **3:1** (24 px ou 18,67 px em negrito, aproximadamente).
- **Contornos de controles e informações gráficas essenciais:** contraste de pelo menos **3:1** quando aplicável.
- **Foco:** sempre visível para teclado; nenhum controle essencial deve depender exclusivamente do mouse.
- **Formulários:** rótulos claros, erros descritivos e navegação por teclado.
- **Semântica:** títulos em ordem lógica, controles com nomes acessíveis, alertas anunciáveis quando necessários.
- **Verificação:** medir contraste nos estados reais e em ambos os temas. A aprovação geral de WCAG **não pode ser presumida** apenas com base na existência de tokens ou no sucesso do build.

## 9. Template de auditoria por tela — preencher na revisão

**Tela/rota:** ______________________________  
**Tema:** claro / escuro  
**Resolução:** ______________________________  
**Revisor:** ______________________________  
**Data:** ______________________________

| Item verificado | Resultado (OK / Falha / N/A) | Evidência / observação |
|---|---|---|
| Fundo, superfícies e texto usam tokens | | |
| Cor da marca e categorias consistentes | | |
| Hierarquia tipográfica e espaçamentos | | |
| Botões, inputs, chips, cards e tabelas | | |
| Hover, foco, seleção, erro e desabilitado | | |
| Tema permanece ao navegar/recarregar | | |
| Contraste AA medido | | |
| Layout responsivo sem sobreposição | | |
| Acessibilidade por teclado | | |
| Alinhamento com protótipo (quando relevante) | | |

### Registro consolidado de divergências

| ID | Tela/arquivo | Divergência | Impacto | Decisão: corrigir tela / revisar padrão | Responsável | Status |
|---|---|---|---|---|---|---|
| VIS-001 | `frontend/src/styles/extraction-status.css` | Cores funcionais em `#hex` no próprio componente, contrariando a diretriz de tokens | Inconsistência potencial entre temas | Substituir por tokens semânticos, após revisão visual | A definir | Aberto |
| VIS-002 | A preencher | A preencher | A preencher | A definir | A definir | Pendente |

**Evidência de VIS-001:** na versão inspecionada, `extraction-status.css` contém cores fixas para texto de status, banner de erro, bordas e rótulos; o `global.css` possui regras de compensação para parte desses elementos no tema escuro. Isso sugere centralizar essas cores nos tokens em uma correção posterior. Esta é uma constatação de código, **não um teste de contraste concluído**.

### Decisão em caso de divergência do Lovable

- **Referência visual do protótipo:** ______________________
- **Regra do design system afetada:** ______________________
- **Diferença observada:** ______________________
- **Decisão da equipe:** ajustar implementação / atualizar design system
- **Justificativa e aprovação:** ______________________

## 10. Checklist de aprovação da US 7.1

- [ ] Tokens, paleta, fontes, espaçamentos e componentes revisados e aprovados pela equipe.
- [ ] Tela inicial/listagem auditada em ambos os temas.
- [ ] Detalhes e favoritos auditados em ambos os temas.
- [ ] Login e formulários auditados em ambos os temas.
- [ ] Administração, tabelas, modais e painel de extração auditados em ambos os temas.
- [ ] Todas as divergências registradas com responsável e decisão.
- [ ] Cores funcionais fora dos tokens corrigidas ou justificadas formalmente.
- [ ] Contraste WCAG AA verificado e evidenciado nos elementos relevantes.
- [ ] Nenhum recurso de demonstração incorporado por influência do protótipo.
- [ ] Documentação aprovada e versionada com as mudanças pertinentes.

## 11. Manutenção do documento

Ao criar um componente ou ajustar uma cor, tipografia ou espaçamento, o autor deve:

1. Consultar os tokens e padrões existentes.
2. Preferir reutilização a criar uma variante pontual.
3. Validar a mudança em ambos os temas, em teclado e tela pequena.
4. Atualizar a documentação se surgir uma decisão nova.
5. Registrar em PR as divergências intencionais e o motivo.

**Critério de encerramento:** o template estar disponível não significa, sozinho, que a US 7.1 está pronta. O aceite exige auditoria das telas e tratamento documentado das divergências.
