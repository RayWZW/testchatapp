<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THUG-CHAT</title>
   <style>
body {
    background-color: #36393e;
    color: #e0e0e0;
    font-family: Arial, sans-serif;
    margin: 0;
    overflow: hidden;
    display: flex;
    height: 100vh;
    flex-direction: row;
}

.open-commands-button {
    background-color: #42464d; /* Dark button background */
    color: #ffffff; /* Button text color */
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    position: absolute;
    top: 10px;
    right: 10px;
    z-index: 1000;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4);
    transition: background-color 0.3s, transform 0.2s;
}

.open-commands-button:hover {
    background-color: #4f545c; /* Lighter on hover */
    transform: scale(1.05);
}

.userbutton {
    background-color: #2f3136; /* Dark background for user buttons */
    color: #dcddde; /* Light gray text */
    border: 1px solid #3f4146; /* Darker border */
    padding: 12px;
    border-radius: 4px; /* Rounded corners */
    cursor: pointer;
    width: 100%;
    text-align: left;
    margin: 5px 0; /* Margin between buttons */
    box-shadow: none;
    transition: background-color 0.3s;
}

.userbutton:hover {
    background-color: #4f545c; /* Hover effect */
}

.userbutton:active {
    background-color: #42464d; /* Darker when active */
}

#sidebar {
    width: 200px; /* Increased width for better spacing */
    background-color: #2c2f33; /* Sidebar background */
    padding: 10px;
    overflow-y: auto;
    height: 100%;
    border-right: 1px solid #40444b; /* Border for separation */
    transition: width 0.3s;
}

#sidebar::-webkit-scrollbar {
    width: 10px; /* Scrollbar width */
}

#sidebar::-webkit-scrollbar-thumb {
    background-color: #444; /* Scrollbar thumb color */
    border-radius: 5px;
}

#sidebar::-webkit-scrollbar-thumb:hover {
    background-color: #666; /* Darker on hover */
}

#sidebar::-webkit-scrollbar-track {
    background: #2c2f33; /* Scrollbar track color */
    border-radius: 5px;
}

#chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    margin-left: 50px; /* Adjust as necessary */
    transition: margin-left 0.3s;
}

#chat-box {
    flex: 1;
    overflow-y: auto; 
    padding: 10px;
    padding-left: 15px;
    border-bottom: 1px solid #333;
    word-wrap: break-word;
    white-space: pre-wrap;
}

#chat-box::-webkit-scrollbar {
    width: 16px; /* Scrollbar width */
}

#chat-box::-webkit-scrollbar-track {
    background: #2C2F33; /* Track color */
    border-radius: 0; 
}

#chat-box::-webkit-scrollbar-thumb {
    background-color: #333333; /* Thumb color */
    border-radius: 0; 
    border: 4px solid transparent; 
}

#chat-box::-webkit-scrollbar-thumb:hover {
    background-color: #5b6eae; /* Thumb hover color */
}

.textarea-container {
    position: relative;
    padding-left: 50px; /* Space for icons or buttons */
}


#message-form {
    display: flex;
    background-color: #2f3136; /* Darker background for the message form */
    padding: 10px;
    border-top: 1px solid #40444b; /* Lighter border for visibility */
    flex-wrap: wrap;
}

#message-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #555; /* Darker border */
    background-color: #40444b; /* Dark input background */
    color: #dcddde; /* Lighter text color */
    min-width: 0;
    resize: none;
    line-height: 1.5em;
    white-space: pre-wrap;
    overflow-wrap: break-word;
    box-sizing: border-box;
    font-family: inherit;
    word-break: break-word;
    padding-bottom: 30px; 
}

#char-count {
    position: absolute;
    left: -40px; /* Move to the left side */
    bottom: 50px; /* Adjust this value to set its height */
    color: #aaa; /* Lighter gray for visibility */
    font-size: 0.8em;
    pointer-events: none; 
}


