// Клиентский поиск рецептов по названию (фильтрация карточек на странице).
const input = document.getElementById('recipe-search');
input?.addEventListener('input', (e) => {
    const q = e.target.value.trim().toLowerCase();
    document.querySelectorAll('.card').forEach((card) => {
        const title = card.dataset.title || '';
        card.style.display = title.includes(q) ? '' : 'none';
    });
});
