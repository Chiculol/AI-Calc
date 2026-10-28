"""Testes da Etapa 4A na janela: círculo interativo, painel de informações e campos."""

import math

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtWidgets import QWidget

from ai_calc.core.preferences import Preferences
from ai_calc.ui.app import PREFERENCES_FILE, build_window, create_app
from ai_calc.ui.main_window import MIN_HEIGHT, MIN_WIDTH, TRIG_TAB
from ai_calc.ui.theme import (
    DARK,
    DISPLAY_ALPHA,
    LIGHT,
    PALETTES,
    min_contrast,
    surface_colors,
)


def _janela(qtbot, pasta, largura=700, altura=640):
    create_app()
    window = build_window(pasta, reduce_motion=lambda: True)
    qtbot.addWidget(window)
    window.resize(largura, altura)
    window.show()
    qtbot.waitExposed(window)
    window.tabs.setCurrentIndex(TRIG_TAB)
    return window


@pytest.fixture
def janela(qtbot, tmp_path):
    return _janela(qtbot, tmp_path)


@pytest.fixture
def pagina(janela):
    return janela.trig_page


def digitar_no_campo(qtbot, campo, texto):
    campo.edit.setFocus()
    campo.edit.selectAll()
    qtbot.keyClicks(campo.edit, texto)
    qtbot.keyClick(campo.edit, Qt.Key.Key_Return)


def ponto_do_angulo(circulo, graus, fracao=1.0):
    centro, raio = circulo._geometry()
    t = math.radians(graus)
    return QPoint(round(centro.x() + raio * fracao * math.cos(t)), round(centro.y() - raio * fracao * math.sin(t)))


# --- abertura --------------------------------------------------------------------
def test_abre_em_30_graus(pagina):
    assert pagina.state.angle == 30
    assert pagina.info.angle_label.text() == "30° = π/6 rad"
    assert pagina.info.quadrant_label.text() == "1º quadrante"
    assert pagina.info.value_labels["sin"].text() == "0,5"
    assert pagina.info.period_label.text() == "Também vale: 30° + 360° × k"
    assert pagina.angle_field.edit.text() == "30"
    assert pagina.sine_field.edit.text() == "0,5"


def test_aba_esconde_visor_e_painel_fixo(qtbot, janela):
    assert not janela.display.isVisible()
    assert not janela.history_docked
    assert janela.history_button.isVisible()        # o histórico continua na gaveta
    janela.tabs.setCurrentIndex(0)
    qtbot.wait(10)
    assert janela.display.isVisible()
    assert janela.history_docked


# --- campos -------------------------------------------------------------------------
def test_seno_meio_e_outra_solucao(qtbot, pagina):
    digitar_no_campo(qtbot, pagina.sine_field, "0,5")
    assert pagina.state.angle == pytest.approx(30)
    assert pagina.toggle_button.isEnabled()
    assert pagina.toggle_button.text() == "Outra: 150°"
    qtbot.mouseClick(pagina.toggle_button, Qt.MouseButton.LeftButton)
    assert pagina.state.angle == pytest.approx(150)
    assert pagina.info.quadrant_label.text() == "2º quadrante"
    assert pagina.angle_field.edit.text() == "150"


def test_seno_um_tem_solucao_unica(qtbot, pagina):
    digitar_no_campo(qtbot, pagina.sine_field, "1")
    assert pagina.state.angle == 90
    assert not pagina.toggle_button.isEnabled()
    assert pagina.toggle_button.text() == "Solução única"
    assert pagina.info.value_labels["tan"].text() == "indefinida"


@pytest.mark.parametrize("texto, esperado", [("450", 90), ("-30", 330), ("45+45", 90), ("22,5", 22.5)])
def test_campo_angulo(qtbot, pagina, texto, esperado):
    digitar_no_campo(qtbot, pagina.angle_field, texto)
    assert pagina.state.angle == pytest.approx(esperado)
    assert not pagina.error_label.isVisible()


def test_campo_invalido_mostra_aviso_e_nao_muda(qtbot, pagina):
    digitar_no_campo(qtbot, pagina.sine_field, "2")
    assert pagina.error_label.isVisible()
    assert pagina.error_label.text() == "Seno: Valor fora do domínio"
    assert pagina.state.angle == 30
    digitar_no_campo(qtbot, pagina.angle_field, "30+")
    assert pagina.error_label.text() == "Ângulo: Expressão incompleta"
    digitar_no_campo(qtbot, pagina.angle_field, "60")
    assert not pagina.error_label.isVisible()


