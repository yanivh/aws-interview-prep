/**
 * Callout Box Component for key points, best practices, warnings
 */

class CalloutBox {
    constructor(type, title, content) {
        this.type = type; // 'info', 'success', 'warning', 'error'
        this.title = title;
        this.content = content; // Can be string or array
    }

    render() {
        const box = document.createElement('div');
        box.className = `callout-box callout-${this.type}`;

        const header = document.createElement('div');
        header.className = 'callout-header';
        header.innerHTML = `
            <span class="callout-icon">${this.getIcon()}</span>
            <h3>${this.title}</h3>
        `;
        box.appendChild(header);

        const body = document.createElement('div');
        body.className = 'callout-body';
        
        if (Array.isArray(this.content)) {
            const list = document.createElement('ul');
            this.content.forEach(item => {
                const li = document.createElement('li');
                li.textContent = item;
                list.appendChild(li);
            });
            body.appendChild(list);
        } else {
            body.textContent = this.content;
        }
        
        box.appendChild(body);
        return box;
    }

    getIcon() {
        const icons = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        };
        return icons[this.type] || icons['info'];
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CalloutBox;
}
