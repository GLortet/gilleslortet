document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector(".nav");

    if (toggle && nav) {
        toggle.addEventListener("click", () => {
            const isOpen = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
    }

    const siteHeader = document.querySelector(".site-header");
    if (siteHeader) {
        const updateHeader = () => {
            const shouldCompact = window.scrollY > 12;
            siteHeader.classList.toggle("is-compact", shouldCompact);
        };
        updateHeader();
        window.addEventListener("scroll", updateHeader, { passive: true });
    }

    const reveals = document.querySelectorAll(".reveal");
    if (reveals.length > 0 && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(
            (entries, currentObserver) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        currentObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.2 }
        );

        reveals.forEach((element) => observer.observe(element));
    } else {
        reveals.forEach((element) => element.classList.add("is-visible"));
    }

    const sectionTitles = document.querySelectorAll(".section-title-reveal");
    if (sectionTitles.length > 0 && "IntersectionObserver" in window) {
        const titleObserver = new IntersectionObserver(
            (entries, currentObserver) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        currentObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.4 }
        );

        sectionTitles.forEach((title) => titleObserver.observe(title));
    } else {
        sectionTitles.forEach((title) => title.classList.add("is-visible"));
    }

    const cookieBanner = document.querySelector(".cookie-banner");
    const cookieAccept = document.querySelector("[data-cookie-accept]");
    const hasConsent = document.cookie
        .split("; ")
        .some((cookie) => cookie.startsWith("gl_cookie_consent="));

    if (cookieBanner && hasConsent) {
        cookieBanner.setAttribute("hidden", "hidden");
    }

    if (cookieBanner && cookieAccept) {
        cookieAccept.addEventListener("click", () => {
            document.cookie = "gl_cookie_consent=1; max-age=15552000; path=/; SameSite=Lax";
            cookieBanner.setAttribute("hidden", "hidden");
        });
    }

    // PCM brochure showcase interactions.
    const showcaseTrack = document.querySelector("[data-showcase-track]");
    const showcaseThumbs = document.querySelectorAll(".pcm-showcase-thumb");
    const showcaseSlides = document.querySelectorAll(".pcm-showcase-slide");
    const showcasePrev = document.querySelector("[data-showcase-prev]");
    const showcaseNext = document.querySelector("[data-showcase-next]");
    const lightbox = document.querySelector("[data-showcase-lightbox]");
    const lightboxImage = document.querySelector(".pcm-showcase-lightbox-image");
    const lightboxClose = document.querySelector("[data-showcase-close]");

    const setActiveSlide = (index) => {
        showcaseSlides.forEach((slide) => slide.classList.remove("is-active"));
        showcaseThumbs.forEach((thumb) => thumb.classList.remove("is-active"));
        const slide = showcaseSlides[index];
        const thumb = showcaseThumbs[index];
        if (slide) {
            slide.classList.add("is-active");
        }
        if (thumb) {
            thumb.classList.add("is-active");
        }
    };

    const openLightbox = (img) => {
        if (!lightbox || !lightboxImage) {
            return;
        }
        lightboxImage.src = img.currentSrc || img.src;
        lightboxImage.alt = img.alt || "Aperçu brochure PCM";
        lightbox.classList.add("is-open");
        lightbox.setAttribute("aria-hidden", "false");
        document.body.classList.add("body-locked");
    };

    const closeLightbox = () => {
        if (!lightbox) {
            return;
        }
        lightbox.classList.remove("is-open");
        lightbox.setAttribute("aria-hidden", "true");
        document.body.classList.remove("body-locked");
    };

    if (showcaseTrack) {
        const scrollToIndex = (index) => {
            const slide = showcaseSlides[index];
            if (slide) {
                slide.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
                setActiveSlide(index);
            }
        };

        showcaseThumbs.forEach((thumb) => {
            thumb.addEventListener("click", () => {
                const index = Number(thumb.dataset.index);
                scrollToIndex(index);
            });
        });

        showcaseSlides.forEach((slide) => {
            slide.addEventListener("click", () => {
                const img = slide.querySelector("img");
                if (img) {
                    openLightbox(img);
                }
            });
        });

        showcaseTrack.addEventListener("scroll", () => {
            const slideWidth = showcaseTrack.clientWidth;
            const index = Math.round(showcaseTrack.scrollLeft / slideWidth);
            setActiveSlide(index);
        });

        if (showcasePrev) {
            showcasePrev.addEventListener("click", () => {
                const activeIndex = [...showcaseSlides].findIndex((slide) =>
                    slide.classList.contains("is-active")
                );
                scrollToIndex(Math.max(activeIndex - 1, 0));
            });
        }

        if (showcaseNext) {
            showcaseNext.addEventListener("click", () => {
                const activeIndex = [...showcaseSlides].findIndex((slide) =>
                    slide.classList.contains("is-active")
                );
                scrollToIndex(Math.min(activeIndex + 1, showcaseSlides.length - 1));
            });
        }
    }

    if (lightbox) {
        lightbox.addEventListener("click", (event) => {
            if (event.target === lightbox) {
                closeLightbox();
            }
        });
    }

    if (lightboxClose) {
        lightboxClose.addEventListener("click", closeLightbox);
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && lightbox?.classList.contains("is-open")) {
            closeLightbox();
        }
    });
});
