/**
 * Feedback Panel Component
 */

class FeedbackPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    display(feedbackData) {
        if (!this.container) return;

        if (!feedbackData || typeof feedbackData !== 'object') {
            this.container.innerHTML = '<p class="feedback-error">Invalid feedback data received.</p>';
            this.container.classList.remove('hidden');
            return;
        }

        if (feedbackData.error) {
            this.container.innerHTML = `<p class="feedback-error">${this._escape(feedbackData.message || feedbackData.error)}</p>`;
            this.container.classList.remove('hidden');
            return;
        }

        const score = Number(feedbackData.score) || 0;
        const feedback = String(feedbackData.feedback || '');
        const strengths = Array.isArray(feedbackData.strengths) ? feedbackData.strengths : [];
        const improvements = Array.isArray(feedbackData.improvements) ? feedbackData.improvements : [];
        const expectedKeyPoints = Array.isArray(feedbackData.expected_key_points) ? feedbackData.expected_key_points : [];
        const missingKeyPoints = Array.isArray(feedbackData.missing_key_points) ? feedbackData.missing_key_points : [];

        this.container.innerHTML = `
            <div class="feedback-header">
                <h3>Answer Evaluation</h3>
                <div class="score-display score-${this.getScoreClass(score)}">
                    Score: ${this._escape(String(score))}/100
                </div>
            </div>
            
            <div class="feedback-content">
                <div class="feedback-text">
                    <h4>Feedback</h4>
                    <p>${this._escape(feedback)}</p>
                </div>
                
                ${strengths.length > 0 ? `
                    <div class="feedback-section strengths">
                        <h4>✅ Strengths</h4>
                        <ul>
                            ${strengths.map(s => `<li>${this._escape(String(s))}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${improvements.length > 0 ? `
                    <div class="feedback-section improvements">
                        <h4>📈 Areas for Improvement</h4>
                        <ul>
                            ${improvements.map(i => `<li>${this._escape(String(i))}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${expectedKeyPoints.length > 0 ? `
                    <div class="feedback-section expected-points">
                        <h4>Key Points Expected</h4>
                        <ul>
                            ${expectedKeyPoints.map(p => `<li>${this._escape(String(p))}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${missingKeyPoints.length > 0 ? `
                    <div class="feedback-section missing-points">
                        <h4>⚠️ Missing Key Points</h4>
                        <ul>
                            ${missingKeyPoints.map(p => `<li>${this._escape(String(p))}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;

        this.container.classList.remove('hidden');
    }

    hide() {
        if (this.container) {
            this.container.classList.add('hidden');
        }
    }

    getScoreClass(score) {
        const n = Number(score);
        if (n >= 80) return 'excellent';
        if (n >= 60) return 'good';
        if (n >= 40) return 'fair';
        return 'poor';
    }

    _escape(str) {
        if (str == null) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FeedbackPanel;
}
