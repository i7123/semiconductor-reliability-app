/**
 * @typedef {Object} Calculator
 * @property {string} id - The unique identifier for the calculator
 * @property {string} name - The display name of the calculator
 * @property {string} description - A short description of the calculator
 * @property {Array<Object>} inputs - The input fields for the calculator
 */

/**
 * Main application class for the Semiconductor Reliability Calculator
 */
class SemiconductorCalculatorApp {
    /**
     * Initialize the application
     * @constructor
     */
    constructor() {
        // Use relative URL for production, localhost for development
        this.apiBase = window.location.hostname === 'localhost' ?
            'http://localhost:8000' : '';
        this.authToken = localStorage.getItem('authToken');
        this.currentCalculator = null;

        this.init();
    }

    /**
     * Initialize the application
     * @async
     * @returns {Promise<void>}
     */
    async init() {
        // Load calculators first (this will show the UI immediately)
        await this.loadCalculators();
        this.setupEventListeners();

        // Try to update usage status, but don't let it block the UI
        this.updateUsageStatus().catch(error => {
            console.warn('Failed to update usage status:', error);
        });

        // Don't set up the interval for now since the endpoint is failing
        // setInterval(() => this.updateUsageStatus(), 30000);
    }

    setupEventListeners() {
        document.getElementById('back-btn').addEventListener('click', () => {
            this.showCalculatorSelection();
        });

        document.getElementById('calculation-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.performCalculation();
        });

