// static/js/quran_analysis.js

// Variabel global
let analysisResults = {};
let preprocessDone = false;

// Inisialisasi ketika DOM siap
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeSectionToggles();
    initializeUpload();
    initializePreprocessing();
    initializeAnalysis();
    initializeModals();
    
    // Load daftar file ketika tab preprocessing dibuka
    const tabPreprocess = document.getElementById('tab-preprocess');
    if (tabPreprocess) {
        tabPreprocess.addEventListener('click', function() {
            loadPreprocessedFiles();
        });
    }
});

// Fungsi untuk inisialisasi tab utama
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    if (tabs.length === 0) return;

    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            // Reset styles
            tabs.forEach((t) =>
                t.classList.remove(
                    'text-emerald-700',
                    'border-b-2',
                    'border-emerald-600'
                )
            );
            tabs.forEach((t) => t.classList.add('text-slate-500'));
            contents.forEach((c) => c.classList.add('hidden'));
            
            // Activate selected
            tab.classList.add(
                'text-emerald-700',
                'border-b-2',
                'border-emerald-600'
            );
            tab.classList.remove('text-slate-500');
            
            const contentId = 'content-' + tab.id.split('-')[1];
            const contentElement = document.getElementById(contentId);
            if (contentElement) {
                contentElement.classList.remove('hidden');
            }
        });
    });
}

// Fungsi untuk toggle section
function initializeSectionToggles() {
    const sectionToggles = document.querySelectorAll('.section-toggle');
    if (sectionToggles.length === 0) return;

    sectionToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const icon = this.querySelector('i.fa-chevron-down');
            
            if (content && icon) {
                // Toggle visibility
                content.classList.toggle('hidden');
                
                // Rotate icon
                icon.classList.toggle('rotate-180');
            }
        });
    });
}

// Fungsi untuk menampilkan pesan
function showMessage(message, type = 'success') {
    let messageBox = document.getElementById('messageBox');
    
    // Buat messageBox jika belum ada
    if (!messageBox) {
        messageBox = document.createElement('div');
        messageBox.id = 'messageBox';
        messageBox.className = 'fixed top-5 right-5 hidden z-50 px-5 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-fade-in';
        document.body.appendChild(messageBox);
    }
    
    const icon = type === 'success' ? 'fa-circle-check' : 
                 type === 'error' ? 'fa-circle-exclamation' : 
                 'fa-circle-info';
    
    const bgColor = type === 'success' ? 'bg-emerald-100 border border-emerald-300 text-emerald-800' : 
                    type === 'error' ? 'bg-red-100 border border-red-300 text-red-800' : 
                    'bg-blue-100 border border-blue-300 text-blue-800';
    
    messageBox.innerHTML = `
        <i class="fa-solid ${icon}"></i>
        <span>${message}</span>
    `;
    messageBox.className = `fixed top-5 right-5 ${bgColor} px-5 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-fade-in z-50`;
    messageBox.classList.remove('hidden');
    
    setTimeout(() => {
        messageBox.classList.add('hidden');
    }, 4000);
}

// Fungsi untuk inisialisasi upload
function initializeUpload() {
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    const fileInfo = document.getElementById('uploadedFileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const nextStep = document.getElementById('nextStep');
    const btnNext = document.getElementById('btnNext');

    if (!fileInput || !uploadForm) return;

    // Tampilkan info file saat dipilih
    fileInput.addEventListener('change', function() {
        const file = fileInput.files[0];
        if (file && fileName && fileSize && fileInfo) {
            fileName.textContent = file.name;
            fileSize.textContent = (file.size / 1024).toFixed(2) + ' KB';
            fileInfo.classList.remove('hidden');
        }
    });

    // Upload form
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            showMessage('Silakan pilih file terlebih dahulu.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/upload', { method: 'POST', body: formData });
            const data = await res.json();

            if (res.ok) {
                showMessage('File berhasil diunggah!', 'success');

                // Tampilkan info file di UI
                if (fileName && fileSize && fileInfo) {
                    fileName.textContent = file.name;
                    fileSize.textContent = (file.size / 1024).toFixed(2) + ' KB';
                    fileInfo.classList.remove('hidden');
                }

                // Tampilkan tombol lanjut
                if (nextStep) {
                    nextStep.classList.remove('hidden');
                }
            } else {
                showMessage('Gagal mengunggah file: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showMessage('Terjadi kesalahan saat mengunggah file', 'error');
        }
    });

    // Klik lanjut ke preprocessing
    if (btnNext) {
        btnNext.addEventListener('click', function() {
            document.getElementById('tab-preprocess').click();
        });
    }
}

