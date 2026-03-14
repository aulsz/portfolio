document.getElementById('year').textContent = new Date().getFullYear();

const obs = new IntersectionObserver((entries)=>{
  entries.forEach((e)=>{
    if(e.isIntersecting){ e.target.classList.add('in'); obs.unobserve(e.target); }
  });
},{threshold:.18});

document.querySelectorAll('.spawn').forEach(el=>obs.observe(el));