        document.getElementById('load-example').addEventListener('click', () => {
            this.loadExample();
        });
    }

    setupCalculatorEventListeners() {
        // Setup event listeners for the new button layout
        const calculateBtn = document.getElementById('calculate-btn');
        const clearBtn = document.getElementById('clear-btn');
        const saveBtn = document.getElementById('save-btn');
        const exportBtn = document.getElementById('export-btn');

        console.log('Setting up calculator event listeners...');
        console.log('Export button found:', !!exportBtn);

        if (calculateBtn) {
            calculateBtn.addEventListener('click', () => {
                this.performCalculation();
            });
        }

        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clearForm();
            });
        }

        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.saveResults();
            });
        }

        if (exportBtn) {
            exportBtn.addEventListener('click', (e) => {
                console.log('Export button clicked');
                e.preventDefault();
                this.exportResults();
            });
        } else {
            console.error('Export button not found!');
        }
    }

    async loadCalculators() {
        // Default calculators that will be shown immediately
        const defaultCalculators = [
            {
                id: 'mtbf',
                name: 'MTBF Calculator',
                description: 'Calculate Mean Time Between Failures',
                category: 'Reliability'
            },
            {
                id: 'duane_model',
                name: 'Duane Model',
                description: 'Reliability growth model',
                category: 'Reliability Growth'
            },
            {
                id: 'test_sample_size',
                name: 'Test Sample Size',
                description: 'Calculate required sample size for reliability testing',
                category: 'Testing'
            },
            {
                id: 'dummy1',
                name: 'Advanced Stress Testing',
                description: 'Stress test parameters calculator',
                category: 'Future Development'
            },
            {
                id: 'dummy2',
                name: 'Burn-in Optimization',
                description: 'Optimize burn-in testing parameters',
                category: 'Future Development'
            },
            {
                id: 'dummy3',
                name: 'Lifetime Data Analysis',
                description: 'Analyze lifetime data with statistical models',
                category: 'Future Development'
            }
        ];

        // Try to fetch calculators from API, but don't wait for it
        this.fetchCalculatorsFromAPI().catch(error => {
            console.warn('Using default calculators due to API error:', error);
        });

        // Show default calculators immediately
        this.displayCalculators(defaultCalculators);
    }

    async fetchCalculatorsFromAPI() {
        try {
            const response = await fetch(`${this.apiBase}/calculators/`);
            if (response.ok) {
                const data = await response.json();
                if (Array.isArray(data) && data.length > 0) {
                    this.displayCalculators(data);
                }
            }
        } catch (error) {
            console.error('Error fetching calculators:', error);
            throw error; // Re-throw to be caught by the caller
        }
    }

    displayCalculators(calculators) {
        const grid = document.getElementById('calculators-grid');
        if (!grid) {
            console.error('Calculators grid element not found');
            return;
        }

        // Clear existing content
        grid.innerHTML = '';

        // Add each calculator card to the grid
        try {
            calculators.forEach(calc => {
                const card = this.createCalculatorCard(calc);
                if (card) {
                    grid.appendChild(card);
                }
            });
        } catch (error) {
            console.error('Error displaying calculators:', error);
            grid.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">
                        <h4>Error Loading Calculators</h4>
                        <p>${error.message || 'An unknown error occurred'}</p>
                        <p>Showing default calculators with limited functionality.</p>
                    </div>
                </div>
            `;
        }
    }

    createCalculatorCard(calculator) {
        const div = document.createElement('div');
        div.className = 'col-md-4 mb-3';

        const isInDevelopment = calculator.category === "Future Development";
        const cardClass = isInDevelopment ? 'card calculator-card h-100 in-development' : 'card calculator-card h-100';
        const onclick = isInDevelopment ? `app.showDevelopmentMessage('${calculator.name}')` : `app.selectCalculator('${calculator.id}')`;

        const developmentBadge = isInDevelopment ? '<div class="in-development-badge">Calculator in Plan</div>' : '';

        div.innerHTML = `
            <div class="${cardClass}" onclick="${onclick}">
                <div class="card-body">
                    ${developmentBadge}
                    <h5 class="card-title">${calculator.name}</h5>
                    <p class="card-text">${calculator.description}</p>
                    <small class="text-muted">Category: ${calculator.category}</small>
                </div>
            </div>
        `;

        return div;
    }

    async selectCalculator(calculatorId) {
        try {
            const response = await fetch(`${this.apiBase}/calculators/${calculatorId}/info`);
            this.currentCalculator = await response.json();

            this.showCalculatorInterface();
            this.generateInputForm();
        } catch (error) {
            console.error('Failed to load calculator info:', error);
        }
    }

    showCalculatorSelection() {
        document.getElementById('calculator-selection').style.display = 'block';
        document.getElementById('calculator-interface').style.display = 'none';
    }

    showCalculatorInterface() {
        document.getElementById('calculator-selection').style.display = 'none';
        document.getElementById('calculator-interface').style.display = 'block';

        document.getElementById('calculator-title').textContent = this.currentCalculator.name;
        document.getElementById('calculator-description').textContent = this.currentCalculator.description;

        // Setup event listeners for the new button layout
        this.setupCalculatorEventListeners();
    }

    generateInputForm() {
        const container = document.getElementById('input-fields');
        container.innerHTML = '';

        this.currentCalculator.input_fields.forEach(field => {
            const div = document.createElement('div');
            div.className = 'mb-3';

            let inputHtml = '';

            if (field.type === 'select') {
                inputHtml = `
                    <select class="form-select" id="${field.name}" ${field.required ? 'required' : ''}>
                        ${field.options.map(option =>
                    `<option value="${option}" ${field.default_value === option ? 'selected' : ''}>${option}</option>`
                ).join('')}
                    </select>
                `;
            } else if (field.type === 'bool') {
                inputHtml = `
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="${field.name}" ${field.default_value ? 'checked' : ''}>
                        <label class="form-check-label" for="${field.name}">
                            ${field.label}
                        </label>
                    </div>
                `;
            } else {
                const inputType = field.type === 'int' || field.type === 'float' ? 'number' : 'text';
                const step = field.type === 'float' ? 'any' : field.type === 'int' ? '1' : '';

                inputHtml = `
                    <label for="${field.name}" class="form-label">
                        ${field.label} ${field.unit ? `(${field.unit})` : ''}
                        ${field.required ? '<span class="text-danger">*</span>' : ''}
                    </label>
                    <input type="${inputType}" class="form-control" id="${field.name}" 
                           ${field.required ? 'required' : ''}
                           ${step ? `step="${step}"` : ''}
                           ${field.min_value != null ? `min="${field.min_value}"` : ''}
                           ${field.max_value != null ? `max="${field.max_value}"` : ''}
                           ${field.default_value != null ? `value="${field.default_value}"` : ''}>
                `;
            }

            if (field.type !== 'bool') {
                div.innerHTML = `
                    ${inputHtml}
                    ${field.description ? `<div class="form-text">${field.description}</div>` : ''}
                `;
            } else {
                div.innerHTML = `
                    ${inputHtml}
                    ${field.description ? `<div class="form-text">${field.description}</div>` : ''}
                `;
            }

            container.appendChild(div);
        });
    }

    async loadExample() {
        try {
            const response = await fetch(`${this.apiBase}/calculators/calculate/${this.currentCalculator.id}/example`);
            const example = await response.json();

            // Fill form with example inputs
            Object.entries(example.example_inputs).forEach(([key, value]) => {
                const element = document.getElementById(key);
                if (element) {
                    if (element.type === 'checkbox') {
                        element.checked = value;
                    } else {
                        element.value = value;
                    }
                }
            });

            // Show example results
            this.displayResults(example.example_results);
        } catch (error) {
            console.error('Failed to load example:', error);
        }
    }

    async performCalculation() {
        const form = document.getElementById('calculation-form');
        const loading = document.querySelector('.loading');

        // Show loading
        loading.style.display = 'block';

        try {
            // Collect input values
            const inputs = {};
            this.currentCalculator.input_fields.forEach(field => {
                const element = document.getElementById(field.name);
                if (element) {
                    if (element.type === 'checkbox') {
                        inputs[field.name] = element.checked;
                    } else if (field.type === 'float') {
                        inputs[field.name] = parseFloat(element.value) || 0;
                    } else if (field.type === 'int') {
                        inputs[field.name] = parseInt(element.value) || 0;
                    } else {
                        inputs[field.name] = element.value;
                    }
                }
            });

            // Make API call
            const headers = {
                'Content-Type': 'application/json'
            };

            if (this.authToken) {
                headers['Authorization'] = `Bearer ${this.authToken}`;
            }

            const response = await fetch(`${this.apiBase}/calculators/calculate/${this.currentCalculator.id}`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ inputs })
            });

            if (response.status === 429) {
                // Usage limit exceeded
                const errorData = await response.json();
                this.showAuthModal(errorData.detail);
                return;
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail?.message || 'Calculation failed');
            }

            const result = await response.json();
            this.displayResults(result.results);

            // Update usage status
            await this.updateUsageStatus();

        } catch (error) {
            console.error('Calculation error:', error);
            this.displayError(error.message);
        } finally {
            loading.style.display = 'none';
        }
    }

    displayResults(results) {
        const container = document.getElementById('results-container');
        container.innerHTML = '';

        // Create a formatted display of results
        const resultsHtml = this.formatResults(results);
        container.innerHTML = resultsHtml;
    }

    formatResults(results) {
        return this.formatObject(results, 0);
    }

    formatObject(obj, level) {
        let html = '';
        const indent = level > 0 ? 'ms-3' : '';

        Object.entries(obj).forEach(([key, value]) => {
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                // Handle nested objects
                const headerTag = level === 0 ? 'h5' : level === 1 ? 'h6' : 'strong';
                const headerClass = level === 0 ? 'text-primary' : level === 1 ? 'text-secondary' : '';

                if (headerTag === 'strong') {
                    html += `<div class="${indent}"><strong>${this.formatKey(key)}:</strong></div>`;
                    html += `<div class="ms-4">${this.formatObject(value, level + 1)}</div>`;
                } else {
                    html += `<${headerTag} class="${headerClass} mt-3">${this.formatKey(key)}</${headerTag}>`;
                    html += `<div class="${indent}">${this.formatObject(value, level + 1)}</div>`;
                }
            } else if (Array.isArray(value)) {
                // Handle arrays
                html += `<div class="${indent}"><strong>${this.formatKey(key)}:</strong></div>`;
                html += `<ul class="ms-4">`;
                value.forEach((item, index) => {
                    if (typeof item === 'object') {
                        html += `<li>Item ${index + 1}:<div class="ms-2">${this.formatObject(item, level + 2)}</div></li>`;
                    } else {
                        html += `<li>${this.formatValue(item)}</li>`;
                    }
                });
                html += `</ul>`;
            } else {
                // Handle primitive values
                const valueClass = level === 0 ? 'mb-2' : 'mb-1';
                html += `<div class="${indent} ${valueClass}"><strong>${this.formatKey(key)}:</strong> ${this.formatValue(value)}</div>`;
            }
        });

        return html;
    }

    formatKey(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatValue(value) {
        if (typeof value === 'number') {
            if (value === Infinity || value === -Infinity) {
                return '∞';
            }
            if (value > 1000000) {
                return value.toExponential(3);
            }
            if (value < 0.001 && value > 0) {
                return value.toExponential(3);
            }
            return value.toLocaleString();
        }
        if (value === null || value === undefined) {
            return 'N/A';
        }
        return String(value);
    }

    displayError(message) {
        const container = document.getElementById('results-container');
        container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
    }

    async updateUsageStatus() {
        try {
            const headers = {};
            if (this.authToken) {
                headers['Authorization'] = `Bearer ${this.authToken}`;
            }

            const response = await fetch(`${this.apiBase}/auth/usage`, { headers });

            if (!response.ok) {
                // Hide usage indicator if API is not available or returns error
                this.hideUsageIndicator();
                return;
            }

            const status = await response.json();

            const statusElement = document.getElementById('usage-status');
            const remaining = status.usage_remaining;
            const total = status.daily_limit;

            // Check if we have valid data
            if (remaining === undefined || total === undefined) {
                this.hideUsageIndicator();
                return;
            }

            let statusClass = 'text-success';
            if (remaining <= total * 0.2) statusClass = 'text-danger';
            else if (remaining <= total * 0.5) statusClass = 'text-warning';

            statusElement.innerHTML = `
                <span class="${statusClass}">
                    ${remaining}/${total} calculations remaining
                    ${status.is_premium ? '(Premium)' : '(Free)'}
                </span>
            `;

            // Show usage indicator if it was hidden
            this.showUsageIndicator();

        } catch (error) {
            console.error('Failed to update usage status:', error);
            // Hide usage indicator on error
            this.hideUsageIndicator();
        }
    }

    hideUsageIndicator() {
        const usageIndicator = document.querySelector('.usage-indicator');
        if (usageIndicator) {
            usageIndicator.style.display = 'none';
        }
    }

    showUsageIndicator() {
        const usageIndicator = document.querySelector('.usage-indicator');
        if (usageIndicator) {
            usageIndicator.style.display = 'block';
        }
    }

    /**
     * Show authentication modal with error details
     * @param {Object} errorDetail - Error details object
     * @param {string} errorDetail.error - Error title
     * @param {string} errorDetail.message - Error message
     * @param {boolean} [errorDetail.requires_auth] - Whether authentication is required
     * @param {boolean} [errorDetail.upgrade_needed] - Whether premium upgrade is needed
     */
    showAuthModal(errorDetail) {
        // @ts-ignore - Bootstrap is loaded from CDN
        const Modal = bootstrap.Modal || {};
        const modal = new Modal(document.getElementById('authModal'));
        const messageDiv = document.getElementById('auth-message');
        const optionsDiv = document.getElementById('auth-options');

        messageDiv.innerHTML = `
            <div class="alert alert-warning">
                <h6>${errorDetail.error}</h6>
                <p>${errorDetail.message}</p>
            </div>
        `;

        let optionsHtml = '';

        if (errorDetail.requires_auth) {
            optionsHtml += `
                <p>Please register or login to continue:</p>
                <button class="btn btn-primary me-2" onclick="app.showRegisterForm()">Register</button>
                <button class="btn btn-outline-primary" onclick="app.showLoginForm()">Login</button>
            `;
        } else if (errorDetail.upgrade_needed) {
            optionsHtml += `
                <p>Upgrade to Premium for unlimited calculations:</p>
                <button class="btn btn-success" onclick="app.upgradeToPremium()">Upgrade to Premium</button>
            `;
        }

        optionsDiv.innerHTML = optionsHtml;
        if (modal.show) {
            modal.show();
        }
    }

    showRegisterForm() {
        // Simple registration form
        const form = `
            <div class="mb-3">
                <input type="email" class="form-control" id="reg-email" placeholder="Email" required>
            </div>
            <div class="mb-3">
                <input type="password" class="form-control" id="reg-password" placeholder="Password" required>
            </div>
            <button class="btn btn-primary" onclick="app.register()">Register</button>
        `;
        document.getElementById('auth-options').innerHTML = form;
    }

    showLoginForm() {
        const form = `
            <div class="mb-3">
                <input type="email" class="form-control" id="login-email" placeholder="Email" required>
            </div>
            <div class="mb-3">
                <input type="password" class="form-control" id="login-password" placeholder="Password" required>
            </div>
            <button class="btn btn-primary" onclick="app.login()">Login</button>
        `;
        document.getElementById('auth-options').innerHTML = form;
    }

    async register() {
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;

        try {
            const response = await fetch(`${this.apiBase}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.authToken = data.access_token;
                localStorage.setItem('authToken', this.authToken);

                const authModal = document.getElementById('authModal');
                if (authModal) {
                    // @ts-ignore - Bootstrap is loaded from CDN
                    const modal = bootstrap.Modal.getInstance(authModal);
                    if (modal) modal.hide();
                }
                await this.updateUsageStatus();
            } else {
                alert('Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
        }
    }

    async login() {
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch(`${this.apiBase}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                const data = await response.json();
                this.authToken = data.access_token;
                localStorage.setItem('authToken', this.authToken);

                const authModal = document.getElementById('authModal');
                if (authModal) {
                    // @ts-ignore - Bootstrap is loaded from CDN
                    const modal = bootstrap.Modal.getInstance(authModal);
                    if (modal) modal.hide();
                }
                await this.updateUsageStatus();
            } else {
                alert('Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
        }
    }

    async upgradeToPremium() {
        if (!this.authToken) {
            alert('Please login first');
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/auth/upgrade`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${this.authToken}` }
            });

            if (response.ok) {
                const authModal = document.getElementById('authModal');
                if (authModal) {
                    // @ts-ignore - Bootstrap is loaded from CDN
                    const modal = bootstrap.Modal.getInstance(authModal);
                    if (modal) modal.hide();
                }
                await this.updateUsageStatus();
                alert('Successfully upgraded to Premium!');
            } else {
                alert('Upgrade failed');
            }
        } catch (error) {
            console.error('Upgrade error:', error);
        }
    }

    clearForm() {
        // Clear all input fields
        this.currentCalculator.input_fields.forEach(field => {
            const element = document.getElementById(field.name);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = false;
                } else {
                    element.value = '';
                }
            }
        });

        // Clear results
        document.getElementById('results-container').innerHTML = '<p class="text-muted">Results will appear here after calculation.</p>';
    }

    saveResults() {
        const resultsContainer = document.getElementById('results-container');
        if (resultsContainer.innerHTML.includes('text-muted')) {
            alert('No results to save. Please perform a calculation first.');
            return;
        }

        // Simple save to localStorage
        const results = {
            calculator: this.currentCalculator.name,
            timestamp: new Date().toISOString(),
            results: resultsContainer.innerHTML
        };

        let savedResults = JSON.parse(localStorage.getItem('calculatorResults') || '[]');
        savedResults.push(results);
        localStorage.setItem('calculatorResults', JSON.stringify(savedResults));

        alert('Results saved successfully!');
    }

    exportResults() {
        const resultsContainer = document.getElementById('results-container');
        if (!resultsContainer || resultsContainer.innerHTML.includes('text-muted')) {
            alert('No results to export. Please perform a calculation first.');
            return;
        }

        try {
            // Get results text
            const results = resultsContainer.innerText || resultsContainer.textContent;

            if (!results || results.trim().length === 0) {
                alert('No results to export. Please perform a calculation first.');
                return;
            }

            // Create filename with current calculator name or default
            const calculatorName = this.currentCalculator?.name || 'Calculator';
            const timestamp = new Date().toISOString().split('T')[0];
            const filename = `${calculatorName.replace(/[^a-z0-9]/gi, '_')}_results_${timestamp}.txt`;

            // Add header to exported content
            const exportContent = `Semiconductor Reliability Calculator Results
Calculator: ${calculatorName}
Generated: ${new Date().toLocaleString()}

${results}`;

            // Create and download file
            const blob = new Blob([exportContent], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);

            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';

            document.body.appendChild(a);
            a.click();

            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 100);

            // Show success message
            console.log('Results exported successfully as:', filename);

        } catch (error) {
            console.error('Export failed:', error);
            alert('Failed to export results. Please try again.');
        }
    }

    showDevelopmentMessage(calculatorName) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Calculator in Development</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center">
                            <div class="mb-3">
                                <i class="bi bi-tools" style="font-size: 3rem; color: #ffc107;"></i>
                            </div>
                            <h6>${calculatorName}</h6>
                            <p class="text-muted mb-3">This calculator is currently in development and will be available in future updates.</p>
                            <div class="alert alert-info">
                                <strong>Coming Soon!</strong><br>
                                We're working on advanced features for this calculator. 
                                Please check back for updates.
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Remove modal from DOM when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
}

// Initialize the app
const app = new SemiconductorCalculatorApp();