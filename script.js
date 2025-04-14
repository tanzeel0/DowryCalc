const form = document.getElementById('prediction-form');
        const incomeInput = document.getElementById('income');
        const incomeRange = document.getElementById('income-range');
        const submitBtn = document.getElementById('submit-btn');
        const loadingMessage = document.getElementById('loading-message');
        const noResultsMessage = document.getElementById('no-results-message');
        const predictionResults = document.getElementById('prediction-results');
        const predictionValue = document.getElementById('prediction-value');
        const incomeFactor = document.getElementById('income-factor');
        const professionImpact = document.getElementById('profession-impact');
        const employmentImpact = document.getElementById('employment-impact');
        const landImpact = document.getElementById('land-impact');
        const errorContainer = document.getElementById('error-container');
        const chartsLoading = document.getElementById('charts-loading');
        const chartsGrid = document.getElementById('charts-grid');

        // Charts
        let scatterChart;
        let professionChart;

        // Sync income input and range
        incomeInput.addEventListener('input', () => {
            incomeRange.value = incomeInput.value;
        });

        incomeRange.addEventListener('input', () => {
            incomeInput.value = incomeRange.value;
        });

        // Form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Show loading state
            submitBtn.disabled = true;
            loadingMessage.style.display = 'flex';
            noResultsMessage.style.display = 'none';
            predictionResults.style.display = 'none';
            errorContainer.innerHTML = '';
            
            const formData = {
                income: Number(incomeInput.value),
                profession: document.getElementById('profession').value,
                employmentType: document.getElementById('employmentType').value,
                land: Number(document.getElementById('land').value)
            };
            
            try {
                const response = await fetch('http://localhost:5000/api/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) {
                    throw new Error('Server error');
                }
                
                const result = await response.json();
                
                // Display results
                predictionValue.textContent = `₹${result.prediction.toLocaleString()}`;
                incomeFactor.textContent = `₹${result.analysis.income_factor.toLocaleString()}`;
                professionImpact.textContent = result.analysis.profession_impact;
                employmentImpact.textContent = result.analysis.employment_impact;
                landImpact.textContent = result.analysis.land_impact;
                
                loadingMessage.style.display = 'none';
                noResultsMessage.style.display = 'none';
                predictionResults.style.display = 'block';
            } catch (error) {
                errorContainer.innerHTML = `
                    <div style="background-color: #fee2e2; border: 1px solid #f87171; color: #b91c1c; padding: 0.75rem; border-radius: 0.25rem; margin-bottom: 1rem;">
                        Error: Could not get prediction. Please make sure the backend server is running.
                    </div>
                `;
                loadingMessage.style.display = 'none';
                noResultsMessage.style.display = 'block';
            } finally {
                submitBtn.disabled = false;
            }
        });

        // Fetch graph data and initialize charts
        async function fetchGraphData() {
            try {
                chartsLoading.style.display = 'flex';
                chartsGrid.style.display = 'none';
                
                const response = await fetch('http://localhost:5000/api/data');
                
                if (!response.ok) {
                    throw new Error('Server error');
                }
                
                const data = await response.json();
                
                // Initialize charts
                initializeCharts(data);
                
                chartsLoading.style.display = 'none';
                chartsGrid.style.display = 'grid';
            } catch (error) {
                chartsLoading.textContent = 'Failed to load data. Please ensure the backend server is running.';
            }
        }

        // Load data when page loads
        window.addEventListener('DOMContentLoaded', fetchGraphData);