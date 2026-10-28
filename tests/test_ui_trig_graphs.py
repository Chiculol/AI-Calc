"""Testes da Etapa 4B na janela: gráficos, layout largo/estreito e animação do ponto."""

import pytest
from PySide6.QtCore import QPoint, Qt

from ai_calc.ui.app import build_window, create_app
from ai_calc.ui.main_window import MIN_HEIGHT, MIN_WIDTH, TRIG_TAB
from ai_calc.ui.theme import DARK, LIGHT, PALETTES
from ai_calc.ui.trig_page import GRAPHS_VIEW, POINT_MS, WIDE_MIN_WIDTH


def _janela(qtbot, pasta, largura=760, altura=640, movimento=False):
    create_app()
    window = build_window(pasta, reduce_motion=lambda: not movimento)
    qtbot.addWidget(window)
    window.resize(largura, altura)
    window.show()
    qtbot.waitExposed(window)
    window.tabs.setCurrentIndex(TRIG_TAB)
    qtbot.wait(10)
    return window


def digitar_no_campo(qtbot, campo, texto):
    campo.edit.setFocus()
    campo.edit.selectAll()
    qtbot.keyClicks(campo.edit, texto)
    qtbot.keyClick(campo.edit, Qt.Key.Key_Return)


# --- layout ---------------------------------------------------------------------------
def test_janela_larga_mostra_circulo_e_graficos_lado_a_lado(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path).trig_page
    assert pagina.width() >= WIDE_MIN_WIDTH
    assert pagina.wide
    assert not pagina.view_tabs.isVisible()
    assert pagina.circle.isVisible() and pagina.graphs.isVisible()
    assert pagina.graphs.geometry().left() > pagina.circle.geometry().right()


def test_janela_estreita_usa_seletor(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path, 400).trig_page
    assert not pagina.wide
    assert pagina.view_tabs.isVisible()
    assert pagina.view_tabs.accessibleName() == "Mostrar círculo ou gráficos"
    assert pagina.circle.isVisible() and not pagina.graphs.isVisible()
    pagina.view_tabs.setCurrentIndex(GRAPHS_VIEW)
    assert pagina.graphs.isVisible() and not pagina.circle.isVisible()
    pagina.view_tabs.setCurrentIndex(0)
    assert pagina.circle.isVisible()


def test_alargar_e_estreitar_troca_o_layout(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path, 400)
    pagina = window.trig_page
    window.resize(800, 640)
    qtbot.wait(20)
    assert pagina.wide and pagina.graphs.isVisible() and pagina.circle.isVisible()
    window.resize(400, 640)
    qtbot.wait(20)
    assert not pagina.wide


@pytest.mark.parametrize("visao", [0, GRAPHS_VIEW])
def test_cabe_na_janela_minima_nas_duas_visoes(qtbot, tmp_path, visao):
    window = _janela(qtbot, tmp_path, MIN_WIDTH, MIN_HEIGHT)
    pagina = window.trig_page
    pagina.view_tabs.setCurrentIndex(visao)
    qtbot.wait(20)
    visual = pagina.graphs if visao == GRAPHS_VIEW else pagina.circle
    assert visual.height() >= 150
    for widget in (pagina.view_tabs, visual, pagina.controls):
        assert widget.geometry().bottom() <= pagina.height(), type(widget).__name__
    assert pagina.view_tabs.sizeHint().width() <= pagina.view_tabs.width()


# --- gráficos ---------------------------------------------------------------------------
def test_marca_acompanha_o_angulo(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path).trig_page
    assert pagina.graphs.marker == 30
    pagina.circle.setFocus()
    qtbot.keyClick(pagina.circle, Qt.Key.Key_Right, Qt.KeyboardModifier.ShiftModifier)
    assert pagina.graphs.marker == 45
    digitar_no_campo(qtbot, pagina.angle_field, "300")
    assert pagina.graphs.marker == 300


def test_rotulos_do_eixo_em_graus_e_radianos(qtbot, tmp_path):
    window = _janela(qtbot, tmp_path)
    graficos = window.trig_page.graphs
    assert [graficos._tick_text(g) for g in (0, 90, 180, 270, 360)] == ["0°", "90°", "180°", "270°", "360°"]
    window.set_angle_mode("RAD")
    assert [graficos._tick_text(g) for g in (0, 90, 180, 270, 360)] == ["0", "π/2", "π", "3π/2", "2π"]


