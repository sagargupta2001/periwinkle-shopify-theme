/*
  Periwinkle coming soon — gentle reveal on scroll.

  Everything is visible by default. The "is-animated" class that hides content
  until it scrolls into view is only added when motion is allowed, outside the
  theme editor, and where IntersectionObserver exists.
*/
if (!customElements.get('periwinkle-coming-soon')) {
  customElements.define(
    'periwinkle-coming-soon',
    class PeriwinkleComingSoon extends HTMLElement {
      connectedCallback() {
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const inEditor = window.Shopify && window.Shopify.designMode;
        if (reducedMotion || inEditor || !('IntersectionObserver' in window)) return;

        const targets = this.querySelectorAll('[data-reveal]');
        if (!targets.length) return;

        this.observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (!entry.isIntersecting) return;
              entry.target.classList.add('is-revealed');
              this.observer.unobserve(entry.target);
            });
          },
          { rootMargin: '0px 0px -12% 0px', threshold: 0.1 }
        );

        this.classList.add('is-animated');
        targets.forEach((target) => this.observer.observe(target));
      }

      disconnectedCallback() {
        if (this.observer) this.observer.disconnect();
      }
    }
  );
}
