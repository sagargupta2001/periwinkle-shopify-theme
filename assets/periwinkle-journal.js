/*
  Periwinkle journal — share links.

  The WhatsApp link works without JS. JS reveals a second button that uses the
  native share sheet where there is one (most phones) and copies the link
  everywhere else.
*/
if (!customElements.get('periwinkle-journal-share')) {
  customElements.define(
    'periwinkle-journal-share',
    class PeriwinkleJournalShare extends HTMLElement {
      connectedCallback() {
        this.button = this.querySelector('[data-share-copy]');
        this.label = this.querySelector('[data-share-label]');
        this.status = this.querySelector('[data-share-status]');
        if (!this.button) return;

        this.canShare = typeof navigator.share === 'function';
        this.canCopy = navigator.clipboard && typeof navigator.clipboard.writeText === 'function';
        if (!this.canShare && !this.canCopy) return;

        this.defaultLabel = this.canShare ? 'More options' : 'Copy link';
        this.label.textContent = this.defaultLabel;
        this.button.hidden = false;
        this.button.addEventListener('click', () => this.share());
      }

      async share() {
        const url = this.dataset.url;

        if (this.canShare) {
          try {
            await navigator.share({ title: this.dataset.title, url });
          } catch (error) {
            /* Dismissing the share sheet rejects; nothing to do. */
          }
          return;
        }

        try {
          await navigator.clipboard.writeText(url);
          this.label.textContent = 'Link copied';
          this.status.textContent = 'Link copied to clipboard';
          clearTimeout(this.resetTimer);
          this.resetTimer = setTimeout(() => {
            this.label.textContent = this.defaultLabel;
            this.status.textContent = '';
          }, 2400);
        } catch (error) {
          this.status.textContent = 'Could not copy the link';
        }
      }
    }
  );
}
