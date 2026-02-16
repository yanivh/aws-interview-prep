/**
 * Configuration for Interview Prep App
 */

const CONFIG = {
    // API Gateway endpoint - must be your REAL URL after deployment.
    // Do NOT use "abc123xyz" or "YOUR_API_ID" - those are placeholders (DNS will fail).
    // Get your real URL by running: ./QUICK_DEPLOY.sh  (it will print and update this for you)
    // Or in AWS Console: API Gateway → your API → "Invoke URL"
    API_ENDPOINT: 'https://s7ow2cvh6i.execute-api.eu-central-1.amazonaws.com/prod',

    // Returns true if the API endpoint is still a placeholder (not configured)
    isApiPlaceholder() {
        const url = (this.API_ENDPOINT || '').toLowerCase();
        return !url ||
            url.includes('your_api_id') ||
            url.includes('abc123xyz') ||
            url.includes('your-api-id');
    },
    
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
