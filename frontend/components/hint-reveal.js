/**
 * Hint/Answer Reveal Component
 */

class HintReveal {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.isRevealed = false;
        this.answerData = null;
    }

    setAnswer(answerData) {
        this.answerData = answerData;
        this.isRevealed = false;
        this.hide();
    }

    show() {
        if (!this.container) return;

        if (this.answerData && !this.isRevealed) {
            // Render answer using answer visualizer
            const visualizer = window.answerVisualizer;
            if (visualizer) {
                visualizer.render(this.answerData);
            }
            
            this.container.classList.remove('hidden');
            this.isRevealed = true;
        }
    }

    hide() {
        if (this.container) {
            this.container.classList.add('hidden');
            this.isRevealed = false;
        }
    }

    toggle() {
        if (this.isRevealed) {
            this.hide();
        } else {
            this.show();
        }
    }

    isAnswerRevealed() {
        return this.isRevealed;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HintReveal;
}
