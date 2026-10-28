"""Testes da Etapa 3D no motor: gravação segura, histórico, preferências e etiqueta DEG/RAD."""

import json
from datetime import datetime

import pytest

from ai_calc.core.calculator import calculate
from ai_calc.core.editor import ExpressionEditor
from ai_calc.core.history import MAX_HISTORY, History, HistoryEntry
from ai_calc.core.preferences import Preferences
from ai_calc.core.storage import quarantine, write_json_atomic


def corrompidos(pasta):
    return sorted(p.name for p in pasta.iterdir() if ".corrompido-" in p.name)


# --- gravação segura ---------------------------------------------------------
def test_gravacao_segura_nao_deixa_temporario(tmp_path):
    arquivo = tmp_path / "dados.json"
    assert write_json_atomic(arquivo, {"a": 1})
    assert write_json_atomic(arquivo, {"a": 2, "texto": "ação"})
    assert json.loads(arquivo.read_text(encoding="utf-8")) == {"a": 2, "texto": "ação"}
    assert [p.name for p in tmp_path.iterdir()] == ["dados.json"]


def test_gravacao_cria_a_pasta(tmp_path):
    arquivo = tmp_path / "nova" / "pasta" / "dados.json"
    assert write_json_atomic(arquivo, [])
    assert arquivo.exists()


def test_gravacao_que_falha_nao_quebra(tmp_path):
    pasta_no_lugar = tmp_path / "dados.json"
    pasta_no_lugar.mkdir()                  # não dá para trocar uma pasta por arquivo
    assert write_json_atomic(pasta_no_lugar, {}) is False
    assert [p.name for p in tmp_path.iterdir()] == ["dados.json"]


def test_nome_do_arquivo_corrompido(tmp_path):
    arquivo = tmp_path / "historico.json"
    momento = datetime(2026, 10, 28, 15, 30, 0)
    arquivo.write_text("x")
    assert quarantine(arquivo, momento).name == "historico.corrompido-20261028-153000.json"
    arquivo.write_text("y")
    assert quarantine(arquivo, momento).name == "historico.corrompido-20261028-153000-2.json"


# --- histórico ---------------------------------------------------------------
def test_mais_novo_primeiro_e_limite_de_20(tmp_path):
    historico = History(tmp_path / "historico.json")
    for n in range(25):
        historico.add(f"{n}+0", str(n))
    assert len(historico.entries) == MAX_HISTORY
    assert historico.entries[0].result == "24"
    assert historico.entries[-1].result == "5"


def test_conta_com_erro_nao_entra():
    historico = History()
    assert not historico.add("5÷0", "")
    assert not historico.add("   ", "3")
    assert historico.entries == []


def test_salva_e_recarrega(tmp_path):
    arquivo = tmp_path / "historico.json"
    historico = History(arquivo)
    historico.add("sin(30)", "0,5", "DEG")
    historico.add("2+3", "5")
    de_novo = History(arquivo)
    assert de_novo.entries == [HistoryEntry("2+3", "5"), HistoryEntry("sin(30)", "0,5", "DEG")]
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    assert dados["versao"] == 1
    assert dados["itens"][1] == {"expressao": "sin(30)", "resultado": "0,5", "modo": "DEG"}


def test_limpar_salva_vazio(tmp_path):
    arquivo = tmp_path / "historico.json"
    historico = History(arquivo)
    historico.add("1+1", "2")
    historico.clear()
    assert History(arquivo).entries == []


@pytest.mark.parametrize(
    "conteudo",
    [
        "{isto não é json",
        "[]",
        '{"versao": 99, "itens": []}',
        '{"versao": 1, "itens": "abc"}',
        '{"versao": 1, "itens": [{"expressao": "1+1"}]}',
        '{"versao": 1, "itens": [{"expressao": "1", "resultado": "1", "modo": "GRAD"}]}',
    ],
)
def test_historico_corrompido_e_renomeado(tmp_path, conteudo):
    arquivo = tmp_path / "historico.json"
    arquivo.write_text(conteudo, encoding="utf-8")
    historico = History(arquivo)
    assert historico.entries == []
    assert not arquivo.exists()
    assert len(corrompidos(tmp_path)) == 1
    historico.add("2+2", "4")                 # recomeça normalmente
    assert History(arquivo).entries == [HistoryEntry("2+2", "4")]


