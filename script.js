document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    const generateForm = document.getElementById('generate-form');
    const promptInput = document.getElementById('prompt-input');
    const generateButton = document.getElementById('generate-button');
    const statusContainer = document.getElementById('status-container');
    const resultContainer = document.getElementById('result-container');
    const statusText = document.getElementById('status-text');

    const API_BASE = window.location.origin;

    let pollingInterval;

    const setUIState = (state, data = {}) => {

        resultContainer.innerHTML = '';
        statusContainer.classList.remove('hidden');
        generateButton.disabled = false;
        statusText.innerHTML = 'Your generated model will appear here.';

        switch (state) {
            case 'IDLE':
                break;
            case 'SUBMITTING':
                generateButton.disabled = true;
                statusContainer.innerHTML = `
                    <i data-lucide="loader-2" class="w-8 h-8 text-gray-400 spinner"></i>
                    <p class="mt-2 text-gray-300">Submitting task...</p>
                `;
                lucide.createIcons();
                break;
            case 'POLLING':
                generateButton.disabled = true;
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
                break;
            case 'ERROR':
                statusContainer.innerHTML = `
                    <i data-lucide="alert-triangle" class="w-8 h-8 text-red-400"></i>
                    <p class="mt-2 font-medium text-red-400">Generation Failed</p>
                    <p class="mt-1 text-sm text-gray-400 max-w-md">${data.error || 'An unknown error occurred.'}</p>
                `;
                lucide.createIcons();
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

    const handleGenerateSubmit = async (event) => {
        event.preventDefault();
        const prompt = promptInput.value.trim();
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
                body: JSON.stringify({ prompt }),
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

    generateForm.addEventListener('submit', handleGenerateSubmit);
    setUIState('IDLE');
});