// Fungsi untuk inisialisasi preprocessing
function initializePreprocessing() {
    const preprocessBtn = document.getElementById('btnPreprocess');
    const displayBtn = document.getElementById('btnDisplay');
    const btnBack = document.getElementById('btnBack');

    if (!preprocessBtn) return;

    // Event listener untuk preprocessing
    preprocessBtn.addEventListener('click', async function() {
        const fileNameElement = document.getElementById('fileName');
        if (!fileNameElement) {
            showMessage('Silakan unggah file terlebih dahulu', 'error');
            return;
        }

        const fileName = fileNameElement.textContent;
        if (!fileName) {
            showMessage('Silakan unggah file terlebih dahulu', 'error');
            return;
        }

        preprocessBtn.disabled = true;
        preprocessBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Memproses...';

        const formData = new FormData();
        formData.append('filename', fileName);
        
        // Konfigurasi preprocessing
        const preprocessingOptions = [
            'case_folding', 'remove_punct', 'remove_numbers', 
            'stopword', 'tokenization', 'stemming', 'lemmatization'
        ];
        
        preprocessingOptions.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                formData.append(id, element.checked);
            }
        });
        
        // Konfigurasi stopwords
        const stopwordFile = document.getElementById('stopword_file');
        const stopwordSastrawi = document.getElementById('stopword_sastrawi');
        formData.append('stopword_file', stopwordFile ? stopwordFile.checked : false);
        formData.append('stopword_sastrawi', stopwordSastrawi ? stopwordSastrawi.checked : false);

        try {
            const res = await fetch('/preprocess', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (data.status === 'success') {
                if (displayBtn) {
                    displayBtn.classList.remove('hidden');
                }
                
                // Refresh daftar file
                await loadPreprocessedFiles();
                
                // Buka section file hasil preprocessing
                const fileSection = document.querySelector('.section-toggle:nth-child(2)');
                if (fileSection) {
                    fileSection.click();
                }
                
                preprocessDone = true;
                showMessage('Preprocessing berhasil! File telah disimpan.', 'success');
            } else {
                showMessage('Gagal melakukan preprocessing: ' + data.message, 'error');
            }
        } catch (error) {
            console.error('Error during preprocessing:', error);
            showMessage('Terjadi kesalahan saat preprocessing', 'error');
        } finally {
            preprocessBtn.disabled = false;
            preprocessBtn.innerHTML = '<i class="fa-solid fa-play"></i> Mulai Preprocessing';
        }
    });

    // Event listener untuk tombol display
    if (displayBtn) {
        displayBtn.addEventListener('click', async function() {
            const selectedFiles = Array.from(document.querySelectorAll('input[name="preprocessed_file"]:checked'));
            if (selectedFiles.length === 0) {
                showMessage('Pilih file preprocessing terlebih dahulu', 'error');
                return;
            }
            
            const filename = selectedFiles[0].value;
            await displayPreprocessedFile(filename);
        });
    }

    // Tombol kembali
    if (btnBack) {
        btnBack.addEventListener('click', function() {
            document.getElementById('tab-upload').click();
        });
    }

    // Toggle description untuk options
    const options = document.querySelectorAll(".option");
    options.forEach((opt) => {
        opt.addEventListener("click", () => {
            const desc = opt.querySelector("p.text-sm");
            if (desc) {
                desc.classList.toggle("hidden");
            }
        });
    });
}

// Fungsi untuk menampilkan progress bar
function showProgressBar() {
    const progressContainer = document.getElementById('analyzeProgressContainer');
    const progressBar = document.getElementById('analyzeProgressBar');
    const progressPercent = document.getElementById('progressPercent');

    progressContainer.classList.remove('hidden');

    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }

        progressBar.style.width = `${progress}%`;
        progressPercent.textContent = `${Math.round(progress)}%`;
    }, 200);
}

// Fungsi untuk menyembunyikan progress bar
function hideProgressBar() {
    const progressContainer = document.getElementById('analyzeProgressContainer');
    progressContainer.classList.add('hidden');
}

