
const socket = io();
let cachedUserRoles = null;
const notifySound = new Audio('static/notification.mp3');
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
    });

    socket.on('message', function(msg) {
const messageId = msg.timestamp;

// Fetch all messages from the server every time a new message is received
fetchMessages();

// Check if the message is already displayed in the chatbox
if (!Array.from(chatBox.children).some(child => child.dataset.timestamp === messageId)) {
    chatBox.appendChild(createMessageElement(msg));

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


});




let previousMessages = [];

function fetchMessages() {
fetch('/data/chatlogs.json')
    .then(response => {
        if (!response.ok) {
            chatBox.innerHTML = '';
            console.error('Chatlogs not found. Chatbox emptied.');
            return;
        }
        return response.json();
    })
    .then(data => {
        const messages = data.messages || [];
        if (JSON.stringify(messages) === JSON.stringify(previousMessages)) {
            return;
        }

        const fragment = document.createDocumentFragment();
        const currentChildren = Array.from(chatBox.children);
        const existingElementsMap = new Map();

        currentChildren.forEach(child => {
            existingElementsMap.set(child.dataset.timestamp, child);
        });

        messages.forEach(msg => {
            const messageId = msg.timestamp;
            const existingElement = existingElementsMap.get(messageId);

            if (!existingElement) {
                fragment.appendChild(createMessageElement(msg));
            } else if (existingElement.innerHTML !== createMessageElement(msg).innerHTML) {
                requestAnimationFrame(() => {
                    existingElement.innerHTML = createMessageElement(msg).innerHTML;
                });
            }
        });

        requestAnimationFrame(() => {
            currentChildren.forEach(child => {
                if (!messages.some(msg => msg.timestamp === child.dataset.timestamp)) {
                    chatBox.removeChild(child);
                }
            });

            chatBox.appendChild(fragment);
            previousMessages = messages;

            setTimeout(() => {
                chatBox.scrollTop = chatBox.scrollHeight;
            }, 100);
        });
    })
    .catch(error => {
        chatBox.innerHTML = 'Error loading messages. Please try again later.';
        console.error('Error loading messages:', error);
    });
}


socket.on('chat_logs_update', function(chatLogs) {
console.log("Received chat logs update:", chatLogs); // Debugging line
fetchMessages().then(() => {
    setTimeout(() => {             
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 100);
});
});

setInterval(fetchMessages, 1600 * 60 * 1); // i put this here so that the chat updates and doesnt have issues where u have to reload after having it open for a while



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





function embedVimeo(url) {
const vimeoPattern = /https?:\/\/(www\.)?vimeo\.com\/([0-9]+)/;
const match = url.match(vimeoPattern);

if (match) {
    const videoId = match[2];
    return `<iframe allowfullscreen src="https://player.vimeo.com/video/${videoId}" frameborder="0" width="640" height="360"></iframe>`;
}
return null; // Return null if the URL doesn't match
}


function embedDiscordInvite(url) {
const discordInvitePattern = /^(https?:\/\/)?(www\.)?(discord\.gg|discord\.com\/invite)\/([a-zA-Z0-9]+)$/;
const match = url.match(discordInvitePattern);

if (match) {
    const formattedUrl = url.startsWith('http') ? url : `https://${url}`;
    const linkText = formattedUrl.replace(/^https?:\/\//, ''); // Remove 'https://' from the URL
    return `<a href="${formattedUrl}" target="_blank" rel="noopener noreferrer">${linkText}</a>`;
}
return ''; // Return empty string if the URL doesn't match
}





function formatCodeBlocks(message) {
// Check if the message starts and ends with "```"
if (message.startsWith('```') && message.endsWith('```')) {
    const innerMessage = message.slice(3, -3).trim(); // Extract inner message without the backticks
    return `<div class="formatted-message"><pre><code>${escapeHtml(innerMessage)}</code></pre></div>`;
}

// If it doesn't meet the condition, return the original message
return message;
}


function escapeHtml(html) {
const escapeChars = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
};
return html.replace(/[&<>"']/g, char => escapeChars[char]);
}

function formatMessage(message) {
return formatCodeBlocks(message);
message = formatLinks(message);
message = formatCodeBlocks(message);
return `<div class="formatted-message">${message}</div>`;
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

const year = date.getFullYear();
const currentYear = now.getFullYear();

if (isToday) {
    return `Today at ${timeString}`;
} else if (isYesterday) {
    return `Yesterday at ${timeString}`;
} else {
    const dateOptions = { month: 'short', day: 'numeric' };
    const dateString = date.toLocaleDateString([], dateOptions);

    if (year !== currentYear) {
        return `${dateString}, ${year} at ${timeString}`;
    } else {
        return `${dateString} at ${timeString}`;
    }
}
}


const specificTimestamp = new Date('2024-10-06T14:30:00').getTime(); // Adjust the date and time as needed
console.log(formatTimestamp(specificTimestamp));


function coloredText(message) {
if (message.startsWith('RR') && message.endsWith('RR')) {
    const innerMessage = message.slice(2, -2);
    return `<span style="color: red; font-weight: bold;">${innerMessage}</span>`;
}
return message; 
}

async function fetchUserRoles() {
if (cachedUserRoles) {
    return cachedUserRoles; // Return cached roles if available
}

try {
    const response = await fetch('https://thugging.org/roles/data/userroles.json');
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    const data = await response.json();
    cachedUserRoles = data; // Cache the roles for future use
    return data;
} catch (error) {
    console.error('Failed to fetch user roles:', error);
    return {}; // Return an empty object if there's an error
}
}

async function updateRoles(username) {
const userRoles = await fetchUserRoles(); // Fetch user roles asynchronously
const roleColorMapping = {
    'owner': 'blue',
    'admin': 'red',
    'moderator': 'green',
    'W THUG': 'cyan',
    'SYSTEM': 'lime' // Add SYSTEM role with a color
};

// Check if userRoles has the username and if it has additionalRoles
if (userRoles[username] && Array.isArray(userRoles[username].additionalRoles)) {
    const roles = userRoles[username].additionalRoles;

    if (roles.includes('SYSTEM')) {
        return `#00FF00`; // Return glowing green for SYSTEM role
    }
    if (roles.includes('owner')) {
        return roleColorMapping['owner'];
    }
    if (roles.includes('admin')) {
        return roleColorMapping['admin']; // Return red if the user is an admin
    }
    if (roles.includes('moderator')) {
        return roleColorMapping['moderator']; // Return green if the user is a moderator
    }
    if (roles.includes('W THUG')) {
        return roleColorMapping['W THUG']; // Return cyan if the user is a W THUG
    }
}

return 'white'; 
}



function createMessageElement(msg) {
const div = document.createElement('div');
div.className = 'message';
const formattedTime = formatTimestamp(msg.timestamp);
const username = msg.username.toLowerCase();
const profilePictureUrlPng = `/static/pfps/${username}.png`;
const defaultProfilePictureUrl = '/static/boring/default.png';

const img = new Image();

img.src = profilePictureUrlPng;

img.onload = function () {
    console.log(`Loaded PNG: ${img.src}`);
    renderMessage();
};

img.onerror = function () {
    img.src = defaultProfilePictureUrl;
    console.log(`Loaded Default: ${img.src}`);
    renderMessage();
};

function renderMessage() {
    if (msg.file_url) {
        div.classList.add('media-message');
        const mediaElement = document.createElement('img');
        mediaElement.src = msg.file_url;
        mediaElement.alt = `${msg.username}'s media`;
        mediaElement.style.maxWidth = '300px';
        mediaElement.style.borderRadius = '8px';
        div.appendChild(mediaElement);
    } else {
        let formattedMessage = formatLinks(msg.message);
        formattedMessage = coloredText(formattedMessage);
        formattedMessage = formatCodeBlocks(formattedMessage);

        const videoEmbed = embedYouTubeVideo(formattedMessage);
        const shortsEmbed = embedYouTubeShorts(formattedMessage);
        const inviteEmbed = embedDiscordInvite(formattedMessage);

        const embeddedMessage = videoEmbed || shortsEmbed || inviteEmbed || formattedMessage;
        const wrappedMessage = wrapLongMessage(embeddedMessage, 850);

        updateRoles(msg.username).then(usernameColor => {
            const usernameStyle = `color: ${usernameColor}; font-weight: bold;`;

            div.innerHTML = `
                <div class="message-content" style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center;">
                        <img src="${img.src}" alt="${msg.username}'s profile picture" class="profile-picture" style="margin-right: 8px;">
                        <div>
                            <span class="username" style="${usernameStyle}; cursor: pointer; display: inline-block; transition: transform 0.2s ease;" data-username="${msg.username}">${msg.username}:</span>
                            ${wrappedMessage}
                        </div>
                    </div>
                    <span class="timestamp">${formattedTime}</span>
                </div>
            `;

            const usernameElement = div.querySelector('.username');

            usernameElement.addEventListener('mouseenter', () => {
                usernameElement.style.transform = 'scale(1.02)';
            });

            usernameElement.addEventListener('mouseleave', () => {
                usernameElement.style.transform = 'scale(1.0)';
            });

            usernameElement.addEventListener('click', () => {
                openUsernameModal(msg.username);
            });
        });
    }
}

return div;
}



function openUsernameModal(username) {
const modal = document.createElement('div');
modal.className = 'modal';
modal.style.position = 'fixed';
modal.style.top = '0';
modal.style.left = '0';
modal.style.width = '100%';
modal.style.height = '100%';
modal.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
modal.style.display = 'flex';
modal.style.alignItems = 'center';
modal.style.justifyContent = 'center';
modal.style.opacity = '0';
modal.style.transition = 'opacity 0.3s ease';

const modalContent = document.createElement('div');
modalContent.className = 'modal-content';
modalContent.style.backgroundColor = '#36393f';
modalContent.style.padding = '30px';
modalContent.style.borderRadius = '12px';
modalContent.style.boxShadow = '0 4px 40px rgba(0, 0, 0, 0.5)';
modalContent.style.transition = 'transform 0.3s ease';
modalContent.style.transform = 'scale(0.9)';
modalContent.style.maxWidth = '600px';
modalContent.style.width = '90%';
modalContent.style.position = 'relative';

const profilePictureUrl = `/static/pfps/${username.toLowerCase()}.png`;

const header = createHeader(username, profilePictureUrl);
const rolesSection = createRolesSection();
const bioSection = createBioSection();

const downloadButton = createDownloadButton(username);

modalContent.appendChild(downloadButton);
modalContent.appendChild(header);
modalContent.appendChild(rolesSection);
modalContent.appendChild(bioSection);

modal.appendChild(modalContent);
document.body.appendChild(modal);

setTimeout(() => {
    modal.style.opacity = '1';
    modalContent.style.transform = 'scale(1)';
}, 10);

modal.addEventListener('click', (event) => {
    if (event.target === modal) {
        closeModal();
    }
});

function closeModal() {
    modal.style.opacity = '0';
    setTimeout(() => {
        document.body.removeChild(modal);
    }, 300);
}

loadUserRoles(username, rolesSection);
loadUserBio(username, bioSection);
}

function createHeader(username, profilePictureUrl) {
const headerDiv = document.createElement('div');
headerDiv.style.display = 'flex';
headerDiv.style.alignItems = 'center';
headerDiv.style.marginBottom = '20px';

const profilePicture = document.createElement('img');
profilePicture.src = profilePictureUrl;
profilePicture.alt = `${username}'s profile picture`;
profilePicture.style.borderRadius = '50%';
profilePicture.style.width = '100px';
profilePicture.style.height = '100px';
profilePicture.style.marginRight = '15px';
profilePicture.style.border = '2px solid #7289da';

const usernameElement = document.createElement('h2');
usernameElement.style.margin = '0';
usernameElement.style.fontSize = '24px';
usernameElement.style.color = '#ffffff';
usernameElement.textContent = username;

headerDiv.appendChild(profilePicture);
headerDiv.appendChild(usernameElement);
return headerDiv;
}

function createRolesSection() {
const rolesDiv = document.createElement('div');
rolesDiv.style.marginTop = '20px';
rolesDiv.style.color = '#b9bbbe';

const rolesHeader = document.createElement('h3');
rolesHeader.textContent = 'Roles';
rolesHeader.style.marginBottom = '10px';
rolesHeader.style.color = '#ffffff';

const rolesList = document.createElement('p');
rolesList.className = 'roles';
rolesList.textContent = 'Loading...';

rolesDiv.appendChild(rolesHeader);
rolesDiv.appendChild(rolesList);

const separator = document.createElement('hr');
separator.style.border = '1px solid #444';
separator.style.margin = '15px 0';
rolesDiv.appendChild(separator);

return rolesDiv;
}

function createBioSection() {
const bioDiv = document.createElement('div');
bioDiv.style.color = '#b9bbbe';

const bioHeader = document.createElement('h3');
bioHeader.textContent = 'Bio';
bioHeader.style.marginBottom = '10px';
bioHeader.style.color = '#ffffff';

const bioParagraph = document.createElement('p');
bioParagraph.className = 'bio';
bioParagraph.textContent = 'Loading...';

bioDiv.appendChild(bioHeader);
bioDiv.appendChild(bioParagraph);

return bioDiv;
}

function createDownloadButton(username) {
const button = document.createElement('button');
button.style.position = 'absolute';
button.style.top = '15px';
button.style.right = '15px';
button.style.backgroundColor = 'transparent';
button.style.border = 'none';
button.style.cursor = 'pointer';
button.style.zIndex = '10';

const downloadIcon = document.createElement('img');
downloadIcon.src = 'https://thugging.org/static/downloadicon.png';
downloadIcon.alt = 'Download Profile Picture';
downloadIcon.style.width = '32px';
downloadIcon.style.height = '32px';

button.appendChild(downloadIcon);
button.addEventListener('click', (event) => {
    event.stopPropagation();
    const profilePictureUrl = `/static/pfps/${username.toLowerCase()}.png`;
    const link = document.createElement('a');
    link.href = profilePictureUrl;
    link.download = `${username.toLowerCase()}_pfp.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});

return button;
}

function loadUserRoles(username, modalContent) {
fetch('https://thugging.org/roles/data/userroles.json')
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(rolesData => {
        const rolesParagraph = modalContent.querySelector('.roles');
        if (rolesData[username]) {
            const roles = rolesData[username].additionalRoles || [];
            rolesParagraph.textContent = `Roles: ${roles.length > 0 ? roles.join(', ') : 'No Role Assigned'}`;
        } else {
            rolesParagraph.textContent = 'Roles: No Role Assigned';
        }
    })
    .catch(error => {
        console.error('Error loading roles:', error);
        modalContent.querySelector('.roles').textContent = 'Roles: Error loading roles';
    });
}

function loadUserBio(username, modalContent) {
fetch('data/bios.json')
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(bioData => {
        const bioParagraph = modalContent.querySelector('.bio');
        if (bioData[username]) {
            bioParagraph.textContent = `Bio: ${bioData[username].bio || 'No Bio Available'}`;
        } else {
            bioParagraph.textContent = 'Bio: No Bio Available';
        }
    })
    .catch(error => {
        console.error('Error loading bio:', error);
        modalContent.querySelector('.bio').textContent = 'Bio: Error loading bio';
    });
}







function handleWebSocketMessages(event) {
const msg = JSON.parse(event.data);
const messageElement = createMessageElement(msg);

const chatContainer = document.getElementById('chat-container'); 
chatContainer.appendChild(messageElement);
chatContainer.scrollTop = chatContainer.scrollHeight; 
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
const fileExtension = fileName.split('.').pop().toLowerCase(); 
let mediaMessage = '';

if (file.type.startsWith('image/')) {
    if (fileExtension === 'gif') {
        mediaMessage = `<img src="${fileUrl}" alt="Uploaded GIF">`;
    } else {
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