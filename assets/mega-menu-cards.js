/**
 * Adds scroll affordances to a mega menu card row.
 *
 * The row scrolls natively, so trackpads, touch and keyboard focus already work without this
 * file. What they do not do is tell a mouse user that the row continues past the edge, which is
 * all this element is for: arrows when the row overflows, and edge fades driven by scroll
 * position. If the script never loads, the row still scrolls and the arrows stay hidden.
 */
class MegaMenuCards extends HTMLElement {
  connectedCallback() {
    this.row = this.querySelector('.mega-menu__cards');
    this.prevButton = this.querySelector('[name="previous"]');
    this.nextButton = this.querySelector('[name="next"]');

    if (!this.row || !this.prevButton || !this.nextButton) return;

    this.update = this.update.bind(this);
    this.details = this.closest('details');

    this.prevButton.addEventListener('click', () => this.scrollByPage(-1));
    this.nextButton.addEventListener('click', () => this.scrollByPage(1));
    this.row.addEventListener('scroll', this.update, { passive: true });
    window.addEventListener('resize', this.update);

    // A closed <details> skips layout for its content, so the row cannot be measured until the
    // menu opens and a ResizeObserver on it never reports that first box. The toggle event is
    // the reliable signal; rAF lets the newly opened panel lay out before we read it.
    this.details?.addEventListener('toggle', () => {
      if (this.details.open) requestAnimationFrame(this.update);
    });

    this.update();
  }

  disconnectedCallback() {
    window.removeEventListener('resize', this.update);
    this.row?.removeEventListener('scroll', this.update);
  }

  scrollByPage(direction) {
    // A near-full step keeps one card in view as an anchor between pages.
    const step = Math.max(this.row.clientWidth * 0.8, 1);
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    this.row.scrollBy({ left: step * direction, behavior: reduceMotion ? 'auto' : 'smooth' });
  }

  update() {
    // Sub-pixel widths mean scrollLeft never quite reaches the arithmetic maximum.
    const tolerance = 1;
    const maxScroll = this.row.scrollWidth - this.row.clientWidth;
    const overflows = maxScroll > tolerance;

    this.toggleAttribute('data-overflows', overflows);
    this.toggleAttribute('data-at-start', this.row.scrollLeft <= tolerance);
    this.toggleAttribute('data-at-end', this.row.scrollLeft >= maxScroll - tolerance);

    // Hidden rather than disabled: a control that cannot act should leave the tab order.
    this.prevButton.hidden = !overflows;
    this.nextButton.hidden = !overflows;
  }
}

customElements.define('mega-menu-cards', MegaMenuCards);
