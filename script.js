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
