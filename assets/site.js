document.body.classList.add('js');
const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('#navigation');
function closeMenu(){nav.classList.remove('open');toggle.setAttribute('aria-expanded','false');}
toggle.addEventListener('click',()=>{const open=nav.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));});
nav.addEventListener('click',e=>{if(e.target.closest('a')) closeMenu();});
document.addEventListener('keydown',e=>{if(e.key==='Escape' && nav.classList.contains('open')){closeMenu();toggle.focus();}});
const links=[...nav.querySelectorAll('a[href^="#"]')];
const targets=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
let scheduled=false;
function updateActive(){let active=targets[0];for(const target of targets){if(target.getBoundingClientRect().top<=160)active=target;}if(window.innerHeight+window.scrollY>=document.documentElement.scrollHeight-4)active=targets.at(-1);links.forEach(a=>{if(a.getAttribute('href')==='#'+active?.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});scheduled=false;}
if(targets.length){window.addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(updateActive);}},{passive:true});updateActive();}
