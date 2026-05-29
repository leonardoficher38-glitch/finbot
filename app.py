import os
import logging
from datetime import datetime

from flask import Flask, request, send_from_directory, url_for
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from database import init_db
import models  # noqa: F401 — garante que os modelos sejam registrados
import services as svc
import responses as res
from parser import parse_message
from chart import generate_expense_chart, CHART_DIR
from export import generate_csv, EXPORT_DIR

# ---------------------------------------------------------------------------
load_dotenv()
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///finbot.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

init_db(app)

BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

MONTH_NAMES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


def current_month_name() -> str:
    now = datetime.utcnow()
    return f"{MONTH_NAMES[now.month]} {now.year}"


# ---------------------------------------------------------------------------
# Rota de arquivos estáticos (gráficos e CSV)
# ---------------------------------------------------------------------------

@app.route("/static/charts/<filename>")
def serve_chart(filename):
    return send_from_directory(CHART_DIR, filename)


@app.route("/static/exports/<filename>")
def serve_export(filename):
    return send_from_directory(
        EXPORT_DIR, filename,
        as_attachment=True,
        download_name=filename,
    )


# ---------------------------------------------------------------------------
# Webhook principal do Twilio
# ---------------------------------------------------------------------------

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming = request.form.get("Body", "").strip()
    phone = request.form.get("From", "unknown")

    logger.info("MSG DE %s: %s", phone, incoming)

    reply = handle_message(phone, incoming)

    logger.info("RESPOSTA: %s", reply[:80])

    twiml = MessagingResponse()
    twiml.message(reply)
    return str(twiml), 200, {"Content-Type": "text/xml"}


# ---------------------------------------------------------------------------
# Roteador de intenções
# ---------------------------------------------------------------------------

def handle_message(phone: str, text: str) -> str:
    parsed = parse_message(text)
    intent = parsed["intent"]
    amount = parsed["amount"]
    category = parsed["category"]
    description = parsed["description"]

    # --- Ajuda ---
    if intent == "help":
        return res.help_message()

    # --- Gasto ---
    if intent == "expense":
        if amount is None or amount <= 0:
            return res.amount_missing("expense")
        svc.add_transaction(phone, "expense", amount, category, description)
        totals = svc.get_monthly_totals(phone)
        profile = svc.get_or_create_profile(phone)
        return res.expense_registered(
            amount, category, description,
            balance=totals["balance"],
            goal=profile.monthly_goal,
            total_expense=totals["expense"],
        )

    # --- Receita ---
    if intent == "income":
        if amount is None or amount <= 0:
            return res.amount_missing("income")
        svc.add_transaction(phone, "income", amount, category, description)
        totals = svc.get_monthly_totals(phone)
        return res.income_registered(amount, category, description, totals["balance"])

    # --- Saldo ---
    if intent == "balance":
        totals = svc.get_monthly_totals(phone)
        profile = svc.get_or_create_profile(phone)
        return res.balance_message(
            totals["balance"], totals["income"], totals["expense"],
            profile.monthly_goal,
        )

    # --- Relatório ---
    if intent == "report":
        totals = svc.get_monthly_totals(phone)
        categories = svc.get_categories(phone)
        return res.report_message(
            totals["income"], totals["expense"], totals["balance"],
            categories, current_month_name(),
        )

    # --- Histórico ---
    if intent == "history":
        transactions = svc.get_recent_transactions(phone, limit=10)
        return res.history_message(transactions)

    # --- Categorias ---
    if intent == "categories":
        categories = svc.get_categories(phone)
        totals = svc.get_monthly_totals(phone)
        return res.categories_message(categories, totals["expense"])

    # --- Meta ---
    if intent == "goal":
        if amount is None or amount <= 0:
            return res.goal_missing_amount()
        svc.set_monthly_goal(phone, amount)
        return res.goal_set_message(amount)

    # --- Gráfico ---
    if intent == "chart":
        categories = svc.get_categories(phone)
        if not categories:
            return "📭 Nenhum gasto registrado este mês para gerar o gráfico."
        filename = generate_expense_chart(categories, phone, current_month_name())
        if not filename:
            return "❌ Não foi possível gerar o gráfico."
        url = f"{BASE_URL}/static/charts/{filename}"
        return (
            f"📊 *Gráfico de gastos — {current_month_name()}*\n\n"
            f"🔗 Acesse: {url}\n\n"
            f"_(Link disponível por 1 hora)_"
        )

    # --- Exportar CSV ---
    if intent == "export":
        transactions = svc.get_all_transactions(phone)
        if not transactions:
            return "📭 Nenhuma transação encontrada para exportar."
        filename = generate_csv(transactions, phone)
        url = f"{BASE_URL}/static/exports/{filename}"
        return res.export_ready(url)

    # --- Desconhecido ---
    return res.unknown_message()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def health():
    return {"status": "ok", "service": "FinBot", "time": datetime.utcnow().isoformat()}, 200


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
