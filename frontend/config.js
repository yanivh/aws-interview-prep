/**
 * Configuration for Interview Prep App
 */

const CONFIG = {
    // API Gateway endpoint (will be set during deployment)
    API_ENDPOINT: 'https://s7ow2cvh6i.execute-api.eu-central-1.amazonaws.com/prod',
    
    // Topics configuration
    TOPICS: {
        linux: {
            name: 'Linux',
            description: 'Linux systems in AWS environments',
            subtopics: [
                'processes', 'memory', 'disk', 'package-management', 
                'boot-process', 'daemons', 'load-average', 'shells', 
                'security-hardening', 'troubleshooting'
            ]
        },
        networking: {
            name: 'Networking',
            description: 'Networking in AWS',
            subtopics: ['tls', 'certificate-validation', 'load-balancing', 'troubleshooting']
        },
        'operational-excellence': {
            name: 'Operational Excellence',
            description: 'Operational Excellence, Automation & Process Improvement',
            subtopics: ['performance', 'automation', 'incidents', 'scale']
        },
        scripting: {
            name: 'Scripting',
            description: 'Scripting for AWS automation',
            subtopics: ['log-parsing', 'system-maintenance', 'monitoring', 'text-manipulation', 'user-management']
        }
    },
    
    // Difficulty levels
    DIFFICULTIES: ['newbie', 'intermediate', 'pro'],
    
    // Timer settings
    TIMER_DEFAULT_MINUTES: 30,
    
    // API endpoints
    ENDPOINTS: {
        generateQuestion: '/generate-question',
        evaluateAnswer: '/evaluate-answer',
        getTopics: '/topics',
        getFlashcard: '/flashcard',
        getLearningPlan: '/learning-plan',
        getProgress: '/progress',
        updateProgress: '/progress'
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
