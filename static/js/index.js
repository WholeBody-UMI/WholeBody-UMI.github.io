const sectionIds = ["overview", "system", "motion-prior", "transfer", "citation"];
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
    window.setTimeout(() => {
      heroVideo.src = compactViewport
        ? heroVideo.dataset.mobileSrc || ""
        : heroVideo.dataset.desktopSrc || "";
      heroVideo.load();
      void heroVideo.play().catch(() => undefined);
    }, 1_500);
  }
}

const mediaObserver = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      const video = entry.target;
      if (!(video instanceof HTMLVideoElement)) continue;
      if (entry.isIntersecting && !reduceMotion.matches) {
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
