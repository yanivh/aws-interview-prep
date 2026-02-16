/**
 * Question Card Component
 */

class QuestionCard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentQuestion = null;
    }

    display(questionData) {
        if (!this.container) return;

        this.currentQuestion = questionData;
        const questionText = this.container.querySelector('#question-text');
        
        if (questionText) {
            questionText.textContent = questionData.question || '';
        }

        // Show container
        const questionContainer = document.getElementById('question-container');
        if (questionContainer) {
            questionContainer.classList.remove('hidden');
        }
    }

    clear() {
        if (this.container) {
            const questionText = this.container.querySelector('#question-text');
            if (questionText) {
                questionText.textContent = '';
            }
        }
        this.currentQuestion = null;
    }

    getCurrentQuestion() {
        return this.currentQuestion;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuestionCard;
}
