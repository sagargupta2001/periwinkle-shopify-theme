/*
  Periwinkle coming soon — gentle reveal on scroll, and the before/after slider.

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

/*
  Before/after slider. Without JS the comparison rests at a 50/50 split.

  Pointer: a mouse press jumps the handle to the cursor, then drags. A touch
  only moves the handle once the finger travels sideways; the frame's
  `touch-action: pan-y` hands vertical swipes back to the browser (which then
  sends pointercancel), so the page still scrolls over the image.

  Keyboard and screen readers use the visually hidden range input.

  When the slider first comes into view it sways once to show that it moves,
  only if motion is allowed, outside the editor, and before any interaction.
*/
if (!customElements.get('periwinkle-compare')) {
  customElements.define(
    'periwinkle-compare',
    class PeriwinkleCompare extends HTMLElement {
      constructor() {
        super();
        this.onPointerDown = this.onPointerDown.bind(this);
        this.onPointerMove = this.onPointerMove.bind(this);
        this.onPointerEnd = this.onPointerEnd.bind(this);
        this.onRangeInput = this.onRangeInput.bind(this);
      }

      connectedCallback() {
        this.frame = this.querySelector('[data-compare-frame]');
        this.range = this.querySelector('input[type="range"]');
        if (!this.frame || !this.range) return;

        this.beforeLabel = this.range.dataset.beforeLabel || 'Before';
        this.afterLabel = this.range.dataset.afterLabel || 'After';
        this.pointerId = null;

        this.range.removeAttribute('tabindex');
        this.range.addEventListener('input', this.onRangeInput);
        this.frame.addEventListener('pointerdown', this.onPointerDown);
        this.frame.addEventListener('pointermove', this.onPointerMove);
        this.frame.addEventListener('pointerup', this.onPointerEnd);
        this.frame.addEventListener('pointercancel', this.onPointerEnd);
        this.frame.addEventListener('lostpointercapture', this.onPointerEnd);

        this.setPosition(Number(this.range.value) || 50);
        this.classList.add('is-ready');
        this.observeForHint();
      }

      disconnectedCallback() {
        this.stopHint();
        if (this.hintObserver) this.hintObserver.disconnect();
        if (!this.frame) return;
        this.range.removeEventListener('input', this.onRangeInput);
        this.frame.removeEventListener('pointerdown', this.onPointerDown);
        this.frame.removeEventListener('pointermove', this.onPointerMove);
        this.frame.removeEventListener('pointerup', this.onPointerEnd);
        this.frame.removeEventListener('pointercancel', this.onPointerEnd);
        this.frame.removeEventListener('lostpointercapture', this.onPointerEnd);
      }

      setPosition(value) {
        const position = Math.round(Math.min(100, Math.max(0, value)) * 10) / 10;
        this.style.setProperty('--compare-position', position);

        const rounded = Math.round(position);
        if (Number(this.range.value) !== rounded) this.range.value = rounded;
        this.range.setAttribute(
          'aria-valuetext',
          `${this.beforeLabel} ${rounded}%, ${this.afterLabel} ${100 - rounded}%`
        );
      }

      positionFromEvent(event) {
        const rect = this.frame.getBoundingClientRect();
        if (!rect.width) return;
        this.setPosition(((event.clientX - rect.left) / rect.width) * 100);
      }

      onRangeInput() {
        this.interacted();
        this.setPosition(Number(this.range.value));
      }

      onPointerDown(event) {
        if (event.pointerType === 'mouse' && event.button !== 0) return;
        this.interacted();
        this.pointerId = event.pointerId;
        this.startX = event.clientX;
        this.dragging = event.pointerType === 'mouse';

        if (this.dragging) {
          event.preventDefault();
          this.capture(event.pointerId);
          this.classList.add('is-dragging');
          this.positionFromEvent(event);
        }
      }

      onPointerMove(event) {
        if (event.pointerId !== this.pointerId) return;

        // A release outside the window can go unreported; a buttonless mouse move means the drag is over.
        if (event.pointerType === 'mouse' && event.buttons === 0) {
          this.onPointerEnd(event);
          return;
        }

        if (!this.dragging) {
          // Touch or pen: wait for a sideways movement before taking over.
          if (Math.abs(event.clientX - this.startX) < 4) return;
          this.dragging = true;
          this.capture(event.pointerId);
          this.classList.add('is-dragging');
        }

        this.positionFromEvent(event);
      }

      capture(pointerId) {
        // Capture keeps the drag alive outside the frame; it can throw if the pointer is already gone.
        try {
          this.frame.setPointerCapture(pointerId);
        } catch (error) {
          /* The drag still works while the pointer stays over the frame. */
        }
      }

      onPointerEnd(event) {
        if (this.pointerId === null || event.pointerId !== this.pointerId) return;
        if (this.frame.hasPointerCapture(event.pointerId)) {
          this.frame.releasePointerCapture(event.pointerId);
        }
        this.pointerId = null;
        this.dragging = false;
        this.classList.remove('is-dragging');
      }

      interacted() {
        this.hasInteracted = true;
        this.stopHint();
        if (this.hintObserver) this.hintObserver.disconnect();
      }

      observeForHint() {
        const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const inEditor = window.Shopify && window.Shopify.designMode;
        if (reducedMotion || inEditor || !('IntersectionObserver' in window)) return;

        this.hintObserver = new IntersectionObserver(
          (entries) => {
            if (!entries.some((entry) => entry.isIntersecting)) return;
            this.hintObserver.disconnect();
            // Let the section's reveal settle before swaying.
            this.hintTimer = setTimeout(() => this.playHint(), 700);
          },
          { threshold: 0.6 }
        );
        this.hintObserver.observe(this);
      }

      playHint() {
        if (this.hasInteracted) return;

        const stops = [50, 64, 36, 50];
        const duration = 2200;
        const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
        const start = performance.now();

        const step = (now) => {
          const progress = Math.min(1, (now - start) / duration);
          const scaled = progress * (stops.length - 1);
          const index = Math.min(stops.length - 2, Math.floor(scaled));
          const local = ease(scaled - index);
          this.setPosition(stops[index] + (stops[index + 1] - stops[index]) * local);
          if (progress < 1) this.hintFrame = requestAnimationFrame(step);
        };

        this.hintFrame = requestAnimationFrame(step);
      }

      stopHint() {
        clearTimeout(this.hintTimer);
        cancelAnimationFrame(this.hintFrame);
      }
    }
  );
}
