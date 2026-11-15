/* RaceStay — shared behaviour across all pages */
var EN2TH={JAN:'ม.ค.',FEB:'ก.พ.',MAR:'มี.ค.',APR:'เม.ย.',MAY:'พ.ค.',JUN:'มิ.ย.',JUL:'ก.ค.',AUG:'ส.ค.',SEP:'ก.ย.',OCT:'ต.ค.',NOV:'พ.ย.',DEC:'ธ.ค.',TBA:'รอยืนยัน'};
var TH2EN={}; (function(){for(var k in EN2TH)TH2EN[EN2TH[k]]=k;})();
var RE_EN=/\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|TBA)\b/g;
var RE_TH=/(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.|รอยืนยัน)/g;
function localizeDates(l){
  var roots=document.querySelectorAll('.when, .databand, .feature, table, .dcover, .statpanel');
  for(var i=0;i<roots.length;i++){
    var w=document.createTreeWalker(roots[i], NodeFilter.SHOW_TEXT, null);
    var n;
    while(n=w.nextNode()){
      var t=n.nodeValue;
      if(l==='th'){ if(t.indexOf('/')===-1 && RE_EN.test(t)){ RE_EN.lastIndex=0; n.nodeValue=t.replace(RE_EN,function(m){return EN2TH[m];}); } }
      else { if(RE_TH.test(t)){ RE_TH.lastIndex=0; n.nodeValue=t.replace(RE_TH,function(m){return TH2EN[m];}); } }
    }
  }
}
/* Thai has no spaces: the browser breaks lines at dictionary word boundaries, which can split a
   compound (ระยะ|เดิน) or a name (เฮอ|ริเทจ). Wrap known phrases, and numbers with their unit or
   month, in a no-wrap span so each moves to the next line whole. Runs after every language switch. */
var KEEP_TH=['ทรานซิชัน','อุทยานแห่งชาติ','ดอยอินทนนท์','อบจ.เชียงใหม่','ระยะเดิน','จุดปล่อยตัว','ปล่อยตัว','จุดสตาร์ท','เส้นชัย','เข้าเส้นชัย','รอยืนยัน','รับบิบ','เช้ามืด','กลางคืน','กลางดึก',
  'ก่อนแข่ง','หลังแข่ง','วันแข่ง','สุดสัปดาห์','เดินทาง','ล่วงหน้า','ติดกัน','หารถ','ก่อนกด','เช็กอิน','เช็กเอาต์','เช็คอิน','เช็คเอาต์',
  'แพ็กเกจ','ไตรกีฬา','ไฮรอกซ์','วิ่งเทรล','วิ่งถนน','สวนน้ำ','ศูนย์ประชุม','เฮอริเทจ','อินเตอร์เนชั่นแนล','เซอร์กิต','มหาราชวัง',
  'กาญจนาภิเษก','ท่าเตียน','ช้างเผือก','นาเกลือ','วงเวียนโลมา','เชิงทะเล','ลากูน่า','ย่าโม','ฝั่งเหนือ','บุ่งตาหลั่ว','รัตนโกสินทร์',
  'สนามหลวง','สนามไชย','สนามช้าง','เชียงใหม่','ขอนแก่น','อุดมสุข','ไบเทค','บางนา','เขาใหญ่','ปากช่อง','จอมทอง','แม่ริม','ปทุมวัน',
  'เจ้าพระยา','ท่าแพ','ไนท์บาซาร์','พระบรมราชานุสาวรีย์','พระบรมมหาราชวัง','อนุสาวรีย์','อารีน่า','บางแสน'];
