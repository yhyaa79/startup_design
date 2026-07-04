let uploadedFiles = [];

function initUpload() {
    const fileInput = document.getElementById('upload-maghaleh');
    const fileListEl = document.getElementById('file-list-names');

    if (!fileInput || !fileListEl) return;

    fileInput.addEventListener('change', (e) => {
        Array.from(e.target.files).forEach(file => {
            if (!uploadedFiles.find(f => f.name === file.name && f.size === file.size)) {
                uploadedFiles.push(file);
            }
        });
        renderFileList(fileListEl);
        fileInput.value = '';
    });
}

function renderFileList(fileListEl) {
    fileListEl.innerHTML = '';
    uploadedFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.innerHTML = `
            <span>${file.name}</span>
            <span style="cursor:pointer;margin-right:8px;color:#ef4444" data-index="${index}">✕</span>`;
        fileListEl.appendChild(item);
    });

    fileListEl.querySelectorAll('[data-index]').forEach(btn => {
        btn.addEventListener('click', () => {
            uploadedFiles.splice(Number(btn.dataset.index), 1);
            renderFileList(fileListEl);
        });
    });
}