def test_modo_radianos(qtbot, janela, pagina):
    qtbot.mouseClick(pagina.mode_button, Qt.MouseButton.LeftButton)
    assert janela.angle_mode == "RAD"
    assert pagina.mode_button.text() == "RAD"
    assert pagina.angle_field.edit.text() == "π/6"
    assert pagina.info.angle_label.text() == "π/6 rad = 30°"
    assert pagina.info.period_label.text() == "Também vale: π/6 + 2π × k"
    # "pi" em vez de "π": o QTest do Qt fecha o processo ao "digitar" π no Windows.
    digitar_no_campo(qtbot, pagina.angle_field, "3pi/4")
    assert pagina.state.angle == pytest.approx(135)
    assert janela.scientific_keypad.button("angle_mode").text() == "RAD"   # sincronizado


# --- círculo: mouse ------------------------------------------------------------
def test_clicar_no_circulo_muda_o_angulo(qtbot, pagina):
    circulo = pagina.circle
    qtbot.mouseClick(circulo, Qt.MouseButton.LeftButton, pos=ponto_do_angulo(circulo, 200))
    assert pagina.state.angle == 200                # graus inteiros com o mouse
    assert pagina.info.quadrant_label.text() == "3º quadrante"
    assert pagina.angle_field.edit.text() == "200"


def test_arrastar_encaixa_nos_notaveis(qtbot, pagina):
    circulo = pagina.circle
    qtbot.mousePress(circulo, Qt.MouseButton.LeftButton, pos=ponto_do_angulo(circulo, 100))
    qtbot.mouseMove(circulo, ponto_do_angulo(circulo, 118.8))
    assert pagina.state.angle == 120              # 118,8° encaixa em 120°
    qtbot.mouseMove(circulo, ponto_do_angulo(circulo, 100))
    assert pagina.state.angle == 100
    qtbot.mouseRelease(circulo, Qt.MouseButton.LeftButton, pos=ponto_do_angulo(circulo, 100))


# --- círculo: teclado e acessibilidade -----------------------------------------------
def test_setas_mudam_o_angulo(qtbot, pagina):
    circulo = pagina.circle
    circulo.setFocus()
    qtbot.keyClick(circulo, Qt.Key.Key_Right)
    assert pagina.state.angle == 31
    qtbot.keyClick(circulo, Qt.Key.Key_Left, Qt.KeyboardModifier.ShiftModifier)
    assert pagina.state.angle == 16
    qtbot.keyClick(circulo, Qt.Key.Key_Down, Qt.KeyboardModifier.ShiftModifier)
    qtbot.keyClick(circulo, Qt.Key.Key_Down, Qt.KeyboardModifier.ShiftModifier)
    assert pagina.state.angle == 346              # passa por 0° e volta para 360°
    qtbot.keyClick(circulo, Qt.Key.Key_Home)
    assert pagina.state.angle == 0


def test_resumo_para_leitor_de_tela(qtbot, pagina):
    circulo = pagina.circle
    assert circulo.accessibleName() == "Círculo trigonométrico"
    assert circulo.accessibleDescription().startswith("Ângulo 30 graus, 1º quadrante, seno 0,5")
    assert pagina.toggle_button.accessibleName() == "Outra solução do seno: 150 graus"
    circulo.setFocus()
    qtbot.keyClick(circulo, Qt.Key.Key_Right)
    assert circulo.accessibleDescription().startswith("Ângulo 31 graus")
    assert pagina.angle_field.edit.accessibleName() == "Ângulo"
    assert pagina.sine_field.edit.accessibleName() == "Seno"
    assert pagina.mode_button.accessibleName() == "Modo de ângulo: graus"


def test_tab_percorre_a_aba(qtbot, janela, pagina):
    pagina.circle.setFocus()
    ordem = []
    atual = pagina.circle
    for _ in range(4):
        qtbot.keyClick(atual, Qt.Key.Key_Tab)
        atual = janela.focusWidget()
        ordem.append(atual)
    assert ordem == [pagina.angle_field.edit, pagina.mode_button, pagina.sine_field.edit, pagina.toggle_button]


