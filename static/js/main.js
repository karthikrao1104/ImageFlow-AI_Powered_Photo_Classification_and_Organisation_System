document.addEventListener('DOMContentLoaded', () => {
    // Handling drag and drop upload zone styling
    const uploadZone = document.querySelector('.upload-zone');
    const fileInput = document.getElementById('photo-upload');
    const uploadForm = document.getElementById('upload-form');

    if (uploadZone && fileInput) {
        uploadZone.addEventListener('click', () => {
            fileInput.click();
        });

        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                updateFileCount(e.dataTransfer.files.length);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateFileCount(e.target.files.length);
            }
        });

        function updateFileCount(count) {
            const countText = document.getElementById('file-count-text');
            if (countText) {
                countText.textContent = `${count} file(s) selected`;
                countText.classList.remove('d-none');
            }
        }
        
        // Handle AJAX upload with progress bar
        if (uploadForm) {
            const progressContainer = document.getElementById('upload-progress-container');
            const progressBar = document.getElementById('upload-progress');
            const uploadStatus = document.getElementById('upload-status');
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            
            uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                
                if (fileInput.files.length === 0) return;
                
                const formData = new FormData(uploadForm);
                
                // Show progress bar
                progressContainer.classList.remove('d-none');
                uploadStatus.classList.remove('d-none');
                uploadStatus.textContent = 'Uploading files...';
                uploadStatus.classList.remove('text-danger', 'text-success');
                uploadStatus.classList.add('text-primary');
                
                progressBar.style.width = '0%';
                progressBar.textContent = '0%';
                progressBar.classList.remove('bg-success', 'bg-danger');
                progressBar.classList.add('bg-primary');
                
                submitBtn.disabled = true;
                
                const xhr = new XMLHttpRequest();
                
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = Math.round((e.loaded / e.total) * 100);
                        progressBar.style.width = percentComplete + '%';
                        progressBar.textContent = percentComplete + '%';
                        progressBar.setAttribute('aria-valuenow', percentComplete);
                        
                        if (percentComplete === 100) {
                            uploadStatus.textContent = 'Upload complete! AI is now processing your photos. This may take a while...';
                            progressBar.classList.remove('bg-primary');
                            progressBar.classList.add('bg-warning');
                            progressBar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
                        }
                    }
                });
                
                xhr.addEventListener('load', () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        uploadStatus.textContent = 'Processing complete! Reloading dashboard...';
                        uploadStatus.classList.remove('text-primary');
                        uploadStatus.classList.add('text-success');
                        progressBar.classList.remove('bg-warning');
                        progressBar.classList.add('bg-success');
                        progressBar.textContent = 'Done!';
                        
                        // Reload page to show new folders after a short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 1000);
                    } else {
                        handleError('Server error during processing. Status: ' + xhr.status);
                    }
                });
                
                xhr.addEventListener('error', () => {
                    handleError('A network error occurred during upload.');
                });
                
                function handleError(msg) {
                    uploadStatus.textContent = msg;
                    uploadStatus.classList.remove('text-primary');
                    uploadStatus.classList.add('text-danger');
                    progressBar.classList.remove('bg-primary', 'bg-warning');
                    progressBar.classList.add('bg-danger');
                    progressBar.textContent = 'Error';
                    submitBtn.disabled = false;
                }
                
                xhr.open('POST', uploadForm.action, true);
                xhr.send(formData);
            });
        }
    }
});
