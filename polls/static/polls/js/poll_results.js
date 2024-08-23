document.addEventListener('DOMContentLoaded', async function() {
    const votedTrueContainer = document.getElementById('voted-true');
    const votedFalseContainer = document.getElementById('voted-false');

    try {
        const response = await fetch('/api/poll_results/');
        const data = await response.json();

        data.polls.forEach(poll => {
            renderPoll(poll);
            connectToPollGroup(poll.id);
        });
    } catch (error) {
        console.error('Error fetching poll data:', error);
    }

    function renderPoll(poll) {
        const pollElement = document.createElement('div');
        pollElement.className = 'poll';
        pollElement.setAttribute('id',`poll_${poll.id}`);

        const pollTitle = document.createElement('h3');
        pollTitle.textContent = poll.title;

        const pollStatus = document.createElement('p');
        pollStatus.textContent = `Status: ${poll.status}`;

        const pollQuestion = document.createElement('h4');
        pollQuestion.textContent = `${poll.questions}`;

        const topChoice = document.createElement('p');
        topChoice.textContent = `Top choice: ${poll.top_choice}`;
        topChoice.className = 'top-choice';

        const choicesList = document.createElement('ul');
        poll.choices.forEach(choice => {
            const choiceItem = document.createElement('li');
            choiceItem.setAttribute('id', `choice_${choice.id}`);
            choiceItem.textContent = `${choice.choice_text} - ${choice.votes} votes`;
            choicesList.appendChild(choiceItem);
        });

        pollElement.appendChild(pollTitle);
        pollElement.appendChild(pollStatus);
        pollElement.appendChild(pollQuestion);
        pollElement.appendChild(topChoice);
        pollElement.appendChild(choicesList);

        if (poll.voted) {
            votedTrueContainer.appendChild(pollElement);
        } else {
            votedFalseContainer.appendChild(pollElement);
        }
    }

    // Function to connect to a WebSocket group for a poll
    function connectToPollGroup(pollId) {
        const socket = new WebSocket(`ws://${window.location.host}/ws/poll_results/${pollId}/`);

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updatePoll(data);
        };

        socket.onclose = function(event) {
            console.log('WebSocket connection closed:', event);
        };
    }

    // Function to update poll data upon receiving WebSocket message
    function updatePoll(data) {
        const pollElement = document.getElementById(`poll_${data.poll_id}`);
        if (pollElement) {
            const topChoiceElement = pollElement.querySelector('.top-choice');
            topChoiceElement.textContent = `Top choice: ${data.top_choice}`;

            const choiceId = Number(data.choice_id);
            const choiceItem = document.querySelector(`#choice_${choiceId}`);
            choiceItem.textContent = `${data.choice_text} - ${data.votes} votes`;

            if (data.voted) {
                const votedTrueContainer = document.getElementById('voted-true');
                votedTrueContainer.appendChild(pollElement);

            }
        }
    }
});
