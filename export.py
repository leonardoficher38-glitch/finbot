import csv
import io
import os
import uuid
from datetime import datetime

EXPORT_DIR = os.path.join(os.path.dirname(__file__), "static", "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


def generate_csv(transactions: list, phone: str) -> str:
    """
    transactions: list of dicts com keys id, type, amount, category, description, created_at
    Retorna o nome do arquivo gerado.
    """
    filename = f"relatorio_{uuid.uuid4().hex[:8]}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["Data", "Tipo", "Categoria", "Valor", "Descrição"],
            delimiter=";",
        )
        writer.writeheader()
        for t in transactions:
            writer.writerow({
                "Data": t["created_at"],
                "Tipo": "Receita" if t["type"] == "income" else "Gasto",
                "Categoria": t["category"],
                "Valor": f"{t['amount']:.2f}".replace(".", ","),
                "Descrição": t["description"],
            })

    return filename