button {
    margin-top: 10px; 
}

.profile-picture {
    width: 40px; /* Set your desired size */
    height: 40px;
    border-radius: 50%; /* Makes the image circular */
    object-fit: cover; /* Ensures the image covers the area without distortion */
}


.container {
    display: flex; /* Use flexbox to align buttons horizontally */
    align-items: flex-end; /* Align buttons to the bottom of the container */
    height: 100%; /* Ensure the container takes the full height */
}

#send-button, #upload-button {
    display: flex; /* Use flexbox for centering */
    align-items: center; /* Center text vertically */
    justify-content: center; /* Center text horizontally */
    height: 100px; /* Set height to 100px */
    padding: 0 20px; /* Adjust padding for horizontal spacing */
    border: none;
    color: #ffffff; /* White text color for better contrast */
    cursor: pointer;
    margin-left: 10px; /* Space between buttons */
    flex-shrink: 0;
    transition: background-color 0.3s, box-shadow 0.3s, transform 0.2s;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    border-radius: 0; /* Straight edges */
    font-size: 14px; /* Consistent font size */
}

#send-button, #upload-button {
    background-color: #4a90e2; /* Softer blue for send/upload buttons */
}

#send-button:hover, #upload-button:hover {
    background-color: #3a80c3; /* Darker blue on hover */
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

#send-button:active, #upload-button:active {
    background-color: #2f65a0; /* Even darker blue when active */
    transform: translateY(2px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

#logout-button {
    display: flex; /* Use flexbox for centering */
    align-items: center; /* Center text vertically */
    justify-content: center; /* Center text horizontally */
    height: 100px; /* Set height to 100px */
    padding: 0 20px; /* Adjust padding for horizontal spacing */
    border: none;
    background-color: #d9534f; /* Bright red background for visibility */
    color: #ffffff; /* White text color for better contrast */
    cursor: pointer;
    margin-left: 10px; /* Space between buttons */
    margin-top: 10px; /* Lower it by 10px */
    flex-shrink: 0;
    transition: background-color 0.3s, box-shadow 0.3s, transform 0.2s;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    border-radius: 0; /* Straight edges */
    font-size: 14px; /* Consistent font size */
    text-decoration: none; /* Remove underline */
    font-weight: bold; /* Make text bold */
    text-transform: uppercase; /* Convert text to uppercase */
}

#logout-button:hover {
    background-color: #c9302c; /* Darker red on hover */
}

#logout-button:active {
    background-color: #a52c2c; /* Even darker red when active */
    transform: translateY(2px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}



.link {
    color: lightblue;
    font-weight: bold;
    white-space: nowrap;
    text-decoration: none;
}

.link:hover {
    text-decoration: underline;
}

.message {
    margin-bottom: 2px;
    padding: 2px 0;
    word-wrap: break-word;
    white-space: pre-wrap;
}

.typing-indicator {
    color: #999;
    font-style: italic;
}

.progress {
    width: 100%;
    background-color: #333;
}

.progress-bar {
    width: 0;
    height: 5px;
    background-color: #ec0a0a;
}

.download-button {
    display: inline-block;
    padding: 8px 16px;
    margin: 8px 0;
    color: #e0e0e0;
    background-color: #444;
    border: none;
    cursor: pointer;
    text-decoration: none;
}

.download-button:hover {
    background-color: #555;
}

#sidebar ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

#sidebar li {
    padding: 5px 0;
    color: #e0e0e0;
    cursor: pointer;
}

#sidebar li:hover {
    background-color: #333;
}


#warning-message {
    color: #8e16f7;
    text-align: center;
    margin: 10px;
    display: none;
}

.timestamp {
    font-size: 10px;
    color: #999;
    float: right;
    margin-left: 10px;
}

#button-container {
    position: relative; /* Position context for absolute children */
}

