/* RaceStay — shared behaviour across all pages */
var EN2TH={JAN:'ม.ค.',FEB:'ก.พ.',MAR:'มี.ค.',APR:'เม.ย.',MAY:'พ.ค.',JUN:'มิ.ย.',JUL:'ก.ค.',AUG:'ส.ค.',SEP:'ก.ย.',OCT:'ต.ค.',NOV:'พ.ย.',DEC:'ธ.ค.'};
var TH2EN={}; (function(){for(var k in EN2TH)TH2EN[EN2TH[k]]=k;})();
var RE_EN=/\b(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\b/g;
var RE_TH=/(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.)/g;
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
var KEEP_TH=['ระยะเดิน','จุดปล่อยตัว','ปล่อยตัว','จุดสตาร์ท','เส้นชัย','เข้าเส้นชัย','รอยืนยัน','รับ BIB','เช้ามืด','กลางคืน','กลางดึก',
  'ก่อนแข่ง','หลังแข่ง','วันแข่ง','สุดสัปดาห์','เดินทาง','ล่วงหน้า','ติดกัน','หารถ','ก่อนกด','เช็กอิน','เช็กเอาต์','เช็คอิน','เช็คเอาต์',
  'แพ็กเกจ','ไตรกีฬา','ไฮรอกซ์','วิ่งเทรล','วิ่งถนน','สวนน้ำ','ศูนย์ประชุม','เฮอริเทจ','อินเตอร์เนชั่นแนล','เซอร์กิต','มหาราชวัง',
  'กาญจนาภิเษก','ท่าเตียน','ช้างเผือก','นาเกลือ','วงเวียนโลมา','เชิงทะเล','ลากูน่า','ย่าโม','ฝั่งเหนือ','บุ่งตาหลั่ว','รัตนโกสินทร์',
  'สนามหลวง','สนามไชย','สนามช้าง','เชียงใหม่','ขอนแก่น','อุดมสุข','ไบเทค','บางนา','เขาใหญ่','ปากช่อง','จอมทอง','แม่ริม','ปทุมวัน',
  'เจ้าพระยา','ท่าแพ','ไนท์บาซาร์','พระบรมราชานุสาวรีย์','พระบรมมหาราชวัง','อนุสาวรีย์','อารีน่า','บางแสน'];
var RE_KEEP=new RegExp('('+
  KEEP_TH.sort(function(a,b){return b.length-a.length;}).map(function(s){return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}).join('|')+
  '|฿\\d[\\d,]*'+
  '|ตี\\s\\d+'+
  '|\\d+(?:[.,]\\d+)?(?:\\s?[–-]\\s?\\d+(?:[.,]\\d+)?)?\\s(?:กม\\.|ม\\.|km|K\\b|นาที|ชม\\.|ชั่วโมง|วัน|คืน|ดาว|บาท|คน|'+
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
  document.documentElement.lang=l;
  localizeDates(l);
  document.querySelectorAll('[data-setlang]').forEach(function(b){ b.classList.toggle('on', b.getAttribute('data-setlang')===l); });
  try{ localStorage.setItem('rs-lang',l); }catch(e){}
  countdowns();
  keepTogether();
  fitDesc();
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
      seg.insertBefore(th, seg.firstChild);
    }
    seg.querySelectorAll('.seg-item').forEach(function(it){
      it.addEventListener('click', function(){ requestAnimationFrame(segSyncAll); });
    });
  });
  segSyncAll();
}
/* ----- marquee pause/play (WAI: moving content needs a pause control) ----- */
function toggleMarquee(btn){
  var mq=document.getElementById(btn.getAttribute('aria-controls')); if(!mq) return;
  var paused=mq.classList.toggle('paused');
  btn.setAttribute('aria-pressed', paused?'true':'false');
  var th=paused?'▶ เลื่อนต่อ':'❚❚ หยุดเลื่อน', en=paused?'▶ Play':'❚❚ Pause';
  btn.setAttribute('data-th',th); btn.setAttribute('data-en',en);
  btn.textContent=(document.documentElement.lang==='en')?en:th;
}
function sizeTopBg(){
  var b=document.querySelector('.topbg'); if(!b) return;
  var r=document.getElementById('races'); if(!r) return;
  var band=r.closest('.band')||r;
  b.style.height=Math.round(band.getBoundingClientRect().top+window.pageYOffset)+'px';
}
window.addEventListener('resize', function(){ segSyncAll(); sizeTopBg(); fitDesc(); });
window.addEventListener('load', sizeTopBg);
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

  initSegments();
  var ec=document.getElementById('evcount');
  if(ec) ec.textContent=[].filter.call(document.querySelectorAll('#races .evcard'),function(c){return c.style.display!=='none';}).length;
  sizeTopBg();
});