var RE_KEEP=new RegExp('('+
  KEEP_TH.sort(function(a,b){return b.length-a.length;}).map(function(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}).join('|')+
  '|฿\\d[\\d,]*'+
  '|ตี\\s\\d+'+
  '|\\d+(?:[.,]\\d+)?(?:\\s?[–-]\\s?\\d+(?:[.,]\\d+)?)?\\s(?:กม\\.|ม\\.(?!ค\\.)|km|K\\b|นาที|ชม\\.|ชั่วโมง|วัน|คืน|ดาว|บาท|คน|'+
  '(?:ม\\.ค\\.|ก\\.พ\\.|มี\\.ค\\.|เม\\.ย\\.|พ\\.ค\\.|มิ\\.ย\\.|ก\\.ค\\.|ส\\.ค\\.|ก\\.ย\\.|ต\\.ค\\.|พ\\.ย\\.|ธ\\.ค\\.)|'+
  '(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\b)'+
  ')','g');
function keepTogether(){
  var w=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {acceptNode:function(n){
    var p=n.parentNode; if(!p||!n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
    if(/^(SCRIPT|STYLE|TEXTAREA|OPTION|TITLE)$/.test(p.nodeName)||p.closest('.nobr,svg')) return NodeFilter.FILTER_REJECT;
    RE_KEEP.lastIndex=0; return RE_KEEP.test(n.nodeValue)?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT; }});
  var hits=[],n; while(n=w.nextNode()) hits.push(n);
  hits.forEach(function(n){
    var t=n.nodeValue,f=document.createDocumentFragment(),last=0,m; RE_KEEP.lastIndex=0;
    while(m=RE_KEEP.exec(t)){
      if(m.index>last) f.appendChild(document.createTextNode(t.slice(last,m.index)));
      var s=document.createElement('span'); s.className='nobr'; s.textContent=m[0]; f.appendChild(s); last=m.index+m[0].length;
    }
    if(last<t.length) f.appendChild(document.createTextNode(t.slice(last)));
    if(/flex|grid/.test(getComputedStyle(n.parentNode).display)){ var box=document.createElement('span'); box.appendChild(f); f=box; }
    n.parentNode.replaceChild(f,n);
  });
}
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
  [['title','title'],['aria','aria-label']].forEach(function(a){
    document.querySelectorAll('[data-th-'+a[0]+']').forEach(function(el){
      el.setAttribute(a[1],el.getAttribute('data-'+l+'-'+a[0]));
    });
  });
  document.documentElement.lang=l;
  localizeDates(l);
  document.querySelectorAll('[data-setlang]').forEach(function(b){ b.classList.toggle('on', b.getAttribute('data-setlang')===l); });
  try{ localStorage.setItem('rs-lang',l); }catch(e){}
  countdowns();
  keepTogether();
  fitDesc();
  sizeTopBg();
  requestAnimationFrame(function(){ if(typeof segSyncAll==='function') segSyncAll(); if(window.navSecSync) navSecSync(); });
}

/* ----- race-detail page only (guards keep it safe elsewhere) ----- */
/* Event cards: show as many whole description lines as fit under the title (CSS alone must assume a 2-line title) */
function fitDesc(){
  document.querySelectorAll('.evcard .desc').forEach(function(d){
    d.style.webkitLineClamp='';
    var b=d.parentElement, lh=parseFloat(getComputedStyle(d).lineHeight);
    if(!b.offsetHeight||!lh) return;
    var room=b.getBoundingClientRect().bottom-parseFloat(getComputedStyle(b).paddingBottom)-d.getBoundingClientRect().top;
    d.style.webkitLineClamp=String(Math.max(1,Math.floor((room+1)/lh)));
  });
}
/* Days to race day, counted live (Bangkok midnight) so the number never goes stale */
function countdowns(){
  var en=document.documentElement.lang==='en';
  document.querySelectorAll('[data-countdown]').forEach(function(el){
    var t=new Date(el.getAttribute('data-countdown')+'T00:00:00+07:00').getTime();
    var days=Math.ceil((t-Date.now())/86400000);
    if(days>0 && el.hasAttribute('data-countdown-text')) el.textContent=en?(days+(days===1?' day':' days')+' to go'):('อีก '+days+' วัน');
    else if(days>0) el.innerHTML=days+'<small>'+(en?(days===1?' day':' days'):' วัน')+'</small>';
    else el.textContent=(days===0)?(en?'Race day':'วันนี้'):(en?'Finished':'จบแล้ว');
  });
}
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
  document.querySelectorAll('[data-stay]').forEach(function(x){ x.classList.toggle('on', x.getAttribute('data-stay')===s); });
  if(typeof segSyncAll==='function') segSyncAll();
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

