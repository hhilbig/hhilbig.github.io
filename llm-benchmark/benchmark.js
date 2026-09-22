
'use strict';
document.documentElement.classList.add('js');
const byId=id=>document.getElementById(id);
document.querySelectorAll('a[href="#methods"]').forEach(a=>a.addEventListener('click',()=>{byId('methods').open=true;}));