def test_nome_acessivel_dos_graficos(qtbot, tmp_path):
    graficos = _janela(qtbot, tmp_path).trig_page.graphs
    assert graficos.accessibleName() == "Gráficos de seno, cosseno e tangente, de 0 a 360 graus"


def _distancia(cor, hex_cor):
    alvo = int(hex_cor[1:3], 16), int(hex_cor[3:5], 16), int(hex_cor[5:7], 16)
    return sum(abs(a - b) for a, b in zip((cor.red(), cor.green(), cor.blue()), alvo))


@pytest.mark.parametrize("tema", [LIGHT, DARK])
def test_curvas_nas_cores_do_tema(qtbot, tmp_path, tema):
    window = _janela(qtbot, tmp_path)
    window.theme.set_theme(tema)
    graficos = window.trig_page.graphs
    qtbot.wait(20)
    imagem = graficos.grab().toImage()

    def perto_da_curva(graus, valor, chave):
        centro = graficos.to_screen(graus, valor).toPoint()
        # Linhas tracejadas e pontilhadas têm vãos: procura num pequeno trecho em volta.
        cores = [imagem.pixelColor(centro + QPoint(dx, dy)) for dx in range(-5, 6) for dy in range(-2, 3)]
        return min(_distancia(c, PALETTES[tema][chave]) for c in cores)

    assert perto_da_curva(150, 0.5, "trig_sin") < 90         # seno em 150° (longe da marca)
    assert perto_da_curva(180, -1.0, "trig_cos") < 90        # cosseno em 180°
    assert perto_da_curva(135, -1.0, "trig_tan") < 120       # tangente em 135° (pontilhada)


# --- animação do ponto -------------------------------------------------------------------
def test_ponto_desliza_ao_digitar_o_angulo(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path, movimento=True).trig_page
    digitar_no_campo(qtbot, pagina.angle_field, "120")
    assert pagina.state.angle == 120                 # o valor muda na hora...
    assert pagina.info.angle_label.text().startswith("120°")
    assert pagina.animating                          # ...e o ponto vai deslizando
    meio = []
    pagina._animation.valueChanged.connect(lambda v: meio.append(float(v)))
    qtbot.waitUntil(lambda: not pagina.animating, timeout=POINT_MS * 5)
    assert pagina.circle.shown_angle == pytest.approx(120)
    assert pagina.graphs.marker == pytest.approx(120)
    assert any(30 < v < 120 for v in meio)


def test_ponto_vai_pelo_caminho_mais_curto(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path, movimento=True).trig_page
    digitar_no_campo(qtbot, pagina.angle_field, "330")    # de 30° para 330°: passa por 0°, não por 180°
    valores = []
    pagina._animation.valueChanged.connect(lambda v: valores.append(float(v)))
    qtbot.waitUntil(lambda: not pagina.animating, timeout=POINT_MS * 5)
    assert all(-31 <= v <= 31 for v in valores)
    assert pagina.circle.shown_angle == pytest.approx(330)


def test_outra_solucao_tambem_desliza(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path, movimento=True).trig_page
    qtbot.mouseClick(pagina.toggle_button, Qt.MouseButton.LeftButton)
    assert pagina.state.angle == 150
    assert pagina.animating
    qtbot.waitUntil(lambda: not pagina.animating, timeout=POINT_MS * 5)
    assert pagina.circle.shown_angle == pytest.approx(150)


def test_arrastar_interrompe_a_animacao(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path, movimento=True).trig_page
    digitar_no_campo(qtbot, pagina.angle_field, "200")
    assert pagina.animating
    pagina.circle.setFocus()
    qtbot.keyClick(pagina.circle, Qt.Key.Key_Right)
    assert not pagina.animating
    assert pagina.state.angle == 201
    assert pagina.circle.shown_angle == 201
    assert pagina.graphs.marker == 201


def test_reduzir_movimento_move_na_hora(qtbot, tmp_path):
    pagina = _janela(qtbot, tmp_path, movimento=False).trig_page
    digitar_no_campo(qtbot, pagina.angle_field, "120")
    assert not pagina.animating
    assert pagina.circle.shown_angle == 120
    assert pagina.graphs.marker == 120
