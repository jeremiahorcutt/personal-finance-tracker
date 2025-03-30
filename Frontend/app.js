async function addTransaction() {
    const token = "your_jwt_token"; // Replace with actual JWT token from login
    const response = await fetch("http://127.0.0.1:5000/transactions", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token,
        },
        body: JSON.stringify({
            amount: 100,
            category: "Food",
            description: "Groceries"
        }),
    });
    const data = await response.json();
    console.log(data);
}