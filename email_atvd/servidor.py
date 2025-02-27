import socket
import json
import bcrypt
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Banco de dados temporário para usuários e mensagens
usuarios = {}  # {usuario: {"nome": "Nome Completo", "senha": senha_hash}}
mensagens = {}  # {destinatario: [{"remetente": remetente, "assunto": "Assunto", "conteudo": "Mensagem", "timestamp": data_hora}]}

def processar_cliente(cliente_socket):
    """Processa as requisições dos clientes conectados ao servidor."""
    try:
        while True:
            dados = cliente_socket.recv(1024).decode()
            if not dados:
                break

            requisicao = json.loads(dados)
            acao = requisicao.get("acao")

            if acao == "cadastrar":
                resposta = cadastrar_usuario(requisicao)
            elif acao == "autenticar":
                resposta = autenticar_usuario(requisicao)
            elif acao == "enviar_email":
                resposta = enviar_mensagem(requisicao)
            elif acao == "receber_emails":
                resposta = receber_mensagens(requisicao)
            else:
                resposta = {"status": "erro", "mensagem": "Ação inválida."}

            cliente_socket.send(json.dumps(resposta).encode())
    except Exception as e:
        print(f"Erro no processamento do cliente: {e}")
    finally:
        cliente_socket.close()

def cadastrar_usuario(dados):
    """Registra um novo usuário no sistema."""
    usuario = dados["usuario"]
    nome = dados["nome"]
    senha = dados["senha"].encode()

    if usuario in usuarios:
        return {"status": "erro", "mensagem": "Usuário já cadastrado."}

    senha_hash = bcrypt.hashpw(senha, bcrypt.gensalt())
    usuarios[usuario] = {"nome": nome, "senha": senha_hash}
    return {"status": "sucesso", "mensagem": "Cadastro realizado com sucesso."}

def autenticar_usuario(dados):
    """Autentica um usuário no sistema."""
    usuario = dados["usuario"]
    senha = dados["senha"].encode()

    conta = usuarios.get(usuario)
    if not conta or not bcrypt.checkpw(senha, conta["senha"]):
        return {"status": "erro", "mensagem": "Credenciais inválidas."}

    return {"status": "sucesso", "mensagem": f"Bem-vindo {conta['nome']}!", "nome": conta["nome"]}

def enviar_mensagem(dados):
    """
    Envia um e-mail para um usuário registrado.
    O timestamp é adicionado automaticamente no envio.
    """
    remetente = dados["de"]
    destinatario = dados["para"]
    assunto = dados["assunto"]
    conteudo = dados["conteudo"]
    
    if destinatario not in usuarios:
        return {"status": "erro", "mensagem": "Destinatário não encontrado."}
    
    if destinatario not in mensagens:
        mensagens[destinatario] = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    mensagens[destinatario].append({
        "remetente": remetente,
        "assunto": assunto,
        "conteudo": conteudo,
        "timestamp": timestamp
    })
    
    return {"status": "sucesso", "mensagem": "Mensagem enviada com sucesso."}

def receber_mensagens(dados):
    """Recupera todas as mensagens de um usuário."""
    usuario = dados["usuario"]
    caixa_mensagens = mensagens.pop(usuario, [])
    return {"status": "sucesso", "emails": caixa_mensagens}

def iniciar_servidor():
    """Inicia o servidor e aguarda conexões de clientes."""
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("0.0.0.0", 50000))
    servidor.listen(5)
    print("📡 Servidor ativo na porta 50000...")

    with ThreadPoolExecutor() as executor:
        while True:
            cliente_socket, _ = servidor.accept()
            executor.submit(processar_cliente, cliente_socket)

if __name__ == "__main__":
    iniciar_servidor()
