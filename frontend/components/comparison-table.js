/**
 * Comparison Table Component
 */

class ComparisonTable {
    constructor(options) {
        this.options = options; // Array of {option, pros, cons, when_to_use}
    }

    render() {
        const table = document.createElement('table');
        table.className = 'comparison-table';

        // Header
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th>Option</th>
                <th>Pros</th>
                <th>Cons</th>
                <th>Use When</th>
            </tr>
        `;
        table.appendChild(thead);

        // Body
        const tbody = document.createElement('tbody');
        this.options.forEach(option => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${option.option}</strong></td>
                <td><ul>${option.pros.map(p => `<li>${p}</li>`).join('')}</ul></td>
                <td><ul>${option.cons.map(c => `<li>${c}</li>`).join('')}</ul></td>
                <td>${option.when_to_use}</td>
            `;
            tbody.appendChild(row);
        });
        table.appendChild(tbody);

        return table;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ComparisonTable;
}
