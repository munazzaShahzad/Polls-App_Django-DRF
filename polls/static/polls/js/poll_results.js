document.addEventListener('DOMContentLoaded', async function() {
    const votedTrueContainer = document.getElementById('voted-true');
    const votedFalseContainer = document.getElementById('voted-false');

    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');

    let currentPage = 1;
    let nextPage = false;

    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            fetchOtherPolls(currentPage - 1);
        }
    });

    nextButton.addEventListener('click', () => {
        if (nextPage) {
            fetchOtherPolls(currentPage + 1);
        }
    });

    try {
        const response = await fetch('/api/poll_results/');
        const data = await response.json();
        const user_polls = data.data.user_polls;

        user_polls.forEach(poll => {
            renderPoll(poll);
            connectToPollGroup(poll.id);
        });
    } catch (error) {
        console.error('Error fetching user polls data:', error);
    }

    async function fetchOtherPolls(page)
    {
        try {
            const response = await fetch(`/api/poll_results/?page=${page}`);
            const data = await response.json();
            const other_polls = data.data.other_polls;

            votedFalseContainer.innerHTML = '';

            other_polls.results.forEach(poll => {
                renderPoll(poll);
                connectToPollGroup(poll.id);
            });

            currentPage = page;

            const nextLink = other_polls.links && other_polls.links.next;
            const prevLink = other_polls.links && other_polls.links.previous;

            // Update button states based on links
            prevButton.disabled = !prevLink;
            nextButton.disabled = !nextLink;
            nextPage = nextLink;

        } catch (error) {
            console.error('Error fetching other polls data:', error);
        }
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
        pollQuestion.textContent = `${poll.question}`;

        const topChoice = document.createElement('p');
        topChoice.textContent = `Top choice: ${poll.top_choice}`;
        topChoice.className = 'top-choice';

        const choicesList = document.createElement('ul');
        poll.choices.forEach(choice => {
            const choiceItem = document.createElement('li');
            choiceItem.setAttribute('id', `choice_${choice.id}`);
            choiceItem.textContent = `${choice.choice_text} - ${choice.vote_count} votes`;
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

    const newPollSocket = new WebSocket(`ws://${window.location.host}/ws/poll_results/`);

    newPollSocket.onmessage = function(event) {
        const poll = JSON.parse(event.data);
        renderPoll(poll);
        connectToPollGroup(poll.id);
        fetchOtherPolls(currentPage);
    };

    newPollSocket.onclose = function(event) {
        console.log('New Poll WebSocket connection closed:', event);
    };

    // Function to connect to a WebSocket group for a poll
    function connectToPollGroup(pollId) {
        const socket = new WebSocket(`ws://${window.location.host}/ws/poll_results/${pollId}/`);

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updatePoll(data);
        };

        socket.onclose = function(event) {
            console.log('Poll Group WebSocket connection closed:', event);
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
                fetchOtherPolls(currentPage);
            }
        }
    }

    // Initial fetch
    fetchOtherPolls(1);

});
