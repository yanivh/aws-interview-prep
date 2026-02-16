/**
 * AWS Service Badge Component
 */

class AWSServiceBadge {
    constructor(serviceName, usage = '') {
        this.serviceName = serviceName;
        this.usage = usage;
    }

    render() {
        const badge = document.createElement('span');
        badge.className = 'aws-service-badge';
        badge.textContent = this.serviceName;
        badge.title = this.usage;
        return badge;
    }

    static renderList(services) {
        const container = document.createElement('div');
        container.className = 'aws-services-container';
        
        services.forEach(service => {
            const badge = new AWSServiceBadge(
                service.name || service,
                service.usage || ''
            );
            container.appendChild(badge.render());
        });
        
        return container;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AWSServiceBadge;
}
