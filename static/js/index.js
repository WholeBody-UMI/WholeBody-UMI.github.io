const sectionIds = ["overview", "system", "motion-prior", "simulation", "transfer", "citation"];
const sectionLinks = [...document.querySelectorAll('.anchor-tabs a[href^="#"]')];

const setActiveSection = (sectionId) => {
  for (const link of sectionLinks) {
    const isActive = link.getAttribute("href") === `#${sectionId}`;
    link.closest("li")?.classList.toggle("is-active", isActive);
    if (isActive) {
      link.setAttribute("aria-current", "location");
    } else {
      link.removeAttribute("aria-current");
    }
  }
};

const sectionObserver = new IntersectionObserver(
  (entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((left, right) => right.intersectionRatio - left.intersectionRatio);
    const sectionId = visible[0]?.target.id;
    if (sectionId) setActiveSection(sectionId);
  },
  { rootMargin: "-20% 0px -60%", threshold: [0.05, 0.25, 0.5] },
);

for (const sectionId of sectionIds) {
  const section = document.getElementById(sectionId);
  if (section) sectionObserver.observe(section);
}

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const heroVideo = document.querySelector(".project-hero video");
if (heroVideo instanceof HTMLVideoElement) {
  const compactViewport = window.matchMedia("(max-width: 768px)").matches;
  heroVideo.poster = compactViewport
    ? heroVideo.dataset.mobilePoster || ""
    : heroVideo.dataset.desktopPoster || "";

  if (!reduceMotion.matches) {
    // Playback is controlled by visibility, including after the source loads.
    heroVideo.autoplay = false;
    let heroIsVisible = false;
    const heroObserver = new IntersectionObserver(([entry]) => {
      heroIsVisible = entry.isIntersecting;
      if (heroIsVisible && heroVideo.getAttribute("src")) {
        void heroVideo.play().catch(() => undefined);
      } else {
        heroVideo.pause();
      }
    });
    heroObserver.observe(heroVideo);
    window.setTimeout(() => {
      heroVideo.src = compactViewport
        ? heroVideo.dataset.mobileSrc || ""
        : heroVideo.dataset.desktopSrc || "";
      heroVideo.load();
      if (heroIsVisible) void heroVideo.play().catch(() => undefined);
    }, 1_500);
  }
}

const mediaObserver = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      const video = entry.target;
      if (!(video instanceof HTMLVideoElement)) continue;
      if (entry.isIntersecting && !video.closest(".demo-slide")?.hidden && !reduceMotion.matches) {
        void video.play().catch(() => undefined);
      } else {
        video.pause();
      }
    }
  },
  { threshold: 0.55 },
);

for (const video of document.querySelectorAll("[data-autoplay-video]")) {
  mediaObserver.observe(video);
}

for (const carousel of document.querySelectorAll("[data-carousel]")) {
  const slides = [...carousel.querySelectorAll(".demo-slide")];
  const controls = carousel.querySelector(".carousel-controls");
  const status = carousel.querySelector("[data-carousel-status]");
  let activeIndex = 0;

  const showSlide = (index) => {
    const outgoing = slides[activeIndex].querySelector("video");
    const muted = outgoing.muted;
    const volume = outgoing.volume;
    outgoing.pause();
    // Release the previous download/decoder so repeated switching cannot
    // exhaust the browser's concurrent media connections.
    outgoing.dataset.src = outgoing.getAttribute("src");
    outgoing.removeAttribute("src");
    outgoing.load();
    slides[activeIndex].hidden = true;

    activeIndex = (index + slides.length) % slides.length;
    const slide = slides[activeIndex];
    const video = slide.querySelector("video");
    video.muted = muted;
    video.volume = volume;
    slide.hidden = false;
    if (video.dataset.src) {
      video.src = video.dataset.src;
      delete video.dataset.src;
      video.load();
    }
    status.textContent = `${activeIndex + 1} / ${slides.length}${slide.dataset.label ? ` · ${slide.dataset.label}` : ""}`;
    // A user click can also start unmuted playback when sound was enabled.
    if (!reduceMotion.matches) void video.play().catch(() => undefined);
  };

  carousel.querySelector("[data-carousel-prev]").addEventListener("click", () => showSlide(activeIndex - 1));
  carousel.querySelector("[data-carousel-next]").addEventListener("click", () => showSlide(activeIndex + 1));
  controls.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    showSlide(activeIndex + (event.key === "ArrowRight" ? 1 : -1));
  });
  controls.hidden = false;
}