/* ----- home page: filter the events marquee into a static grid by sport ----- */
function applyFilter(sport){
  var mq=document.querySelector('.mq-events'); if(!mq) return;
  var reset=document.getElementById('filterReset');
  if(!sport || sport==='all'){
    mq.classList.remove('filtering');
    mq.querySelectorAll('.evcard').forEach(function(c){ c.style.display=''; });
    if(mq._mq){ mq._mq.todo=0; mq._mq.set(0); }
    if(reset) reset.style.display='none';
    fitDesc();
    return;
  }
  mq.classList.add('filtering');                 // CSS: stop animation, grid layout, hide duplicate group
  var first=mq.querySelector('.mq-group');
  if(first) first.querySelectorAll('.evcard').forEach(function(c){
    c.style.display=(c.getAttribute('data-sport')===sport)?'':'none';
  });
  if(reset) reset.style.display='';
  fitDesc();
}
function clearFilter(){
  applyFilter('all');
  try{ history.replaceState(null,'','index.html#races'); }catch(e){}
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
      /* first placement is instant: otherwise the thumb grows sideways from 0 on every page load */
      th.style.transition='none';
      seg.insertBefore(th, seg.firstChild);
    }
    seg.querySelectorAll('.seg-item').forEach(function(it){
      it.addEventListener('click', function(){ requestAnimationFrame(segSyncAll); });
    });
  });
  segSyncAll();
  requestAnimationFrame(function(){ requestAnimationFrame(function(){
    document.querySelectorAll('.seg-thumb').forEach(function(th){ th.style.transition=''; });
  }); });
}
/* ----- home marquees: rows drift only while the page is scrolled, and can be swiped / dragged.
   Nothing moves on its own, so no pause control is needed (WCAG 2.2.2).
   Each row is a native horizontal scroller holding two copies of its cards; the position wraps
   by one copy's width so the row never runs out. ----- */
function initMarquee(){
  var rows=[].slice.call(document.querySelectorAll('.mq')); if(!rows.length) return;
  var reduce=window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var raf=0;
  function kick(){ if(!raf) raf=requestAnimationFrame(tick); }
  function tick(){
    raf=0; var more=false;
    rows.forEach(function(mq){
      var st=mq._mq; if(!st || st.drag) return;
      if(Math.abs(st.todo)<0.1){ st.todo=0; return; }
      var step=st.todo*0.12; st.todo-=step; st.set(st.pos+step); more=true;
    });
    if(more) kick();
  }
  rows.forEach(function(mq){
    var g=mq.querySelector('.mq-group');
    var st={pos:0, todo:0, drag:null, dir:mq.classList.contains('mq-events')?-1:1};
    st.set=function(p){
      var w=g?g.offsetWidth:0;
      if(w && w>mq.clientWidth){ while(p>=w) p-=w; while(p<0) p+=w; }
      st.pos=p; mq.scrollLeft=p;
    };
    mq._mq=st;
    /* swipe, trackpad or keyboard focus moved the row: adopt that position, wrapping if needed */
    mq.addEventListener('scroll', function(){
      if(Math.abs(mq.scrollLeft-st.pos)>1.5) st.set(mq.scrollLeft);
    }, {passive:true});
    /* mouse drag (touch already swipes natively) */
    mq.addEventListener('pointerdown', function(e){
      if(e.pointerType!=='mouse' || e.button!==0) return;
      st.drag={x:e.clientX, t:e.timeStamp, v:0, moved:false}; st.todo=0;
    });
    mq.addEventListener('pointermove', function(e){
      var d=st.drag; if(!d) return;
      var dx=e.clientX-d.x;
      if(!d.moved){
        if(Math.abs(dx)<5) return;
        d.moved=true; mq.classList.add('dragging');
        try{ mq.setPointerCapture(e.pointerId); }catch(_){}
      }
      var dt=Math.max(1, e.timeStamp-d.t);
      d.v=dx/dt; d.x=e.clientX; d.t=e.timeStamp;
      st.set(st.pos-dx);
    });
    function end(){
      var d=st.drag; st.drag=null; if(!d || !d.moved) return;
      st.todo=-d.v*220; kick();                       /* a short glide after letting go */
      st.justDragged=true;
      setTimeout(function(){ st.justDragged=false; mq.classList.remove('dragging'); }, 0);
    }
    mq.addEventListener('pointerup', end);
    mq.addEventListener('pointercancel', end);
    mq.addEventListener('click', function(e){ if(st.justDragged){ e.preventDefault(); e.stopPropagation(); } }, true);
    mq.addEventListener('dragstart', function(e){ e.preventDefault(); });
  });
  if(reduce) return;                                  /* reduced motion: rows stay put unless swiped */
  var lastY=window.scrollY;
  window.addEventListener('scroll', function(){
    var y=window.scrollY, dy=y-lastY; lastY=y; if(!dy) return;
    var vh=window.innerHeight;
    rows.forEach(function(mq){
      var st=mq._mq; if(!st || st.drag || mq.classList.contains('filtering')) return;
      var r=mq.getBoundingClientRect(); if(r.bottom<0 || r.top>vh) return;
      st.todo+=dy*0.7*st.dir;
    });
    kick();
  }, {passive:true});
}
/* ----- race pages: once the reader scrolls past the stat panel, the main nav's middle links
   swap to this page's sections (one sticky bar, nothing added). Phones get a "section ▾" chip
   with a dropdown instead. A mint pill slides to the section in view. ----- */
