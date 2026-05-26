"use strict";

// ── CONSTANTS ────────────────────────────────────────────────────────────────
const TOTAL_FRAMES   = 242;
const FRAME_SPEED    = 2.0;   // product animation completes at 50% scroll
const IMAGE_SCALE    = 0.88;  // padded cover — slight breathing room
const LENIS_DURATION = 1.2;
const DPR            = Math.min(window.devicePixelRatio || 1, 2);

// Scroll % thresholds (0–1)
const STATS_ENTER    = 0.50;
const STATS_LEAVE    = 0.65;
const MARQUEE_ENTER  = 0.32;
const MARQUEE_LEAVE  = 0.82;
const OVERLAY_FADE   = 0.04;

// ── DOM ──────────────────────────────────────────────────────────────────────
const loader      = document.getElementById("loader");
const loaderBar   = document.getElementById("loader-bar");
const loaderPct   = document.getElementById("loader-percent");
const canvas      = document.getElementById("canvas");
const ctx         = canvas.getContext("2d");
const canvasWrap  = document.getElementById("canvas-wrap");
const darkOverlay = document.getElementById("dark-overlay");
const marqueeWrap = document.getElementById("marquee");
const marqueeText = marqueeWrap.querySelector(".marquee-text");
const heroSection = document.getElementById("hero");
const scrollCont  = document.getElementById("scroll-container");

// ── STATE ────────────────────────────────────────────────────────────────────
const frames = new Array(TOTAL_FRAMES).fill(null);
let currentFrame = 0;
let bgColor      = "#B8681A";

// ── UTILITIES ────────────────────────────────────────────────────────────────

function framePath(i) {
  return `frames/frame_${String(i).padStart(4, "0")}.webp`;
}

function sampleBgColor(img) {
  try {
    const off  = Object.assign(document.createElement("canvas"), { width: 4, height: 4 });
    const octx = off.getContext("2d");
    octx.drawImage(img, 0, 0, 4, 4);
    const corners = [
      octx.getImageData(0, 0, 1, 1).data,
      octx.getImageData(3, 0, 1, 1).data,
      octx.getImageData(0, 3, 1, 1).data,
      octx.getImageData(3, 3, 1, 1).data,
    ];
    const avg = [0, 1, 2].map(
      ch => Math.round(corners.reduce((s, c) => s + c[ch], 0) / 4)
    );
    bgColor = `rgb(${avg[0]},${avg[1]},${avg[2]})`;
    canvasWrap.style.background = bgColor;
  } catch (_) { /* cross-origin or offscreen error — keep fallback */ }
}

function drawFrame(index) {
  const img = frames[index];
  if (!img) return;

  const cw = canvas.width  / DPR;
  const ch = canvas.height / DPR;
  const iw = img.naturalWidth;
  const ih = img.naturalHeight;

  const scale = Math.max(cw / iw, ch / ih) * IMAGE_SCALE;
  const dw = iw * scale;
  const dh = ih * scale;
  const dx = (cw - dw) / 2;
  const dy = (ch - dh) / 2;

  ctx.fillStyle = bgColor;
  ctx.fillRect(0, 0, cw, ch);
  ctx.drawImage(img, dx, dy, dw, dh);
}

function resizeCanvas() {
  canvas.width  = window.innerWidth  * DPR;
  canvas.height = window.innerHeight * DPR;
  canvas.style.width  = window.innerWidth  + "px";
  canvas.style.height = window.innerHeight + "px";
  ctx.scale(DPR, DPR);
  drawFrame(currentFrame);
}

// ── PRELOADER ────────────────────────────────────────────────────────────────

function preloadFrames(onComplete) {
  let loaded = 0;

  function onLoad(i, img) {
    frames[i] = img;
    if (i === 0) sampleBgColor(img);
    else if (i % 20 === 0) sampleBgColor(img);
    loaded++;
    const pct = Math.round((loaded / TOTAL_FRAMES) * 100);
    loaderBar.style.width  = pct + "%";
    loaderPct.textContent  = pct + "%";
    if (loaded === TOTAL_FRAMES) onComplete();
  }

  for (let i = 0; i < TOTAL_FRAMES; i++) {
    const img = new Image();
    const idx = i;
    img.onload  = () => onLoad(idx, img);
    img.onerror = () => { loaded++; if (loaded === TOTAL_FRAMES) onComplete(); };
    img.src = framePath(i + 1); // frames are 1-indexed filenames
  }
}

