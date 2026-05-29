import re

# ---------------------------------------------------------------------------
# Mapeamento de palavras-chave para categorias
# ---------------------------------------------------------------------------
CATEGORY_MAP = {
    "Alimentação": [
        "lanche", "comida", "almoço", "jantar", "café", "cafe", "restaurante",
        "hamburger", "hamburguer", "pizza", "sushi", "mercado", "supermercado",
        "feira", "padaria", "snack", "delivery", "ifood", "rappi", "uber eats",
        "refeição", "refeicao", "marmita", "churrasco",
    ],
    "Transporte": [
        "uber", "99", "taxi", "táxi", "ônibus", "onibus", "metrô", "metro",
        "gasolina", "combustivel", "combustível", "estacionamento", "pedágio",
        "pedagio", "passagem", "transporte", "moto", "carro", "bicicleta",
    ],
    "Saúde": [
        "farmácia", "farmacia", "remédio", "remedio", "médico", "medico",
        "consulta", "exame", "hospital", "plano de saúde", "academia",
        "dentista", "fisio", "psicólogo", "psicologo",
    ],
    "Moradia": [
        "aluguel", "condomínio", "condominio", "água", "agua", "luz",
        "energia", "internet", "gás", "gas", "iptu", "seguro", "reforma",
        "manutenção", "manutencao",
    ],
    "Lazer": [
        "cinema", "show", "teatro", "viagem", "hotel", "Netflix", "spotify",
        "disney", "amazon prime", "jogo", "game", "bar", "balada", "festa",
        "ingresso", "passeio",
    ],
    "Educação": [
        "curso", "livro", "faculdade", "escola", "mensalidade", "apostila",
        "material", "treinamento", "certificado",
    ],
    "Vestuário": [
        "roupa", "sapato", "tênis", "tenis", "calçado", "calcado", "camisa",
        "calça", "calca", "vestido", "acessório", "acessorio", "bolsa",
    ],
    "Receita": [
        "salário", "salario", "freelance", "renda", "recebi", "recebimento",
        "pagamento", "bonus", "bônus", "dividendo", "aluguel recebido",
        "venda", "comissão", "comissao",
    ],
}


