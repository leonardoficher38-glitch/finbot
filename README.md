# 🤖 FinBot — Controle Financeiro pelo WhatsApp

Chatbot para WhatsApp que registra gastos, receitas e gera relatórios financeiros.
Construído com Python, Flask, Twilio e SQLite.

---

## 📁 Estrutura do Projeto

```
finbot/
├── app.py           # Flask app + webhook Twilio
├── database.py      # Configuração do SQLAlchemy
├── models.py        # Modelos Transaction e UserProfile
├── services.py      # Regras de negócio e queries
├── parser.py        # Interpretação de mensagens (regex + NLP)
├── responses.py     # Geração de respostas formatadas
├── chart.py         # Geração de gráficos (matplotlib)
├── export.py        # Exportação de CSV
├── requirements.txt
├── .env.example
└── static/
    ├── charts/      # Gráficos PNG gerados
    └── exports/     # Arquivos CSV gerados
```

---

## ⚡ Como rodar localmente

### 1. Clonar e criar ambiente virtual
```bash
git clone https://github.com/seu-usuario/finbot.git
cd finbot
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env com suas credenciais Twilio
```

### 4. Rodar o servidor
```bash
python app.py
```
Servidor rodando em `http://localhost:5000`

### 5. Expor localmente com ngrok
Para o Twilio conseguir chamar seu webhook local:
```bash
# Instale o ngrok: https://ngrok.com/download
ngrok http 5000
```
Copie a URL gerada (ex: `https://xxxx.ngrok-free.app`) e:
- Cole no `.env` como `BASE_URL`
- Configure como webhook no Twilio (veja abaixo)

---

## 📱 Conectar ao Twilio WhatsApp Sandbox

1. Acesse [console.twilio.com](https://console.twilio.com)
2. Vá em **Messaging → Try it out → Send a WhatsApp message**
3. Siga as instruções para entrar no Sandbox (enviar código via WhatsApp)
4. Em **Sandbox Settings**, configure:
   - **When a message comes in:** `https://sua-url.ngrok-free.app/webhook`
   - Método: **POST**
5. Salve.

Agora envie mensagens pelo WhatsApp para o número do Sandbox!

---

## 🤖 Comandos do Bot

| Comando / Frase | Ação |
|---|---|
| `ajuda` / `help` | Lista todos os comandos |
| `saldo` | Mostra saldo atual do mês |
| `relatório` / `resumo` | Relatório completo do mês |
| `histórico` / `extrato` | Últimas 10 transações |
| `categorias` | Gastos por categoria com barra visual |
| `gráfico` | Gera gráfico de pizza + barras |
| `exportar` / `csv` | Baixar relatório em CSV |
| `meta 2000` | Define meta de gastos mensais |
| `gastei 50 no lanche` | Registra gasto |
| `uber 23` | Registra gasto (categoria automática) |
| `mercado 120,50` | Registra gasto |
| `recebi 1500` | Registra receita |
| `salário 3000` | Registra receita |

---

## 🚀 Deploy no Render (produção gratuita)

### 1. Preparar o repositório
```bash
git init
git add .
git commit -m "initial commit"
# Crie um repo no GitHub e faça push
```

### 2. Criar serviço no Render
1. Acesse [render.com](https://render.com) e crie conta
2. **New → Web Service → Connect GitHub repo**
3. Configure:
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Em **Environment Variables**, adicione todas as variáveis do `.env`
5. Em `BASE_URL`, coloque a URL do Render: `https://seu-app.onrender.com`
6. Clique em **Create Web Service**

### 3. Atualizar webhook no Twilio
Substitua a URL do ngrok pela URL do Render nas configurações do Sandbox.

---

## 🔒 Variáveis de ambiente obrigatórias

| Variável | Descrição |
|---|---|
| `TWILIO_ACCOUNT_SID` | Account SID do Twilio |
| `TWILIO_AUTH_TOKEN` | Auth Token do Twilio |
| `BASE_URL` | URL pública do servidor |
| `DATABASE_URL` | URL do banco (SQLite local ou PostgreSQL) |
| `SECRET_KEY` | Chave secreta Flask |

---

## 🧪 Testar sem WhatsApp

Você pode testar o parser diretamente:
```bash
python -c "from parser import parse_message; print(parse_message('gastei 50 no lanche'))"
```

Ou simular o webhook com curl:
```bash
curl -X POST http://localhost:5000/webhook \
  -d "Body=gastei 50 no lanche" \
  -d "From=whatsapp:+5511999999999"
```

---

## 📄 Licença
MIT
