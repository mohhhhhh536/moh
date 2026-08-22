if (!customElements.get('before-after-slider')) {
  class BeforeAfterSlider extends HTMLElement {
    connectedCallback() {
      this.range = this.querySelector('.thessvane-ba__range');
      if (!this.range) return;
      this.update = this.update.bind(this);
      this.range.addEventListener('input', this.update);
      this.update();
    }

    disconnectedCallback() {
      if (this.range) this.range.removeEventListener('input', this.update);
    }

    update() {
      this.style.setProperty('--reveal', `${this.range.value}%`);
    }
  }

  customElements.define('before-after-slider', BeforeAfterSlider);
}