#reload-button {
    position: absolute; /* Use absolute positioning */
    background-color: #42464d; /* Dark button background */
    border: none; /* No border */
    width: 120px; /* Set width */
    height: 50px; /* Set height */
    color: #ffffff; /* Button text color */
    cursor: pointer; /* Cursor style */
    z-index: 1000; /* Stack order */
    transition: background-color 0.3s, transform 0.2s; /* Transition effects */
    font-size: 14px; /* Font size */
    display: flex; /* Use flexbox for alignment */
    align-items: center; /* Vertical alignment */
    justify-content: center; /* Horizontal alignment */
    top: 5px; /* Set y-coordinate */
    right: 420px; /* Set x-coordinate */
    text-transform: uppercase; /* Uppercase text */
    font-weight: bold; /* Bold text */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4); /* Box shadow */
    border-radius: 0; /* No border-radius for a rectangular shape */
}

#reload-button:hover {
    background-color: #4f545c; /* Lighter on hover */
    transform: scale(1.05); /* Slightly scale on hover */
}

#reload-button:active {
    background-color: #3a3a3a; /* Darker on active */
    transform: scale(0.98); /* Slightly scale down on active */
}



#adminButton {
    position: absolute; /* Use absolute positioning */
    background-color: #42464d; /* Dark button background */
    color: #ffffff; /* Button text color */
    border: none;
    width: 150px; /* Set width to 50px for a square button */
    height: 50px; /* Set height to 50px for a square button */
    cursor: pointer;
    z-index: 1000;
    padding: 10px 15px; /* Adjusted padding for visual balance */
    border-radius: 4px; /* Subtle rounded corners */
    display: flex;
    align-items: center;
    justify-content: center;
    top: 5px; /* Set y-coordinate */
    right: 230px; /* Set x-coordinate */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4); /* Updated box shadow */
    transition: background-color 0.3s, transform 0.2s; /* Smooth transitions */
}

#adminButton:hover {
    background-color: #51565e; /* Slightly lighter background on hover */
    transform: scale(1.05); /* Scale effect on hover */
}

#adminButton:active {
    background-color: #3a3a3a; /* Darker background on active */
    transform: scale(0.98); /* Slight scale effect on active */
}



#adminButton:hover {
    background-color: #444;
    transform: scale(1.05);
}

#adminButton:active {
    background-color: #3a3a3a;
    transform: scale(0.98);
}


@media (max-width: 768px) {
    body {
        flex-direction: column;
        height: auto; 
        overflow: auto; 
    }

    #sidebar {
        width: 100%;
        height: auto;
        border-right: none;
        border-bottom: 1px solid #333333;
        padding: 5px;
    }

    #chat-container {
        margin-left: 0;
        margin-top: 10px;
        flex: 1;
        height: calc(100vh - 150px); 
        display: flex;
        flex-direction: column;
    }

    #chat-box {
        flex: 1;
        padding: 10px;
        padding-left: 15px;
        border-bottom: 1px solid #333;
        overflow-y: auto; 
    }

    #message-form {
        flex-direction: row; 
    }

    #message-input {
        flex: 1;
        margin-bottom: 0; 
    }

    #send-button, #upload-button {
        flex-shrink: 0; 
        margin-left: 10px; 
    }

    .custom-alert {
        display: none; 
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.6);
        z-index: 1000;
        justify-content: center;
        align-items: center;
    }

    .alert-content {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        width: 300px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    .alert-content span {
        display: block;
        margin-bottom: 15px;
        font-size: 16px;
        color: #333;
    }

    .close-button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 15px;
        cursor: pointer;
        font-size: 14px;
    }

    .close-button:hover {
        background-color: #0056b3;
    }

    #edit-account-button, #reload-button {
        width: 100%; 
    }

    #adminButton {
        width: 100%; 
        margin-bottom: 10px; 
    }
}

