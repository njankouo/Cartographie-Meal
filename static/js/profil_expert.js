

(function(){
  const PROFILE={nom:"Dr Aminata Diallo",titre:"Évaluatrice senior MEAL",mail:"aminata.diallo@exemple.org",tel:"+221771234567",ville:"Dakar",pays:"Sénégal",url:location.href.split('#')[0]};
  const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
  function toast(m){const t=$('#toast');t.textContent=m;t.classList.add('show');clearTimeout(t._h);t._h=setTimeout(()=>t.classList.remove('show'),2200)}

  /* Partage, lien et QR construits sur l'URL réelle */
  const u=encodeURIComponent(PROFILE.url), t=encodeURIComponent(`${PROFILE.nom} - ${PROFILE.titre} | Expert MEAL Afrique`);
  const L={linkedin:`https://www.linkedin.com/sharing/share-offsite/?url=${u}`,whatsapp:`https://wa.me/?text=${t}%20${u}`,facebook:`https://www.facebook.com/sharer/sharer.php?u=${u}`,x:`https://twitter.com/intent/tweet?text=${t}&url=${u}`,telegram:`https://t.me/share/url?url=${u}&text=${t}`,email:`mailto:?subject=${encodeURIComponent('Profil expert MEAL : '+PROFILE.nom)}&body=${encodeURIComponent("Je vous recommande ce profil d'expert MEAL : ")}${u}`};
  $$('[data-share]').forEach(a=>a.href=L[a.dataset.share]);
  $('#linkField').value=PROFILE.url;
  const qr=(s,m)=>`https://api.qrserver.com/v1/create-qr-code/?size=${s}x${s}&margin=${m}&color=0D2B5C&data=${u}`;
  $('#qrImg').src=qr(264,0); $('#qrDl').href=qr(800,16)+'&format=png';

  /* E-mail de proposition pré-rempli */
  const body=`Bonjour ${PROFILE.nom},\n\nJ'ai consulté votre profil d'expert sur MEAL Afrique et souhaiterais vous proposer une mission.\n\nOrganisation :\nNature de la mission :\nPériode et durée :\nLieu :\nBudget indicatif :\n\nCordialement,`;
  $('#mailBtn').href=`mailto:${PROFILE.mail}?subject=${encodeURIComponent('Proposition de mission MEAL - via MEAL Afrique')}&body=${encodeURIComponent(body)}`;

  /* Copier le lien */
  $('#copyBtn').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(PROFILE.url)}catch(e){const f=$('#linkField');f.select();document.execCommand('copy')}toast('Lien copié')});

  /* Partage natif, sinon section Partager */
  $$('[data-share-native]').forEach(b=>b.addEventListener('click',async()=>{
    if(navigator.share){try{await navigator.share({title:`${PROFILE.nom} - Expert MEAL Afrique`,text:`${PROFILE.nom}, ${PROFILE.titre}`,url:PROFILE.url});return}catch(e){if(e.name==='AbortError')return}}
    $('#partager').scrollIntoView({behavior:'smooth'});
  }));

  /* vCard */
  $('#vcardBtn').addEventListener('click',()=>{
    const v=['BEGIN:VCARD','VERSION:3.0',`FN:${PROFILE.nom}`,`TITLE:${PROFILE.titre}`,'ORG:MEAL Afrique',`EMAIL;TYPE=WORK:${PROFILE.mail}`,`TEL;TYPE=CELL:${PROFILE.tel}`,`ADR;TYPE=WORK:;;;${PROFILE.ville};;;${PROFILE.pays}`,`URL:${PROFILE.url}`,'NOTE:Expert MEAL - communauté MEAL Afrique (OPERAPLUS)','END:VCARD'].join('\r\n');
    const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([v],{type:'text/vcard;charset=utf-8'}));a.download='Aminata-Diallo-MEAL.vcf';document.body.appendChild(a);a.click();a.remove();toast('Contact téléchargé');
  });

  /* Navigation : bordure au défilement, lien actif, barre mobile */
  const nav=$('#nav'),mbar=$('#mbar'),hero=$('#top');
  function onScroll(){const y=scrollY;nav.classList.toggle('scrolled',y>8);mbar.classList.toggle('show',y>hero.offsetHeight*.6)}
  addEventListener('scroll',onScroll,{passive:true});onScroll();
  const links=[...$$('.nav-links a')];
  const sio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id))}}),{rootMargin:'-45% 0px -50% 0px'});
  links.forEach(l=>{const s=document.querySelector(l.getAttribute('href'));if(s)sio.observe(s)});

  /* Apparition discrète (contenu visible sans JS ou mouvement réduit) */
  if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window)){document.documentElement.classList.remove('js');return}
  const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.12,rootMargin:'0px 0px -40px 0px'});
  $$('.rv').forEach(el=>io.observe(el));
  setTimeout(()=>$$('.rv').forEach(el=>el.classList.add('in')),3000);
})();

<!-- ═════════ Améliorations UI/UX (script ajouté, indépendant du précédent) ═════════ -->

