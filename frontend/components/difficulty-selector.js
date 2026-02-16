/**
 * Difficulty Selector Component
 */

class DifficultySelector {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.selectedDifficulty = 'intermediate';
        this.onChange = null;
    }

    init() {
        if (!this.container) return;

        const difficulties = ['newbie', 'intermediate', 'pro'];
        
        difficulties.forEach(difficulty => {
            const button = document.createElement('button');
            button.className = 'difficulty-btn';
            button.dataset.difficulty = difficulty;
            button.textContent = difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
            button.addEventListener('click', () => this.select(difficulty));
            
            if (difficulty === this.selectedDifficulty) {
                button.classList.add('active');
            }
            
            this.container.appendChild(button);
        });
    }

    select(difficulty) {
        this.selectedDifficulty = difficulty;

        // Update button states
        this.container.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.difficulty === difficulty) {
                btn.classList.add('active');
            }
        });

        if (this.onChange) {
            this.onChange(difficulty);
        }
    }

    getSelected() {
        return this.selectedDifficulty;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DifficultySelector;
}
