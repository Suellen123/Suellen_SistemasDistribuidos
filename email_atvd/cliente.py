import socket
import json

HOST = 'suellanalves.ddns.net'
PORTA = 50000
usuario_logado = None
servidor_configurado = False

def apontar_servidor():
    """Configura o endereço e porta do servidor, testando a conexão."""
    global HOST, PORTA, servidor_configurado
    novo_host = input(f"Digite o IP do servidor (atual: {HOST}): ").strip() or HOST
    nova_porta_str = input(f"Digite a porta do servidor (atual: {PORTA}): ").strip()
    try:
        nova_porta = int(nova_porta_str) if nova_porta_str else PORTA
    except ValueError:
        print("Porta inválida!")
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as teste:
            teste.settimeout(2)
            teste.connect((novo_host, nova_porta))
        HOST = novo_host
        PORTA = nova_porta
        servidor_configurado = True
        print("Serviço Disponível!")
    except Exception:
        print("Falha ao conectar. Verifique o IP e a porta.")

def enviar_requisicao(dados):
    """Envia uma requisição ao servidor e retorna a resposta."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cliente:
        cliente.connect((HOST, PORTA))
        cliente.send(json.dumps(dados).encode())
        resposta = json.loads(cliente.recv(1024).decode())
    return resposta

def cadastrar_usuario():
    """Permite que o usuário crie uma conta no sistema."""
    nome = input("Nome completo: ")
    usuario = input("Nome de usuário: ")
    senha = input("Senha: ")

    resposta = enviar_requisicao({
        "acao": "cadastrar",
        "nome": nome,
        "usuario": usuario,
        "senha": senha
    })
    print(resposta["mensagem"])

def autenticar_usuario():
    """Realiza o login do usuário."""
    global usuario_logado
    usuario = input("Nome de usuário: ")
    senha = input("Senha: ")

    resposta = enviar_requisicao({
        "acao": "autenticar",
        "usuario": usuario,
        "senha": senha
    })
    
    if resposta["status"] == "sucesso":
        usuario_logado = usuario
        print(f"\n✅ Bem-vindo, {resposta['nome']}!")
        menu_principal()
    else:
        print(resposta["mensagem"])

def enviar_mensagem():
    """Permite ao usuário enviar um e-mail para outro usuário."""
    if not usuario_logado:
        print("⚠️ Você precisa estar logado para enviar mensagens.")
        return

    destinatario = input("Para: ")
    assunto = input("Assunto: ")
    conteudo = input("Mensagem: ")

    resposta = enviar_requisicao({
        "acao": "enviar_email",
        "de": usuario_logado,
        "para": destinatario,
        "assunto": assunto,
        "conteudo": conteudo
    })
    print(resposta["mensagem"])

def receber_mensagens():
    """Obtém e exibe os e-mails do usuário logado."""
    if not usuario_logado:
        print("⚠️ Você precisa estar logado para visualizar mensagens.")
        return

    resposta = enviar_requisicao({
        "acao": "receber_emails",
        "usuario": usuario_logado
    })

    emails = resposta.get("emails", [])
    if emails:
        print(f"\n📩 {len(emails)} mensagens encontradas:")
        for i, email in enumerate(emails, 1):
            print(f"[{i}] {email['timestamp']} - {email['remetente']}: {email['assunto']}")
        
        while True:
            escolha = input("\nSelecione um e-mail para leitura (ou pressione Enter para voltar): ")
            if not escolha:
                return
            if escolha.isdigit():
                escolha = int(escolha) - 1
                if 0 <= escolha < len(emails):
                    email = emails[escolha]
                    print(f"\n📬 De: {email['remetente']}\n📅 Data: {email['timestamp']}\n📜 Assunto: {email['assunto']}\n✉️ Mensagem: {email['conteudo']}")
                    break
                else:
                    print("⚠️ Número inválido. Escolha um e-mail da lista.")
            else:
                print("⚠️ Entrada inválida. Digite um número.")
    else:
        print("📭 Nenhuma nova mensagem.")

def menu_principal():
    """Exibe o menu principal após o login."""
    while True:
        print("\n1️⃣ Escrever Mensagem\n2️⃣ Caixa de Entrada\n3️⃣ Logout")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            enviar_mensagem()
        elif opcao == "2":
            receber_mensagens()
        elif opcao == "3":
            print("👋 Logout efetuado.")
            break
        else:
            print("⚠️ Opção inválida.")

if __name__ == "__main__":
    while True:
        print("\nCliente E-mail Service BSI Online")
        print("1️⃣ Apontar Servidor")
        print("2️⃣ Cadastrar Conta")
        print("3️⃣ Acessar E-mail")
        print("4️⃣ Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            apontar_servidor()
        elif opcao == "2":
            if servidor_configurado:
                cadastrar_usuario()
            else:
                print("⚠️ Servidor não configurado! Aponte o servidor primeiro.")
        elif opcao == "3":
            if servidor_configurado:
                autenticar_usuario()
            else:
                print("⚠️ Servidor não configurado! Aponte o servidor primeiro.")
        elif opcao == "4":
            print("🚪 Encerrando...")
            break
        else:
            print("⚠️ Opção inválida.")
