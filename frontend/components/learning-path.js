/**
 * Learning Path Visualization Component
 */

class LearningPath {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(learningPlan, currentProgress) {
        if (!this.container) return;

        this.container.innerHTML = '';

        learningPlan.phases.forEach((phase, index) => {
            const phaseElement = this.renderPhase(phase, index, currentProgress);
            this.container.appendChild(phaseElement);
        });
    }

    renderPhase(phase, index, progress) {
        const phaseDiv = document.createElement('div');
        phaseDiv.className = 'learning-phase';
        phaseDiv.dataset.phase = phase.phase;

        const progressPercent = this.calculatePhaseProgress(phase, progress);

        phaseDiv.innerHTML = `
            <div class="phase-header">
                <div class="phase-number">Phase ${phase.phase}</div>
                <div class="phase-name">${phase.name}</div>
                <div class="phase-weeks">${phase.weeks}</div>
            </div>
            <div class="phase-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${progressPercent}%"></div>
                </div>
                <span class="progress-text">${Math.round(progressPercent)}%</span>
            </div>
            <div class="phase-description">${phase.description}</div>
            <div class="phase-topics">
                ${this.renderTopics(phase.topics)}
            </div>
        `;

        return phaseDiv;
    }

    renderTopics(topics) {
        return topics.map(topicConfig => {
            const topicName = topicConfig.topic;
            const subtopics = topicConfig.subtopics;
            return `
                <div class="phase-topic">
                    <strong>${topicName}</strong>
                    <span class="subtopics">${subtopics.length} subtopics</span>
                </div>
            `;
        }).join('');
    }

    calculatePhaseProgress(phase, progress) {
        let total = 0;
        let completed = 0;

        phase.topics.forEach(topicConfig => {
            const topic = topicConfig.topic;
            const subtopics = topicConfig.subtopics;
            const difficulties = Array.isArray(topicConfig.difficulty)
                ? topicConfig.difficulty
                : [topicConfig.difficulty];

            subtopics.forEach(subtopic => {
                difficulties.forEach(difficulty => {
                    total++;
                    const key = `${topic}-${subtopic}-${difficulty}`;
                    if (progress[key] && progress[key].completed) {
                        completed++;
                    }
                });
            });
        });

        return total > 0 ? (completed / total) * 100 : 0;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LearningPath;
}
