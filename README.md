# AI Calc

Calculadora desktop em Python e PySide6, toda em português do Brasil, com visual de
"vidro líquido", tema claro e escuro e histórico das contas. O motor de cálculo é próprio:
nada de `eval()`.

Projeto feito durante uma imersão da Alura em engenharia de software com IA, construído em
etapas pequenas, cada uma com testes automáticos.

<p align="center">
  <img src="docs/imagens/claro-cientifica.png" alt="AI Calc no tema claro, aba Científica, com o histórico ao lado" width="49%">
  <img src="docs/imagens/escuro-cientifica.png" alt="AI Calc no tema escuro, aba Científica, com o histórico ao lado" width="49%">
</p>

## O que ela faz

**Contas**
- Abas **Comum** e **Científica**: seno, cosseno, tangente e inversas, `ln`, `log`, `√`,
  raiz de índice n (`raiz(3; −8)` = −2), potência, fatorial, `π`, `e` e valor absoluto.
- Modo de ângulo **DEG/RAD**, com resultados exatos nos ângulos notáveis (`tan(45)` = 1,
  `tan(90)` é "Indefinida").
- Porcentagem como numa calculadora de mesa: `200 + 10%` = 220.
- Multiplicação implícita com aviso: `2(3+4)` mostra "Interpretado como: 2 × (3 + 4)".
- Números com vírgula decimal, até 12 dígitos significativos e notação científica (`1e+20`).
- Mensagens de erro em português ("Divisão por zero inválida", "Expressão incompleta"...).
  O app nunca fecha por causa de uma conta.
- Funciona pelo teclado físico: `12*3-6/2` e Enter.

**Visual**
- Teclas, visor, abas e painéis de vidro semitransparente com brilho e borda, sobre um fundo
  com manchas de cor.
- Tema claro (azul-gelo, lavanda e coral) e escuro (azul-marinho, roxo suave e turquesa), com
  transição de 450 ms. Um segundo clique no meio da transição a faz voltar do ponto em que
  estava.
- Abre seguindo o tema do Windows. Depois de escolhido no botão de lua/sol, vale o tema escolhido.
- Animações discretas de clique. Com "reduzir movimento" ligado no Windows, tudo fica instantâneo.

**Histórico e preferências**
- As 20 últimas contas, com a mais nova em cima e a etiqueta DEG/RAD nas contas com trigonometria.
- Clicar num item insere só o número na conta atual (um número negativo entra entre parênteses).
- Painel fixo ao lado em janelas largas e gaveta com botão em janelas estreitas (mínimo de 360 px).
- "Limpar" pede confirmação numa janela de vidro.
- Tema, DEG/RAD e última aba são lembrados. Os arquivos são gravados de forma segura, e um
  arquivo corrompido é renomeado e o app recomeça vazio.

**Acessibilidade**
- Todas as teclas e itens têm nome para leitor de tela (ex.: "Multiplicar", "sin(30) igual a
  0,5, graus").
- Navegação por Tab com contorno de foco visível.
- Contraste de 4,5:1 para texto e de 3:1 para foco e ícones, verificado por testes nos dois
  temas e levando em conta a transparência do vidro.

<p align="center">
  <img src="docs/imagens/claro-comum-estreita.png" alt="Aba Comum na largura mínima, tema claro" width="30%">
  &nbsp;
  <img src="docs/imagens/escuro-gaveta-historico.png" alt="Gaveta do histórico aberta na janela estreita, tema escuro" width="30%">
</p>

## Como rodar

Requisitos: Windows 10 ou 11 e Python 3.12 ou mais novo.

```bash
git clone https://github.com/Chiculol/AI-Calc.git
cd AI-Calc
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m ai_calc
```

> **Dica:** no Windows, o PySide6 não carrega se o caminho da pasta do ambiente virtual for
> muito longo. Se aparecer o erro `DLL load failed ... nome do arquivo ou a extensão é muito
> grande`, crie o ambiente num caminho curto (por exemplo, `C:\venvs\ai_calc`).

O histórico e as preferências ficam em `%APPDATA%\AI Calc`.

## Testes

```bash
pytest
```

São 448 testes. Eles cobrem o motor de cálculo, o círculo trigonométrico, o histórico e as
preferências, além da janela (com [pytest-qt](https://pytest-qt.readthedocs.io/), em modo
offscreen, sem abrir nada na tela). Os testes de janela clicam nas teclas, usam o teclado,
trocam o tema no meio da transição e conferem as cores de cada elemento.

Para conferir à mão, veja a [lista de conferência](docs/LISTA_DE_CONFERENCIA.md), que inclui
como simular um arquivo corrompido e o "reduzir movimento".

## Como o código está organizado

```
ai_calc/
├── core/          motor sem interface (testado sozinho)
│   ├── tokenizer.py, parser.py, evaluator.py   leitura e cálculo das contas
│   ├── calculator.py, formatting.py, errors.py resultado, formatação pt-BR e erros
│   ├── editor.py                                o que cada tecla faz
│   ├── trig.py                                  funções e círculo trigonométrico
│   └── history.py, preferences.py, storage.py   histórico, preferências e gravação segura
└── ui/            interface PySide6
    ├── main_window.py, app.py                   janela e inicialização
    ├── theme.py, system.py                      paletas, transição e "reduzir movimento"
    ├── glass.py, glass_button.py, tabs.py       desenho do vidro, teclas e abas
    └── display.py, keypad.py, history_panel.py, confirm_dialog.py
```

As decisões de comportamento (porcentagem, fatorial, erros, precedência...) estão em
[docs/ESPECIFICACAO.md](docs/ESPECIFICACAO.md).

## Andamento

| Etapa | Conteúdo | Status |
|---|---|---|
| 1 | Motor de cálculo e testes | ✅ |
| 2 | Lógica do círculo trigonométrico | ✅ |
| 3 | Interface Comum e Científica, tema claro/escuro, vidro, histórico e preferências | ✅ |
| 4 | Aba Trigonometria: círculo interativo e gráficos | próxima |
| 5 | Acabamento e animações | planejada |
