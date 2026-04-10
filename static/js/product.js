(function(){
  const main = document.querySelector('.product-main-img');
  const thumbsWrap = document.querySelector('[data-thumbs]');
  const lightbox = document.getElementById('lightbox');

  // Collect image sources (main + thumbs)
  const sources = [];
  function uniqPush(src){
    if(!src) return;
    if(!sources.includes(src)) sources.push(src);
  }
  if(main) uniqPush(main.getAttribute('src'));

  if(thumbsWrap){
    thumbsWrap.querySelectorAll('button[data-img-src]').forEach(btn=>{
      uniqPush(btn.getAttribute('data-img-src'));
    });
  }

  // --- Main image swap with light zoom-in ---
  function swapMain(src){
    if(!main || !src) return;
    if(main.getAttribute('src') === src) return;

    main.classList.add('is-changing');
    const onLoad = () => {
      main.removeEventListener('load', onLoad);
      // вернуть в норму после кадра
      requestAnimationFrame(() => main.classList.remove('is-changing'));
    };
    main.addEventListener('load', onLoad);
    main.setAttribute('src', src);
  }

  if(thumbsWrap && main){
    thumbsWrap.addEventListener('click', (e)=>{
      const btn = e.target.closest('button[data-img-src]');
      if(!btn) return;
      const src = btn.getAttribute('data-img-src');
      swapMain(src);

      thumbsWrap.querySelectorAll('.thumb').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');

      // плавно проскроллить ленту так, чтобы активная была видна
      btn.scrollIntoView({behavior:'smooth', inline:'center', block:'nearest'});
    });

    const first = thumbsWrap.querySelector('.thumb');
    if(first) first.classList.add('active');
  }

  // --- Lightbox (modal) ---
  if(!lightbox || sources.length === 0) return;

  const lbImg = lightbox.querySelector('[data-lb-img]');
  const lbCounter = lightbox.querySelector('[data-lb-counter]');
  const btnPrev = lightbox.querySelector('[data-lb-prev]');
  const btnNext = lightbox.querySelector('[data-lb-next]');
  let index = 0;

  function render(){
    const src = sources[index];
    lbImg.classList.add('is-zoom');
    const onLoad = () => {
      lbImg.removeEventListener('load', onLoad);
      requestAnimationFrame(() => lbImg.classList.remove('is-zoom'));
    };
    lbImg.addEventListener('load', onLoad);
    lbImg.setAttribute('src', src);
    if(lbCounter) lbCounter.textContent = `${index+1} / ${sources.length}`;
  }

  function openAt(src){
    const i = sources.indexOf(src);
    index = i >= 0 ? i : 0;
    lightbox.classList.add('is-open');
    lightbox.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
    render();
  }

  function close(){
    lightbox.classList.remove('is-open');
    lightbox.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
  }

  function prev(){
    index = (index - 1 + sources.length) % sources.length;
    render();
  }
  function next(){
    index = (index + 1) % sources.length;
    render();
  }

  // open on click main image
  if(main){
    main.style.cursor = 'zoom-in';
    main.addEventListener('click', ()=> openAt(main.getAttribute('src')));
  }

  // close handlers
  lightbox.querySelectorAll('[data-lb-close]').forEach(el=>{
    el.addEventListener('click', close);
  });
  btnPrev && btnPrev.addEventListener('click', prev);
  btnNext && btnNext.addEventListener('click', next);

  // keyboard
  document.addEventListener('keydown', (e)=>{
    if(!lightbox.classList.contains('is-open')) return;
    if(e.key === 'Escape') close();
    if(e.key === 'ArrowLeft') prev();
    if(e.key === 'ArrowRight') next();
  });

  // basic swipe (touch)
  let startX = null;
  lbImg.addEventListener('touchstart', (e)=>{
    startX = e.touches[0].clientX;
  }, {passive:true});
  lbImg.addEventListener('touchend', (e)=>{
    if(startX === null) return;
    const endX = (e.changedTouches && e.changedTouches[0]) ? e.changedTouches[0].clientX : startX;
    const dx = endX - startX;
    startX = null;
    if(Math.abs(dx) < 40) return;
    if(dx > 0) prev(); else next();
  });
})();