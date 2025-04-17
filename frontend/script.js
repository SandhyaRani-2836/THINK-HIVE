function signup() {
    const name = document.getElementById("signup-name").value;
    const email = document.getElementById("signup-email").value;
    const password = document.getElementById("signup-password").value;

    fetch('http://127.0.0.1:5000/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
    })
    .then(response => response.json())
    .then(data => alert(data.message));
}

function login() {
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
    .then(response => {
        if (response.ok) {
            alert("Login successful!");
            window.location.href = "menu.html";
        } else {
            alert("Invalid credentials");
        }
    });
}

function uploadProject() {
    const title = document.getElementById("project-title").value;
    const description = document.getElementById("project-description").value;
    const file = document.getElementById("project-file").files[0];

    let formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('file', file);

    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => alert(data.message));
}
