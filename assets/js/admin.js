const csrfToken = '{{ csrf_token() }}';

function formatDate(dateString) {
    const optionsDate = { year: 'numeric', month: 'long', day: 'numeric' };
    const optionsTime = { hour: 'numeric', minute: 'numeric', hour12: true };
    const date = new Date(dateString);
    const formattedDate = date.toLocaleDateString('en-US', optionsDate);
    const formattedTime = date.toLocaleTimeString('en-US', optionsTime);
    return `${formattedDate} at ${formattedTime}`;
}

function sortUsers() {
    const userGrid = document.getElementById('user-grid');
    const userCards = Array.from(userGrid.children);

    userCards.sort((a, b) => {
        const dateA = new Date(a.getAttribute('data-registered-at'));
        const dateB = new Date(b.getAttribute('data-registered-at'));
        return dateA - dateB;
    });

    userCards.forEach(card => userGrid.appendChild(card));
}

function displayFormattedDates() {
    const dateElements = document.querySelectorAll('.formatted-date');
    dateElements.forEach(element => {
        const registeredAt = element.getAttribute('data-registered-at');
        element.textContent = formatDate(registeredAt);
    });
}

function loadUserRoles() {
    fetch('https://thugging.org/roles/data/userroles.json')
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(rolesData => {
        const userCards = document.querySelectorAll('.user-card');
        userCards.forEach(card => {
            const username = card.getAttribute('data-username');
            const roleContainer = card.querySelector('.role-container');
            const roles = rolesData[username]?.additionalRoles || [];
            roleContainer.textContent = roles.length > 0 ? roles.join(', ') : 'No Role Assigned';
        });
    })
    .catch(error => {
        console.error('Error loading roles:', error);
    });
}

function loadChatLogs() {
    fetch('/path/to/chatlogs.json')
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    })
    .then(data => {
        const chatContainer = document.getElementById('chat-container'); // Ensure you have this element in your HTML
        chatContainer.innerHTML = ''; // Clear previous chat logs

        data.messages.forEach(log => {
            const messageElement = document.createElement('div');
            const timestamp = formatDate(log.timestamp);
            messageElement.innerHTML = `<strong>${log.username}:</strong> <span>${log.message}</span> <em>(${timestamp})</em>`;
            chatContainer.appendChild(messageElement);
        });
    })
    .catch(error => {
        console.error('Error loading chat logs:', error);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    displayFormattedDates();
    sortUsers();
    loadUserRoles();
    loadChatLogs(); // Load chat logs after the DOM is ready
});

function toggleMenu(event) {
    const menuContent = event.currentTarget.querySelector('.menu-content');
    menuContent.style.display = menuContent.style.display === 'block' ? 'none' : 'block';
}

function banUser(username) {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value; // Retrieve CSRF token

    fetch('/admin/users/ban', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken // Include CSRF token
        },
        body: JSON.stringify({ username })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function clearMessages(username) {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value; // Ensure you get the CSRF token correctly
    
    fetch('/admin/users/clear_messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken // Include the CSRF token here
        },
        body: JSON.stringify({ username })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function addRole(username) {
    const select = document.getElementById(`roleSelect_${username}`);
    const role = select.value;
    if (!role) return;

    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    fetch('/roles/add_role', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Ensure the correct header name for CSRF token
        },
        body: JSON.stringify({ username, role })
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function removeRole(username) {
    const select = document.getElementById(`roleSelect_${username}`);
    const role = select.value;
    if (!role) return;

    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    fetch('/roles/remove_role', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken // Ensure the correct header name for CSRF token
        },
        body: JSON.stringify({ username, role })
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function clearAllChats() {
    const csrfToken = document.querySelector('input[name="csrf_token"]').value;

    fetch('/admin/chats/clear_all', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function filterUsers() {
    const input = document.getElementById("searchInput");
    const filter = input.value.toLowerCase();
    const userCards = document.querySelectorAll(".user-card");

    userCards.forEach(card => {
        const username = card.getAttribute("data-username").toLowerCase();
        const registeredAt = card.getAttribute("data-registered-at").toLowerCase();

        if (username.includes(filter) || registeredAt.includes(filter)) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }
    });

    localStorage.setItem("searchInputValue", filter);
}

document.addEventListener('DOMContentLoaded', () => {
    const savedInputValue = localStorage.getItem("searchInputValue") || "";
    const input = document.getElementById("searchInput");
    input.value = savedInputValue;
    filterUsers();
});
