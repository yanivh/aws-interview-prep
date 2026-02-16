/**
 * Progress Dashboard Component
 */

class ProgressDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(progress, topics) {
        if (!this.container) return;

        const overall = this.calculateOverallProgress(progress, topics);

        this.container.innerHTML = `
            <div class="progress-overview">
                <h3>Overall Progress</h3>
                <div class="overall-progress-bar">
                    <div class="progress-fill" style="width: ${overall.percentage}%"></div>
                </div>
                <div class="progress-stats">
                    <span>${overall.completed} / ${overall.total} completed</span>
                    <span class="percentage">${Math.round(overall.percentage)}%</span>
                </div>
            </div>

            <div class="topic-progress-list">
                ${this.renderTopicProgress(progress, topics)}
            </div>
        `;
    }

    calculateOverallProgress(progress, topics) {
        let total = 0;
        let completed = 0;

        Object.keys(topics).forEach(topicKey => {
            const topic = topics[topicKey];
            topic.subtopics.forEach(subtopic => {
                ['newbie', 'intermediate', 'pro'].forEach(difficulty => {
                    total++;
                    const key = `${topicKey}-${subtopic}-${difficulty}`;
                    if (progress[key] && progress[key].completed) {
                        completed++;
                    }
                });
            });
        });

        return {
            total,
            completed,
            percentage: total > 0 ? (completed / total) * 100 : 0
        };
    }

    renderTopicProgress(progress, topics) {
        return Object.keys(topics).map(topicKey => {
            const topic = topics[topicKey];
            const topicProgress = this.calculateTopicProgress(progress, topicKey, topic);

            return `
                <div class="topic-progress-item">
                    <div class="topic-progress-header">
                        <strong>${topic.name}</strong>
                        <span class="topic-progress-percentage">${Math.round(topicProgress.percentage)}%</span>
                    </div>
                    <div class="topic-progress-bar">
                        <div class="progress-fill" style="width: ${topicProgress.percentage}%"></div>
                    </div>
                    <div class="topic-progress-stats">
                        ${topicProgress.completed} / ${topicProgress.total} completed
                    </div>
                </div>
            `;
        }).join('');
    }

    calculateTopicProgress(progress, topicKey, topic) {
        let total = 0;
        let completed = 0;

        topic.subtopics.forEach(subtopic => {
            ['newbie', 'intermediate', 'pro'].forEach(difficulty => {
                total++;
                const key = `${topicKey}-${subtopic}-${difficulty}`;
                if (progress[key] && progress[key].completed) {
                    completed++;
                }
            });
        });

        return {
            total,
            completed,
            percentage: total > 0 ? (completed / total) * 100 : 0
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProgressDashboard;
}
