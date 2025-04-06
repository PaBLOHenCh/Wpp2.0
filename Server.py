from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask import request  # Para pegar detalhes da requisição

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')
   
# Simulação de banco de dados: mensagens pendentes + status de entrega
mensagens_pendentes = {}

@socketio.on("enviar_mensagem")
def handle_enviar_mensagem(data):
    """
    Recebe uma mensagem e armazena caso o destinatário não esteja online.
    Adiciona status "Enviada".
    """

    required_fields = ['origem', 'destino', 'texto', 'id_msg']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Campo obrigatório faltando: {field}" )

    destino = data["destino"]
    origem = data["origem"]

    # Criando estrutura de mensagens pendentes para cada destinatário
    if destino not in mensagens_pendentes:
        mensagens_pendentes[destino] = []

    # Adiciona a mensagem ao "banco de dados" com status inicial
    mensagem = {
        "origem": data["origem"],
        "texto": data["texto"],
        "status": "Enviada",  # Status inicial
        "sids_origem": request.sid,
        "id_msg" : data["id_msg"],
        "destino" : data["destino"]
    }

    mensagens_pendentes[destino].append(mensagem)
    print(f"💬 Mensagem armazenada para {destino}: {mensagem}")

    #Emite um evento para o cliente que esse servidor recebeu a mensagem
    emit("ack_recebido", {"origem": origem, "destino": destino, "id_msg": data["id_msg"]})

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
    emit("status_mensagem", {"origem": data["origem"], "status": "Lida", "destino": data["destino"]}, room=request.sid)
    print(f"👀 Mensagem de {data['origem']} marcada como Lida.")

@socketio.on("ack_entregue")
def handle_ack_entregue(data):
    origem = data["origem"]
    destino = data["destino"]

    # Confirma que a mensagem foi entregue
    socketio.emit("ack_entregue", {"origem": origem, "destino": destino}, to=origem)

if __name__ == "__main__":
    from gevent import pywsgi
    server = pywsgi.WSGIServer(("0.0.0.0", 5000), app)
    print("🚀 Servidor rodando em http://192.168.1.16:5000") #IP do Servidor
    server.serve_forever()