(() => {
  const menuButton = document.querySelector('.menu-toggle');
  const menu = document.querySelector('#mobile-menu');
  const pageContent = [document.querySelector('main'), document.querySelector('footer')];
  function closeMenu(returnFocus = false) {
    menuButton.setAttribute('aria-expanded', 'false');
    menuButton.setAttribute('aria-label', 'メニューを開く');
    menu.hidden = true;
    document.body.classList.remove('menu-open');
    pageContent.forEach(element => { element.inert = false; });
    if (returnFocus) menuButton.focus();
  }
  menuButton.addEventListener('click', () => {
    const opening = menuButton.getAttribute('aria-expanded') !== 'true';
    menuButton.setAttribute('aria-expanded', String(opening));
    menuButton.setAttribute('aria-label', opening ? 'メニューを閉じる' : 'メニューを開く');
    menu.hidden = !opening;
    document.body.classList.toggle('menu-open', opening);
    pageContent.forEach(element => { element.inert = opening; });
  });
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !menu.hidden) closeMenu(true);
  });
  window.matchMedia('(min-width:901px)').addEventListener('change', event => {
    if (event.matches) closeMenu();
  });

  const tabs = [...document.querySelectorAll('[role="tab"]')];
  function activateTab(selected, focus = false) {
    tabs.forEach(tab => {
      const active = tab === selected;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
    });
    if (focus) selected.focus();
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', event => {
      let target;
      if (event.key === 'ArrowRight') target = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') target = (index + tabs.length - 1) % tabs.length;
      if (event.key === 'Home') target = 0;
      if (event.key === 'End') target = tabs.length - 1;
      if (target !== undefined) {
        event.preventDefault();
        activateTab(tabs[target], true);
      }
    });
  });

  const motionButton = document.querySelector('.motion-toggle');
  if (motionButton) motionButton.addEventListener('click', () => {
    const paused = document.documentElement.classList.toggle('motion-paused');
    motionButton.setAttribute('aria-pressed', String(paused));
    motionButton.textContent = paused ? '動きを再開する' : '動きを止める';
  });
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const items = [...document.querySelectorAll('.reveal')];
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.remove('pending');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.08 });
    document.documentElement.classList.add('js');
    items.forEach(item => {
      if (item.getBoundingClientRect().top > window.innerHeight) item.classList.add('pending');
      observer.observe(item);
    });
  }
})();
