const socket = io();

document.addEventListener('DOMContentLoaded', function() {
    fetch('/get_messages')
        .then(response => response.json())
        .then(messages => {
            const chatBox = document.getElementById('chat-box');
            messages.forEach(msg => {
                const div = document.createElement('div');
                div.className = 'message';
                if (msg.message) {
                    div.innerHTML = `<span class="timestamp">${msg.timestamp}</span> <span class="username">${msg.username}:</span> ${msg.message}`;
                } else if (msg.file_url) {
                    div.innerHTML = `<span class="timestamp">${msg.timestamp}</span> <span class="username">${msg.username}:</span> <a href="${msg.file_url}" target="_blank">File</a>`;
                }
                chatBox.appendChild(div);
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        });

    document.getElementById('message-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    document.getElementById('send-button').addEventListener('click', sendMessage);

    document.getElementById('upload-button').addEventListener('click', function(event) {
        event.preventDefault();
        const fileInput = document.getElementById('file-input');
        const file = fileInput.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);
            fetch('/files/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                if (result.file_url) {
                    socket.send(JSON.stringify({
                        file_url: result.file_url
                    }));
                } else {
                    alert('File upload failed');
                }
            });
        }
    });

    socket.on('message', function(msg) {
        const chatBox = document.getElementById('chat-box');
        const div = document.createElement('div');
        div.className = 'message';
        if (msg.message) {
            div.innerHTML = `<span class="timestamp">${msg.timestamp}</span> <span class="username">${msg.username}:</span> ${msg.message}`;
        } else if (msg.file_url) {
            div.innerHTML = `<span class="timestamp">${msg.timestamp}</span> <span class="username">${msg.username}:</span> <a href="${msg.file_url}" target="_blank">File</a>`;
        }
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    function sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value;
        if (message.trim() !== '') {
            socket.send(message);
            input.value = '';
        }
    }
});