function initNavSections(){
  var stat=document.querySelector('.statpanel'), navbar=document.querySelector('.navbar');
  var links0=navbar && navbar.querySelector('.navlinks');
  if(!stat || !links0) return;                       /* only race pages have the stat panel */
  var secs=[].slice.call(document.querySelectorAll('.sec.banded')).filter(function(s){ return s.querySelector('.seclabel .n'); });
  if(secs.length<3) return;
  var RENAME={Why:['ภาพรวม','Overview']};          /* "ทำไม" reads oddly as a menu item */
  var isEn=function(){ return document.documentElement.lang==='en'; };
  var reduce=window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items=secs.map(function(s){
    var n=s.querySelector('.seclabel .n');
    var en=n.getAttribute('data-en')||n.textContent, th=n.getAttribute('data-th')||n.textContent;
    if(RENAME[en]){ th=RENAME[en][0]; en=RENAME[en][1]; }
    if(!s.id) s.id=en.toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
    return {sec:s, th:th, en:en};
  });
  function go(it, e){
    if(e) e.preventDefault();
    closeSm();
    it.sec.scrollIntoView({behavior:reduce?'auto':'smooth', block:'start'});
    try{ history.replaceState(null,'','#'+it.sec.id); }catch(_){}
  }
  function mkLink(it, cls){
    var a=document.createElement('a'); a.href='#'+it.sec.id; if(cls) a.className=cls;
    a.setAttribute('data-th',it.th); a.setAttribute('data-en',it.en); a.textContent=isEn()?it.en:it.th;
    a.addEventListener('click', function(e){ go(it,e); }); return a;
  }
  function aria(el, th, en){ el.setAttribute('data-th-aria',th); el.setAttribute('data-en-aria',en); el.setAttribute('aria-label', isEn()?en:th); }

  /* desktop: both link sets share one grid cell and cross-fade */
  var swap=document.createElement('div'); swap.className='navswap';
  links0.parentNode.insertBefore(swap, links0); swap.appendChild(links0);
  var secNav=document.createElement('nav'); secNav.className='navsecs'; aria(secNav,'ส่วนต่างๆ ในหน้านี้','On this page');
  var pill=document.createElement('span'); pill.className='ns-pill'; pill.setAttribute('aria-hidden','true'); secNav.appendChild(pill);
  var dl=items.map(function(it){ return secNav.appendChild(mkLink(it)); });
  swap.appendChild(secNav);

  /* phones: chip + dropdown */
  var chip=document.createElement('button'); chip.type='button'; chip.className='secchip';
  chip.setAttribute('aria-expanded','false'); chip.setAttribute('aria-controls','secmenu');
  chip.innerHTML='<span class="sc-k" data-th="ส่วน" data-en="Section">'+(isEn()?'Section':'ส่วน')+'</span><span class="sc-l"></span><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>';
  var chipL=chip.querySelector('.sc-l');
  navbar.insertBefore(chip, navbar.querySelector('.navright'));
  var sm=document.createElement('div'); sm.className='menu secmenu'; sm.id='secmenu';
  var ml=items.map(function(it){ return sm.appendChild(mkLink(it)); });
  navbar.parentNode.appendChild(sm);
  function closeSm(){ sm.classList.remove('open'); chip.setAttribute('aria-expanded','false'); }
  chip.addEventListener('click', function(e){
    e.stopPropagation();
    var m=document.getElementById('menu'); if(m && m.classList.contains('open')){ m.classList.remove('open'); var b=document.querySelector('.menubtn'); if(b) b.setAttribute('aria-expanded','false'); }
    var open=sm.classList.toggle('open'); chip.setAttribute('aria-expanded', open?'true':'false');
  });
  document.addEventListener('click', function(e){ if(!e.target.closest('#secmenu')) closeSm(); });
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') closeSm(); });
  var mb=document.querySelector('.menubtn'); if(mb) mb.addEventListener('click', closeSm);

  var de=document.documentElement, cur=-2, mode=null;
  function placePill(){
    var a=dl[cur]; if(!a){ pill.style.opacity='0'; return; }
    pill.style.opacity='1'; pill.style.width=a.offsetWidth+'px'; pill.style.height=a.offsetHeight+'px';
    pill.style.transform='translate('+a.offsetLeft+'px,'+a.offsetTop+'px)';
  }
  window.navSecSync=function(){ placePill(); var it=items[Math.max(cur,0)]; chipL.textContent=isEn()?it.en:it.th; aria(chip,'ส่วนในหน้านี้: '+it.th,'On this page: '+it.en); };
  function update(){
    var nb=navbar.getBoundingClientRect().bottom;
    de.style.scrollPaddingTop=(Math.round(nb)+12)+'px';
    var on=stat.getBoundingClientRect().bottom < nb;
    if(on!==mode){
      mode=on; navbar.classList.toggle('secmode', on);
      links0.inert=on; secNav.inert=!on;              /* hidden set is skipped by Tab and screen readers */
      if(!on) closeSm();
    }
    var line=nb+40, c=-1;
    secs.forEach(function(s,i){ if(s.getBoundingClientRect().top<=line) c=i; });
    if(c===cur) return; cur=c;
    dl.concat(ml).forEach(function(a,i){ var hit=(i%items.length)===c; a.classList.toggle('active',hit); if(hit) a.setAttribute('aria-current','true'); else a.removeAttribute('aria-current'); });
    window.navSecSync();
  }
  var t=0; window.addEventListener('scroll', function(){ if(!t) t=requestAnimationFrame(function(){ t=0; update(); }); }, {passive:true});
  window.addEventListener('resize', function(){ cur=-2; update(); });
  update();
}
function sizeTopBg(){
  var b=document.querySelector('.topbg'); if(!b) return;
  var h=document.querySelector('.hero.home'), r=document.getElementById('races');
  var band=h?h.closest('.band'):(r?(r.closest('.band')||r):null); if(!band) return;
  if(h){ var f=document.querySelector('.onvid'); if(f) band=f;
    b.style.height=Math.round(band.getBoundingClientRect().bottom+window.pageYOffset)+'px'; return; }
  b.style.height=Math.round(band.getBoundingClientRect().top+window.pageYOffset)+'px';
}
window.addEventListener('resize', function(){ segSyncAll(); sizeTopBg(); fitDesc(); });
window.addEventListener('load', sizeTopBg);
/* home hero video: phones get the portrait crop; reduced motion or save-data keep the still poster */
function setVidBtn(btn,paused){
  if(!btn) return; btn.classList.toggle('paused',paused);
  var s=btn.querySelector('.vh'), th=paused?'เล่นวิดีโอพื้นหลัง':'หยุดวิดีโอพื้นหลัง', en=paused?'Play background video':'Pause background video';
  s.setAttribute('data-th',th); s.setAttribute('data-en',en); s.textContent=(document.documentElement.lang==='en')?en:th;
}
function toggleHeroVid(btn){
  var v=document.querySelector('.herovid'); if(!v) return;
  v.dataset.userPaused=v.paused?'':'1';
  if(v.paused){ v.play(); setVidBtn(btn,false); } else { v.pause(); setVidBtn(btn,true); }
}
function initHeroVid(){
  var v=document.querySelector('.herovid'); if(!v) return;
  var btn=document.querySelector('.vidtoggle');
  var reduce=window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var save=navigator.connection && navigator.connection.saveData;
  if(reduce||save){ if(btn) btn.hidden=true; return; }
  v.src=(window.innerWidth<700)?v.getAttribute('data-src-sm'):v.getAttribute('data-src-lg');
  /* the button follows the video's real state (autoplay can be blocked, then start later on scroll) */
  v.addEventListener('play',function(){ setVidBtn(btn,false); });
  v.addEventListener('pause',function(){ setVidBtn(btn,true); });
  var p=v.play(); if(p&&p.catch) p.catch(function(){ setVidBtn(btn,true); });
  if('IntersectionObserver' in window) new IntersectionObserver(function(es){
    es.forEach(function(e){ if(v.dataset.userPaused) return; if(e.isIntersecting) v.play().catch(function(){}); else v.pause(); });
  }).observe(v);
}
/* ----- scroll reveal: each section's blocks (and grid cards, staggered) rise in once as they enter ----- */
function initReveal(){
  var reduce=window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce || !('IntersectionObserver' in window)) return;
  var els=[].slice.call(document.querySelectorAll('.sec > *:not(.grid), .grid > *'));
  var io=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting) return;
      var el=e.target; el.classList.add('rv-on'); io.unobserve(el);
      /* hand the element back to its own transitions (card hover lift etc.) once it has landed */
      setTimeout(function(){ el.classList.remove('rv','rv-on'); el.style.removeProperty('--rv-d'); }, 1100);
    });
  },{rootMargin:'0px 0px -8% 0px'});
  var fold=window.innerHeight;
  els.forEach(function(el){
    /* already on screen at load: show it as is, so arriving on a page never replays a reveal */
    if(el.getBoundingClientRect().top < fold) return;
    if(el.parentElement.classList.contains('grid')){
      var i=[].indexOf.call(el.parentElement.children, el);
      el.style.setProperty('--rv-d', Math.min(i,3)*90+'ms');
    }
    el.classList.add('rv'); io.observe(el);
  });
}
if(document.fonts && document.fonts.ready) document.fonts.ready.then(fitDesc);

/* apply saved language on every page load */
document.addEventListener('DOMContentLoaded',function(){
  var l='th';
  try{ l=localStorage.getItem('rs-lang')||'th'; }catch(e){}
  setLang(l);

  var sp=null; try{ sp=new URLSearchParams(location.search).get('sport'); }catch(e){}
  if(sp && sp!=='all'){
    applyFilter(sp);
    var r=document.getElementById('races'); if(r) r.scrollIntoView();
  }

  initNavSections();
  initSegments();
  initHeroVid();
  initMarquee();
  initReveal();
  var ec=document.getElementById('evcount');
  if(ec) ec.textContent=[].filter.call(document.querySelectorAll('#races .evcard'),function(c){return c.style.display!=='none';}).length;
  sizeTopBg();
});
