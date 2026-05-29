from datetime import datetime


def _fmt(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def help_message() -> str:
    return (
        "🤖 *FinBot — Controle Financeiro*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📌 *Registrar gastos:*\n"
        "• _gastei 50 reais com lanche_\n"
        "• _uber 23_\n"
        "• _mercado 120,50_\n\n"
        "📌 *Registrar ganhos:*\n"
        "• _recebi 1500_\n"
        "• _salário 3000_\n"
        "• _freelance 500_\n\n"
        "📌 *Consultas:*\n"
        "• *saldo* — ver saldo atual\n"
        "• *relatório* — resumo do mês\n"
        "• *histórico* — últimas transações\n"
        "• *categorias* — gastos por categoria\n"
        "• *gráfico* — gráfico de gastos\n"
        "• *exportar* — baixar CSV\n\n"
        "📌 *Meta mensal:*\n"
        "• _meta 2000_ — define limite de gastos\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Pode escrever naturalmente!\n"
        "Ex: _hoje almocei no restaurante e gastei 35 reais_"
    )


def expense_registered(amount: float, category: str, description: str,
                        balance: float, goal: float, total_expense: float) -> str:
    alert = ""
    if goal > 0 and total_expense >= goal:
        pct = (total_expense / goal) * 100
        alert = (
            f"\n\n⚠️ *ATENÇÃO!* Você atingiu *{pct:.0f}%* da sua meta mensal "
            f"de {_fmt(goal)}!\nTotal gasto: {_fmt(total_expense)}"
        )

    return (
        f"💸 *Gasto registrado!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 Categoria: {category}\n"
        f"💰 Valor: {_fmt(amount)}\n"
        f"📝 Descrição: {description}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Saldo atual: {_fmt(balance)}"
        f"{alert}"
    )


def income_registered(amount: float, category: str, description: str, balance: float) -> str:
    return (
        f"✅ *Receita registrada!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 Categoria: {category}\n"
        f"💰 Valor: {_fmt(amount)}\n"
        f"📝 Descrição: {description}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Saldo atual: {_fmt(balance)}"
    )


def balance_message(balance: float, total_income: float, total_expense: float,
                     goal: float) -> str:
    goal_line = ""
    if goal > 0:
        remaining = goal - total_expense
        pct = min((total_expense / goal) * 100, 100)
        bar_filled = int(pct / 10)
        bar = "🟥" * bar_filled + "⬜" * (10 - bar_filled)
        goal_line = (
            f"\n\n🎯 *Meta mensal:* {_fmt(goal)}\n"
            f"📉 Gasto: {_fmt(total_expense)} ({pct:.0f}%)\n"
            f"{bar}\n"
            f"💡 Restante: {_fmt(max(remaining, 0))}"
        )

    emoji = "😊" if balance >= 0 else "😟"
    return (
        f"{emoji} *Seu saldo atual*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 Receitas do mês: {_fmt(total_income)}\n"
        f"📉 Gastos do mês:   {_fmt(total_expense)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 Saldo: *{_fmt(balance)}*"
        f"{goal_line}"
    )


def report_message(total_income: float, total_expense: float, balance: float,
                    categories: list, month_name: str) -> str:
    cat_lines = ""
    for cat, total in sorted(categories, key=lambda x: x[1], reverse=True):
        pct = (total / total_expense * 100) if total_expense > 0 else 0
        cat_lines += f"  • {cat}: {_fmt(total)} ({pct:.0f}%)\n"

    if not cat_lines:
        cat_lines = "  Nenhum gasto registrado.\n"

    emoji = "🟢" if balance >= 0 else "🔴"
    return (
        f"📋 *Relatório — {month_name}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📈 Total recebido: {_fmt(total_income)}\n"
        f"📉 Total gasto:    {_fmt(total_expense)}\n"
        f"{emoji} Saldo:          *{_fmt(balance)}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 *Por categoria:*\n"
        f"{cat_lines}"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Digite *gráfico* para visualizar ou *exportar* para baixar o CSV."
    )


def history_message(transactions: list) -> str:
    if not transactions:
        return "📭 Nenhuma transação encontrada ainda.\n\nComece registrando um gasto ou receita!"

    lines = ""
    for t in transactions:
        icon = "📉" if t["type"] == "expense" else "📈"
        signal = "-" if t["type"] == "expense" else "+"
        lines += (
            f"{icon} {t['created_at']}\n"
            f"   {t['category']} — {_fmt(t['amount'])} ({signal})\n"
            f"   _{t['description']}_\n\n"
        )

    return (
        f"📜 *Últimas transações*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{lines.strip()}"
    )


def categories_message(categories: list, total_expense: float) -> str:
    if not categories:
        return "📭 Nenhum gasto registrado este mês."

    lines = ""
    for cat, total in sorted(categories, key=lambda x: x[1], reverse=True):
        pct = (total / total_expense * 100) if total_expense > 0 else 0
        bar_filled = int(pct / 10)
        bar = "🟦" * bar_filled + "⬜" * (10 - bar_filled)
        lines += f"*{cat}*\n{bar} {_fmt(total)} ({pct:.0f}%)\n\n"

    return (
        f"📊 *Gastos por categoria*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{lines.strip()}"
    )


def goal_set_message(goal: float) -> str:
    return (
        f"🎯 *Meta mensal definida!*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Limite de gastos: *{_fmt(goal)}*\n\n"
        f"Vou te avisar quando você se aproximar do limite! 💪"
    )


def goal_missing_amount() -> str:
    return (
        "❓ Qual será sua meta de gastos mensais?\n\n"
        "Ex: _meta 2000_ ou _meta 1500 reais_"
    )


def amount_missing(intent: str) -> str:
    if intent == "expense":
        return (
            "❓ Não entendi o valor do gasto. Tente assim:\n\n"
            "• _gastei 50 no lanche_\n"
            "• _uber 23_\n"
            "• _mercado 120,50_"
        )
    return (
        "❓ Não entendi o valor recebido. Tente assim:\n\n"
        "• _recebi 1500_\n"
        "• _salário 3000_\n"
        "• _freelance 500_"
    )


def unknown_message() -> str:
    return (
        "🤔 Não entendi sua mensagem.\n\n"
        "Tente algo como:\n"
        "• _gastei 30 no lanche_\n"
        "• _recebi 500_\n"
        "• _saldo_\n"
        "• _relatório_\n\n"
        "Digite *ajuda* para ver todos os comandos."
    )


def chart_unavailable() -> str:
    return (
        "📊 O gráfico foi gerado!\n"
        "Confira em: {url}\n\n"
        "_(Disponível por 1 hora)_"
    )


def export_ready(url: str) -> str:
    return (
        f"📥 *Relatório CSV pronto!*\n"
        f"Acesse: {url}\n\n"
        f"_(Link válido por 1 hora)_"
    )
