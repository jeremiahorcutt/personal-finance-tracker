async function loadDashboard() {
    const token = localStorage.getItem("access_token");
  
    if (!token) {
      window.location.href = "/login";
      return;
    }
  
    const response = await fetch("/transactions", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      }
    });
  
    if (response.status === 401) {
      alert("Session expired. Please login again.");
      localStorage.clear();
      window.location.href = "/login";
      return;
    }
  
    const transactions = await response.json();
  
    let html = "<table border='1'><tr><th>Amount</th><th>Category</th><th>Description</th><th>Date</th></tr>";
    transactions.forEach(tx => {
      html += `<tr>
        <td>${tx.amount}</td>
        <td>${tx.category}</td>
        <td>${tx.description}</td>
        <td>${tx.date}</td>
      </tr>`;
    });
    html += "</table>";
  
    document.getElementById("transactions-container").innerHTML = html;
  }

  function logout() {
    localStorage.clear();
    window.location.href = "/login";
  }
  
  
  window.onload = loadDashboard;