function hideLoader() {
  loader.classList.add("hidden");
  setTimeout(() => { loader.style.display = "none"; }, 750);
}

// ── LENIS ────────────────────────────────────────────────────────────────────

function initLenis() {
  const lenis = new Lenis({
    duration:     LENIS_DURATION,
    easing:       t => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel:  true,
    wheelMultiplier: 1.0,
  });
  lenis.on("scroll", ScrollTrigger.update);
  gsap.ticker.add(time => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);
}

// ── HERO TRANSITION ───────────────────────────────────────────────────────────

function initHeroTransition() {
  // Word-split entrance (plays once after loader hides)
  gsap.from(".hero-heading .word", {
    y: "110%",
    opacity: 0,
    stagger:  0.1,
    duration: 1.3,
    ease:     "power4.out",
    delay:    0.2,
  });
  gsap.from(".hero-eyebrow, .hero-tagline, .hero-sub, .scroll-indicator", {
    y:        30,
    opacity:  0,
    stagger:  0.13,
    duration: 1.0,
    ease:     "power3.out",
    delay:    0.55,
  });

  // Scroll-driven: hero fades, canvas circle-wipes in
  ScrollTrigger.create({
    trigger: scrollCont,
    start:   "top top",
    end:     "bottom bottom",
    scrub:   true,
    onUpdate(self) {
      const p = self.progress;

      // Hero: 1→0 opacity over first 12% of scroll
      const heroOpacity = Math.max(0, 1 - p / 0.12);
      heroSection.style.opacity      = heroOpacity;
      heroSection.style.pointerEvents = heroOpacity < 0.01 ? "none" : "auto";

      // Canvas circle-wipe: starts at 1% scroll, fully open (75%) by 8%
      const wipe   = Math.min(1, Math.max(0, (p - 0.01) / 0.07));
      const radius = wipe * 75;
      canvasWrap.style.clipPath = `circle(${radius}% at 50% 50%)`;
    }
  });
}

// ── FRAME SCRUB ───────────────────────────────────────────────────────────────

function initFrameScrub() {
  ScrollTrigger.create({
    trigger: scrollCont,
    start:   "top top",
    end:     "bottom bottom",
    scrub:   true,
    onUpdate(self) {
      const accelerated = Math.min(self.progress * FRAME_SPEED, 1);
      const index = Math.min(
        Math.floor(accelerated * TOTAL_FRAMES),
        TOTAL_FRAMES - 1
      );
      if (index !== currentFrame) {
        currentFrame = index;
        requestAnimationFrame(() => drawFrame(currentFrame));
      }
    }
  });
}

// ── DARK OVERLAY ──────────────────────────────────────────────────────────────

function initDarkOverlay() {
  ScrollTrigger.create({
    trigger: scrollCont,
    start:   "top top",
    end:     "bottom bottom",
    scrub:   true,
    onUpdate(self) {
      const p  = self.progress;
      const e  = STATS_ENTER;
      const l  = STATS_LEAVE;
      const fd = OVERLAY_FADE;
      let opacity = 0;

      if (p >= e - fd && p < e) {
        opacity = (p - (e - fd)) / fd;
      } else if (p >= e && p <= l) {
        opacity = 0.9;
      } else if (p > l && p <= l + fd) {
        opacity = 0.9 * (1 - (p - l) / fd);
      }

      darkOverlay.style.opacity = opacity.toFixed(4);
    }
  });
}

// ── MARQUEE ───────────────────────────────────────────────────────────────────

function initMarquee() {
  const speed = parseFloat(marqueeWrap.dataset.scrollSpeed) || -25;

  gsap.to(marqueeText, {
    xPercent: speed,
    ease: "none",
    scrollTrigger: {
      trigger: scrollCont,
      start:   "top top",
      end:     "bottom bottom",
      scrub:   true,
    }
  });

  // Opacity fade in/out around the visible range
  ScrollTrigger.create({
    trigger: scrollCont,
    start:   "top top",
    end:     "bottom bottom",
    scrub:   true,
    onUpdate(self) {
      const p  = self.progress;
      const fd = 0.04;
      let opacity = 0;

      if (p >= MARQUEE_ENTER - fd && p < MARQUEE_ENTER) {
        opacity = (p - (MARQUEE_ENTER - fd)) / fd;
      } else if (p >= MARQUEE_ENTER && p <= MARQUEE_LEAVE) {
        opacity = 1;
      } else if (p > MARQUEE_LEAVE && p <= MARQUEE_LEAVE + fd) {
        opacity = 1 - (p - MARQUEE_LEAVE) / fd;
      }

      marqueeWrap.style.opacity = opacity.toFixed(4);
    }
  });
}

