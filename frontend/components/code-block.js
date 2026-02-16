/**
 * Code Block Component with syntax highlighting
 */

class CodeBlock {
    constructor(code, language = 'bash', description = '') {
        this.code = code;
        this.language = language;
        this.description = description;
    }

    render() {
        const container = document.createElement('div');
        container.className = 'code-block-container';
        
        if (this.description) {
            const desc = document.createElement('p');
            desc.className = 'code-description';
            desc.textContent = this.description;
            container.appendChild(desc);
        }

        const codeBlock = document.createElement('pre');
        codeBlock.className = `code-block language-${this.language}`;
        
        const codeElement = document.createElement('code');
        codeElement.className = `language-${this.language}`;
        codeElement.textContent = this.code;
        
        codeBlock.appendChild(codeElement);
        
        // Add copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-code-btn';
        copyBtn.textContent = 'Copy';
        copyBtn.addEventListener('click', () => this.copyToClipboard(this.code));
        
        const codeWrapper = document.createElement('div');
        codeWrapper.className = 'code-wrapper';
        codeWrapper.appendChild(codeBlock);
        codeWrapper.appendChild(copyBtn);
        
        container.appendChild(codeWrapper);
        return container;
    }

    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            // Show feedback
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = 'Copied!';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 2000);
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CodeBlock;
}
