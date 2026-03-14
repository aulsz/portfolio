const year = document.getElementById("year");
if (year) year.textContent = new Date().getFullYear();

const revealTargets = document.querySelectorAll(
  ".case, .timeline__item, .community-card, .cta__card"
);
revealTargets.forEach((el) => el.setAttribute("data-reveal", ""));

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.3 }
);

revealTargets.forEach((el) => observer.observe(el));

const tiltCards = document.querySelectorAll("[data-tilt]");
tiltCards.forEach((card) => {
  const rect = () => card.getBoundingClientRect();

  card.addEventListener("mousemove", (event) => {
    const bounds = rect();
    const x = ((event.clientX - bounds.left) / bounds.width - 0.5) * 20;
    const y = ((event.clientY - bounds.top) / bounds.height - 0.5) * -20;
    card.style.transform = `perspective(900px) rotateX(${y}deg) rotateY(${x}deg)`;
  });

  card.addEventListener("mouseleave", () => {
    card.style.transform = "perspective(900px) rotateX(0deg) rotateY(0deg)";
  });
});

const sparkCards = document.querySelectorAll("[data-spark]");
setInterval(() => {
  const card = sparkCards[Math.floor(Math.random() * sparkCards.length)];
  if (!card) return;
  card.animate(
    [
      { boxShadow: "0 0 0 rgba(73,255,224,0)" },
      { boxShadow: "0 0 30px rgba(73,255,224,0.35)" },
      { boxShadow: "0 0 0 rgba(73,255,224,0)" },
    ],
    {
      duration: 2200,
      easing: "ease-out",
    }
  );
}, 2600);

// Spawn-in text animation (character reveal)
(function () {
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduceMotion) return;

  const targets = document.querySelectorAll('.fx-title, .fx-section, .tag');
  const textObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      if (el.dataset.spawned === '1') {
        textObserver.unobserve(el);
        return;
      }

      const original = (el.dataset.originalText || el.textContent || '').trim();
      el.dataset.originalText = original;
      el.textContent = '';

      const frag = document.createDocumentFragment();
      let idx = 0;
      for (const ch of original) {
        const span = document.createElement('span');
        span.className = 'spawn-char';
        span.textContent = ch === ' ' ? '\u00A0' : ch;
        span.style.animationDelay = `${idx * 24}ms`;
        frag.appendChild(span);
        idx++;
      }
      el.appendChild(frag);
      el.dataset.spawned = '1';
      textObserver.unobserve(el);
    });
  }, { threshold: 0.22 });

  targets.forEach((el) => textObserver.observe(el));
})();
