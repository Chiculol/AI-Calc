"""Limites e tolerâncias do motor de cálculo (fáceis de ajustar)."""

# Tamanho máximo da expressão digitada.
MAX_EXPRESSION_LENGTH = 500

# Maior fatorial aceito (171! ultrapassa o maior número representável).
MAX_FACTORIAL = 170

# Um valor a menos disto de um inteiro conta como inteiro (ex.: 0,1 * 30).
INTEGER_TOLERANCE = 1e-9

# Tolerância, em quartos de volta, para tratar um ângulo como múltiplo exato de 90°.
TRIG_TOLERANCE = 1e-12

# Se |cos(x)| ficar abaixo disto, a tangente é considerada indefinida.
COS_UNDEFINED_THRESHOLD = 1e-12

# Círculo trigonométrico: um ângulo a menos disto (em graus) de um inteiro
# vira esse inteiro (ex.: 30,000000000000004° vira 30°).
ANGLE_SNAP_TOLERANCE = 1e-9

# Ao arrastar o ponto no círculo, a menos disto (em graus) de um ângulo notável, encaixa nele.
NOTABLE_SNAP_DEGREES = 2.0

# Gráficos: a curva da tangente é cortada acima deste valor (em módulo).
GRAPH_LIMIT = 2.0

# Formatação do resultado.
SIGNIFICANT_DIGITS = 12
SCIENTIFIC_UPPER_EXPONENT = 12   # a partir de 10**12 usa notação científica
SCIENTIFIC_LOWER_EXPONENT = -6   # abaixo de 10**-6 usa notação científica

ANGLE_MODES = ("DEG", "RAD")
