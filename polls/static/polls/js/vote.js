const pollIdElement = document.getElementById('poll-id');
const pollId = pollIdElement.getAttribute('data-poll-id');
const voteApiUrl = `/api/vote/${pollId}/`;
var status = "Open";

fetch(voteApiUrl)
    .then(response => response.json())
    .then(data => {
        document.getElementById('poll-title').textContent = data.poll.title;
        document.getElementById('poll-question').textContent = data.poll.question;

        const choicesList = document.getElementById('choices-list');
        choicesList.innerHTML = '';

        const voteChoices = document.getElementById('vote-choices');
        voteChoices.innerHTML = '';

        if (data.status === "Closed"){
            status = "Closed";
            document.getElementById('vote-button').style.display = 'none';
            document.getElementById('status').textContent = "Status: Closed";
            data.poll.choices.forEach(choice => {
                const li = document.createElement('li');
                li.setAttribute('id', `choice_${choice.id}`);
                li.innerHTML = `${choice.choice_text} (${choice.votes} votes)`;
                choicesList.appendChild(li);
            });
        } else {
            data.poll.choices.forEach(choice => {
                const li = document.createElement('li');
                li.setAttribute('id', `choice_${choice.id}`);
                li.innerHTML = `<label><input type="radio" name="choice" value="${choice.id}" required>
                    ${choice.choice_text} (${choice.votes} votes)</label>`;
                voteChoices.appendChild(li);
            });
        }
    })
    .catch(error => {
        console.error('Error fetching poll data:', error);
    });

if (status === "Closed") {
    console.log("Poll is closed.");
} else {
    const socket = new WebSocket(`ws://${window.location.host}/ws/vote/${pollId}/`);

    socket.onmessage = function(e) {
        try {
            const data = JSON.parse(e.data);

            if ('error' in data) {
                alert(data.error);
            } else {
                const choiceId = Number(data.choice_id);
                const choiceElement = document.querySelector(`#choice_${choiceId}`);
                if (choiceElement) {
                    const voteLabel = choiceElement.querySelector('label');
                    if (data.choice_text && data.votes !== undefined) {
                        voteLabel.innerHTML = `<input type="radio" name="choice" value="${data.choice_id}" required> ${data.choice_text} (${data.votes} votes)`;
                    }
                }
            }
        } catch (err) {
            console.error("Failed to parse message data:", err);
        }
    };

    document.getElementById('voteForm').onsubmit = function(event) {
        event.preventDefault();

        const selectedChoice = document.querySelector('input[name="choice"]:checked');
        if (selectedChoice) {
            socket.send(JSON.stringify({
                'choice_id': selectedChoice.value
            }));
        } else {
            alert('Please select a choice before voting.');
        }
    };
}