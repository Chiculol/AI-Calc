"""Testes da Etapa 3B: teclado Científico, DEG/RAD e botão de tema."""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QPushButton

from ai_calc.ui.app import create_app
from ai_calc.ui.keypad import ANGLE_MODE, EVALUATE, SCIENTIFIC_KEYS
from ai_calc.ui.main_window import MIN_HEIGHT, MIN_WIDTH, SCIENTIFIC_TAB, MainWindow
from ai_calc.ui.theme import DARK, LIGHT, PALETTES, ThemeManager


@pytest.fixture
def janela(qtbot):
    create_app()
    window = MainWindow(ThemeManager(LIGHT, reduce_motion=lambda: True))
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    window.tabs.setCurrentIndex(SCIENTIFIC_TAB)
    return window


def clicar(qtbot, janela, *teclas):
    for tecla in teclas:
        qtbot.mouseClick(janela.scientific_keypad.button(tecla), Qt.MouseButton.LeftButton)


def resultado(janela):
    return janela.display.result_label.text()


# --- teclado Científico ------------------------------------------------------
def test_aba_cientifica_mostra_o_teclado(janela):
    assert janela.current_keypad is janela.scientific_keypad


def test_seno_em_graus(qtbot, janela):
    clicar(qtbot, janela, "sin(", "3", "0", ")", EVALUATE)
    assert resultado(janela) == "0,5"


def test_alternar_para_radianos(qtbot, janela):
    clicar(qtbot, janela, ANGLE_MODE)
    assert janela.angle_mode == "RAD"
    botao = janela.scientific_keypad.button(ANGLE_MODE)
    assert botao.text() == "RAD"
    assert botao.accessibleName() == "Modo de ângulo: radianos"
    assert janela.display.angle_mode_label.text() == "RAD"
    clicar(qtbot, janela, "sin(", "π", "÷", "2", ")", EVALUATE)
    assert resultado(janela) == "1"
    clicar(qtbot, janela, ANGLE_MODE)
    assert janela.angle_mode == "DEG"
    assert botao.text() == "DEG"


def test_tangente_indefinida(qtbot, janela):
    clicar(qtbot, janela, "tan(", "9", "0", ")", EVALUATE)
    assert janela.display.message_label.text() == "Indefinida"


def test_raiz_quadrado_fatorial_e_constantes(qtbot, janela):
    clicar(qtbot, janela, "√", "9", "+", "3", "^2", "+", "4", "!", EVALUATE)
    assert resultado(janela) == "36"           # 3 + 9 + 24
    clicar(qtbot, janela, "raiz(", "3", ";", "−", "8", ")", EVALUATE)
    assert resultado(janela) == "-2"
    clicar(qtbot, janela, "ln(", "e", ")", "+", "log(", "1", "0", "0", ")", EVALUATE)
    assert resultado(janela) == "3"
    clicar(qtbot, janela, "abs(", "−", "5", ")", EVALUATE)
    assert resultado(janela) == "5"


def test_funcoes_inversas(qtbot, janela):
    clicar(qtbot, janela, "asin(", "1", ")", EVALUATE)
    assert resultado(janela) == "90"


def test_mesma_conta_nas_duas_abas(qtbot, janela):
    clicar(qtbot, janela, "2", "+")
    janela.tabs.setCurrentIndex(0)
    qtbot.mouseClick(janela.common_keypad.button("3"), Qt.MouseButton.LeftButton)
    assert janela.editor.expression == "2+3"


def test_toda_tecla_cientifica_tem_nome_acessivel(janela):
    botoes = janela.scientific_keypad.findChildren(QPushButton)
    assert len(botoes) == sum(len(linha) for linha in SCIENTIFIC_KEYS)
    for botao in botoes:
        assert botao.accessibleName(), botao.text()
        assert botao.focusPolicy() & Qt.FocusPolicy.TabFocus, botao.text()


def test_teclado_cientifico_cabe_na_largura_minima(qtbot, janela):
    janela.resize(MIN_WIDTH, MIN_HEIGHT)
    qtbot.wait(20)
    teclado = janela.scientific_keypad
    for botao in teclado.findChildren(QPushButton):
        geometria = botao.geometry()
        assert geometria.width() >= 48, botao.text()
        assert geometria.height() >= 34, botao.text()
        assert geometria.right() <= teclado.width(), botao.text()
        assert geometria.bottom() <= teclado.height(), botao.text()
    assert janela.tabs.sizeHint().width() <= janela.tabs.width()


# --- botão de tema -----------------------------------------------------------
def test_botao_de_tema_troca_tudo(qtbot, janela):
    app = QApplication.instance()
    assert janela.theme.name == LIGHT
    assert janela.theme_button.accessibleName() == "Mudar para o tema escuro"
    qtbot.mouseClick(janela.theme_button, Qt.MouseButton.LeftButton)
    assert janela.theme.name == DARK
    assert janela.theme_button.accessibleName() == "Mudar para o tema claro"
    assert app.palette().toolTipBase().color().name().upper() == PALETTES[DARK]["tooltip_bg"]
    qtbot.mouseClick(janela.theme_button, Qt.MouseButton.LeftButton)
    assert janela.theme.name == LIGHT


def test_botao_de_tema_com_teclado(qtbot, janela):
    janela.theme_button.setFocus()
    qtbot.keyClick(janela.theme_button, Qt.Key.Key_Space)
    assert janela.theme.name == DARK


def test_comeca_no_tema_do_sistema(qtbot):
    create_app()
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.theme.name in (LIGHT, DARK)


def test_tema_desconhecido():
    create_app()
    with pytest.raises(ValueError):
        ThemeManager(LIGHT).set_theme("roxo")
