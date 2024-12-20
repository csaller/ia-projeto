import os

from openai import OpenAI
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure sua API key aqui
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Você é um assistente de suporte técnico especializado no software ProjectMaster. "
        "Responda de forma clara, simples e educada, ajudando o usuário a resolver problemas "
        "ou entender funcionalidades do ProjectMaster. Não responda perguntas fora do contexto "
        "de suporte técnico ao ProjectMaster."
    )
}


@app.route('/')
def index():
    # Inicializa o histórico na sessão
    if 'chat_history' not in session:
        session['chat_history'] = [SYSTEM_PROMPT]
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    user_message = request.form['message']

    # Recupera o histórico da sessão
    chat_history = session.get('chat_history', [])

    # Opcional: Verifica se a mensagem do usuário está dentro do contexto
    if not is_in_context(user_message):
        response_text = "Desculpe, mas só posso ajudar com questões relacionadas ao software ProjectMaster."
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": response_text})
        session['chat_history'] = chat_history
        return jsonify({"answer": response_text})

    # Adiciona a mensagem do usuário ao histórico
    chat_history.append({"role": "user", "content": user_message})

    # Chama a API do OpenAI com todo o histórico
    response = client.chat.completions.create(model="gpt-4o-mini",
                                              messages=chat_history,
                                              temperature=0.7,
                                              max_tokens=300)

    # Extrai a resposta do modelo
    response_text = response.choices[0].message.content.strip()

    # Adiciona a resposta do modelo ao histórico
    chat_history.append({"role": "assistant", "content": response_text})
    # Atualiza a sessão
    session['chat_history'] = chat_history

    return jsonify({"answer": response_text})


def is_in_context(message: str) -> bool:
    # Verifica se o usuário menciona o produto "ProjectMaster" ou algo relacionado a suporte.
    # Caso não, retorna False. Isso é um critério simples, pode ser refinado com técnicas de NLP.
    keywords = ["projectmaster", "sistema", "erro", "bug", "instalação", "funcionalidade", "versão", "login", "atualização"]
    # Colocar tudo em minúsculas e checar se alguma keyword aparece
    msg_lower = message.lower()
    return any(k in msg_lower for k in keywords)


if __name__ == '__main__':
    app.run(debug=True)
