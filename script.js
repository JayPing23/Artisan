document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    const generateForm = document.getElementById('generate-form');
    const promptInput = document.getElementById('prompt');
    const generateButton = document.getElementById('generate-button');
    const statusContainer = document.getElementById('status-container');
    const resultContainer = document.getElementById('result-container');
    const statusText = document.getElementById('status-text');
    // Remove qualitySelect and related logic
    // const qualitySelect = document.getElementById('quality-select');
    const downloadContainer = document.getElementById('download-container');
    const downloadBtn = document.getElementById('download-btn');
    const toastContainer = document.getElementById('toast-container');
    const generateBtnText = document.getElementById('generate-btn-text');
    const generateBtnSpinner = document.getElementById('generate-btn-spinner');
    // const artisanBody = document.getElementById('artisan-body');

    // Advanced options toggle (now hidden)
    const toggleAdvanced = document.getElementById('toggle-advanced');
    const advancedSection = document.getElementById('advanced-options');
    let advancedVisible = false;
    if (toggleAdvanced && advancedSection) {
        toggleAdvanced.addEventListener('click', function (e) {
            e.preventDefault();
            advancedVisible = !advancedVisible;
            advancedSection.style.display = advancedVisible ? 'block' : 'none';
            toggleAdvanced.textContent = advancedVisible ? 'Advanced Options ▲' : 'Advanced Options ▼';
        });
    }

    // Progress Bar Logic
    const progressBar = document.getElementById('progress-bar');
    function showProgressBar() {
        progressBar.style.width = '0%';
        progressBar.classList.remove('hidden');
        setTimeout(() => {
            progressBar.style.width = '80%';
        }, 100);
    }
    function completeProgressBar() {
        progressBar.style.width = '100%';
        setTimeout(() => {
            progressBar.style.width = '0%';
            progressBar.classList.add('hidden');
        }, 600);
    }

    // (Theme toggle code removed)

    const API_BASE = window.location.origin;

    let pollingInterval;

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type === 'error' ? 'bg-red-600' : 'bg-indigo-600'}`;
        toast.innerHTML = `<span>${message}</span>`;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('opacity-0');
            setTimeout(() => toast.remove(), 400);
        }, 3500);
    }

    const setUIState = (state, data = {}) => {
        resultContainer.innerHTML = '';
        statusContainer.classList.remove('hidden');
        generateButton.disabled = false;
        downloadContainer.classList.add('hidden');
        generateBtnText.classList.remove('opacity-0');
        generateBtnSpinner.classList.add('hidden');
        statusText.innerHTML = 'Your generated model will appear here.';

        switch (state) {
            case 'IDLE':
                break;
            case 'SUBMITTING':
                generateButton.disabled = true;
                generateBtnText.classList.add('opacity-0');
                generateBtnSpinner.classList.remove('hidden');
                statusContainer.innerHTML = `
                    <i data-lucide="loader-2" class="w-8 h-8 text-gray-400 spinner"></i>
                    <p class="mt-2 text-gray-300">Submitting task...</p>
                `;
                lucide.createIcons();
                break;
            case 'POLLING':
                generateButton.disabled = true;
                generateBtnText.classList.add('opacity-0');
                generateBtnSpinner.classList.remove('hidden');
                const statusMessage = data.status ? `Status: ${data.status}` : 'Waiting for status...';
                statusContainer.innerHTML = `
                    <i data-lucide="loader-2" class="w-8 h-8 text-gray-400 spinner"></i>
                    <p class="mt-2 text-gray-300">Generating model...</p>
                    <p class="mt-1 text-sm text-gray-500">${statusMessage}</p>
                `;
                lucide.createIcons();
                break;
            case 'SUCCESS':
                statusContainer.classList.add('hidden');
                displayModel(data.taskId);
                showToast('Model is ready! Click Download to save.', 'info');
                break;
            case 'ERROR':
                statusContainer.innerHTML = `
                    <i data-lucide="alert-triangle" class="w-8 h-8 text-red-400"></i>
                    <p class="mt-2 font-medium text-red-400">Generation Failed</p>
                    <p class="mt-1 text-sm text-gray-400 max-w-md">${data.error || 'An unknown error occurred.'}</p>
                `;
                lucide.createIcons();
                showToast(data.error || 'An unknown error occurred.', 'error');
                break;
            default:
                break;
        }
    };
    
    const displayModel = (taskId) => {
        resultContainer.innerHTML = '';
        const modelViewer = document.createElement('model-viewer');
        modelViewer.setAttribute('src', `${API_BASE}/model/${taskId}`);
        modelViewer.setAttribute('alt', 'Generated 3D model');
        modelViewer.setAttribute('auto-rotate', '');
        modelViewer.setAttribute('camera-controls', '');
        modelViewer.setAttribute('shadow-intensity', '1');
        modelViewer.setAttribute('ar', '');
        modelViewer.setAttribute('touch-action', 'pan-y');
        resultContainer.appendChild(modelViewer);
        downloadContainer.classList.remove('hidden');
        downloadBtn.onclick = () => {
            window.open(`${API_BASE}/model/${taskId}`, '_blank');
        };
    };

    const checkStatus = async (taskId) => {
        try {
            const response = await fetch(`${API_BASE}/status/${taskId}`);
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            const data = await response.json();

            setUIState('POLLING', { status: data.status });

            if (data.status === 'SUCCESS') {
                clearInterval(pollingInterval);
                setUIState('SUCCESS', { taskId });
            } else if (data.status === 'FAILURE') {
                clearInterval(pollingInterval);
                setUIState('ERROR', { error: data.result });
            }
        } catch (error) {
            clearInterval(pollingInterval);
            console.error('Polling failed:', error);
            setUIState('ERROR', { error: 'Could not fetch generation status.' });
        }
    };

    // Advanced Options Modal Logic
    // const openAdvancedBtn = document.getElementById('open-advanced');
    // const advancedModal = document.getElementById('advanced-modal');
    // const closeAdvancedBtn = document.getElementById('close-advanced');
    // if (openAdvancedBtn && advancedModal) {
    //     openAdvancedBtn.addEventListener('click', () => {
    //         advancedModal.style.display = 'flex';
    //     });
    // }
    // if (closeAdvancedBtn && advancedModal) {
    //     closeAdvancedBtn.addEventListener('click', () => {
    //         advancedModal.style.display = 'none';
    //     });
    // }
    // Optional: close modal on outside click
    // if (advancedModal) {
    //     advancedModal.addEventListener('click', (e) => {
    //         if (e.target === advancedModal) {
    //             advancedModal.style.display = 'none';
    //         }
    //     });
    // }

    const handleGenerateSubmit = async (event) => {
        event.preventDefault();
        const prompt = promptInput.value.trim();
        // Collect all advanced fields
        const style = document.getElementById('style').value.trim();
        const environment = document.getElementById('environment').value.trim();
        const lighting = document.getElementById('lighting').value.trim();
        const color_scheme = document.getElementById('color_scheme').value.trim();
        const special_features = document.getElementById('special_features').value.trim();
        const scale = document.getElementById('scale').value.trim();
        const level_of_detail = document.getElementById('level_of_detail').value.trim();
        const material_appearance = document.getElementById('material_appearance').value.trim();
        const symmetry = document.getElementById('symmetry').value.trim();
        const animation = document.getElementById('animation').value.trim();
        const output_format = document.getElementById('output_format').value.trim();
        const other_requirements = document.getElementById('other_requirements').value.trim();
        if (!prompt) {
            setUIState('ERROR', { error: 'Prompt cannot be empty.' });
            return;
        }
        if (pollingInterval) clearInterval(pollingInterval);
        setUIState('SUBMITTING');
        try {
            const response = await fetch(`${API_BASE}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    style,
                    environment,
                    lighting,
                    color_scheme,
                    special_features,
                    scale,
                    level_of_detail,
                    material_appearance,
                    symmetry,
                    animation,
                    output_format,
                    other_requirements
                }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }
            const { task_id } = await response.json();
            setUIState('POLLING', {});
            pollingInterval = setInterval(() => checkStatus(task_id), 3000);
            checkStatus(task_id);
        } catch (error) {
            console.error('Generation request failed:', error);
            setUIState('ERROR', { error: error.message });
        }
    };

    if (generateForm) {
        generateForm.addEventListener('submit', handleGenerateSubmit);
        setUIState('IDLE');
    } else {
        console.error('generate-form not found in DOM. Please check your index.html.');
    }
});
