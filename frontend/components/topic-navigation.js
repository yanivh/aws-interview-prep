/**
 * Topic Navigation Component
 */

class TopicNavigation {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.onTopicChange = null;
        this.onSubtopicChange = null;
    }

    render(topics) {
        if (!this.container) return;

        const nav = document.createElement('nav');
        nav.className = 'topic-nav';

        Object.keys(topics).forEach(topicKey => {
            const topic = topics[topicKey];
            const topicSection = this.createTopicSection(topicKey, topic);
            nav.appendChild(topicSection);
        });

        this.container.innerHTML = '';
        this.container.appendChild(nav);
    }

    createTopicSection(topicKey, topic) {
        const section = document.createElement('div');
        section.className = 'topic-section';
        section.dataset.topic = topicKey;

        const header = document.createElement('div');
        header.className = 'topic-header';
        header.textContent = topic.name;
        header.addEventListener('click', () => this.toggleTopic(topicKey));
        section.appendChild(header);

        const subtopicList = document.createElement('ul');
        subtopicList.className = 'subtopic-list';
        subtopicList.style.display = 'none';

        topic.subtopics.forEach(subtopic => {
            const item = document.createElement('li');
            item.className = 'subtopic-item';
            item.textContent = this.formatSubtopicName(subtopic);
            item.dataset.topic = topicKey;
            item.dataset.subtopic = subtopic;
            item.addEventListener('click', () => this.selectSubtopic(topicKey, subtopic));
            subtopicList.appendChild(item);
        });

        section.appendChild(subtopicList);
        return section;
    }

    toggleTopic(topicKey) {
        const section = document.querySelector(`[data-topic="${topicKey}"]`);
        const list = section.querySelector('.subtopic-list');
        list.style.display = list.style.display === 'none' ? 'block' : 'none';
    }

    selectSubtopic(topic, subtopic) {
        // Remove active class from all items
        document.querySelectorAll('.subtopic-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to selected item
        const item = document.querySelector(`[data-topic="${topic}"][data-subtopic="${subtopic}"]`);
        if (item) {
            item.classList.add('active');
        }

        if (this.onSubtopicChange) {
            this.onSubtopicChange(topic, subtopic);
        }
    }

    formatSubtopicName(subtopic) {
        return subtopic.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TopicNavigation;
}