(function(){
  const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s);
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Menu mobile */
  const mb=$('#menuBtn'), mn=$('#mnav');
  function closeMenu(){mn.hidden=true;mb.setAttribute('aria-expanded','false');mb.setAttribute('aria-label','Ouvrir le menu')}
  mb.addEventListener('click',()=>{const open=mn.hidden;mn.hidden=!open;mb.setAttribute('aria-expanded',String(open));mb.setAttribute('aria-label',open?'Fermer le menu':'Ouvrir le menu')});
  mn.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
  addEventListener('keydown',e=>{if(e.key==='Escape'&&!mn.hidden){closeMenu();mb.focus()}});
  const desk=[...$$('.nav-links a')], mob=[...mn.querySelectorAll('a')];
  const mo=new MutationObserver(()=>desk.forEach((d,i)=>mob[i]&&mob[i].classList.toggle('active',d.classList.contains('active'))));
  desk.forEach(d=>mo.observe(d,{attributes:true,attributeFilter:['class']}));

  /* Barre de progression, rail du parcours, retour en haut */
  const prog=$('#progress'), totop=$('#totop');
  const tlw=$('.timeline'), rail=tlw&&tlw.querySelector('.rail'), items=tlw?[...tlw.querySelectorAll('.tl')]:[];
  let ticking=false;
  function update(){
    ticking=false;
    const max=document.documentElement.scrollHeight-innerHeight;
    prog.style.transform='scaleX('+(max>0?Math.min(scrollY/max,1):0)+')';
    totop.classList.toggle('show',scrollY>900);
    if(tlw){const r=tlw.getBoundingClientRect(),mid=innerHeight*.6;
      rail.style.height=Math.max(0,Math.min(r.height,mid-r.top))+'px';
      items.forEach(it=>it.classList.toggle('lit',it.getBoundingClientRect().top+37<mid));}
  }
  addEventListener('scroll',()=>{if(!ticking){ticking=true;requestAnimationFrame(update)}},{passive:true});
  addEventListener('resize',update);update();
  totop.addEventListener('click',()=>scrollTo({top:0,behavior:reduce?'auto':'smooth'}));

  /* Chiffres clés : comptage animé */
  const figs=$$('.fig');
  function count(f){
    const n=f.querySelector('b').firstChild, end=parseInt(n.textContent,10);
    if(reduce||isNaN(end))return;
    const t0=performance.now(),d=1400;
    (function step(t){const p=Math.min((t-t0)/d,1);n.textContent=Math.round(end*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(step)})(t0);
  }
  if('IntersectionObserver' in window){
    const fio=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');count(e.target);fio.unobserve(e.target)}}),{threshold:.5});
    figs.forEach(f=>fio.observe(f));
  }else figs.forEach(f=>f.classList.add('in'));

  /* Contact : types de mission sélectionnables → message pré-rempli */
  const mailBtn=$('#mailBtn'), mail=mailBtn.getAttribute('href').replace(/^mailto:/,'').split('?')[0];
  const nom=document.title.split(' - ')[0].trim();
  const offers=[...$$('.offer li')];
  function buildMail(){
    const sel=offers.filter(li=>li.getAttribute('aria-pressed')==='true').map(li=>li.textContent.trim());
    const nature=sel.length?sel.join(', '):'';
    const body=`Bonjour ${nom},\n\nJ'ai consulté votre profil d'expert sur MEAL Afrique et souhaiterais vous proposer une mission.\n\nOrganisation :\nNature de la mission : ${nature}\nPériode et durée :\nLieu :\nBudget indicatif :\n\nCordialement,`;
    const subj='Proposition de mission MEAL'+(sel.length===1?' ('+sel[0]+')':'')+' - via MEAL Afrique';
    mailBtn.href=`mailto:${mail}?subject=${encodeURIComponent(subj)}&body=${encodeURIComponent(body)}`;
  }
  offers.forEach(li=>{
    li.setAttribute('role','button');li.setAttribute('tabindex','0');li.setAttribute('aria-pressed','false');
    const tog=()=>{li.setAttribute('aria-pressed',li.getAttribute('aria-pressed')==='true'?'false':'true');buildMail()};
    li.addEventListener('click',tog);
    li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();tog()}});
  });
})();


<!-- ═════════ Entrée dynamique : mots du nom, parallaxe, rideau ═════════ -->

(function(){
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const intro=document.querySelector('.intro');
  if(intro){if(reduce)intro.remove();else intro.addEventListener('animationend',e=>{if(e.animationName==='curtain')intro.remove()});setTimeout(()=>intro.isConnected&&intro.remove(),2500)}
  if(reduce)return;

  /* Nom révélé mot par mot (fonctionne avec {{personnel.nom}} rendu par Django) */
  const h=document.querySelector('.hero h1');
  if(h){
    let i=0;
    const walk=node=>[...node.childNodes].forEach(c=>{
      if(c.nodeType===3){
        const f=document.createDocumentFragment();
        c.textContent.split(/(\s+)/).forEach(p=>{
          if(!p)return;
          if(/^\s+$/.test(p)){f.appendChild(document.createTextNode(p));return}
          const w=document.createElement('span'),wi=document.createElement('span');
          w.className='w';wi.className='wi';wi.textContent=p;wi.style.animationDelay=(.8+i++*.12)+'s';
          w.appendChild(wi);f.appendChild(w);
        });
        c.replaceWith(f);
      }else if(c.nodeType===1&&c.namespaceURI!=='http://www.w3.org/2000/svg')walk(c);
    });
    walk(h);
  }

  /* Parallaxe du portrait à la souris */
  const hero=document.getElementById('top');
  if(hero&&matchMedia('(hover: hover)').matches){
    hero.addEventListener('pointermove',e=>{
      const r=hero.getBoundingClientRect();
      hero.style.setProperty('--mx',((e.clientX-r.left)/r.width-.5).toFixed(3));
      hero.style.setProperty('--my',((e.clientY-r.top)/r.height-.5).toFixed(3));
    });
    hero.addEventListener('pointerleave',()=>{hero.style.setProperty('--mx',0);hero.style.setProperty('--my',0)});
  }
})();