def test_historico_com_bytes_invalidos(tmp_path):
    arquivo = tmp_path / "historico.json"
    arquivo.write_bytes(b"\xff\xfe\x00lixo")
    assert History(arquivo).entries == []
    assert len(corrompidos(tmp_path)) == 1


# --- preferências ------------------------------------------------------------
def test_preferencias_padrao(tmp_path):
    preferencias = Preferences(tmp_path / "preferencias.json")
    assert preferencias.theme is None
    assert preferencias.angle_mode == "DEG"
    assert preferencias.last_tab == "comum"


def test_preferencias_salvam_e_recarregam(tmp_path):
    arquivo = tmp_path / "preferencias.json"
    Preferences(arquivo).update(theme="escuro", angle_mode="RAD", last_tab="cientifica")
    de_novo = Preferences(arquivo)
    assert (de_novo.theme, de_novo.angle_mode, de_novo.last_tab) == ("escuro", "RAD", "cientifica")


def test_preferencias_ignoram_valores_desconhecidos(tmp_path):
    arquivo = tmp_path / "preferencias.json"
    arquivo.write_text(
        '{"versao": 1, "tema": "roxo", "modo_angulo": "GRAD", "ultima_aba": "trig"}',
        encoding="utf-8",
    )
    preferencias = Preferences(arquivo)
    assert (preferencias.theme, preferencias.angle_mode, preferencias.last_tab) == (None, "DEG", "comum")
    assert corrompidos(tmp_path) == []


@pytest.mark.parametrize("conteudo", ["{", "[1, 2]", '{"versao": 2}'])
def test_preferencias_corrompidas_sao_renomeadas(tmp_path, conteudo):
    arquivo = tmp_path / "preferencias.json"
    arquivo.write_text(conteudo, encoding="utf-8")
    preferencias = Preferences(arquivo)
    assert preferencias.theme is None
    assert len(corrompidos(tmp_path)) == 1
    preferencias.update(theme="claro")
    assert Preferences(arquivo).theme == "claro"


def test_preferencia_desconhecida_e_erro_de_programacao():
    with pytest.raises(AttributeError):
        Preferences().update(cor="azul")


# --- conta com trigonometria (etiqueta DEG/RAD) -------------------------------
@pytest.mark.parametrize(
    "conta, usa",
    [
        ("sin(30)", True),
        ("2 + cos(0)", True),
        ("(1 + atan(1))!", True),      # função dentro de parênteses e fatorial
        ("asin(1) × 2", True),
        ("2 + 3", False),
        ("ln(e) + √4", False),
        ("raiz(3; 8)", False),
    ],
)
def test_conta_usa_trigonometria(conta, usa):
    assert calculate(conta).uses_trig is usa


# --- número vindo do histórico -----------------------------------------------
@pytest.mark.parametrize(
    "antes, numero, depois",
    [
        ("", "5", "5"),
        ("", "-6", "(-6)"),
        ("2+", "-6", "2+(-6)"),
        ("2+", "1,5", "2+1,5"),
        ("2", "5", "2×5"),
        ("(1+2)", "-3", "(1+2)×(-3)"),
        ("π", "2", "π×2"),
        ("4!", "2", "4!×2"),
        ("sin(", "30", "sin(30"),
    ],
)
def test_inserir_numero_do_historico(antes, numero, depois):
    editor = ExpressionEditor()
    for tecla in antes:
        editor.insert(tecla)
    editor.insert_value(numero)
    assert editor.expression == depois


def test_numero_negativo_do_historico_ao_quadrado():
    editor = ExpressionEditor()
    editor.insert_value("-6")
    editor.insert("^2")
    editor.evaluate()
    assert editor.result == "36"


def test_numero_do_historico_depois_do_igual_comeca_conta_nova():
    editor = ExpressionEditor()
    for tecla in "2+3":
        editor.insert(tecla)
    editor.evaluate()
    editor.insert_value("42")
    assert editor.expression == "42"
    assert editor.result == ""
