// Positions
const positions = [
    "Seeker",
    "Beater",
    "Chaser",
    "Keeper"
];

// Houses
const houses = [
    "Gryffindor",
    "Hufflepuff",
    "Ravenclaw",
    "Slytherin"
];

// Registered team players
const teamPlayers = [];

// Function to randomly assign a house
function assignHouse() {
    return houses[Math.floor(Math.random() * houses.length)];
}

// Function to add a player to the team
function addPlayer() {
    const playerName = document.getElementById("playerName").value;
    const position = document.getElementById("position").value;

    if (playerName && position) {
        const player = {
            playerName,
            position
        };

        teamPlayers.push(player);

        // Clear input fields
        document.getElementById("playerName").value = "";
        document.getElementById("position").value = "";

        // Add player to the table
        addPlayerToTable(player);
    }
}

// Function to add a player to the table
function addPlayerToTable(player) {
    const teamTableBody = document.getElementById("teamTableBody");

    const newRow = document.createElement("tr");
    newRow.innerHTML = `
        <td>${player.playerName}</td>
        <td>${player.position}</td>
        <td></td>
    `;

    teamTableBody.appendChild(newRow);
}

// Function to handle form submission
function handleFormSubmit(event) {
    event.preventDefault();

    if (teamPlayers.length > 0) {
        const assignedHouse = assignHouse(); // Assign a single house to the entire team

        teamPlayers.forEach(player => {
            player.house = assignedHouse;
            updatePlayerInTable(player);
        });

        fetch('/add_team_players', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ teamPlayers })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            alert(`The entire team has been assigned to ${assignedHouse} house!`);
        })
        .catch(error => {
            console.error(error);
        });
    }
}

// Function to update player house in the table
function updatePlayerInTable(player) {
    const teamTableBody = document.getElementById("teamTableBody");
    const rows = teamTableBody.getElementsByTagName("tr");

    for (let i = 0; i < rows.length; i++) {
        const playerNameCell = rows[i].getElementsByTagName("td")[0];

        if (playerNameCell.textContent === player.playerName) {
            const houseCell = rows[i].getElementsByTagName("td")[2];
            houseCell.innerText = player.house; // Use innerText instead of textContent
            break;
        }
    }
}

// Add event listener to "Add Player" button
document.getElementById("addPlayerButton").addEventListener("click", addPlayer);

// Add event listener to form submission
document.getElementById("registrationForm").addEventListener("submit", handleFormSubmit);
