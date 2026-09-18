/*
  Periwinkle journal — share icons.

  The WhatsApp link works without JS. JS reveals a second icon button whose
  mode depends on the device: "share" opens the native share sheet (most
  phones), "copy" copies the link and briefly shows a tick and a toast.
*/
if (!customElements.get('periwinkle-journal-share')) {
  customElements.define(
    'periwinkle-journal-share',
    class PeriwinkleJournalShare extends HTMLElement {
      connectedCallback() {
        this.button = this.querySelector('[data-share-copy]');
        this.status = this.querySelector('[data-share-status]');
        if (!this.button) return;

        const canShare = typeof navigator.share === 'function';
        const canCopy = navigator.clipboard && typeof navigator.clipboard.writeText === 'function';
        if (!canShare && !canCopy) return;

        this.mode = canShare ? 'share' : 'copy';
        this.button.dataset.mode = this.mode;
        const label = this.mode === 'share' ? 'More sharing options' : 'Copy link';
        this.button.setAttribute('aria-label', label);
        this.button.title = label;
        this.button.hidden = false;
        this.button.addEventListener('click', () => this.share());
      }

      async share() {
        const url = this.dataset.url;

        if (this.mode === 'share') {
          try {
            await navigator.share({ title: this.dataset.title, url });
          } catch (error) {
            /* Dismissing the share sheet rejects; nothing to do. */
          }
          return;
        }

        try {
          await navigator.clipboard.writeText(url);
          this.button.dataset.state = 'copied';
          this.status.textContent = 'Link copied to clipboard';
          clearTimeout(this.resetTimer);
          this.resetTimer = setTimeout(() => {
            delete this.button.dataset.state;
            this.status.textContent = '';
          }, 2000);
        } catch (error) {
          this.status.textContent = 'Could not copy the link';
        }
      }

      disconnectedCallback() {
        clearTimeout(this.resetTimer);
      }
    }
  );
}
