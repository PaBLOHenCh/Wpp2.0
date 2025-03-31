from flask import Flask
from flask_socketio import SocketIO, emit
from flask import request  # Para pegar detalhes da requisição

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Simulação de banco de dados: mensagens pendentes + status de entrega
mensagens_pendentes = {}

@socketio.on("enviar_mensagem")
def handle_enviar_mensagem(data):
    """
    Recebe uma mensagem e armazena caso o destinatário não esteja online.
    Adiciona status "Enviada".
    """
    destino = data["destino"]

    # Criando estrutura de mensagens pendentes para cada destinatário
    if destino not in mensagens_pendentes:
        mensagens_pendentes[destino] = []

    # Adiciona a mensagem ao "banco de dados" com status inicial
    mensagem = {
        "origem": data["origem"],
        "texto": data["texto"],
        "status": "Enviada",  # Status inicial
        "sids_origem": request.sid 
    }

    mensagens_pendentes[destino].append(mensagem)
    print(f"💬 Mensagem armazenada para {destino}: {mensagem}")

    # Informa ao remetente que a mensagem foi enviada
    emit("status_mensagem", {"destino": destino, "status": "Enviada"}, room=request.sid)

@socketio.on("verificar_mensagens")
def handle_verificar_mensagens(data):
    """
    Retorna mensagens pendentes para o IP do cliente e altera status para "Entregue".
    """
    ip_cliente = data["ip"]

    #Verifica se o ip do cliente está em msg_pendentes
    # E se a lista na chave ip_cliente não é vazia(tipo falsy do python) 
    if ip_cliente in mensagens_pendentes and mensagens_pendentes[ip_cliente]:
        for msg in mensagens_pendentes[ip_cliente]:
            msg["status"] = "Entregue"  # Atualiza status

            # Envia cada mensagem pendente para o cliente destinatário
            # romm é basicamente a variável que define para quem será enviado
            # request.sid é o id do socket que fez a requisição
            #melhoria: esperar uma resposta do cliente, para que o status não se perca
            emit("nova_mensagem", msg, room=request.sid)

        # Limpa mensagens do armazenamento depois de entregues
        mensagens_pendentes[ip_cliente] = []

@socketio.on("mensagem_lida")
def handle_mensagem_lida(data):
    """
    Marca uma mensagem como "Lida".
    """
    emit("status_mensagem", {"origem": data["origem"], "status": "Lida"}, room=request.sid)
    print(f"👀 Mensagem de {data['origem']} marcada como Lida.")
