(() => {
  const group = document.querySelector('.column-filters');
  const results = document.querySelector('#column-results');
  const count = document.querySelector('#column-count');
  if (!group || !results || !count) return;
  const cards = [...results.querySelectorAll('.column-card')];
  const buttons = [...group.querySelectorAll('button[data-filter]')];
  group.hidden = false;
  buttons.forEach(button => button.addEventListener('click', () => {
    const category = button.dataset.filter;
    buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    cards.forEach(card => { card.hidden = category !== 'all' && card.dataset.category !== category; });
    const total = cards.filter(card => !card.hidden).length;
    count.textContent = category === 'all' ? `${total}件の記事` : `${category}：${total}件の記事`;
  }));
})();