def test_teclas_da_calculadora_nao_vao_para_a_conta(qtbot, janela, pagina):
    pagina.circle.setFocus()
    qtbot.keyClicks(pagina.circle, "123+")
    qtbot.keyClick(pagina.circle, Qt.Key.Key_Return)
    assert janela.editor.expression == ""


def test_campo_nao_e_sobrescrito_enquanto_se_digita(qtbot, pagina):
    campo = pagina.angle_field
    campo.edit.setFocus()
    campo.edit.setText("12")
    pagina.circle._set_angle(200)                 # o círculo muda, mas o campo em foco não
    assert campo.edit.text() == "12"


# --- preferências e tamanho ---------------------------------------------------------
def test_ultima_aba_trigonometria_e_lembrada(qtbot, tmp_path):
    _janela(qtbot, tmp_path)
    assert Preferences(tmp_path / PREFERENCES_FILE).last_tab == "trigonometria"
    de_novo = build_window(tmp_path, reduce_motion=lambda: True)
    qtbot.addWidget(de_novo)
    assert de_novo.tabs.currentIndex() == TRIG_TAB
    assert de_novo.trig_page.state.angle == 30    # o ângulo não é guardado


def test_cabe_na_janela_minima(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, MIN_WIDTH, MIN_HEIGHT)
    window.resize(MIN_WIDTH, MIN_HEIGHT)
    qtbot.wait(20)
    pagina = window.trig_page
    for widget in (pagina.circle, pagina.info, pagina.angle_field, pagina.mode_button,
                   pagina.sine_field, pagina.toggle_button):
        geometria = widget.geometry()
        assert geometria.bottom() <= pagina.height(), type(widget).__name__
        assert geometria.right() <= pagina.width(), type(widget).__name__
    assert pagina.circle.height() >= 180


# --- cores e contraste --------------------------------------------------------------
@pytest.mark.parametrize("tema", [LIGHT, DARK])
def test_contraste_das_funcoes(tema):
    paleta = PALETTES[tema]
    painel = surface_colors(paleta, paleta["display_bg"], DISPLAY_ALPHA, False)
    for chave in ("trig_sin", "trig_cos", "trig_tan"):
        assert min_contrast(paleta, chave, painel) >= 4.5, chave     # rótulos coloridos
    assert min_contrast(paleta, "error", painel) >= 4.5      # aviso dos campos, dentro do painel


def _distancia(cor, hex_cor):
    alvo = int(hex_cor[1:3], 16), int(hex_cor[3:5], 16), int(hex_cor[5:7], 16)
    return sum(abs(a - b) for a, b in zip((cor.red(), cor.green(), cor.blue()), alvo))


@pytest.mark.parametrize("nome", [LIGHT, DARK])
def test_segmentos_com_as_cores_do_tema(qtbot, janela, pagina, nome):
    janela.theme.set_theme(nome)
    pagina.state.set_angle(45)
    pagina.refresh(True)
    qtbot.wait(20)
    circulo = pagina.circle
    imagem = circulo.grab().toImage()
    centro, raio = circulo._geometry()
    c = math.cos(math.radians(45))
    # Seno: meio do segmento vertical. Cosseno: um traço do segmento horizontal.
    seno = QPointF(centro.x() + raio * c, centro.y() - raio * c / 2).toPoint()
    outro = DARK if nome == LIGHT else LIGHT
    cor = imagem.pixelColor(seno)
    assert _distancia(cor, PALETTES[nome]["trig_sin"]) < _distancia(cor, PALETTES[outro]["trig_sin"])
    assert _distancia(cor, PALETTES[nome]["trig_sin"]) < 120
    tangente = QPointF(centro.x() + raio, centro.y() - raio * 0.5).toPoint()
    perto = [imagem.pixelColor(tangente + QPoint(dx, dy)) for dx in (-1, 0, 1) for dy in range(-4, 5)]
    assert min(_distancia(p, PALETTES[nome]["trig_tan"]) for p in perto) < 120


def test_botao_desativado_parece_desativado(qtbot, pagina):
    digitar_no_campo(qtbot, pagina.sine_field, "1")
    botao: QWidget = pagina.toggle_button
    assert not botao.isEnabled()
    imagem = botao.grab().toImage()
    cor = imagem.pixelColor(QPoint(8, botao.height() // 2))
    tema = pagina._theme.name
    assert _distancia(cor, PALETTES[tema]["tab_disabled_bg"]) < _distancia(cor, PALETTES[tema]["function_bg"])
