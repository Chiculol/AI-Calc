"""Converte a árvore de volta em texto legível (linha "Interpretado como")."""

from __future__ import annotations

from .ast_nodes import Binary, Const, Func, Group, Node, Number, Postfix, Sqrt, Unary

_OPERATORS = {
    "+": " + ",
    "-": " − ",
    "*": " × ",
    "/": " ÷ ",
    "^": "^",
}


def to_text(node: Node) -> str:
    if isinstance(node, Number):
        return node.text.replace(".", ",")
    if isinstance(node, Const):
        return "π" if node.name == "pi" else node.name
    if isinstance(node, Group):
        return "(" + to_text(node.expr) + ")"
    if isinstance(node, Unary):
        sign = "−" if node.op == "-" else "+"
        return sign + to_text(node.operand)
    if isinstance(node, Binary):
        return to_text(node.left) + _OPERATORS[node.op] + to_text(node.right)
    if isinstance(node, Postfix):
        return to_text(node.operand) + node.op
    if isinstance(node, Func):
        return node.name + "(" + "; ".join(to_text(a) for a in node.args) + ")"
    if isinstance(node, Sqrt):
        return "√" + to_text(node.operand)
    raise TypeError(f"Nó desconhecido: {node!r}")


def contains_implicit(node: Node) -> bool:
    """Diz se alguma multiplicação foi inserida pelo app."""
    if isinstance(node, Binary):
        return node.implicit or contains_implicit(node.left) or contains_implicit(node.right)
    if isinstance(node, (Group,)):
        return contains_implicit(node.expr)
    if isinstance(node, (Unary, Postfix, Sqrt)):
        return contains_implicit(node.operand)
    if isinstance(node, Func):
        return any(contains_implicit(a) for a in node.args)
    return False
