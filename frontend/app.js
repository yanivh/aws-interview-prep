/**
 * Main Application Logic
 */

// Initialize components
let topicNavigation;
let difficultySelector;
let questionCard;
let timer;
let hintReveal;
let feedbackPanel;
let learningPath;
let progressDashboard;

// Application state
let currentTopic = null;
let currentSubtopic = null;
let currentDifficulty = 'intermediate';
let currentQuestion = null;
let questionHistory = [];
let currentQuestionIndex = -1;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initComponents();
    setupEventListeners();
    loadTopics();
});

function initComponents() {
    // Initialize components
    topicNavigation = new TopicNavigation('topic-nav');
    difficultySelector = new DifficultySelector('difficulty-selector');
    difficultySelector.init();
    questionCard = new QuestionCard('question-card');
    timer = new Timer('timer');
    hintReveal = new HintReveal('hint-container');
    feedbackPanel = new FeedbackPanel('feedback-panel');
    learningPath = new LearningPath('learning-plan-content');
    progressDashboard = new ProgressDashboard('progress-dashboard');

    // Setup component callbacks
    difficultySelector.onChange = (difficulty) => {
        currentDifficulty = difficulty;
    };

    topicNavigation.onSubtopicChange = (topic, subtopic) => {
        currentTopic = topic;
        currentSubtopic = subtopic;
        updateSubtopicSelectors(topic, subtopic);
    };
}

function setupEventListeners() {
    // Mode switching
    document.getElementById('practice-mode-btn')?.addEventListener('click', () => switchMode('practice'));
    document.getElementById('flashcard-mode-btn')?.addEventListener('click', () => switchMode('flashcard'));

    // Question generation
    document.getElementById('generate-question-btn')?.addEventListener('click', generateQuestion);
    document.getElementById('generate-flashcard-btn')?.addEventListener('click', generateFlashcard);

    // Answer submission
    document.getElementById('submit-answer-btn')?.addEventListener('click', submitAnswer);

    // Hint reveal
    document.getElementById('show-hint-btn')?.addEventListener('click', () => {
        hintReveal.toggle();
    });

    // Timer
    document.getElementById('reset-timer-btn')?.addEventListener('click', () => {
        timer.reset();
        timer.start();
    });

    // Navigation
    document.getElementById('next-question-btn')?.addEventListener('click', nextQuestion);
    document.getElementById('prev-question-btn')?.addEventListener('click', prevQuestion);

    // Modals
    document.getElementById('learning-plan-btn')?.addEventListener('click', showLearningPlan);
    document.getElementById('progress-btn')?.addEventListener('click', showProgress);
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', closeModals);
    });

    // Topic/Subtopic selectors
    document.getElementById('topic-select')?.addEventListener('change', (e) => {
        currentTopic = e.target.value;
        updateSubtopicOptions(currentTopic);
    });

    document.getElementById('subtopic-select')?.addEventListener('change', (e) => {
        currentSubtopic = e.target.value;
    });
}

function loadTopics() {
    // Load topics from config
    const topics = CONFIG.TOPICS;
    
    // Render topic navigation
    if (topicNavigation) {
        topicNavigation.render(topics);
    }

    // Populate topic selectors
    populateTopicSelectors(topics);
}

function populateTopicSelectors(topics) {
    const practiceTopicSelect = document.getElementById('topic-select');
    const flashcardTopicSelect = document.getElementById('flashcard-topic-select');

    Object.keys(topics).forEach(topicKey => {
        const topic = topics[topicKey];
        
        [practiceTopicSelect, flashcardTopicSelect].forEach(select => {
            if (select) {
                const option = document.createElement('option');
                option.value = topicKey;
                option.textContent = topic.name;
                select.appendChild(option);
            }
        });
    });

    // Set default
    if (Object.keys(topics).length > 0) {
        currentTopic = Object.keys(topics)[0];
        updateSubtopicOptions(currentTopic);
    }
}

function updateSubtopicOptions(topic) {
    const practiceSubtopicSelect = document.getElementById('subtopic-select');
    const flashcardSubtopicSelect = document.getElementById('flashcard-subtopic-select');

    const topicConfig = CONFIG.TOPICS[topic];
    if (!topicConfig) return;

    [practiceSubtopicSelect, flashcardSubtopicSelect].forEach(select => {
        if (select) {
            select.innerHTML = '';
            topicConfig.subtopics.forEach(subtopic => {
                const option = document.createElement('option');
                option.value = subtopic;
                option.textContent = subtopic.split('-').map(w => 
                    w.charAt(0).toUpperCase() + w.slice(1)
                ).join(' ');
                select.appendChild(option);
            });
            
            if (topicConfig.subtopics.length > 0) {
                currentSubtopic = topicConfig.subtopics[0];
            }
        }
    });
}

function updateSubtopicSelectors(topic, subtopic) {
    const practiceTopicSelect = document.getElementById('topic-select');
    const practiceSubtopicSelect = document.getElementById('subtopic-select');
    
    if (practiceTopicSelect) practiceTopicSelect.value = topic;
    if (practiceSubtopicSelect) practiceSubtopicSelect.value = subtopic;
}

