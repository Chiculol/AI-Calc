"""Testes da Etapa 5A: liga/desliga das funções, ajustes visuais, transições e ícone."""

import math

import pytest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import QApplication

from ai_calc.core.preferences import Preferences
from ai_calc.core.trig import TRIG_FUNCTIONS, toggle_visible
from ai_calc.ui.app import PREFERENCES_FILE, build_window, create_app
from ai_calc.ui.icons import ICON_SIZES, app_icon
from ai_calc.ui.main_window import MIN_HEIGHT, MIN_WIDTH, SCIENTIFIC_TAB, TRIG_TAB
from ai_calc.ui.motion import FADE_MS
from ai_calc.ui.theme import (
    DARK,
    KEY_ALPHA,
    LIGHT,
    PALETTES,
    min_contrast,
    surface_colors,
)
from ai_calc.ui.trig_circle import QUADRANT_LABEL_GAP
from tests.ajudantes import distancia

TODAS = frozenset(TRIG_FUNCTIONS)


# --- regra do liga/desliga (motor) ----------------------------------------------------
def test_desligar_e_ligar():
    sem_tan = toggle_visible(TODAS, "tan")
    assert sem_tan == {"sin", "cos"}
    assert toggle_visible(sem_tan, "tan") == TODAS


def test_ultima_funcao_nao_desliga():
    so_seno = frozenset({"sin"})
    assert toggle_visible(so_seno, "sin") == so_seno
    assert toggle_visible(so_seno, "cos") == {"sin", "cos"}


def test_funcao_desconhecida():
    with pytest.raises(ValueError):
        toggle_visible(TODAS, "sec")


# --- preferência -----------------------------------------------------------------------
def test_funcoes_visiveis_salvas(tmp_path):
    arquivo = tmp_path / PREFERENCES_FILE
    assert Preferences(arquivo).visible_functions == ("sin", "cos", "tan")
    Preferences(arquivo).update(visible_functions=("cos", "sin"))
    assert Preferences(arquivo).visible_functions == ("sin", "cos")       # ordem fixa


@pytest.mark.parametrize("valor", ['[]', '["sec"]', '"sin"', '["sin", 3]'])
def test_funcoes_visiveis_invalidas_voltam_ao_padrao(tmp_path, valor):
    arquivo = tmp_path / PREFERENCES_FILE
    arquivo.write_text(f'{{"versao": 1, "funcoes_visiveis": {valor}}}', encoding="utf-8")
    assert Preferences(arquivo).visible_functions == ("sin", "cos", "tan")


# --- janela ----------------------------------------------------------------------------
def _janela(qtbot, pasta, largura=900, altura=640, movimento=False, aba=TRIG_TAB):
    create_app()
    window = build_window(pasta, reduce_motion=lambda: not movimento)
    qtbot.addWidget(window)
    window.resize(largura, altura)
    window.show()
    qtbot.waitExposed(window)
    window.tabs.setCurrentIndex(aba)
    qtbot.wait(10)
    return window


def test_desligar_a_tangente_some_de_tudo(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path)
    pagina = window.trig_page
    botao = pagina.toggles["tan"]
    assert botao.isChecked()
    assert botao.accessibleName() == "Mostrar tangente"
    qtbot.mouseClick(botao, Qt.MouseButton.LeftButton)
    assert not botao.isChecked()
    assert "tan" not in pagina.circle.visible
    assert "tan" not in pagina.graphs.visible
    assert not pagina.info.value_labels["tan"].isVisible()
    assert pagina.info.value_labels["sin"].isVisible()
    assert Preferences(tmp_path / PREFERENCES_FILE).visible_functions == ("sin", "cos")


def test_escolha_vale_ao_reabrir(qtbot, tmp_path):
    Preferences(tmp_path / PREFERENCES_FILE).update(visible_functions=("cos",))
    pagina = _janela(qtbot, tmp_path).trig_page
    assert pagina.visible == {"cos"}
    assert not pagina.toggles["sin"].isChecked()
    assert not pagina.toggles["cos"].isEnabled()          # a única ligada fica bloqueada
    assert pagina.toggles["cos"].toolTip() == "Pelo menos uma função fica visível"


def test_ultima_ligada_fica_bloqueada(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path).trig_page
    qtbot.mouseClick(pagina.toggles["sin"], Qt.MouseButton.LeftButton)
    qtbot.mouseClick(pagina.toggles["cos"], Qt.MouseButton.LeftButton)
    assert pagina.visible == {"tan"}
    assert not pagina.toggles["tan"].isEnabled()
    qtbot.mouseClick(pagina.toggles["sin"], Qt.MouseButton.LeftButton)
    assert pagina.toggles["tan"].isEnabled()


def test_teclado_liga_e_desliga(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path).trig_page
    botao = pagina.toggles["cos"]
    botao.setFocus()
    qtbot.keyClick(botao, Qt.Key.Key_Space)
    assert "cos" not in pagina.visible


