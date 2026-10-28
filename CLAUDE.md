# AI Calc: contexto do projeto

Calculadora desktop em Python (PySide6), em português do Brasil, com três modos:
Comum, Científica e Trigonometria (círculo trigonométrico interativo).
Leia também `docs/ESPECIFICACAO.md`: ela tem todas as decisões já aprovadas
(pontos 1 a 7) e deve ser seguida à risca.

## Sobre quem está pedindo

- Francisco, iniciante em programação, fazendo uma imersão da Alura em engenharia de software com IA.
- Fala português. Explique em linguagem simples, sem pressa de despejar código.
- Método combinado: **um passo de cada vez**. Apresente o que vai fazer, espere o "ok" e só então siga para a próxima etapa.
- Avise sempre que mudar algo que não foi aprovado e liste essas decisões ao final.

## Estado atual

| Etapa | Conteúdo | Status |
|---|---|---|
| 1 | Motor de cálculo e testes (`ai_calc/core`) | feita |
| 2 | Lógica da trigonometria (`core/trig.py`) | feita (271 testes passando no total) |
| 3A | Janela, visor e teclado Comum (com teclado físico), visual simples | feita |
| 3B | Teclado Científico, DEG/RAD e botão de tema (troca simples) | feita |
| 3C | Transição suave do tema e visual de vidro | feita |
| 3D | Histórico, preferências e lista de conferência final | feita (448 testes no total) |
| 4 | Aba Trigonometria (círculo e gráficos) | **próxima** |
| 5 | Acabamento, animações, README | pendente |

Comandos (da raiz do projeto): `pip install -r requirements.txt`, `pytest` e `python -m ai_calc` (abre o app).
Os testes de janela usam pytest-qt em modo offscreen (`tests/conftest.py`).
Atenção: o PySide6 não carrega se o caminho do ambiente virtual for longo demais
(limite do Windows); o ambiente atual fica em `C:/Users/fcoau/.venvs/ai_calc`.

## Regras de arquitetura

- `ai_calc/core` NÃO pode importar nada de interface. Toda lógica nova fica lá e é testada com pytest.
- Nunca usar `eval()` nem `exec()`. O cálculo passa pelo tokenizador, parser e avaliador próprios.
- Erros do usuário são `CalcError` (mensagens em português já definidas em `core/errors.py`). O app nunca pode fechar por causa de uma conta.
- Limites e tolerâncias ficam em `core/limits.py`.
- Números exibidos com vírgula decimal, 12 dígitos significativos, sem separador de milhar.

## Etapa 2 (feita): lógica do círculo em `core/trig.py`

- O círculo guarda o ângulo sempre em graus, em [0°, 360°) (360° vira 0°); radianos só na exibição.
- Funções: `normalize_degrees`, `quadrant`/`quadrant_label` ("1º quadrante"… ou "Sobre o eixo"),
  `circle_values` (tangente `None` quando indefinida), `signs` ("+", "-", "0" ou "indefinida"),
  `side_of`, `angles_from_sin` (devolve (direita, esquerda) ou uma solução só em ±1) e `periodicity_text`.
- Em RAD, `radians_text` escreve os notáveis como fração de π (`π/6`, `3π/4`) e os demais com 4 casas (`0,1745`).
- `TrigCircleState` é o que a interface da Etapa 4 vai usar: `set_angle`, `set_sin`, `toggle`,
  `can_toggle`, `side` (começa na direita; mantido em 90° e 270°).
- Seno fora de [−1, 1]: "Valor fora do domínio". Testes em `tests/test_trig_circle.py`.

## Etapa 3A (feita)

- `core/editor.py` (`ExpressionEditor`): o que cada tecla faz (inserir, apagar, limpar, calcular).
  Depois do "=", operador continua do resultado; número começa conta nova; "," no começo vira "0,".
- `ui/`: `app.py` (estilo Fusion, fonte Segoe UI Variable com reserva em Segoe UI),
  `main_window.py` (abas, teclado físico), `display.py` (visor), `keypad.py` (teclas a partir de listas).
- Toda tecla tem `accessibleName`, recebe foco com Tab e mostra contorno de foco visível.

## Etapa 3B (feita)

- Teclado Científico (`SCIENTIFIC_KEYS`, 5 colunas, teclas de 34 px de altura mínima) com tecla
  DEG/RAD; o modo também aparece no canto do visor e vale para as duas abas.
- Botão de tema no topo, ícone de lua/sol. Abre no tema do Windows
  (`styleHints().colorScheme()`); a escolha ainda não é salva (3D).

