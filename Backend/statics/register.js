document.getElementById('registerForm').addEventListener('submit', async function (e) {
    e.preventDefault();
  
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
  
    const response = await fetch('/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username,
        email: email,
        password: password
      })
    });
  
    const result = await response.json();
  
    const messageEl = document.getElementById('responseMessage');
    if (response.ok) {
      messageEl.textContent = result.message;
      messageEl.style.color = "green";
      window.location.href = "/login"
    } else {
      messageEl.textContent =(result.error || "Something went wrong.");
      messageEl.style.color = "red";
    }
  });