// Fungsi untuk menampilkan hasil analisis topik
function displayTopicResults(results) {
    const container = document.getElementById('modelResultsContainer');
    container.innerHTML = '';

    results.forEach((result) => {
        const modelSection = document.createElement('div');
        modelSection.className = 'bg-emerald-50 rounded-lg p-6 border border-emerald-200';

        // Header model
        const modelHeader = document.createElement('div');
        modelHeader.className = 'flex items-center justify-between mb-4';

        const modelTitle = document.createElement('h3');
        modelTitle.className = 'text-xl font-bold text-emerald-800';
        modelTitle.innerHTML = `<i class="fa-solid fa-brain mr-2"></i>Hasil Model ${result.model_type.toUpperCase()}`;

        const topicCount = document.createElement('span');
        topicCount.className = 'bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-sm font-medium';
        topicCount.textContent = `${result.topics.length} Topik Ditemukan`;

        modelHeader.appendChild(modelTitle);
        modelHeader.appendChild(topicCount);
        modelSection.appendChild(modelHeader);

        // Daftar topik
        result.topics.forEach((topic) => {
            const topicCard = document.createElement('div');
            topicCard.className = 'bg-white rounded-lg p-4 mb-4 border border-emerald-100';

            // Header topik
            const topicHeader = document.createElement('div');
            topicHeader.className = 'flex justify-between items-start mb-3';

            const topicName = document.createElement('h4');
            topicName.className = 'text-lg font-semibold text-emerald-800';
            topicName.textContent = topic.name;

            const topicPercentage = document.createElement('span');
            topicPercentage.className = 'bg-emerald-500 text-white px-3 py-1 rounded-full text-sm font-bold';
            topicPercentage.textContent = `${topic.percentage}%`;

            topicHeader.appendChild(topicName);
            topicHeader.appendChild(topicPercentage);
            topicCard.appendChild(topicHeader);

            // Kata kunci
            const keywordsContainer = document.createElement('div');
            keywordsContainer.className = 'flex flex-wrap gap-2 mb-3';

            topic.keywords.forEach((keyword) => {
                const keywordSpan = document.createElement('span');
                keywordSpan.className = 'bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full text-sm border border-emerald-200';
                keywordSpan.textContent = keyword;
                keywordsContainer.appendChild(keywordSpan);
            });

            topicCard.appendChild(keywordsContainer);

            // Sumber representatif
            if (topic.representative_sources && topic.representative_sources.length > 0) {
                const sourcesTitle = document.createElement('p');
                sourcesTitle.className = 'text-sm font-medium text-slate-600 mb-2';
                sourcesTitle.textContent = 'Sumber Representatif:';
                topicCard.appendChild(sourcesTitle);

                const sourcesContainer = document.createElement('div');
                sourcesContainer.className = 'space-y-2';

                topic.representative_sources.forEach((source) => {
                    const sourceDiv = document.createElement('div');
                    sourceDiv.className = 'text-sm text-slate-600 bg-slate-50 p-2 rounded';
                    sourceDiv.innerHTML = `<strong>${source.source}:</strong> ${source.content_preview}`;
                    if (source.verse) {
                        sourceDiv.innerHTML += ` <span class="text-emerald-600 font-medium">(${source.verse})</span>`;
                    }
                    sourcesContainer.appendChild(sourceDiv);
                });

                topicCard.appendChild(sourcesContainer);
            }

            modelSection.appendChild(topicCard);
        });

        container.appendChild(modelSection);
    });
}

// Fungsi untuk menampilkan sumber dokumen
function displaySources(sources) {
    const container = document.getElementById('sourcesContainer');
    container.innerHTML = '';

    if (sources.length === 0) {
        container.innerHTML = `
            <div class="text-center text-slate-500 py-8">
                <i class="fa-solid fa-book-open text-3xl mb-3 text-slate-300"></i>
                <p>Tidak ada data sumber yang tersedia</p>
            </div>
        `;
        return;
    }

    sources.forEach((source) => {
        const sourceCard = document.createElement('div');
        sourceCard.className = 'bg-white rounded-lg p-4 border border-slate-200';

        sourceCard.innerHTML = `
            <div class="flex justify-between items-start mb-2">
                <h4 class="font-semibold text-emerald-800">${source.reference}</h4>
                <span class="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs">Dokumen ${source.doc_id}</span>
            </div>
            <p class="text-sm text-slate-600">${source.preview}</p>
        `;

        container.appendChild(sourceCard);
    });
}

