"""Analisador de expressões (descida recursiva).

Precedência, da menor para a maior:
    1. + e -
    2. x, / e multiplicação implícita (esquerda para a direita)
    3. menos unário
    4. ^ (direita para a esquerda)
    5. ! e % (sufixos)
    6. parênteses, funções, constantes, números e a raiz quadrada
"""

from __future__ import annotations

from .ast_nodes import Binary, Const, Func, Group, Node, Number, Postfix, Sqrt, Unary
from .errors import (
    IncompleteExpressionError,
    InvalidExpressionError,
    ParenthesesError,
)
from .render import to_text
from .tokenizer import (
    DIV,
    FACT,
    LPAREN,
    MINUS,
    MUL,
    NAME,
    NUMBER,
    PERCENT,
    PLUS,
    POW,
    RPAREN,
    SEMI,
    SQRT,
    Token,
)

CONSTANTS = {"pi": "pi", "π": "pi", "e": "e"}

# nome da função -> quantidade de argumentos
FUNCTIONS = {
    "sin": 1,
    "cos": 1,
    "tan": 1,
    "asin": 1,
    "acos": 1,
    "atan": 1,
    "ln": 1,
    "log": 1,
    "sqrt": 1,
    "abs": 1,
    "raiz": 2,
}


def parse(tokens: list[Token]) -> Node:
    if not tokens:
        raise IncompleteExpressionError()
    parser = _Parser(tokens)
    node = parser.expression()
    leftover = parser.peek()
    if leftover is not None:
        if leftover.kind == RPAREN:
            raise ParenthesesError()
        raise InvalidExpressionError()
    return node


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    # --- utilidades -----------------------------------------------------
    def peek(self) -> Token | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self) -> Token | None:
        token = self.peek()
        if token is not None:
            self.pos += 1
        return token

    def _expect_rparen(self) -> None:
        token = self.peek()
        if token is None:
            raise ParenthesesError()
        if token.kind != RPAREN:
            raise InvalidExpressionError()
        self.pos += 1

    # --- gramática --------------------------------------------------------
    def expression(self) -> Node:
        left = self._term()
        while (token := self.peek()) is not None and token.kind in (PLUS, MINUS):
            self._next()
            right = self._term()
            left = Binary("+" if token.kind == PLUS else "-", left, right)
        return left

    def _term(self) -> Node:
        left = self._unary()
        while (token := self.peek()) is not None:
            if token.kind in (MUL, DIV):
                self._next()
                right = self._unary()
                left = Binary("*" if token.kind == MUL else "/", left, right)
            elif token.kind in (LPAREN, SQRT, NAME):
                # multiplicação implícita: 2pi, 3(4+5), 2sin(30), 2√9
                right = self._unary()
                left = Binary("*", left, right, implicit=True)
            else:
                break
        return left

    def _unary(self) -> Node:
        token = self.peek()
        if token is not None and token.kind in (PLUS, MINUS):
            self._next()
            return Unary("+" if token.kind == PLUS else "-", self._unary())
        return self._power()

    def _power(self) -> Node:
        base = self._postfix()
        token = self.peek()
        if token is not None and token.kind == POW:
            self._next()
            exponent = self._unary()  # direita para a esquerda; aceita sinal
            return Binary("^", base, exponent)
        return base

    def _postfix(self) -> Node:
        node = self._primary()
        last_kind = None
        while (token := self.peek()) is not None and token.kind in (FACT, PERCENT):
            self._next()
            if token.kind == FACT and last_kind == FACT:
                raise InvalidExpressionError(f"Use parênteses: ({to_text(node)})!")
            node = Postfix(token.text, node)
            last_kind = token.kind
        return node

    def _primary(self) -> Node:
        token = self._next()
        if token is None:
            raise IncompleteExpressionError()

        if token.kind == NUMBER:
            return Number(token.value, token.text)

        if token.kind == NAME:
            if token.text in CONSTANTS:
                return Const(CONSTANTS[token.text])
            if token.text in FUNCTIONS:
                return self._function_call(token.text)
            raise InvalidExpressionError()

        if token.kind == LPAREN:
            inner = self.expression()
            self._expect_rparen()
            return Group(inner)

        if token.kind == SQRT:
            return Sqrt(self._primary())

        if token.kind == RPAREN:
            raise ParenthesesError()

        raise InvalidExpressionError()

    def _function_call(self, name: str) -> Node:
        following = self.peek()
        if following is None:
            raise IncompleteExpressionError()
        if following.kind != LPAREN:
            example = f"{name}({following.text})" if following.kind == NUMBER else f"{name}(...)"
            raise InvalidExpressionError(f"Use parênteses: {example}")
        self._next()  # consome "("
        args = [self.expression()]
        while (token := self.peek()) is not None and token.kind == SEMI:
            self._next()
            args.append(self.expression())
        self._expect_rparen()
        if len(args) != FUNCTIONS[name]:
            raise InvalidExpressionError()
        return Func(name, tuple(args))