function switchMode(mode) {
    const practiceView = document.getElementById('practice-view');
    const flashcardView = document.getElementById('flashcard-view');
    const practiceBtn = document.getElementById('practice-mode-btn');
    const flashcardBtn = document.getElementById('flashcard-mode-btn');

    if (mode === 'practice') {
        practiceView?.classList.remove('hidden');
        flashcardView?.classList.add('hidden');
        practiceBtn?.classList.add('active');
        flashcardBtn?.classList.remove('active');
    } else {
        practiceView?.classList.add('hidden');
        flashcardView?.classList.remove('hidden');
        practiceBtn?.classList.remove('active');
        flashcardBtn?.classList.add('active');
    }
}

async function generateQuestion() {
    if (CONFIG.isApiPlaceholder()) {
        alert(
            'API not configured.\n\n' +
            'Replace YOUR_API_ID in frontend/config.js with your API Gateway ID.\n\n' +
            'After deploying your Lambda and API Gateway, set:\n' +
            'API_ENDPOINT: \'https://<your-api-id>.execute-api.eu-central-1.amazonaws.com/prod\''
        );
        return;
    }

    const topic = document.getElementById('topic-select')?.value || currentTopic;
    const subtopic = document.getElementById('subtopic-select')?.value || currentSubtopic;
    const difficulty = difficultySelector.getSelected() || currentDifficulty;

    if (!topic || !subtopic || !difficulty) {
        alert('Please select topic, subtopic, and difficulty');
        return;
    }

    // Show loading state
    const btn = document.getElementById('generate-question-btn');
    const originalText = btn.textContent;
    btn.textContent = 'Generating...';
    btn.disabled = true;

    try {
        const response = await fetch(`${CONFIG.API_ENDPOINT}${CONFIG.ENDPOINTS.generateQuestion}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic, subtopic, difficulty })
        });

        const data = await response.json();

        // Handle API Gateway response format (if body is a string, parse it)
        let questionData = data;
        if (data.body && typeof data.body === 'string') {
            try {
                questionData = JSON.parse(data.body);
            } catch (e) {
                console.error('Error parsing response body:', e);
            }
        }

        // On HTTP error, surface the API error message
        if (!response.ok) {
            const msg = questionData.message || questionData.error || `HTTP error! status: ${response.status}`;
            throw new Error(msg);
        }
        
        // Check if we got an error response (e.g. 200 with error payload)
        if (questionData.error) {
            throw new Error(questionData.message || questionData.error);
        }
        
        // Validate required fields
        if (!questionData.question || !questionData.answer) {
            throw new Error('Invalid response format: missing question or answer');
        }
        
        // Add to history
        questionHistory.push(questionData);
        currentQuestionIndex = questionHistory.length - 1;
        currentQuestion = questionData;

        // Display question
        questionCard.display(questionData);
        hintReveal.setAnswer(questionData.answer);
        feedbackPanel.hide();

        // Start timer
        timer.reset();
        timer.start();

        // Update progress tracking
        updateProgressTracking(topic, subtopic, difficulty);

        updateQuestionNavButtons();

    } catch (error) {
        console.error('Error generating question:', error);
        if (error.message === 'Failed to fetch' && CONFIG.isApiPlaceholder()) {
            alert(
                'Could not reach the API. Make sure YOUR_API_ID in frontend/config.js is replaced with your real API Gateway ID.'
            );
            return;
        }
        const errorMessage = error.message || 'Failed to generate question. Please try again.';
        alert(`Error: ${errorMessage}\n\nCheck the browser console for more details.`);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function submitAnswer() {
    if (CONFIG.isApiPlaceholder()) {
        alert(
            'API not configured. Replace YOUR_API_ID in frontend/config.js with your API Gateway ID.'
        );
        return;
    }
    if (!currentQuestion) {
        alert('Please generate a question first');
        return;
    }

    const userAnswer = document.getElementById('user-answer')?.value;
    if (!userAnswer || userAnswer.trim() === '') {
        alert('Please enter your answer');
        return;
    }

    // Show loading
    const btn = document.getElementById('submit-answer-btn');
    const originalText = btn.textContent;
    btn.textContent = 'Evaluating...';
    btn.disabled = true;

    try {
        const topic = currentQuestion.topic ?? currentTopic;
        const difficulty = currentQuestion.difficulty ?? currentDifficulty;
        if (!topic || !currentQuestion.question) {
            alert('Missing question data. Please generate a new question.');
            return;
        }

        const response = await fetch(`${CONFIG.API_ENDPOINT}${CONFIG.ENDPOINTS.evaluateAnswer}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                topic,
                question: currentQuestion.question,
                user_answer: userAnswer,
                difficulty
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Handle API Gateway response format (body may be a string)
        let feedback = data;
        if (data.body !== undefined) {
            if (typeof data.body === 'string') {
                try {
                    feedback = JSON.parse(data.body);
                } catch (e) {
                    console.error('Error parsing evaluate response body:', e);
                    throw new Error('Invalid response format from server');
                }
            } else {
                feedback = data.body;
            }
        }

        if (feedback.error) {
            throw new Error(feedback.message || feedback.error);
        }

        feedbackPanel.display(feedback);

        // Stop timer
        timer.stop();

        // Mark as completed
        if (currentQuestion) {
            updateProgress(currentQuestion.topic, currentQuestion.subtopic, currentQuestion.difficulty, true);
        }

    } catch (error) {
        console.error('Error evaluating answer:', error);
        const message = error.message || 'Failed to evaluate answer. Please try again.';
        alert(`Error: ${message}\n\nCheck the browser console for details.`);
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

async function generateFlashcard() {
    const topic = document.getElementById('flashcard-topic-select')?.value;
    const subtopic = document.getElementById('flashcard-subtopic-select')?.value;
    const difficulty = document.getElementById('flashcard-difficulty-select')?.value;

    if (!topic || !subtopic || !difficulty) {
        alert('Please select topic, subtopic, and difficulty');
        return;
    }

    const btn = document.getElementById('generate-flashcard-btn');
    const originalText = btn.textContent;
    btn.textContent = 'Generating...';
    btn.disabled = true;

    try {
        const response = await fetch(`${CONFIG.API_ENDPOINT}${CONFIG.ENDPOINTS.getFlashcard}?topic=${topic}&subtopic=${subtopic}&difficulty=${difficulty}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Handle API Gateway response format (if body is a string, parse it)
        let flashcardData = data;
        if (data.body && typeof data.body === 'string') {
            try {
                flashcardData = JSON.parse(data.body);
            } catch (e) {
                console.error('Error parsing response body:', e);
            }
        }
        
        // Display flashcard
        const front = document.getElementById('flashcard-front');
        const back = document.getElementById('flashcard-back');
        const flashcard = document.getElementById('flashcard');
        
        if (front) {
            front.textContent = flashcardData.front || 'No front content';
        }
        
        if (back) {
            // Remove hidden class and ensure content is set
            back.classList.remove('hidden');
            back.innerHTML = `
                <div class="flashcard-content">
                    <p>${flashcardData.back || 'No answer provided'}</p>
                    ${flashcardData.key_points && flashcardData.key_points.length > 0 ? `
                        <div class="key-points">
                            <strong>Key Points:</strong>
                            <ul>
                                ${flashcardData.key_points.map(p => `<li>${p}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        // Reset flip state
        if (flashcard) {
            flashcard.classList.remove('flipped');
        }

        document.getElementById('flashcard-display')?.classList.remove('hidden');

    } catch (error) {
        console.error('Error generating flashcard:', error);
        alert('Failed to generate flashcard. Please try again.');
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

function flipFlashcard() {
    const flashcard = document.getElementById('flashcard');
    const front = document.getElementById('flashcard-front');
    const back = document.getElementById('flashcard-back');
    
    if (flashcard && front && back) {
        flashcard.classList.toggle('flipped');
    }
}

document.getElementById('flip-flashcard-btn')?.addEventListener('click', flipFlashcard);

function nextQuestion() {
    if (currentQuestionIndex < questionHistory.length - 1) {
        currentQuestionIndex++;
        currentQuestion = questionHistory[currentQuestionIndex];
        questionCard.display(currentQuestion);
        hintReveal.setAnswer(currentQuestion.answer);
        hintReveal.hide();
        feedbackPanel.hide();
        document.getElementById('user-answer').value = '';
        timer.reset();
        timer.start();
        updateQuestionNavButtons();
    } else {
        // At end of history: generate a new question (same topic/subtopic/difficulty)
        generateQuestion();
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        currentQuestion = questionHistory[currentQuestionIndex];
        questionCard.display(currentQuestion);
        hintReveal.setAnswer(currentQuestion.answer);
        hintReveal.hide();
        feedbackPanel.hide();
        document.getElementById('user-answer').value = '';
        timer.reset();
        timer.start();
        updateQuestionNavButtons();
    }
}

function updateQuestionNavButtons() {
    const prevBtn = document.getElementById('prev-question-btn');
    const nextBtn = document.getElementById('next-question-btn');
    if (prevBtn) prevBtn.disabled = currentQuestionIndex <= 0;
    // Next is always enabled: either goes to next in history or generates new question
    if (nextBtn) nextBtn.disabled = false;
}

function showLearningPlan() {
    const modal = document.getElementById('learning-plan-modal');
    const progress = getProgress();
    const learningPlan = getLearningPlan();
    
    if (learningPath && modal) {
        learningPath.render(learningPlan, progress);
        modal.classList.remove('hidden');
    }
}

function showProgress() {
    const modal = document.getElementById('progress-modal');
    const progress = getProgress();
    
    if (progressDashboard && modal) {
        progressDashboard.render(progress, CONFIG.TOPICS);
        modal.classList.remove('hidden');
    }
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.add('hidden');
    });
}

function updateProgressTracking(topic, subtopic, difficulty) {
    // Track that user has viewed this question
    // Completion will be marked when answer is submitted
}

// Make functions available globally
window.generateQuestion = generateQuestion;
window.submitAnswer = submitAnswer;
window.generateFlashcard = generateFlashcard;
