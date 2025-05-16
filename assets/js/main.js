document.addEventListener('DOMContentLoaded', function() {
    const addCardBtn = document.querySelector('.add-card button');
    const frontInput = document.getElementById('frontInput');
    const backInput = document.getElementById('backInput');
    const cardsContainer = document.getElementById('cardsContainer');

    function createCardElement(card) {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        cardElement.innerHTML = `
            <div class="card-front">${card.front}</div>
            <div class="card-back">${card.back}</div>
            <button class="mark-known-btn" data-id="${card.id}">✓</button>
            <button class="delete-btn" data-id="${card.id}">×</button>
        `;
        return cardElement; 
    }

    async function displayCards() {
        try {
            const cards = await fetchCards();
            cardsContainer.innerHTML = '';
            cards.forEach(card => {
                cardsContainer.appendChild(createCardElement(card));
            });
            
            // Обработчики для кнопок "✓"
            document.querySelectorAll('.mark-known-btn').forEach(btn => {
                btn.addEventListener('click', async function() {
                    const cardId = this.getAttribute('data-id');
                    await markCardAsKnown(cardId);
                    await displayCards();
                    await updateProgressBar();
                });
            });

            // Обработчики для кнопок удаления "×"
            document.querySelectorAll('.delete-btn').forEach(btn => {
                btn.addEventListener('click', async function() {
                    const cardId = this.getAttribute('data-id');
                    try {
                        await deleteCard(cardId);
                        await displayCards();
                        await updateProgressBar();
                    } catch (error) {
                        console.error('Error deleting card:', error);
                        alert('Failed to delete card');
                    }
                });
            });

        } catch (error) {
            console.error('Error loading cards:', error);
        }
    }

    async function updateProgressBar() {
        try {
            const progress = await getProgress();
            const percentage = progress.percentage;
            document.getElementById('progressBar').style.width = `${percentage}%`;
            document.getElementById('progressText').textContent = `${Math.round(percentage)}%`;
        } catch (error) {
            console.error('Error updating progress:', error);
        }
    }

    addCardBtn.addEventListener('click', async function() {
        if (!frontInput.value.trim() || !backInput.value.trim()) {
            alert('Please fill both fields');
            return;
        }

        try {
            await addNewCard(frontInput.value, backInput.value);
            frontInput.value = '';
            backInput.value = '';
            await displayCards();
            await updateProgressBar();
        } catch (error) {
            console.error('Error adding card:', error);
            alert('Error adding card');
        }
    });

    // Первоначальная загрузка
    displayCards();
    updateProgressBar();
});