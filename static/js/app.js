const API_URL = 'http://127.0.0.1:5000';

let currentPublicKey = null;

// Function to handle login
async function login(event) {
    event.preventDefault();
    const publicKey = document.getElementById('login-public-key').value;
    const privateKeyPem = document.getElementById('login-private-key').value;

    // Request a login challenge
    const challengeResponse = await fetch(`${API_URL}/login_challenge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ public_key: publicKey })
    });

    const challengeData = await challengeResponse.json();
    if (challengeData.error) {
        document.getElementById('login-message').innerText = challengeData.error;
        return;
    }

    const challenge = challengeData.challenge;

    // Convert the private key to a CryptoKey object
    const privateKey = await window.crypto.subtle.importKey(
        "pkcs8",
        str2ab(privateKeyPem), // Convert PEM to ArrayBuffer
        {
            name: "RSA-PSS",
            hash: { name: "SHA-256" }
        },
        false,
        ["sign"]
    );

    // Sign the challenge
    const signedChallenge = await window.crypto.subtle.sign(
        { name: "RSA-PSS", saltLength: 32 },
        privateKey,
        new TextEncoder().encode(challenge)
    );

    // Convert the signed challenge to Base64
    const signedChallengeB64 = btoa(String.fromCharCode(...new Uint8Array(signedChallenge)));

    // Send the signed challenge back to the server
    const verifyResponse = await fetch(`${API_URL}/verify_login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ public_key: publicKey, signed_challenge: signedChallengeB64 })
    });

    const verifyData = await verifyResponse.json();
    if (verifyData.error) {
        document.getElementById('login-message').innerText = verifyData.error;
    } else {
        document.getElementById('login-message').innerText = 'Login successful!';
        currentPublicKey = publicKey;

        // Show the main tabs and hide the login section
        document.getElementById('login-section').style.display = 'none';
        document.getElementById('tabs').style.display = 'block';

        // Pre-fill the public key in relevant fields
        document.getElementById('sender-key').value = currentPublicKey;
        document.getElementById('view-key').value = currentPublicKey;
        document.getElementById('earn-key').value = currentPublicKey;

        // Load wallet data
        viewWallet();
    }
}

// Helper to convert PEM private key to ArrayBuffer
function str2ab(pem) {
    const binaryString = atob(pem.replace(/-----[^-]+-----/g, "").replace(/\s+/g, ""));
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

// Function to create a new wallet
async function createWallet() {
    const response = await fetch(`${API_URL}/create_wallet`, { method: 'POST' });
    const data = await response.json();

    if (data.error) {
        alert(data.error);
    } else {
        document.getElementById('signup-info').innerHTML = `
            <strong>Public Key:</strong> <pre>${data.public_key}</pre>
            <strong>Private Key:</strong> <pre>${data.private_key}</pre>
            <p><strong>Important:</strong> Save your private key securely. It won't be shown again.</p>
        `;
    }
}

// Function to send tokens
async function sendTokens() {
    const receiverKey = document.getElementById('receiver-key').value;
    const amount = parseInt(document.getElementById('amount').value);

    const response = await fetch(`${API_URL}/send_tokens_with_alias`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            sender_alias: currentPublicKey, // Using alias in this example
            receiver_alias: receiverKey,
            amount
        })
    });

    const data = await response.json();
    document.getElementById('transaction-result').innerText = data.message || data.error;

    // Update wallet balance if transaction succeeds
    if (data.message) {
        viewWallet();
    }
}

// Function to view wallet
async function viewWallet() {
    const response = await fetch(`${API_URL}/wallet/${currentPublicKey}`);
    const data = await response.json();

    if (data.error) {
        document.getElementById('wallet-details').innerText = data.error;
    } else {
        document.getElementById('wallet-balance').innerText = `Balance: ${data.balance}`;
        const transactionList = document.getElementById('transaction-history');
        transactionList.innerHTML = data.transactions
            .map(tx => `<li>${tx.sender} → ${tx.receiver}: ${tx.amount} Tokens</li>`)
            .join('');
    }
}

// Function to perform actions to earn tokens
async function performAction(action) {
    const response = await fetch(`${API_URL}/perform_action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ public_key: currentPublicKey, action })
    });

    const data = await response.json();
    alert(data.message || data.error);

    // Update wallet balance if the action succeeds
    if (data.message) {
        viewWallet();
    }
}

// Function to handle purchases in the marketplace
async function buyItem(itemName, cost) {
    const response = await fetch(`${API_URL}/perform_action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            public_key: currentPublicKey,
            action: 'buy_item',
            item_name: itemName,
            cost
        })
    });

    const data = await response.json();
    alert(data.message || data.error);

    // Update wallet balance if the purchase succeeds
    if (data.message) {
        viewWallet();
    }
}

// Function to open tabs
function openTab(event, tabId) {
    // Hide all tab content
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => tab.style.display = 'none');

    // Remove active class from all buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));

    // Show the clicked tab content
    document.getElementById(tabId).style.display = 'block';

    // Highlight the clicked button
    event.currentTarget.classList.add('active');
}

// Function to return to the landing page
function backToLanding() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('sign-up-section').style.display = 'none';
    document.getElementById('landing-section').style.display = 'block';
}

// Function to show the sign-up page
function showSignUp() {
    document.getElementById('landing-section').style.display = 'none';
    document.getElementById('sign-up-section').style.display = 'block';
}

// Function to show the login page
function showLogin() {
    document.getElementById('landing-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
}
