// Toggle избранного и лайков с обновлением UI без перезагрузки.

async function toggle(url) {
    const res = await fetch(url, { method: 'POST', credentials: 'same-origin' });
    if (res.status === 401) { window.location.href = '/auth'; return null; }
    if (!res.ok) return null;
    return res.json();
}

document.addEventListener('click', async (e) => {
    const fav = e.target.closest('.card__fav, .js-fav');
    if (fav) {
        e.preventDefault();
        if (fav.dataset.needsAuth) { window.location.href = '/auth'; return; }
        const id = fav.dataset.recipeId;
        const data = await toggle(`/recipes/${id}/favorite`);
        if (data) {
            fav.classList.toggle('is-on', data.in_favorites);
            const txt = fav.querySelector('.js-fav-text');
            if (txt) txt.textContent = data.in_favorites ? 'В избранном' : 'В избранное';
        }
        return;
    }

    const like = e.target.closest('.js-like');
    if (like) {
        e.preventDefault();
        if (like.dataset.needsAuth) { window.location.href = '/auth'; return; }
        const id = like.dataset.recipeId;
        const data = await toggle(`/recipes/${id}/like`);
        if (data) {
            like.classList.toggle('is-on', data.liked);
            const cnt = like.querySelector('.js-like-count');
            if (cnt) cnt.textContent = data.count;
        }
    }
});
