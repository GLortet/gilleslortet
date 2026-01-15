document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".nav-toggle");
    const nav = document.querySelector(".nav");

    if (toggle && nav) {
        toggle.addEventListener("click", () => {
            const isOpen = nav.classList.toggle("is-open");
            toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
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
});
