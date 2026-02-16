/**
 * Learning Plan Data and Logic
 */

const LEARNING_PLAN = {
    phases: [
        {
            phase: 1,
            name: 'Foundation (Newbie Level)',
            description: 'Build foundational knowledge',
            weeks: 'Week 1-3',
            topics: [
                {
                    topic: 'linux',
                    subtopics: ['processes', 'memory', 'disk', 'package-management', 'boot-process', 'daemons', 'load-average', 'shells'],
                    difficulty: 'newbie'
                },
                {
                    topic: 'networking',
                    subtopics: ['tls', 'certificate-validation', 'load-balancing'],
                    difficulty: 'newbie'
                }
            ]
        },
        {
            phase: 2,
            name: 'Application (Intermediate Level)',
            description: 'Apply knowledge to practical scenarios',
            weeks: 'Week 4-7',
            topics: [
                {
                    topic: 'linux',
                    subtopics: ['security-hardening', 'troubleshooting'],
                    difficulty: 'intermediate'
                },
                {
                    topic: 'networking',
                    subtopics: ['troubleshooting'],
                    difficulty: 'intermediate'
                },
                {
                    topic: 'operational-excellence',
                    subtopics: ['performance', 'automation', 'incidents', 'scale'],
                    difficulty: ['newbie', 'intermediate']
                },
                {
                    topic: 'scripting',
                    subtopics: ['log-parsing', 'system-maintenance', 'monitoring', 'text-manipulation', 'user-management'],
                    difficulty: ['newbie', 'intermediate']
                }
            ]
        },
        {
            phase: 3,
            name: 'Integration & Practice',
            description: 'Cross-topic practice and real-world scenarios',
            weeks: 'Week 8',
            topics: [
                {
                    topic: 'mixed',
                    subtopics: ['all'],
                    difficulty: 'intermediate'
                }
            ]
        }
    ],
    totalWeeks: 8,
    description: 'Structured 8-week curriculum covering all topics from basic to intermediate level'
};

/**
 * Get learning plan data
 */
function getLearningPlan() {
    return LEARNING_PLAN;
}

/**
 * Get current phase based on progress
 */
function getCurrentPhase(progress) {
    // Simple logic - can be enhanced
    for (const phase of LEARNING_PLAN.phases) {
        const phaseProgress = calculatePhaseProgress(phase, progress);
        if (phaseProgress < 1.0) {
            return phase;
        }
    }
    return LEARNING_PLAN.phases[LEARNING_PLAN.phases.length - 1];
}

/**
 * Calculate progress for a phase
 */
function calculatePhaseProgress(phase, progress) {
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
                if (progress[key]) {
                    completed++;
                }
            });
        });
    });
    
    return total > 0 ? completed / total : 0;
}

/**
 * Get recommended next step
 */
function getRecommendedNextStep(progress) {
    const currentPhase = getCurrentPhase(progress);
    
    for (const topicConfig of currentPhase.topics) {
        const topic = topicConfig.topic;
        const subtopics = topicConfig.subtopics;
        const difficulties = Array.isArray(topicConfig.difficulty) 
            ? topicConfig.difficulty 
            : [topicConfig.difficulty];
        
        for (const subtopic of subtopics) {
            for (const difficulty of difficulties) {
                const key = `${topic}-${subtopic}-${difficulty}`;
                if (!progress[key]) {
                    return { topic, subtopic, difficulty, phase: currentPhase };
                }
            }
        }
    }
    
    return null;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getLearningPlan,
        getCurrentPhase,
        calculatePhaseProgress,
        getRecommendedNextStep
    };
}
