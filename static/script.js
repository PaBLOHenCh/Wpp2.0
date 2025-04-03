var socket = io.connect("http://127.0.0.1:5000");

socket.on("nova_mensagem", function(data) {
    let chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p><strong>${data.origem}:</strong> ${data.texto}</p>`;
});

function sendMessage() {
    let messageInput = document.getElementById("message-input");
    let message = messageInput.value;
    
    socket.emit("enviar_mensagem", {
        origem: "Meu_PC",
        destino: "Outro_PC",
        texto: message,
        id_msg: new Date().getTime()
    });

    messageInput.value = "";
}
