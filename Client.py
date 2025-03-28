import socketio
import socket

# Obtém o IP da máquina local automaticamente
def get_local_ip():
    return socket.gethostbyname(socket.gethostname())

sio = socketio.Client()
meu_ip = get_local_ip()

@sio.event
def connect():
    print(f"✅ Conectado ao servidor! Meu IP: {meu_ip}")
    verificar_novas_mensagens()  # Assim que conectar, busca mensagens pendentes

@sio.on("nova_mensagem")
def receber_mensagem(data):
    """
    Recebe mensagens do servidor e marca como "Lida" após exibir.
    """
    print(f"\n📩 Nova mensagem de {data['origem']}: {data['texto']} (Status: {data['status']})")

    # Após receber, informa ao servidor que a mensagem foi lida
    marcar_como_lida(data["origem"])

@sio.on("status_mensagem")
def atualizar_status_mensagem(data):
    """
    Atualiza o status das mensagens enviadas.
    """
    print(f"📢 Status da mensagem para {data['destino']}: {data['status']}")

def verificar_novas_mensagens():
    """
    Solicita ao servidor se há novas mensagens para este IP.
    """
    sio.emit("verificar_mensagens", {"ip": meu_ip})

def enviar_mensagem(destinatario, mensagem):
    """
    Envia uma mensagem para um IP específico e exibe status.
    """
    sio.emit("enviar_mensagem", {"origem": meu_ip, "destino": destinatario, "texto": mensagem})
    print("📤 Mensagem enviada!")

def marcar_como_lida(origem):
    """
    Informa ao servidor que a mensagem de 'origem' foi lida.
    """
    sio.emit("mensagem_lida", {"origem": origem})

sio.connect("http://IP_DO_SERVIDOR:5000")  # Substitua pelo IP do servidor

while True:
    opcao = input("\n1. Verificar mensagens\n2. Enviar mensagem\nEscolha: ")
    
    if opcao == "1":
        verificar_novas_mensagens()
    
    elif opcao == "2":
        destino = input("Digite o IP do destinatário: ")
        texto = input("Digite sua mensagem: ")
        enviar_mensagem(destino, texto)
