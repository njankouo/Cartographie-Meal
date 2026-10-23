
(function(){
  var root=document.documentElement, btns=document.querySelectorAll('.lang-switch button');
  function setLang(l){
    root.setAttribute('lang',l);
    btns.forEach(function(b){b.setAttribute('aria-pressed',b.dataset.lang===l?'true':'false')});
    try{localStorage.setItem('ma-lang',l)}catch(e){}
  }
  btns.forEach(function(b){b.addEventListener('click',function(){setLang(b.dataset.lang)})});
  try{var s=localStorage.getItem('ma-lang'); if(s==='fr'||s==='en') setLang(s);}catch(e){}
})();

/* ═════════ Dynamisme ═════════ */
(function(){
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $$ = function(s){return Array.prototype.slice.call(document.querySelectorAll(s))};

  var links=$$('.nav a');

  /* Flèches des boutons : animées au survol */
  $$('.btn').forEach(function(b){
    b.childNodes.forEach(function(n){
      if(n.nodeType===3 && n.textContent.indexOf('→')>-1){
        var sp=document.createElement('span');sp.className='arrow-anim';sp.setAttribute('aria-hidden','true');sp.textContent='→';
        n.textContent=n.textContent.replace('→','');n.after(sp);
      }
    });
    var a=b.querySelector('span[aria-hidden="true"]');
    if(a && a.textContent.trim()==='→') a.classList.add('arrow-anim');
  });

  /* Barre de lecture, bouton haut */
  var prog=document.getElementById('readProgress'), top=document.getElementById('toTop');
  function onScroll(){
    var y=scrollY, max=document.documentElement.scrollHeight-innerHeight;
    prog.style.transform='scaleX('+(max>0?y/max:0)+')';
    top.classList.toggle('show', y>innerHeight*.8);
  }
  addEventListener('scroll',onScroll,{passive:true}); onScroll();
  top.addEventListener('click',function(){scrollTo({top:0,behavior:reduce?'auto':'smooth'})});

  /* Nav : onglet actif selon la section visible */
  if('IntersectionObserver' in window){
    var sio=new IntersectionObserver(function(es){es.forEach(function(e){
      if(!e.isIntersecting) return;
      links.forEach(function(l){l.classList.toggle('on', l.getAttribute('href')==='#'+e.target.id)});
    })},{rootMargin:'-40% 0px -55% 0px'});
    links.forEach(function(l){var t=document.querySelector(l.getAttribute('href')); if(t) sio.observe(t)});
  }

  /* Liens externes : icône ↗ et mention « nouvel onglet » pour les lecteurs d'écran */
  $$('a[target="_blank"]').forEach(function(a){
    var arrow=a.querySelector('.arrow-anim');
    var ext=document.createElement('span');ext.className='ext';ext.setAttribute('aria-hidden','true');ext.textContent='↗';
    if(arrow){arrow.replaceWith(ext)} else if(!a.classList.contains('issue')) a.appendChild(ext);
    var sr=document.createElement('span');sr.className='sr';
    sr.innerHTML='<span lang="fr"> (nouvel onglet)</span><span lang="en"> (new tab)</span>';a.appendChild(sr);
  });

  /* Fil d'actualités : bouton pause / lecture */
  var tk=document.querySelector('.ticker'), tg=document.getElementById('tickerToggle');
  if(tk&&tg){
    function setPaused(p){tk.classList.toggle('paused',p);tg.setAttribute('aria-pressed',p?'true':'false');
      tg.querySelectorAll('.sr').forEach(function(x){x.textContent=x.lang==='fr'?(p?'Relancer le fil':'Mettre en pause le fil'):(p?'Resume the feed':'Pause the feed')})}
    tg.addEventListener('click',function(){setPaused(!tk.classList.contains('paused'))});
    if(reduce) setPaused(true);
  }

  /* Onglet actif annoncé aux lecteurs d'écran */
  var navObs=new MutationObserver(function(){links.forEach(function(l){l.classList.contains('on')?l.setAttribute('aria-current','true'):l.removeAttribute('aria-current')})});
  links.forEach(function(l){navObs.observe(l,{attributes:true,attributeFilter:['class']})});

  /* Compte à rebours AfrEA */
  $$('[data-countdown]').forEach(function(el){
    var d=Math.ceil((new Date(el.dataset.countdown+'T09:00:00')-new Date())/864e5);
    if(d>0){el.querySelector('b').innerHTML='<span lang="fr">J-'+d+'</span><span lang="en">'+d+(d>1?' days':' day')+'</span>';el.hidden=false;}
  });

  if(reduce || !('IntersectionObserver' in window)){ $$('.lead,.cta').forEach(function(e){e.classList.add('in')}); return; }

  /* Apparition au défilement, en cascade */
  var targets=$$('.lead,.side > *,.section-head,.issue,.opera-intro,.tool,.cta,.perks li,.foot > div');
  targets.forEach(function(el){
    el.classList.add('reveal');
    var sib=Array.prototype.filter.call(el.parentNode.children,function(c){return targets.indexOf(c)>-1});
    el.style.transitionDelay=(sib.indexOf(el)%6)*90+'ms';
  });
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}
  })},{threshold:.12,rootMargin:'0px 0px -40px 0px'});
  targets.forEach(function(el){io.observe(el)});
  setTimeout(function(){targets.forEach(function(el){el.classList.add('in')})},4000);

})();

/* Ajout : section « À propos » : apparition au défilement, compteurs et parts qui se remplissent */
(function(){
  var cols=[].slice.call(document.querySelectorAll('.about > *')), box=document.querySelector('.about-stats');
  if(!box) return;
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var nums=[].slice.call(box.querySelectorAll('[data-count],[data-count-n]')).map(function(el){
    var target=parseInt(el.dataset.count||el.dataset.countN,10);
    return {el:el,target:target,fr:el.querySelector('[lang="fr"]'),en:el.querySelector('[lang="en"]')};
  });
  function paint(n,v){n.fr.textContent=v.toLocaleString('fr-FR');n.en.textContent=v.toLocaleString('en-US')}

  if(reduce||!('IntersectionObserver' in window)){cols.forEach(function(c){c.classList.add('in')});return;}

  cols.forEach(function(c,i){c.classList.add('reveal');c.style.transitionDelay=(i*90)+'ms'});
  nums.forEach(function(n){paint(n,0)});          /* les compteurs partent de zéro, sans saut visuel avant l'entrée */

  function count(){
    var t0=null, dur=1400;
    function step(t){
      if(t0===null) t0=t;
      var p=Math.min(1,(t-t0)/dur), e=1-Math.pow(1-p,3);
      nums.forEach(function(n){paint(n,Math.round(n.target*e))});
      if(p<1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  var io=new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting) return;
    cols.forEach(function(c){c.classList.add('in')});
    count(); io.disconnect();
  })},{threshold:.25});
  io.observe(box);
})();