#header {
    background-color: #36393e; /* Discord dark mode background color */
    padding: 10px 20px; /* Add horizontal padding for spacing */
    border-radius: 4px; /* Rounded corners */
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.5); /* Subtle shadow */
    color: #ffffff; /* White text color */
    text-align: center; /* Center the text */
    position: absolute; /* Positioning */
    top: 10px; /* Distance from the top */
    left: 50%; /* Centering */
    transform: translateX(-50%); /* Offset the center */
    font-size: 18px; /* Font size */
    width: auto; /* Width based on content */
    min-width: 200px; /* Minimum width for better appearance */
    z-index: 1000; /* Keeps it above other elements */
    border: 1px solid rgba(255, 255, 255, 0.1); /* Subtle border for distinction */
    font-weight: bold; /* Make text bold */
    text-transform: uppercase; /* Make text uppercase */
}


</style>

</head>
<body>
    <button class="open-commands-button" onclick="window.open('/commands', '_blank')">Open Commands Console</button>
    <div id="sidebar">        
        <h3>TRUE THUGS</h3>
        <ul id="user-list"></ul>
        </div>

        <div id="customAlert" style="display:none; position:fixed; top:20%; left:50%; transform:translate(-50%, -50%); background-color:rgba(0,0,0,0.8); color:white; padding:20px; border-radius:5px;">
            <span id="alertMessage"></span>
            <button id="alertCloseButton" style="margin-left:10px;">Close</button>
        </div>
        <div id="header" style="background-color: #1c1c1c; padding: 10px; border-radius: 4px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.4); color: #ffffff; text-align: center; position: absolute; top: 10px; left: 50%; transform: translateX(-50%);">
            LOGGED IN AS <span id="username-placeholder">{{ username }}</span>
        </div>
        
 <button id="adminButton" class="open-commands-button">ADMIN PANEL</button>

    </div>
    <button id="reload-button" class="open-commands-button">Reload</button>
        <div id="chat-container">

        <div id="chat-box">
            <!-- Messages will be loaded here -->
        </div>
        <div class="typing-indicator" id="typing-indicator"></div>
        <div id="warning-message"></div>
        <form id="message-form" style="position: relative;">
            <textarea id="message-input" placeholder="Type your message..." autofocus></textarea>
            <script>
                document.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter') {
                        document.getElementById('message-input').focus();
                    }
                });
            </script>
                        <span id="char-count" style="position: absolute; right: 10px; bottom: 10px; color: #aaa; font-size: 0.8em;">0</span>
            <button id="send-button" type="button">>>>></button>
            <button id="upload-button" type="button">Upload File</button>
            <a id="logout-button" href="/logout">Logout</a>
        </form>

        <input id="file-input" type="file" style="display: none;">
        <div class="progress">
            <div class="progress-bar" id="progress-bar"></div>
        </div>
    </div>
    <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        const socket = io();
        const notifySound = new Audio('static/notify.mp3');
        notifySound.preload = 'auto';

        document.addEventListener('DOMContentLoaded', function() {
            const chatBox = document.getElementById('chat-box');
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');

document.getElementById('adminButton').addEventListener('click', function() {
    window.open('/admin', '_blank'); 
});

sendButton.addEventListener('click', () => {
    let messageText = messageInput.value.trim();
    messageText = messageText.replace(/\n{2,}/g, '\n'); 

    sendMessage(messageText);
});
            const fileInput = document.getElementById('file-input');
            const progressBar = document.getElementById('progress-bar');
            const userList = document.getElementById('user-list');
            const sidebar = document.getElementById('sidebar');
            const chatContainer = document.getElementById('chat-container');
            const toggleSidebar = document.getElementById('toggle-sidebar');
            const typingIndicator = document.getElementById('typing-indicator');
            const warningMessage = document.getElementById('warning-message');
            const charCount = document.getElementById('char-count');
            const maxChars = 10000;

            messageInput.addEventListener('input', function() {
        if (messageInput.value.length > maxChars) {
            messageInput.value = messageInput.value.substring(0, maxChars); 
        }
        const count = messageInput.value.length;
        charCount.textContent = count; 
    });

        const reloadButton = document.getElementById('reload-button');
        reloadButton.addEventListener('click', function() {
            location.reload(); 
        });            

        socket.on('ban_packet', function(data) {
    alert('You have been banned from the chat: ' + data.username);

    fetch('/logout', {
        method: 'POST', 
        credentials: 'include' 
    })
    .then(response => {
        if (response.ok) {
            window.location.reload(); 
        } else {
            console.error('Failed to log out.');
        }
    })
    .catch(error => {
        console.error('Error during logout:', error);
    });
});

            initializeUserList();
            initializeChat();

            function initializeUserList() {
    // Preload the audio file
    const hoverSound = new Audio('static/enter-cmd.ogg');

    fetch('/get_user_accounts')
        .then(response => response.json())
        .then(users => {
            users.forEach(user => {
                const li = document.createElement('li');
                const button = document.createElement('button');
                button.textContent = user;
                button.classList.add('userbutton');

                button.addEventListener('click', () => {
                    window.open(`/userinfo-${user}`, '_blank');
                });

                // Add hover event listener to play sound
                button.addEventListener('mouseenter', () => {
                    hoverSound.currentTime = 0; // Reset the audio to the beginning
                    hoverSound.play(); // Play the sound
                });

                li.appendChild(button);
                userList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error fetching user accounts:', error);
        }); // Add error handling for the fetch call
}


            function initializeChat() {
    fetch('/get_messages')
        .then(response => response.json())
        .then(messages => {
            messages.forEach(msg => {
                chatBox.appendChild(createMessageElement(msg));
            });
            chatBox.scrollTop = chatBox.scrollHeight;
        });

    socket.on('message', function(msg) {
        const messageId = msg.timestamp; // Assuming timestamp is unique for each message
        if (!Array.from(chatBox.children).some(child => child.dataset.timestamp === messageId)) {
            chatBox.appendChild(createMessageElement(msg));
            chatBox.scrollTop = chatBox.scrollHeight;

            const videos = document.querySelectorAll('video');
            let isPlaying = false;

            videos.forEach(video => {
                if (!video.paused) {
                    isPlaying = true;
                }
            });

            if (!isPlaying) {
                notifySound.play().catch(error => {
                    console.error('Error playing sound:', error);
                });
            }
        }

        setTimeout(() => {
            if (msg.type === 'file') {
                window.scrollTo(0, document.body.scrollHeight);
            } else {
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        }, 1000);
    });

    


    function fetchMessages() {
        fetch('/get_messages')
            .then(response => response.json())
            .then(messages => {
                messages.forEach(msg => {
                    const messageId = msg.timestamp; // Assuming timestamp is unique for each message
                    if (!Array.from(chatBox.children).some(child => child.dataset.timestamp === messageId)) {
                        chatBox.appendChild(createMessageElement(msg));
                    }
                });
                chatBox.scrollTop = chatBox.scrollHeight; 
            });
    }


                let typingUsers = new Set();
                let typingTimeouts = new Map();

                socket.on('typing', function(data) {
                    typingUsers.add(data.username);
                    updateTypingIndicator(data.username);

                    if (typingTimeouts.has(data.username)) {
                        clearTimeout(typingTimeouts.get(data.username));
                    }

                    typingTimeouts.set(data.username, setTimeout(() => {
                        typingUsers.delete(data.username);
                        updateTypingIndicator();
                    }, 2000));
                });

                function updateTypingIndicator(username) {
                    if (username) {
                        typingIndicator.textContent = `${Array.from(typingUsers).join(', ')} ${typingUsers.size > 1 ? 'are' : 'is'} typing...`;
                    } else {
                        typingIndicator.textContent = '';
                    }
                }

                socket.on('error', function(data) {
                    warningMessage.textContent = data.error;
                    warningMessage.style.display = 'block';
                    setTimeout(() => {
                        warningMessage.style.display = 'none';
                    }, 3000);
                });

                document.getElementById('send-button').addEventListener('click', sendMessage);
                let typingInterval;

                document.getElementById('message-input').addEventListener('focus', function() {
                    socket.emit('typing');
                    typingInterval = setInterval(() => {
                        socket.emit('typing');
                    }, 2000);
                });

                document.getElementById('message-input').addEventListener('blur', function() {
                    clearInterval(typingInterval);
                });

                document.getElementById('message-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); 
        sendMessage(); 
    } else if (e.key === 'Enter' && e.shiftKey) {

        const start = this.selectionStart;
        const end = this.selectionEnd;
        this.value = this.value.substring(0, start) + '\n' + this.value.substring(end);
        this.selectionStart = this.selectionEnd = start + 1;
        e.preventDefault(); 
    }
});

                document.getElementById('upload-button').addEventListener('click', function() {
                    fileInput.click();
                });

                fileInput.addEventListener('change', function() {
                    const file = fileInput.files[0];
                    if (file) {
                        uploadFile(file);
                    }
                });

                toggleSidebar.addEventListener('click', function() {
                    sidebar.classList.toggle('expanded');
                    chatContainer.classList.toggle('expanded');
                });
            }

            function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        const formattedMessage = formatMessage(message);
        socket.send(formattedMessage);
        messageInput.value = '';

        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

function embedYouTubeVideo(url) {
    const youtubePattern = /https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/(watch\?v=|embed\/|v\/)?([^\s&]+)/;

    if (url.includes('/shorts/')) {
        return null; 
    }

    const match = url.match(youtubePattern);

    if (match) {
        const videoId = match[4]; 
        return `<iframe width="560" height="315" src="https://www.youtube.com/embed/${videoId}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
    }
    return null; 
}

function embedYouTubeShorts(url) {
    const youtubeShortsPattern = /https?:\/\/(www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]+)/;
    const match = url.match(youtubeShortsPattern);

    if (match) {
        const shortsId = match[2]; 
        return `<iframe width="350" height="560" src="https://www.youtube.com/embed/${shortsId}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
    }
    return null; 
}

function embedDiscordInvite(url) {
    const discordInvitePattern = /^(https?:\/\/)?(www\.)?(discord\.gg|discord\.com\/invite)\/[a-zA-Z0-9]+$/;
    const match = url.match(discordInvitePattern);

    if (match) {
        const formattedUrl = url.startsWith('http') ? url : `https://${url}`;
        return `
            <a href="${formattedUrl}" target="_blank" rel="noopener noreferrer">
                <img src="static/discordinvite.png" style="width: 200px; height: 400px; border-radius: 8px;"/>
            </a>`;
    }
    return null;
}


function formatLinks(message) {
    const urlPattern = /(?<!\S)(https?:\/\/[^\s]+)/g;

    return message.replace(urlPattern, function(url) {
        const embedVideo = embedYouTubeVideo(url);
        const embedShorts = embedYouTubeShorts(url);
        const embedInvite = embedDiscordInvite(url);

        return embedVideo || embedShorts || embedInvite || `<a href="${url}" class="link" target="_blank" rel="noopener noreferrer">${url}</a>`;
    });
}

function formatMessage(message) {
    message = message

    message = formatLinks(message);
    return message;
}

function showCustomAlert(message) {
    const alertBox = document.getElementById('customAlert');
    const alertMessage = document.getElementById('alertMessage');
    const alertCloseButton = document.getElementById('alertCloseButton');

    alertMessage.innerText = message;
    alertBox.style.display = 'block';

    alertCloseButton.onclick = function() {
        alertBox.style.display = 'none';
    };
}

function uploadFile(file) {
    const maxFileSize = 10 * 1024 * 1024 * 1024; 

    if (file.size > maxFileSize) {
        showCustomAlert('File size exceeds the maximum limit of 10 GB.');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    progressBar.style.display = 'block'; 
    progressBar.style.width = '0%'; 

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/files/upload', true);

    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            if (response.file_url) {
                const message = getMediaMessage(file, response.file_url);
                socket.send(message);
                progressBar.style.width = '0%'; 
                progressBar.style.display = 'none'; 
            }
        } else {
            showCustomAlert('File upload failed. Please try again.');
        }
    };

    xhr.onerror = function() {
        showCustomAlert('An error occurred while uploading the file.');
    };

    xhr.send(formData);
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();

    const isToday = date.toDateString() === now.toDateString();
    const isYesterday = new Date(now.setDate(now.getDate() - 1)).toDateString() === date.toDateString();

    const timeOptions = { hour: '2-digit', minute: '2-digit', hour12: true };
    const timeString = date.toLocaleTimeString([], timeOptions);

    if (isToday) {
        return `Today at ${timeString}`;
    } else if (isYesterday) {
        return `Yesterday at ${timeString}`;
    } else {
        const dateOptions = { month: 'short', day: 'numeric' };
        const dateString = date.toLocaleDateString([], dateOptions);
        return `${dateString} at ${timeString}`;
    }
}

function createMessageElement(msg) {
    const div = document.createElement('div');
    div.className = 'message';

    const formattedMessage = formatLinks(msg.message); 
    const wrappedMessage = wrapLongMessage(formattedMessage, 85);
    const formattedTime = formatTimestamp(msg.timestamp);

    const usernameStyle = (msg.username === 'George' || msg.username === 'CERTIFIEDL0YALIST' || msg.username === 'certifiedloyalist') 
    ? 'color: red; font-weight: bold;' 
    : '';

    const profilePictureUrl = `/static/pfps/${msg.username.toLowerCase()}.png`; 
    const defaultProfilePictureUrl = '/static/boring/default.png'; 

    const img = new Image();
    img.src = profilePictureUrl;

    img.onerror = function() {
        img.src = defaultProfilePictureUrl; 
    };

    div.innerHTML = `
        <div class="message-content" style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center;">
                <img src="${profilePictureUrl}" alt="${msg.username}'s profile picture" class="profile-picture" style="margin-right: 8px;" onerror="this.src='${defaultProfilePictureUrl}';">
                <div>
                    <span class="username" style="${usernameStyle}">${msg.username}:</span>
                    ${wrappedMessage}
                </div>
            </div>
            <span class="timestamp">${formattedTime}</span>
        </div>
    `;

    return div;
}





            function wrapLongMessage(text, maxLength) {
                if (text.length <= maxLength) {
                    return text;
                }

                let result = '';
                while (text.length > maxLength) {
                    result += text.slice(0, maxLength) + '<br>';
                    text = text.slice(maxLength);
                }
                result += text;

                return result;
            }

            function getMediaMessage(file, fileUrl) {
    const fileName = file.name;
    const fileExtension = fileName.split('.').pop().toLowerCase(); // Ensure it's lowercase
    let mediaMessage = '';

    if (file.type.startsWith('image/')) {
        if (fileExtension === 'gif') {
            // GIF files should display normally
            mediaMessage = `<img src="${fileUrl}" alt="Uploaded GIF">`;
        } else {
            // Other image files
            mediaMessage = `<img src="${fileUrl}" alt="Uploaded image">`;
        }
    } else if (file.type.startsWith('video/') || fileExtension === 'mov') {
        mediaMessage = `<video src="${fileUrl}" controls>Your browser does not support video playback.</video>`;
    } else if (file.type.startsWith('audio/')) {
        mediaMessage = `<audio src="${fileUrl}" controls>Your browser does not support audio playback.</audio>`;
    } else {
        mediaMessage = `<a href="${fileUrl}" download class="download-button">Download ${fileName}</a>`;
    }

    return mediaMessage;
}






        });
    </script>
</body>
</html>