// ── SECTIONS ──────────────────────────────────────────────────────────────────

function buildTimeline(section, animation) {
  const children = Array.from(section.querySelectorAll(
    ".section-label, .section-heading, .section-body, .section-link, .cta-form, .cta-note, .stat"
  ));

  const tl = gsap.timeline({ paused: true });

  const stagger  = 0.13;
  const duration = 0.9;

  switch (animation) {
    case "slide-left":
      tl.fromTo(children,
        { x: -90, opacity: 0 },
        { x: 0, opacity: 1, stagger, duration, ease: "power3.out" }
      );
      break;

    case "slide-right":
      tl.fromTo(children,
        { x: 90, opacity: 0 },
        { x: 0, opacity: 1, stagger, duration, ease: "power3.out" }
      );
      break;

    case "stagger-up":
      tl.fromTo(children,
        { y: 65, opacity: 0 },
        { y: 0, opacity: 1, stagger: 0.15, duration: 0.85, ease: "power3.out" }
      );
      break;

    case "scale-up":
      tl.fromTo(children,
        { scale: 0.84, opacity: 0 },
        { scale: 1, opacity: 1, stagger: 0.12, duration: 1.0, ease: "power2.out" }
      );
      break;

    case "fade-up":
    default:
      tl.fromTo(children,
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, stagger: 0.12, duration, ease: "power3.out" }
      );
      break;
  }

  return tl;
}

function initSections() {
  const sections = document.querySelectorAll(".scroll-section");

  sections.forEach(section => {
    const enterPct  = parseFloat(section.dataset.enter) / 100;
    const leavePct  = parseFloat(section.dataset.leave) / 100;
    const animation = section.dataset.animation || "fade-up";
    const persist   = section.dataset.persist === "true";

    const tl = buildTimeline(section, animation);

    let hasEntered = false;
    let reverseTimeout = null;

    function enter() {
      if (reverseTimeout) { clearTimeout(reverseTimeout); reverseTimeout = null; }
      hasEntered = true;
      section.style.opacity = "1";
      section.classList.add("is-visible");
      tl.restart();
    }

    function leave(pastLeave) {
      if (persist && pastLeave) {
        section.style.opacity = "1";
        section.classList.add("is-visible");
        return;
      }
      hasEntered = false;
      tl.reverse();
      section.classList.remove("is-visible");
      reverseTimeout = setTimeout(() => {
        if (!hasEntered) section.style.opacity = "0";
      }, (tl.duration() * 1000) + 100);
    }

    ScrollTrigger.create({
      trigger: scrollCont,
      start:   "top top",
      end:     "bottom bottom",
      scrub:   false,
      onUpdate(self) {
        const p         = self.progress;
        const inRange   = p >= enterPct && p <= leavePct;
        const pastLeave = p > leavePct;

        if (inRange && !hasEntered) {
          enter();
        } else if (!inRange && hasEntered) {
          leave(pastLeave);
        } else if (persist && pastLeave && !hasEntered) {
          // Ensure persisted CTA is visible if user jumps to end
          enter();
        }
      }
    });
  });
}

// ── COUNTERS ──────────────────────────────────────────────────────────────────

function initCounters() {
  document.querySelectorAll(".stat-number").forEach(el => {
    const target   = parseFloat(el.dataset.value);
    const decimals = parseInt(el.dataset.decimals || "0");
    const proxy    = { val: 0 };

    gsap.to(proxy, {
      val:      target,
      duration: 2.2,
      ease:     "power2.out",
      scrollTrigger: {
        trigger:      el.closest(".scroll-section"),
        start:        "top 80%",
        toggleActions: "play none none reverse",
      },
      onUpdate() {
        el.textContent = decimals === 0
          ? Math.round(proxy.val).toLocaleString()
          : proxy.val.toFixed(decimals);
      }
    });
  });
}

// ── INIT ──────────────────────────────────────────────────────────────────────

function init() {
  gsap.registerPlugin(ScrollTrigger);

  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  initLenis();
  initHeroTransition();
  initFrameScrub();
  initDarkOverlay();
  initMarquee();
  initSections();
  initCounters();

  if (frames[0]) drawFrame(0);
}

// ── ENTRY POINT ───────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  preloadFrames(() => {
    hideLoader();
    init();
  });
});
