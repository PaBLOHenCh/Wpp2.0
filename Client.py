import socketio
import socket
import time

# Obtém o IP da máquina local automaticamente
def get_local_ip():
    try:

        return socket.gethostbyname(socket.gethostname())
    except:
        print("Houve uma falha na obtenção do endereço IP da sua máquina!")
        exit()

sio = socketio.Client()
meu_ip = get_local_ip()
mensagens_pendentes = {}

@sio.event
def connect():
    print(f"✅ Conectado ao servidor! Meu IP: {meu_ip}")
    verificar_novas_mensagens()  # Assim que conectar, busca mensagens pendentes

@sio.on("nova_mensagem")
def receber_mensagem(data):
    
    #Recebe mensagens do servidor e marca como "Lida" após exibir.
    print(f"\n📩 Nova mensagem de {data['origem']}: {data['texto']} (Status: {data['status']})")

    # Após receber, informa ao servidor que a mensagem foi lida
    marcar_como_lida(data)

@sio.on("status_mensagem")
def atualizar_status_mensagem(data):
    """
    Atualiza o status das mensagens enviadas.
    """
    print(f"📢 Status da mensagem para {data['destino']}: {data['status']}")
    

def verificar_novas_mensagens():

    #solicita ao servidor se há novas mensagens para este IP.
    sio.emit("verificar_mensagens", {"ip": meu_ip})

def enviar_mensagem(destinatario, mensagem):
    
    #envia uma mensagem para um IP específico e exibe status.
    msg_id = f"{meu_ip}-{int(time.time())}"
    mensagens_pendentes[msg_id] = (mensagem, destinatario)

    tentar_enviar_msg(destinatario, mensagem, msg_id)
    

def tentar_enviar_msg(destinatario, mensagem, msg_id, tentativas=0, max_tentativas=5):
    
    while tentativas <= max_tentativas:
        sio.emit("enviar_mensagem", {"origem": meu_ip, "destino": destinatario, "texto": mensagem, "id_msg": msg_id})
        time.sleep(3)
        if msg_id not in mensagens_pendentes:
            break
        print(f"❌ Falha ao enviar mensagem para {destinatario} após {tentativas} tentativas.")
        print("\nEnviando novamente\n")
    
    return

@sio.on("ack_recebido")
def confirmar_envio(data):
    del mensagens_pendentes[data["id_msg"]]
    print("📤 Mensagem enviada!")


def marcar_como_lida(msg):
    """
    Informa ao servidor que a mensagem de 'origem' foi lida.
    """
    sio.emit("mensagem_lida", msg)

sio.connect("http://192.168.0.125:5000")  # Substitua pelo IP do servidor

while True:
    opcao = input("\n1. Verificar mensagens\n2. Enviar mensagem\nEscolha: ")
    
    if opcao == "1":
        verificar_novas_mensagens()
    
    elif opcao == "2":
        destino = input("Digite o IP do destinatário: ")
        texto = input("Digite sua mensagem: ")
        enviar_mensagem(destino, texto, )
