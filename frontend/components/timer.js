/**
 * Timer Component
 */

class Timer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.startTime = null;
        this.elapsedTime = 0;
        this.interval = null;
        this.isRunning = false;
    }

    start() {
        if (this.isRunning) return;

        this.startTime = Date.now() - this.elapsedTime;
        this.isRunning = true;
        this.interval = setInterval(() => this.update(), 1000);
        this.update();
    }

    stop() {
        if (!this.isRunning) return;

        this.isRunning = false;
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    reset() {
        this.stop();
        this.elapsedTime = 0;
        this.startTime = null;
        this.update();
    }

    update() {
        if (this.isRunning && this.startTime) {
            this.elapsedTime = Date.now() - this.startTime;
        }

        const minutes = Math.floor(this.elapsedTime / 60000);
        const seconds = Math.floor((this.elapsedTime % 60000) / 1000);

        if (this.container) {
            this.container.textContent = 
                `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
    }

    getElapsedTime() {
        return this.elapsedTime;
    }

    getFormattedTime() {
        const minutes = Math.floor(this.elapsedTime / 60000);
        const seconds = Math.floor((this.elapsedTime % 60000) / 1000);
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Timer;
}
