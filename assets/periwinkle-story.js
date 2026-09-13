/*
  <periwinkle-story> — the story timeline.

  - Grows a single periwinkle down the timeline as the page scrolls. The stem's
    tip follows a point just below the middle of the viewport, eased so it
    feels grown rather than dragged, and stops at the closing chapter.
      --story-track   full stem length in px (timeline top → closing chapter)
      --story-growth  0–1, how much of the stem has grown
    Chapters get .is-reached as the tip passes them (their leaves unfurl), and
    the element gets .is-bloomed when the flower comes to rest.
  - Reveals each chapter's content once it scrolls into the lower part of the
    viewport. Checked on scroll so chapters jumped past still reveal.
  - Dispatches `periwinkle-story:progress` with { growth }.

  With reduced motion the flower is shown fully grown and content is visible.
  In the theme editor content is visible and the flower still grows. The
  editor re-renders sections by replacing the element, so connected and
  disconnectedCallback handle set-up and teardown.
*/

if (!customElements.get('periwinkle-story')) {
  customElements.define(
    'periwinkle-story',
    class PeriwinkleStory extends HTMLElement {
      constructor() {
        super();
        this.current = 0;
        this.target = 0;
        this.track = 0;
        this.growth = -1;
        this.frame = null;
        this.pending = [];
        this.onScroll = this.onScroll.bind(this);
        this.measure = this.measure.bind(this);
        this.tick = this.tick.bind(this);
      }

      connectedCallback() {
        this.reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.chapters = Array.from(this.querySelectorAll('.periwinkle-story__chapter'));
        this.nodes = this.chapters.map((chapter) => chapter.querySelector('.periwinkle-story__node'));
        this.nodeOffsets = [];

        this.setUpReveal();
        this.classList.add('periwinkle-story--growing');

        window.addEventListener('scroll', this.onScroll, { passive: true });
        window.addEventListener('resize', this.measure, { passive: true });

        // Images and fonts change the timeline's height after load.
        if ('ResizeObserver' in window) {
          this.resizeObserver = new ResizeObserver(this.measure);
          this.resizeObserver.observe(this);
        }

        this.measure();
        this.current = this.target;
        this.render();
      }

      disconnectedCallback() {
        window.removeEventListener('scroll', this.onScroll);
        window.removeEventListener('resize', this.measure);
        if (this.resizeObserver) this.resizeObserver.disconnect();
        if (this.frame) cancelAnimationFrame(this.frame);
        this.frame = null;
      }

      setUpReveal() {
        const designMode = window.Shopify && window.Shopify.designMode;

        if (this.reduceMotion || designMode) {
          this.chapters.forEach((chapter) => chapter.classList.add('is-revealed'));
          return;
        }

        this.pending = this.chapters.slice();
        (this.closest('.periwinkle-story') || this).classList.add('periwinkle-story--animated');
      }

      measure() {
        const top = this.getBoundingClientRect().top;

        this.nodeOffsets = this.nodes.map((node) =>
          node ? node.getBoundingClientRect().top - top + node.offsetHeight / 2 : 0
        );

        // The stem ends at the top of the closing chapter's node, where the
        // flower rests; without a closing chapter, at the last chapter's node.
        const lastChapter = this.chapters[this.chapters.length - 1];
        const lastNode = this.nodes[this.nodes.length - 1];
        if (lastChapter && lastNode && lastChapter.classList.contains('periwinkle-story__chapter--finale')) {
          this.track = lastNode.getBoundingClientRect().top - top;
        } else {
          this.track = this.nodeOffsets[this.nodeOffsets.length - 1] || this.offsetHeight;
        }

        this.style.setProperty('--story-track', `${Math.round(this.track)}px`);
        this.growth = -1;
        this.onScroll();
      }

      onScroll() {
        this.revealPassedChapters();

        if (this.reduceMotion) {
          this.target = this.track;
        } else {
          const tip = window.innerHeight * 0.55 - this.getBoundingClientRect().top;
          this.target = Math.min(Math.max(tip, 0), this.track);
        }

        if (!this.frame) this.frame = requestAnimationFrame(this.tick);
      }

      tick() {
        this.frame = null;

        const distance = this.target - this.current;
        if (this.reduceMotion || Math.abs(distance) < 0.5) {
          this.current = this.target;
        } else {
          this.current += distance * 0.12;
        }

        this.render();
        if (this.current !== this.target) this.frame = requestAnimationFrame(this.tick);
      }

      render() {
        const growth = this.track > 0 ? Math.round((this.current / this.track) * 1000) / 1000 : 0;
        if (growth === this.growth) return;
        this.growth = growth;

        this.style.setProperty('--story-growth', growth);
        this.classList.toggle('is-bloomed', growth >= 0.995);
        this.chapters.forEach((chapter, index) => {
          chapter.classList.toggle('is-reached', this.current >= this.nodeOffsets[index] - 8);
        });

        this.dispatchEvent(new CustomEvent('periwinkle-story:progress', { bubbles: true, detail: { growth } }));
      }

      revealPassedChapters() {
        if (this.pending.length === 0) return;

        const threshold = window.innerHeight * 0.88;
        this.pending = this.pending.filter((chapter) => {
          if (chapter.getBoundingClientRect().top > threshold) return true;
          chapter.classList.add('is-revealed');
          return false;
        });
      }
    }
  );
}