// Fungsi untuk menampilkan visualisasi
function displayVisualization(visualizationData) {
    const container = document.getElementById('visualizationContainer');

    let visualizationHTML = '';

    visualizationData.forEach((data) => {
        visualizationHTML += `
            <div class="bg-slate-50 rounded-lg p-4 border border-slate-200">
                <h4 class="font-medium text-slate-700 mb-3">Distribusi Topik - ${data.model_type}</h4>
                <div class="space-y-2">
                    ${data.topic_names.map((name, index) => `
                        <div class="flex items-center justify-between">
                            <span class="text-sm text-slate-600">${name}</span>
                            <div class="w-32 bg-slate-200 rounded-full h-2">
                                <div class="bg-emerald-500 h-2 rounded-full" style="width: ${data.topic_distribution[index]}%"></div>
                            </div>
                            <span class="text-sm font-medium text-emerald-600">${data.topic_distribution[index]}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });

    container.innerHTML = visualizationHTML;
}

// Fungsi untuk menangani pencarian
function setupSearchFunctionality(searchData) {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');

    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();

        if (query.length < 2) {
            searchResults.innerHTML = `
                <div class="text-center text-slate-500 py-8">
                    <i class="fa-solid fa-search text-3xl mb-3 text-slate-300"></i>
                    <p>Masukkan minimal 2 karakter untuk mencari</p>
                </div>
            `;
            return;
        }

        const filteredResults = searchData.filter(
            (item) =>
                item.keyword.toLowerCase().includes(query) ||
                item.topic_name.toLowerCase().includes(query)
        );

        if (filteredResults.length === 0) {
            searchResults.innerHTML = `
                <div class="text-center text-slate-500 py-8">
                    <i class="fa-solid fa-search text-3xl mb-3 text-slate-300"></i>
                    <p>Tidak ditemukan hasil untuk "${query}"</p>
                </div>
            `;
            return;
        }

        // Kelompokkan hasil berdasarkan topik
        const groupedResults = {};
        filteredResults.forEach((item) => {
            if (!groupedResults[item.topic_id]) {
                groupedResults[item.topic_id] = {
                    topic_name: item.topic_name,
                    percentage: item.percentage,
                    keywords: [],
                };
            }
            groupedResults[item.topic_id].keywords.push(item.keyword);
        });

        let resultsHTML = '';
        Object.values(groupedResults).forEach((topic) => {
            resultsHTML += `
                <div class="bg-white rounded-lg p-4 border border-emerald-200">
                    <div class="flex justify-between items-start mb-3">
                        <h4 class="font-semibold text-emerald-800">${topic.topic_name}</h4>
                        <span class="bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-sm">${topic.percentage}%</span>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        ${topic.keywords.map((keyword) => `
                            <span class="bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-sm border border-emerald-200">${keyword}</span>
                        `).join('')}
                    </div>
                </div>
            `;
        });

        searchResults.innerHTML = resultsHTML;
    });
}

