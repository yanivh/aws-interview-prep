/**
 * Step Indicator Component (used by answer visualizer)
 */

class StepIndicator {
    constructor(stepNumber, title, description, commands, awsServices) {
        this.stepNumber = stepNumber;
        this.title = title;
        this.description = description;
        this.commands = commands || [];
        this.awsServices = awsServices || [];
    }

    render() {
        const stepElement = document.createElement('div');
        stepElement.className = 'step-indicator';
        stepElement.innerHTML = `
            <div class="step-header">
                <span class="step-number">${this.stepNumber}</span>
                <h4>${this.title}</h4>
            </div>
            <p>${this.description}</p>
            ${this.commands.length > 0 ? this.renderCommands() : ''}
            ${this.awsServices.length > 0 ? this.renderServices() : ''}
        `;
        return stepElement;
    }

    renderCommands() {
        return `
            <div class="step-commands">
                <strong>Commands:</strong>
                <pre><code>${this.commands.join('\n')}</code></pre>
            </div>
        `;
    }

    renderServices() {
        return `
            <div class="step-services">
                <strong>AWS Services:</strong> ${this.awsServices.join(', ')}
            </div>
        `;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StepIndicator;
}
