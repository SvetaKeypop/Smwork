// Динамическое добавление и удаление полей ингредиентов и шагов.

const ingredients = document.getElementById('ingredients');
const steps = document.getElementById('steps');

document.getElementById('add-ingredient')?.addEventListener('click', () => {
    const row = document.createElement('div');
    row.className = 'ingredient-row';
    row.innerHTML = `
        <input type="text" name="ingredient_name" placeholder="название...">
        <input type="text" name="ingredient_amount" placeholder="кол-во">
        <button type="button" class="btn-remove" aria-label="Удалить">×</button>`;
    ingredients.appendChild(row);
});

document.getElementById('add-step')?.addEventListener('click', () => {
    const num = steps.children.length + 1;
    const row = document.createElement('div');
    row.className = 'step-row';
    row.innerHTML = `
        <span class="step__num">${num}</span>
        <textarea name="step_text" rows="2" placeholder="описание шага..."></textarea>
        <button type="button" class="btn-remove" aria-label="Удалить">×</button>`;
    steps.appendChild(row);
});

// Удаление строки + перенумерация шагов.
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-remove');
    if (!btn) return;
    const row = btn.parentElement;
    const parent = row.parentElement;
    if (parent.children.length > 1) row.remove();
    if (parent.id === 'steps') {
        [...parent.children].forEach((r, i) => {
            r.querySelector('.step__num').textContent = i + 1;
        });
    }
});

// Показать имя выбранного файла в зоне загрузки.
const upload = document.querySelector('.upload');
upload?.querySelector('input[type=file]').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) upload.querySelector('.upload__text').textContent = file.name;
});