## Etapa 3C (feita)

- Sem folha de estilo (QSS): tudo é desenhado à mão como vidro (`ui/glass.py`: `paint_glass`,
  `Backdrop`; `ui/glass_button.py`: `GlassButton`, `ThemeToggleButton`; `ui/tabs.py`: `GlassTabBar`;
  visor em `ui/display.py`). Cada elemento pede a cor ao `ThemeManager` (`theme.hex/color`).
- `ui/theme.py`: `PALETTES` (mesmas chaves nos dois temas), `ROLE_COLORS` (cores de cada tipo de
  superfície), constantes do vidro (opacidades e brilhos) e `THEME_TRANSITION_MS = 450` (InOutCubic).
  O progresso vai de 0 (claro) a 1 (escuro); clicar de novo inverte a animação do ponto atual.
  O sinal `changed` faz a janela inteira se redesenhar a cada quadro.
- Contraste testado sobre o vidro (`surface_colors`/`backdrop_colors`): 4,5:1 texto, 3:1 foco e ícone.
  Ao criar um elemento novo, dê cor a ele pela paleta e acrescente-o aos testes de contraste.
- "Reduzir movimento" do Windows (`ui/system.py`) desliga a transição e as animações de clique.
- Aba Trigonometria: "Trig. · Em breve" (nome acessível completo) até a Etapa 4.

## Etapa 3D (feita)

- `core/storage.py`: `write_json_atomic` (temporário na mesma pasta + `os.replace`) e
  `load_or_quarantine` (arquivo estragado vira `<nome>.corrompido-AAAAMMDD-HHMMSS.json`).
- `core/history.py` (`History`, 20 itens, mais novo primeiro, `modo` só com trigonometria via
  `CalcResult.uses_trig`) e `core/preferences.py` (`Preferences`: tema, modo_angulo, ultima_aba).
  Sem caminho, os dois ficam só na memória (é o que os testes de janela usam).
- `ExpressionEditor.insert_value`: número do histórico; negativo entre parênteses; depois de
  número, `)`, constante, `!` ou `%` entra com "×".
- `ui/history_panel.py` (painel, itens, `GlassScrollBar`), `ui/confirm_dialog.py` (confirmação de
  vidro sobre a janela escurecida). Painel fixo a partir de 660 px; abaixo, gaveta com botão.
- `ui/app.py`: `build_window(pasta)` liga tudo; dados em `QStandardPaths.AppDataLocation`
  (`%APPDATA%/AI Calc`). O tema salvo pelo botão vale sobre o do Windows.
- Lista de conferência manual: `docs/LISTA_DE_CONFERENCIA.md`.

## Interface (Etapas 3 e 4)

- Aprovado: pytest-qt (offscreen); histórico em painel lateral recolhível; `preferencias.json`
  (tema, DEG/RAD, última aba) com gravação segura e tratamento de arquivo corrompido igual ao
  histórico; na primeira vez segue o tema do Windows; janela mínima 360 × 560; teclado
  Científico testado na largura mínima; contraste adequado nos dois temas.

- PySide6 com `QPainter` e `QPropertyAnimation`; janela redimensionável com tamanho mínimo.
- "Vidro líquido" simulado com translucidez, gradientes, bordas e brilho (blur real pesa e é instável).
- Tema claro (azul-gelo, lavanda, coral) e escuro (azul-marinho profundo, nunca preto puro; roxo suave; turquesa). A troca muda TODOS os elementos, com transição suave.
- Cores de seno, cosseno e tangente diferentes, mais rótulo escrito e estilo de linha (não depender só da cor).
- Respeitar a preferência de "reduzir movimento" do sistema.
- Histórico: 20 itens, JSON em pasta de configuração do sistema (usar `QStandardPaths`), etiqueta DEG/RAD nos itens com trigonometria, clique insere só o número do resultado.

## Confirmados pelo Francisco (decididos na Etapa 1)

1. Raiz de índice n: `raiz(n; x)`, com `;` separando os argumentos; radicando negativo só com índice inteiro ímpar.
2. A digitação aceita `.` e `,` como decimal.
3. Parênteses desligam a regra especial do `%`: `200 + (10%)` = 200,1.
4. `√` age sobre o próximo termo: `√4pi` = (√4) × π.
5. Expressões com mais de 500 caracteres: "Expressão longa demais".

## Ambiente

- Windows 11 (confirmado). Histórico e preferências em `%APPDATA%`, obtido via `QStandardPaths`.
