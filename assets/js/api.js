const API_URL = window.location.origin + '/api';

async function fetchCards() {
    const response = await fetch(`${API_URL}/cards`);
    if (!response.ok) throw new Error('Network response was not ok');
    return await response.json();
}

async function addNewCard(front, back) {
    const response = await fetch(`${API_URL}/cards`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ front, back }),
    });
    if (!response.ok) throw new Error('Failed to add card');
    return await response.json();
}

async function markCardAsKnown(id) {
    const response = await fetch(`${API_URL}/cards/${id}/known`, {
        method: 'PUT',
    });
    if (!response.ok) throw new Error('Failed to mark card as known');
    return await response.json();
}

async function deleteCard(id) {
    try {
        const response = await fetch(`${API_URL}/cards/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to delete card');
        }
        return await response.json();
    } catch (error) {
        console.error('Delete error:', error);
        throw error;
    }
}
async function getProgress() {
    const response = await fetch(`${API_URL}/progress`);
    if (!response.ok) throw new Error('Failed to get progress');
    return await response.json();
}