def test_tangente_desligada_nao_e_desenhada(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path).trig_page
    pagina.state.set_angle(45)
    pagina.refresh(True)
    circulo = pagina.circle
    centro, raio = circulo._geometry()
    ponto = QPointF(centro.x() + raio, centro.y() - raio * 0.5).toPoint()
    cor_tan = PALETTES[pagina._theme.name]["trig_tan"]

    def menor_distancia():
        imagem = circulo.grab().toImage()
        perto = [imagem.pixelColor(ponto + QPoint(dx, dy)) for dx in (-1, 0, 1) for dy in range(-4, 5)]
        return min(distancia(c, cor_tan) for c in perto)

    assert menor_distancia() < 120
    qtbot.mouseClick(pagina.toggles["tan"], Qt.MouseButton.LeftButton)
    assert menor_distancia() > 150


def test_cabe_na_janela_minima_com_os_botoes(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, MIN_WIDTH, MIN_HEIGHT)
    window.resize(MIN_WIDTH, MIN_HEIGHT)
    qtbot.wait(20)
    pagina = window.trig_page
    for botao in pagina.toggles.values():
        assert botao.geometry().right() <= pagina.top_bar.width()
    assert pagina.view_tabs.sizeHint().width() <= pagina.view_tabs.width()
    assert pagina.controls.geometry().bottom() <= pagina.height()
    assert pagina.circle.height() >= 140


@pytest.mark.parametrize("tema", [LIGHT, DARK])
def test_contraste_dos_botoes_de_funcao(tema):
    paleta = PALETTES[tema]
    botao = surface_colors(paleta, paleta["key_bg"], KEY_ALPHA)
    for chave in ("trig_sin", "trig_cos", "trig_tan", "text_muted"):
        assert min_contrast(paleta, chave, botao) >= 4.5, chave


# --- ajustes visuais -------------------------------------------------------------------
@pytest.mark.parametrize("angulo", [30, 45, 50, 135, 225, 240, 315])
def test_numero_do_quadrante_se_afasta_do_raio(qtbot, tmp_path, angulo):
    circulo = _janela(qtbot, tmp_path).trig_page.circle
    centro, raio = circulo._geometry()
    for numero in range(1, 5):
        ponto = circulo._quadrant_spot(centro, raio, numero, angulo)
        direcao = math.degrees(math.atan2(centro.y() - ponto.y(), ponto.x() - centro.x())) % 360
        distancia = abs((direcao - angulo + 180) % 360 - 180)
        assert distancia >= QUADRANT_LABEL_GAP, (numero, distancia)


def test_texto_longo_no_campo_diminui(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, MIN_WIDTH, MIN_HEIGHT)
    campo = window.trig_page.sine_field
    campo.set_value("0,5")
    curto = campo.edit.font().pointSize()
    campo.set_value("-0,707106781187")
    longo = campo.edit.font().pointSize()
    assert longo < curto
    assert QFontMetrics(campo.edit.font()).horizontalAdvance(campo.edit.text()) <= campo.edit.width()


# --- transições ------------------------------------------------------------------------
def test_troca_de_aba_esmaece(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, movimento=True, aba=0)
    window.tabs.setCurrentIndex(SCIENTIFIC_TAB)
    pagina = window.pages.currentWidget()
    assert pagina.graphicsEffect() is not None
    qtbot.waitUntil(lambda: pagina.graphicsEffect() is None, timeout=FADE_MS * 10)


def test_resultado_esmaece(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, movimento=True, aba=0)
    qtbot.wait(FADE_MS * 3)
    qtbot.keyClicks(window, "2+3")
    qtbot.keyClick(window, Qt.Key.Key_Return)
    rotulo = window.display.result_label
    assert rotulo.text() == "5"
    assert rotulo.graphicsEffect() is not None
    qtbot.waitUntil(lambda: rotulo.graphicsEffect() is None, timeout=FADE_MS * 10)


def test_seletor_circulo_graficos_esmaece(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path, 400, movimento=True).trig_page
    qtbot.wait(FADE_MS * 3)
    pagina.view_tabs.setCurrentIndex(1)
    assert pagina.graphs.graphicsEffect() is not None
    qtbot.waitUntil(lambda: pagina.graphs.graphicsEffect() is None, timeout=FADE_MS * 10)


def test_sem_esmaecer_quando_reduzir_movimento(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, movimento=False, aba=0)
    window.tabs.setCurrentIndex(SCIENTIFIC_TAB)
    assert window.pages.currentWidget().graphicsEffect() is None


def test_trocas_rapidas_nao_quebram(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, movimento=True, aba=0)
    for indice in (1, 2, 0, 1, 2, 0, 1):
        window.tabs.setCurrentIndex(indice)
    qtbot.waitUntil(lambda: all(window.pages.widget(i).graphicsEffect() is None for i in range(3)),
                    timeout=FADE_MS * 10)


# --- ícone -------------------------------------------------------------------------------
def test_icone_do_app():
    create_app()
    icone = app_icon()
    assert not icone.isNull()
    assert {s.width() for s in icone.availableSizes()} == set(ICON_SIZES)
    assert not QApplication.windowIcon().isNull()