// Fungsi untuk inisialisasi modal
function initializeModals() {
    // Modal untuk stopwords
    const stopwordsModal = document.getElementById('stopwordsModal');
    const editStopwordsModal = document.getElementById('editStopwordsModal');
    const viewStopwordsModal = document.getElementById('viewStopwordsModal');
    const displayModal = document.getElementById('displayModal');

    // Stopwords management
    const btnManageStopwords = document.getElementById('btnManageStopwords');
    if (btnManageStopwords) {
        btnManageStopwords.addEventListener('click', function() {
            if (stopwordsModal) stopwordsModal.classList.remove('hidden');
        });
    }

    const btnCloseStopwords = document.getElementById('btnCloseStopwords');
    if (btnCloseStopwords) {
        btnCloseStopwords.addEventListener('click', function() {
            if (stopwordsModal) stopwordsModal.classList.add('hidden');
        });
    }

    // Edit stopwords
    const btnEditStopwords = document.getElementById('btnEditStopwords');
    if (btnEditStopwords) {
        btnEditStopwords.addEventListener('click', async function() {
            const response = await fetch('/get_stopwords');
            const data = await response.json();
            if (data.status === 'success') {
                const stopwordsContent = document.getElementById('stopwordsContent');
                if (stopwordsContent) {
                    stopwordsContent.value = data.content;
                }
                if (editStopwordsModal) editStopwordsModal.classList.remove('hidden');
                if (stopwordsModal) stopwordsModal.classList.add('hidden');
            }
        });
    }

    const btnSaveStopwords = document.getElementById('btnSaveStopwords');
    if (btnSaveStopwords) {
        btnSaveStopwords.addEventListener('click', async function() {
            const stopwordsContent = document.getElementById('stopwordsContent');
            if (!stopwordsContent) return;

            const content = stopwordsContent.value;
            const response = await fetch('/save_stopwords', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: content })
            });
            const data = await response.json();
            if (data.status === 'success') {
                showMessage('Stopwords berhasil disimpan!', 'success');
                if (editStopwordsModal) editStopwordsModal.classList.add('hidden');
            } else {
                showMessage('Gagal menyimpan stopwords: ' + data.message, 'error');
            }
        });
    }

    const btnResetStopwords = document.getElementById('btnResetStopwords');
    if (btnResetStopwords) {
        btnResetStopwords.addEventListener('click', async function() {
            if (confirm('Reset stopwords ke default?')) {
                const response = await fetch('/reset_stopwords', { method: 'POST' });
                const data = await response.json();
                if (data.status === 'success') {
                    const stopwordsContent = document.getElementById('stopwordsContent');
                    if (stopwordsContent) {
                        stopwordsContent.value = data.content;
                    }
                    showMessage('Stopwords berhasil direset!', 'success');
                }
            }
        });
    }

    const btnCancelEdit = document.getElementById('btnCancelEdit');
    if (btnCancelEdit) {
        btnCancelEdit.addEventListener('click', function() {
            if (editStopwordsModal) editStopwordsModal.classList.add('hidden');
        });
    }

    // View stopwords
    const btnViewStopwords = document.getElementById('btnViewStopwords');
    if (btnViewStopwords) {
        btnViewStopwords.addEventListener('click', async function() {
            const response = await fetch('/get_stopwords');
            const data = await response.json();
            if (data.status === 'success') {
                const stopwordsList = document.getElementById('stopwordsList');
                if (stopwordsList) {
                    const words = data.content.split('\n').filter(word => word.trim());
                    stopwordsList.innerHTML = words.map(word => 
                        `<span class="inline-block bg-emerald-100 text-emerald-800 px-2 py-1 rounded text-sm m-1">${word.trim()}</span>`
                    ).join('');
                }
                if (viewStopwordsModal) viewStopwordsModal.classList.remove('hidden');
                if (stopwordsModal) stopwordsModal.classList.add('hidden');
            }
        });
    }

    const btnCloseView = document.getElementById('btnCloseView');
    if (btnCloseView) {
        btnCloseView.addEventListener('click', function() {
            if (viewStopwordsModal) viewStopwordsModal.classList.add('hidden');
        });
    }

    // Display modal
    const btnCloseDisplay = document.getElementById('btnCloseDisplay');
    if (btnCloseDisplay) {
        btnCloseDisplay.addEventListener('click', function() {
            if (displayModal) displayModal.classList.add('hidden');
        });
    }

    const btnCloseDisplayBottom = document.getElementById('btnCloseDisplayBottom');
    if (btnCloseDisplayBottom) {
        btnCloseDisplayBottom.addEventListener('click', function() {
            if (displayModal) displayModal.classList.add('hidden');
        });
    }

    // Template info toggle
    const toggle = document.getElementById('toggleTemplateInfo');
    const info = document.getElementById('templateInfo');

    if (toggle && info) {
        toggle.addEventListener('click', () => {
            if (info.classList.contains('hidden')) {
                info.classList.remove('hidden');
                setTimeout(() => (info.style.opacity = '1'), 10);
            } else {
                info.style.opacity = '0';
                setTimeout(() => info.classList.add('hidden'), 500);
            }
        });
    }

    // Download template
    const downloadTemplate = document.getElementById('downloadTemplate');
    if (downloadTemplate) {
        downloadTemplate.addEventListener('click', (e) => {
            e.preventDefault();
            fetch('/static/template_file.csv')
                .then((response) => {
                    if (!response.ok) throw new Error('File tidak ditemukan!');
                    return response.blob();
                })
                .then((blob) => {
                    const link = document.createElement('a');
                    const url = window.URL.createObjectURL(blob);
                    link.href = url;
                    link.download = 'template_file.csv';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    window.URL.revokeObjectURL(url);
                    showMessage('Template berhasil diunduh!', 'success');
                })
                .catch((err) => {
                    console.error(err);
                    showMessage('File template tidak ditemukan di folder static!', 'error');
                });
        });
    }
}

// ... (fungsi-fungsi lainnya tetap sama)