/**
 * Progress Tracking System (localStorage-based)
 */

const PROGRESS_STORAGE_KEY = 'aws_interview_prep_progress';

/**
 * Initialize progress tracker
 */
function initProgressTracker() {
    if (!localStorage.getItem(PROGRESS_STORAGE_KEY)) {
        localStorage.setItem(PROGRESS_STORAGE_KEY, JSON.stringify({}));
    }
}

/**
 * Get all progress
 */
function getProgress() {
    const stored = localStorage.getItem(PROGRESS_STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
}

/**
 * Update progress for a topic/subtopic/difficulty
 */
function updateProgress(topic, subtopic, difficulty, completed = true) {
    const progress = getProgress();
    const key = `${topic}-${subtopic}-${difficulty}`;
    
    progress[key] = {
        completed,
        timestamp: new Date().toISOString(),
        topic,
        subtopic,
        difficulty
    };
    
    localStorage.setItem(PROGRESS_STORAGE_KEY, JSON.stringify(progress));
    return progress;
}

/**
 * Get progress for specific topic/subtopic/difficulty
 */
function getProgressFor(topic, subtopic, difficulty) {
    const progress = getProgress();
    const key = `${topic}-${subtopic}-${difficulty}`;
    return progress[key] || null;
}

/**
 * Check if topic/subtopic/difficulty is completed
 */
function isCompleted(topic, subtopic, difficulty) {
    const item = getProgressFor(topic, subtopic, difficulty);
    return item ? item.completed : false;
}

/**
 * Calculate completion percentage for a topic
 */
function getTopicCompletion(topic) {
    const progress = getProgress();
    const CONFIG = window.CONFIG || {};
    const topicConfig = CONFIG.TOPICS?.[topic];
    
    if (!topicConfig) return 0;
    
    let total = 0;
    let completed = 0;
    
    topicConfig.subtopics.forEach(subtopic => {
        CONFIG.DIFFICULTIES?.forEach(difficulty => {
            total++;
            if (isCompleted(topic, subtopic, difficulty)) {
                completed++;
            }
        });
    });
    
    return total > 0 ? (completed / total) * 100 : 0;
}

/**
 * Get overall progress
 */
function getOverallProgress() {
    const progress = getProgress();
    const CONFIG = window.CONFIG || {};
    const topics = Object.keys(CONFIG.TOPICS || {});
    
    let total = 0;
    let completed = 0;
    
    topics.forEach(topic => {
        const topicConfig = CONFIG.TOPICS[topic];
        topicConfig.subtopics.forEach(subtopic => {
            CONFIG.DIFFICULTIES?.forEach(difficulty => {
                total++;
                if (isCompleted(topic, subtopic, difficulty)) {
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

/**
 * Clear all progress
 */
function clearProgress() {
    localStorage.removeItem(PROGRESS_STORAGE_KEY);
    initProgressTracker();
}

// Initialize on load
if (typeof window !== 'undefined') {
    initProgressTracker();
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initProgressTracker,
        getProgress,
        updateProgress,
        getProgressFor,
        isCompleted,
        getTopicCompletion,
        getOverallProgress,
        clearProgress
    };
}
