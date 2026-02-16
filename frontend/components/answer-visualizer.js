/**
 * Answer Visualizer Component
 * Renders structured answers with visual formatting
 */

class AnswerVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }

    render(answerData) {
        if (!this.container || !answerData) return;

        this.container.innerHTML = '';

        // Summary Card
        if (answerData.summary) {
            this.renderSummary(answerData.summary);
        }

        // Step-by-Step Guide
        if (answerData.steps && answerData.steps.length > 0) {
            this.renderSteps(answerData.steps);
        }

        // AWS Services
        if (answerData.aws_services && answerData.aws_services.length > 0) {
            this.renderAWSServices(answerData.aws_services);
        }

        // Key Points
        if (answerData.key_points && answerData.key_points.length > 0) {
            this.renderKeyPoints(answerData.key_points);
        }

        // Best Practices
        if (answerData.best_practices && answerData.best_practices.length > 0) {
            this.renderBestPractices(answerData.best_practices);
        }

        // Common Pitfalls
        if (answerData.common_pitfalls && answerData.common_pitfalls.length > 0) {
            this.renderCommonPitfalls(answerData.common_pitfalls);
        }

        // Code Examples
        if (answerData.code_examples && answerData.code_examples.length > 0) {
            this.renderCodeExamples(answerData.code_examples);
        }

        // Comparison Table
        if (answerData.comparison_table && answerData.comparison_table.length > 0) {
            this.renderComparisonTable(answerData.comparison_table);
        }
    }

    renderSummary(summary) {
        const card = document.createElement('div');
        card.className = 'answer-section summary-card';
        card.innerHTML = `
            <div class="section-header">
                <span class="icon">📋</span>
                <h3>Summary</h3>
            </div>
            <p>${summary}</p>
        `;
        this.container.appendChild(card);
    }

    renderSteps(steps) {
        const card = document.createElement('div');
        card.className = 'answer-section steps-section';
        card.innerHTML = `
            <div class="section-header">
                <span class="icon">🔢</span>
                <h3>Step-by-Step Solution</h3>
            </div>
        `;

        const stepsList = document.createElement('div');
        stepsList.className = 'steps-list';

        steps.forEach(step => {
            const stepElement = document.createElement('div');
            stepElement.className = 'step-item';
            stepElement.innerHTML = `
                <div class="step-header">
                    <span class="step-number">[${step.step}]</span>
                    <span class="step-icon">🔍</span>
                    <strong>${step.title}</strong>
                </div>
                <p class="step-description">${step.description}</p>
                ${step.commands && step.commands.length > 0 ? `
                    <div class="step-commands">
                        <span class="icon">💻</span> Commands:
                        <pre><code>${step.commands.join('\n')}</code></pre>
                    </div>
                ` : ''}
                ${step.aws_services && step.aws_services.length > 0 ? `
                    <div class="step-services">
                        <span class="icon">☁️</span> AWS Services: ${step.aws_services.join(', ')}
                    </div>
                ` : ''}
            `;
            stepsList.appendChild(stepElement);
        });

        card.appendChild(stepsList);
        this.container.appendChild(card);
    }

    renderAWSServices(services) {
        const card = document.createElement('div');
        card.className = 'answer-section aws-services-section';
        card.innerHTML = `
            <div class="section-header">
                <span class="icon">☁️</span>
                <h3>AWS Services Used</h3>
            </div>
            <div class="aws-services-list">
                ${services.map(service => `
                    <div class="aws-service-item">
                        <span class="aws-service-badge">${service.name}</span>
                        <span class="aws-service-usage">${service.usage || ''}</span>
                    </div>
                `).join('')}
            </div>
        `;
        this.container.appendChild(card);
    }

    renderKeyPoints(keyPoints) {
        const card = document.createElement('div');
        card.className = 'answer-section key-points-section callout-box';
        card.innerHTML = `
            <div class="section-header">
                <span class="icon">⭐</span>
                <h3>Key Points</h3>
            </div>
            <ul>
                ${keyPoints.map(point => `<li>${point}</li>`).join('')}
            </ul>
        `;
        this.container.appendChild(card);
    }

    renderBestPractices(practices) {
        const card = document.createElement('div');
        card.className = 'answer-section best-practices-section callout-box success';
        card.innerHTML = `
            <div class="section-header">
                <span class="icon">✅</span>
                <h3>Best Practices</h3>
            </div>
            <ul>
                ${practices.map(practice => `<li>${practice}</li>`).join('')}
            </ul>
        `;
        this.container.appendChild(card);
    }

    renderCommonPitfalls(pitfalls) {
        const card = document.createElement('div');
        card.className = 'answer-section pitfalls-section callout-box warning';
        card.innerHTML = `
            <div class="section-header">
                <span class="icon">⚠️</span>
                <h3>Common Pitfalls</h3>
            </div>
            <ul>
                ${pitfalls.map(pitfall => `<li>${pitfall}</li>`).join('')}
            </ul>
        `;
        this.container.appendChild(card);
    }

    renderCodeExamples(examples) {
        examples.forEach(example => {
            const card = document.createElement('div');
            card.className = 'answer-section code-example-section';
            card.innerHTML = `
                <div class="section-header">
                    <span class="icon">💻</span>
                    <h3>Code Example (${example.language})</h3>
                </div>
                ${example.description ? `<p>${example.description}</p>` : ''}
                <pre><code class="language-${example.language}">${example.code}</code></pre>
            `;
            this.container.appendChild(card);
        });
    }

    renderComparisonTable(comparison) {
        const card = document.createElement('div');
        card.className = 'answer-section comparison-table-section';
        card.innerHTML = `
            <div class="section-header">
                <span class="icon">📊</span>
                <h3>Comparison</h3>
            </div>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>Option</th>
                        <th>Pros</th>
                        <th>Cons</th>
                        <th>Use When</th>
                    </tr>
                </thead>
                <tbody>
                    ${comparison.map(option => `
                        <tr>
                            <td><strong>${option.option}</strong></td>
                            <td><ul>${option.pros.map(p => `<li>${p}</li>`).join('')}</ul></td>
                            <td><ul>${option.cons.map(c => `<li>${c}</li>`).join('')}</ul></td>
                            <td>${option.when_to_use}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        this.container.appendChild(card);
    }
}

// Make globally available
window.answerVisualizer = new AnswerVisualizer('answer-visualizer');

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnswerVisualizer;
}
