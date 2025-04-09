//MUDAR PARA O IP DO SERVIDOR QUE ESTA RODANDO
socket = io.connect("http://192.168.182.213:5000"); //IP do Servidor
var meu_ip;
var ip_destino;
var mensagens_pendentes = {}

// Obtém o IP público do usuário
async function get_public_ip(){
    try{
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return data.ip;
    } catch (error){
        console.error("Erro ao obter o IP público: ", error);
        return null;
    }
}

// Gera um IP aleatório
function get_random_ip() {
    return `${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}`;
}


// Função para conectar ao servidor
async function conectar_servidor(){
    //meu_ip = await get_public_ip();
    meu_ip = get_random_ip();

    if(!meu_ip) {
        console.error("Não foi possível obter o IP público. Conexão cancelada")
        return;
    }
    console.log("Meu IP:", meu_ip);
    alert("📡 Seu IP: " + meu_ip);

    do {
        ip_destino = prompt("Digite o IP do destinatário:");
        if (!ip_destino) {
            alert("⚠️ É obrigatório informar o IP do destinatário.");
        }
    } while (!ip_destino);
    console.log("📡 IP do destinatário:", ip_destino);

    if(socket.connected) {
        verificar_novas_mensagens();
    }

    socket.on('nova_mensagem', receber_mensagem);
    socket.on('status_mensagem', atualizar_status_mensagem);
    socket.on('ack_recebido', confirmar_envio);
}

function verificar_novas_mensagens(){
    // Solicita ao servidor se há novas mensagens para este IP
    socket.emit("verificar_mensagens", {"ip": meu_ip});
}

function enviar_mensagem(destinatario, mensagem){
    const msg_id = `${meu_ip}-${Date.now()}`;
    mensagens_pendentes[msg_id] = {mensagem, destinatario};

    tentar_enviar_msg(destinatario, mensagem, msg_id);
}

function tentar_enviar_msg(destinatario, mensagem, msg_id, tentativas=0, max_tentativas = 5){
    if (tentativas > max_tentativas){
        console.log(`❌ Falha ao enviar mensagem para ${destinatario} após ${max_tentativas} tentativas`);
        return; 
    }

    socket.emit("enviar_mensagem", {"origem": meu_ip, "destino":destinatario, "texto": mensagem, "id_msg": msg_id});

    // Verifica se a mensagem foi confirmada após 3 segundos
    setTimeout(() => {
        if (msg_id in mensagens_pendentes){
            tentar_enviar_msg(destinatario, mensagem, msg_id, tentativas+1, max_tentativas);
        }
    }, 3000);
}

function receber_mensagem(data){
    console.log(`📩 Nova mensagem de ${data.origem}: ${data.texto}`);
    console.log(`Status: ${data.status}`);
    adicionar_mensagem(data.texto, false, ip_destino);
    marcar_como_lida(data);
}

function atualizar_status_mensagem(data) {
    console.log(`📢 Status da mensagem para ${data.destino}: ${data.status}`);
}

function confirmar_envio(data){
    if (data.id_msg in mensagens_pendentes) {
        delete mensagens_pendentes[data.id_msg];
        console.log(`📤Mensagem enviada!`);
    }
}

function marcar_como_lida(msg) {
    socket.emit("mensagem_lida", msg);
}

function sendMessage() {
    let messageInput = document.getElementById("msg-input");
    let texto = messageInput.value;
    if (texto == "") return; 
    enviar_mensagem(ip_destino, texto);
    adicionar_mensagem(texto, true, ip_destino);
    messageInput.value = "";
}

conectar_servidor();
verificar_novas_mensagens();
// Verificar novas mensagens a cada segundo
setInterval(verificar_novas_mensagens, 1000);

// Função para adicionar mensagem ao chat do whatsApp
function adicionar_mensagem(mensagem, tipo_envio, destino){
    const messagesContainer = document.getElementById('messages-container');
    if(!messagesContainer) {
        console.error("Elemento messages-container não encontrado");
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `mensagem ${tipo_envio ? 'envio' : 'receber'}`;
    messageDiv.textContent = mensagem;

    // Hora que a mensagem foi enviada
    const timeSpan = document.createElement('span');
    const time = new Date();
    timeSpan.textContent = `${time.getHours()}:${time.getMinutes()}`
    timeSpan.className = `mensagem-time`;

    // Mostrar o IP na mensagem
    const ipSpan = document.createElement('span');
    ipSpan.className = `remetente`;
    ipSpan.textContent = tipo_envio ? "Você" : destino;


    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    messageDiv.appendChild(timeSpan);
    messageDiv.appendChild(ipSpan);

}
