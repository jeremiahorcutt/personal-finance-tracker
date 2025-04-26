document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
  
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
  
    const response = await fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    });
  
    const result = await response.json();
  
    const messageEl = document.getElementById('loginMessage');
    if (response.ok) {
      messageEl.textContent = "Login successful!";
      messageEl.style.color = "green";
  
      // Save token in localStorage for future use
      localStorage.setItem("access_token", response.access_token);
      localStorage.setItem("user_id", result.user_id);
      window.location.href = "/dashboard"
      
    } else {
      messageEl.textContent = (result.error || "Login failed.");
      messageEl.style.color = "red";
    }
  });