/* RaceStay — shared behaviour across all pages */
function setLang(l){
  document.querySelectorAll('[data-th]').forEach(function(el){
    var v=(l==='en')?el.getAttribute('data-en'):el.getAttribute('data-th');
    if(v===null)return;
    if(el.tagName==='TITLE'){document.title=v;return;}
    if(!el.querySelector('[data-th]')) el.innerHTML=v;
  });
  document.querySelectorAll('[data-th-ph]').forEach(function(el){
    el.setAttribute('placeholder',(l==='en')?el.getAttribute('data-en-ph'):el.getAttribute('data-th-ph'));
  });
  document.documentElement.lang=l;
  document.querySelectorAll('[data-setlang]').forEach(function(b){ b.classList.toggle('on', b.getAttribute('data-setlang')===l); });
  try{ localStorage.setItem('rs-lang',l); }catch(e){}
}

/* ----- race-detail page only (guards keep it safe elsewhere) ----- */
function setTab(t){
  var el;
  if(el=document.getElementById('tab-a')) el.classList.toggle('on',t==='a');
  if(el=document.getElementById('tab-b')) el.classList.toggle('on',t==='b');
  if(el=document.getElementById('pane-a')) el.classList.toggle('on',t==='a');
  if(el=document.getElementById('pane-b')) el.classList.toggle('on',t==='b');
}
function setStay(s){
  var el;
  if(el=document.getElementById('st-start')) el.classList.toggle('on',s==='start');
  if(el=document.getElementById('st-finish')) el.classList.toggle('on',s==='finish');
  if(el=document.getElementById('bstay-start')) el.classList.toggle('on',s==='start');
  if(el=document.getElementById('bstay-finish')) el.classList.toggle('on',s==='finish');
}
function setPrice(btn,min,max){
  var bar=btn.closest('.pricebar');
  bar.querySelectorAll('.pchip').forEach(function(c){c.classList.toggle('on',c===btn)});
  var f=document.getElementById(bar.getAttribute('data-map'));
  var src=f.getAttribute('data-base');
  if(min) src+='&min='+min;
  if(max) src+='&max='+max;
  f.src=src;
}

/* ----- home page: filter races by sport ----- */
function filterSport(btn, sport){
  var bar=btn.closest('.sportbar');
  if(bar) bar.querySelectorAll('.pchip').forEach(function(c){c.classList.toggle('on',c===btn)});
  var shown=0;
  document.querySelectorAll('#races .grid [data-sport]').forEach(function(el){
    var ok=(sport==='all'||el.getAttribute('data-sport')===sport);
    el.style.display=ok?'':'none'; if(ok) shown++;
  });
  var ec=document.getElementById('evcount'); if(ec) ec.textContent=shown;
}

/* ----- header hamburger menu ----- */
function toggleMenu(btn){
  var m=document.getElementById('menu'); if(!m) return;
  var open=m.classList.toggle('open');
  if(btn) btn.setAttribute('aria-expanded', open?'true':'false');
}
document.addEventListener('keydown',function(e){
  if(e.key==='Escape'){ var m=document.getElementById('menu'); if(m){ m.classList.remove('open'); var b=document.querySelector('.menubtn'); if(b) b.setAttribute('aria-expanded','false'); } }
});
document.addEventListener('click',function(e){
  var m=document.getElementById('menu'); if(!m||!m.classList.contains('open')) return;
  if(e.target.closest('#menu')||e.target.closest('.menubtn')) return;
  m.classList.remove('open');
  var b=document.querySelector('.menubtn'); if(b) b.setAttribute('aria-expanded','false');
});

/* ----- unified segmented control (sliding thumb) ----- */
function segSyncAll(){
  document.querySelectorAll('.seg').forEach(function(seg){
    var th=seg.querySelector('.seg-thumb'); if(!th) return;
    var act=seg.querySelector('.seg-item.on,.seg-item.active');
    if(!act){ th.style.opacity='0'; return; }
    th.style.opacity='1';
    th.style.width=act.offsetWidth+'px';
    th.style.height=act.offsetHeight+'px';
    th.style.transform='translate('+act.offsetLeft+'px,'+act.offsetTop+'px)';
  });
}
function initSegments(){
  document.querySelectorAll('.seg').forEach(function(seg){
    if(!seg.querySelector('.seg-thumb')){
      var th=document.createElement('span'); th.className='seg-thumb';
      seg.insertBefore(th, seg.firstChild);
    }
    seg.querySelectorAll('.seg-item').forEach(function(it){
      it.addEventListener('click', function(){ requestAnimationFrame(segSyncAll); });
    });
  });
  segSyncAll();
}
window.addEventListener('resize', function(){ segSyncAll(); });

/* apply saved language on every page load */
document.addEventListener('DOMContentLoaded',function(){
  var l='th';
  try{ l=localStorage.getItem('rs-lang')||'th'; }catch(e){}
  setLang(l);

  var sp=null; try{ sp=new URLSearchParams(location.search).get('sport'); }catch(e){}
  if(sp){
    var chip=document.querySelector('.sportbar .pchip[data-sport="'+sp+'"]');
    if(chip){ filterSport(chip,sp); var r=document.getElementById('races'); if(r) r.scrollIntoView(); }
  }

  initSegments();
  var ec=document.getElementById('evcount');
  if(ec) ec.textContent=[].filter.call(document.querySelectorAll('#races .grid .card'),function(c){return c.style.display!=='none';}).length;
});