def detect_category(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return "Geral"


# ---------------------------------------------------------------------------
# Padrões regex para extração de valor e intenção
# ---------------------------------------------------------------------------
AMOUNT_PATTERNS = [
    r"r\$\s*([\d]+(?:[.,][\d]{1,2})?)",
    r"([\d]+(?:[.,][\d]{1,2})?)\s*reais?",
    r"([\d]+(?:[.,][\d]{1,2})?)\s*conto",
    r"(?:^|\s)([\d]+(?:[.,][\d]{1,2})?)(?:\s|$)",
]

EXPENSE_KEYWORDS = [
    r"\bgastei\b", r"\bgasto\b", r"\bpaguei\b", r"\bpagar\b",
    r"\bcomprei\b", r"\bcompra\b", r"\bsaiu\b", r"\bsaída\b",
    r"\bdebitou\b", r"\bdebito\b", r"\bdébito\b",
]

INCOME_KEYWORDS = [
    r"\brecebi\b", r"\brenda\b", r"\bganho\b", r"\bganhei\b",
    r"\bsalário\b", r"\bsalario\b", r"\bfreelance\b", r"\brecebimento\b",
    r"\bentrou\b", r"\bdepósito\b", r"\bdeposito\b",
]

BALANCE_KEYWORDS   = [r"\bsaldo\b", r"\bsituação\b", r"\bsituacao\b", r"\bcomo (estou|tô|to)\b"]
REPORT_KEYWORDS    = [r"\brelatório\b", r"\brelatorio\b", r"\bresumo\b", r"\bbalanço\b", r"\bbalanco\b"]
HISTORY_KEYWORDS   = [r"\bhistórico\b", r"\bhistorico\b", r"\bextrato\b", r"\búltimos\b", r"\bultimos\b"]
CATEGORY_KEYWORDS  = [r"\bcategorias?\b", r"\bgastos por\b", r"\bonde gastei\b"]
GOAL_KEYWORDS      = [r"\bmeta\b", r"\bobjetivo\b", r"\blimite\b"]
CHART_KEYWORDS     = [r"\bgráfico\b", r"\bgrafico\b", r"\bcharts?\b", r"\bvisual\b"]
EXPORT_KEYWORDS    = [r"\bexportar?\b", r"\bcsv\b", r"\bplanilha\b", r"\bdownload\b"]
HELP_KEYWORDS      = [r"\bajuda\b", r"\bhelp\b", r"\bcomandos?\b", r"\bo que (você|voce) faz\b"]


def _match_any(patterns: list, text: str) -> bool:
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def extract_amount(text: str) -> float | None:
    for pattern in AMOUNT_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            raw = m.group(1).replace(",", ".")
            try:
                return float(raw)
            except ValueError:
                continue
    return None


def parse_message(text: str) -> dict:
    """
    Retorna um dict com:
      intent  : "expense" | "income" | "balance" | "report" | "history" |
                "categories" | "goal" | "chart" | "export" | "help" | "unknown"
      amount  : float | None
      category: str
      description: str
    """
    result = {
        "intent": "unknown",
        "amount": None,
        "category": "Geral",
        "description": text.strip(),
    }

    t = text.strip()

    # --- comandos explícitos (slash ou palavra-chave pura) ---
    lower = t.lower()
    if lower in ("/help", "/ajuda", "ajuda", "help", "comandos"):
        result["intent"] = "help"
        return result
    if lower in ("/saldo", "saldo"):
        result["intent"] = "balance"
        return result
    if lower in ("/relatorio", "/relatório", "relatório", "relatorio", "resumo"):
        result["intent"] = "report"
        return result
    if lower in ("/historico", "/histórico", "histórico", "historico", "extrato"):
        result["intent"] = "history"
        return result
    if lower in ("/categorias", "categorias"):
        result["intent"] = "categories"
        return result
    if lower in ("/grafico", "/gráfico", "gráfico", "grafico"):
        result["intent"] = "chart"
        return result
    if lower in ("/exportar", "exportar", "csv"):
        result["intent"] = "export"
        return result

    # --- meta ---
    if _match_any(GOAL_KEYWORDS, t):
        result["intent"] = "goal"
        result["amount"] = extract_amount(t)
        return result

    # --- relatório / balanço ---
    if _match_any(REPORT_KEYWORDS, t):
        result["intent"] = "report"
        return result

    # --- saldo ---
    if _match_any(BALANCE_KEYWORDS, t):
        result["intent"] = "balance"
        return result

    # --- histórico ---
    if _match_any(HISTORY_KEYWORDS, t):
        result["intent"] = "history"
        return result

    # --- categorias ---
    if _match_any(CATEGORY_KEYWORDS, t):
        result["intent"] = "categories"
        return result

    # --- gráfico ---
    if _match_any(CHART_KEYWORDS, t):
        result["intent"] = "chart"
        return result

    # --- exportar ---
    if _match_any(EXPORT_KEYWORDS, t):
        result["intent"] = "export"
        return result

    # --- ajuda ---
    if _match_any(HELP_KEYWORDS, t):
        result["intent"] = "help"
        return result

    # --- gasto / receita ---
    amount = extract_amount(t)
    category = detect_category(t)

    if _match_any(INCOME_KEYWORDS, t) or category == "Receita":
        result["intent"] = "income"
        result["amount"] = amount
        result["category"] = "Receita" if category == "Geral" else category
        return result

    if _match_any(EXPENSE_KEYWORDS, t) or amount is not None:
        result["intent"] = "expense"
        result["amount"] = amount
        result["category"] = category
        return result

    return result
