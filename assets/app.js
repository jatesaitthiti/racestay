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
  var bt=document.getElementById('btn-th'), be=document.getElementById('btn-en');
  if(bt) bt.classList.toggle('on',l==='th');
  if(be) be.classList.toggle('on',l==='en');
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
  document.querySelectorAll('#races [data-sport]').forEach(function(el){
    el.style.display=(sport==='all'||el.getAttribute('data-sport')===sport)?'':'none';
  });
}

/* apply saved language on every page load */
document.addEventListener('DOMContentLoaded',function(){
  var l='th';
  try{ l=localStorage.getItem('rs-lang')||'th'; }catch(e){}
  setLang(l);
});
