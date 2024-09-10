document.addEventListener('DOMContentLoaded', async function() {
    const votedTrueContainer = document.getElementById('voted-true');
    const votedFalseContainer = document.getElementById('voted-false');

    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');

    let currentPage = 1;
    const itemsPerPage = 9;
    let userPolls = [];
    let allOtherPolls = [];

    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            displayPage(currentPage);
        }
    });

    nextButton.addEventListener('click', () => {
        const maxPage = Math.ceil(allOtherPolls.length / itemsPerPage);
        if (currentPage < maxPage) {
            currentPage++;
            displayPage(currentPage);
        }
    });

    try {
        const response = await fetch('/api/poll_results/');
        const data = await response.json();
        userPolls = data.data.user_polls;

        userPolls.forEach(poll => {
            renderPoll(poll);
            connectToPollGroup(poll.id);
        });

        allOtherPolls = data.data.other_polls;

        // Connect all other polls to their WebSocket groups
        allOtherPolls.forEach(poll => {
            connectToPollGroup(poll.id);
        });

        // Display the first page of other polls
        displayPage(1);
    } catch (error) {
        console.error('Error fetching polls data:', error);
    }

    function displayPage(page) {
        votedFalseContainer.innerHTML = '';

        const startIndex = (page - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        const pollsToDisplay = allOtherPolls.slice(startIndex, endIndex);

        pollsToDisplay.forEach(poll => {
            renderPoll(poll);
        });

        // Update button states
        const maxPage = Math.ceil(allOtherPolls.length / itemsPerPage);
        prevButton.disabled = currentPage === 1;
        nextButton.disabled = currentPage === maxPage;
    }

    function renderPoll(poll) {
        const pollElement = document.createElement('div');
        pollElement.className = 'poll';
        pollElement.setAttribute('id', `poll_${poll.id}`);

        const pollLink = document.createElement('a');
        pollLink.href = `http://${window.location.host}/vote/${poll.id}`;

        const pollTitle = document.createElement('h3');
        pollTitle.textContent = poll.title;

        pollLink.appendChild(pollTitle);

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

        pollElement.appendChild(pollLink);
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
        allOtherPolls.push(poll);
        connectToPollGroup(poll.id);
        const maxPage = Math.ceil(allOtherPolls.length / itemsPerPage);
        if (currentPage === maxPage) {
            displayPage(currentPage);
        }
    };

    newPollSocket.onclose = function(event) {
        console.log('New Poll WebSocket connection closed:', event);
    };

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

    function updatePoll(data) {
        const pollId = Number(data.poll_id);
        const choiceId = Number(data.choice_id);
        const newVotes = Number(data.votes);
        const newTopChoice = data.top_choice;

        let index = -1;

        for (let i = 0; i < allOtherPolls.length; i++) {
            if (allOtherPolls[i].id === pollId) {
                index = i;
                break;
            }
        }

        if (index != -1) {
            const choices = allOtherPolls[index].choices;
            for (let j = 0; j < choices.length; j++) {
                if (choices[j].id === choiceId) {
                    choices[j].vote_count = newVotes;
                }
            }
            allOtherPolls[index].top_choice = newTopChoice;

            // Check if the poll is currently displayed on the current page
            const pollElement = document.getElementById(`poll_${pollId}`);
            if (pollElement) {
                const topChoiceElement = pollElement.querySelector('.top-choice');
                topChoiceElement.textContent = `Top choice: ${newTopChoice}`;

                const choiceItem = document.querySelector(`#choice_${choiceId}`);
                if (choiceItem) {
                    choiceItem.textContent = `${data.choice_text} - ${newVotes} votes`;
                }
            }
            if (data.voted) {
                if (data.up_voted) {
                    allOtherPolls[index].voted = true;
                    const poll = allOtherPolls.splice(index, 1)[0];
                    userPolls.push(poll);
                    if (pollElement) {
                        const votedTrueContainer = document.getElementById('voted-true');
                        votedTrueContainer.appendChild(pollElement);
                        displayPage(currentPage);
                    } else {
                        renderPoll(poll);
                    }
                }
            }
        } else {
            let index = -1;
            for (let i = 0; i < userPolls.length; i++) {
                if (userPolls[i].id === pollId) {
                    index = i;
                    break;
                }
            }

            const choices = userPolls[index].choices;
            for (let j = 0; j < choices.length; j++) {
                if (choices[j].id === choiceId) {
                    choices[j].vote_count = newVotes;
                }
            }
            userPolls[index].top_choice = newTopChoice;

            const pollElement = document.getElementById(`poll_${pollId}`);
            if (pollElement) {
                const topChoiceElement = pollElement.querySelector('.top-choice');
                topChoiceElement.textContent = `Top choice: ${newTopChoice}`;

                const choiceItem = document.querySelector(`#choice_${choiceId}`);
                if (choiceItem) {
                    choiceItem.textContent = `${data.choice_text} - ${newVotes} votes`;
                }
            }
            if (data.voted) {
                if (!data.up_voted) {
                    userPolls[index].voted = false;
                    const poll = userPolls.splice(index, 1)[0];
                    allOtherPolls.push(poll);
                    if (pollElement) {
                        pollElement.parentNode.removeChild(pollElement);
                    }
                    displayPage(currentPage);
                }
            }
        }
    }
});
