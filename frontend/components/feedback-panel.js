/**
 * Feedback Panel Component
 */

class FeedbackPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    display(feedbackData) {
        if (!this.container) return;

        const score = feedbackData.score || 0;
        const feedback = feedbackData.feedback || '';
        const strengths = feedbackData.strengths || [];
        const improvements = feedbackData.improvements || [];
        const expectedKeyPoints = feedbackData.expected_key_points || [];
        const missingKeyPoints = feedbackData.missing_key_points || [];

        this.container.innerHTML = `
            <div class="feedback-header">
                <h3>Answer Evaluation</h3>
                <div class="score-display score-${this.getScoreClass(score)}">
                    Score: ${score}/100
                </div>
            </div>
            
            <div class="feedback-content">
                <div class="feedback-text">
                    <h4>Feedback</h4>
                    <p>${feedback}</p>
                </div>
                
                ${strengths.length > 0 ? `
                    <div class="feedback-section strengths">
                        <h4>✅ Strengths</h4>
                        <ul>
                            ${strengths.map(s => `<li>${s}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${improvements.length > 0 ? `
                    <div class="feedback-section improvements">
                        <h4>📈 Areas for Improvement</h4>
                        <ul>
                            ${improvements.map(i => `<li>${i}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${expectedKeyPoints.length > 0 ? `
                    <div class="feedback-section expected-points">
                        <h4>Key Points Expected</h4>
                        <ul>
                            ${expectedKeyPoints.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                ${missingKeyPoints.length > 0 ? `
                    <div class="feedback-section missing-points">
                        <h4>⚠️ Missing Key Points</h4>
                        <ul>
                            ${missingKeyPoints.map(p => `<li>${p}</li>`).join('')}
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
        if (score >= 80) return 'excellent';
        if (score >= 60) return 'good';
        if (score >= 40) return 'fair';
        return 'poor';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FeedbackPanel;
}
