function initBylawSelect() {
    const trigger = document.getElementById('select-trigger');
    const customSelect = document.getElementById('custom-select');
    const selectItems = document.querySelectorAll('.custom-select-item');
    const infoBox = document.getElementById('bylaw-info');
    const hiddenInput = document.getElementById('selected-bylaw');
    const placeholder = document.getElementById('select-placeholder');

    if (!trigger || !customSelect) {
        console.warn('Custom select elements not found!');
        return;
    }

    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        customSelect.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
        if (!customSelect.contains(e.target)) {
            customSelect.classList.remove('open');
        }
    });

    selectItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();

            selectItems.forEach(i => i.classList.remove('selected'));
            item.classList.add('selected');

            const value = item.dataset.value;
            const desc = item.dataset.desc || '';
            const link = item.dataset.link || '#';
            const labelEl = item.querySelector('span:last-child');
            const label = labelEl ? labelEl.innerText : value;

            if (hiddenInput) hiddenInput.value = value;

            if (placeholder) {
                placeholder.textContent = label;
                placeholder.style.color = 'var(--gray-800)';
            }

            if (infoBox) {
                infoBox.style.display = 'block';
                infoBox.innerHTML = `
                    <div style="display:flex; align-items:flex-start; gap:10px;">
                        <span style="font-size:20px;">📄</span>
                        <div style="flex:1;">
                            <p style="margin:0 0 8px; color:var(--gray-700); line-height:1.7;">
                                ${desc}
                            </p>
                            <a href="${link}" download
                               style="display:inline-flex; align-items:center; gap:6px;
                                      color:var(--primary);
                                      text-decoration:none; font-weight:600;">
                                ⬇ دانلود فایل آیین‌نامه
                            </a>
                        </div>
                    </div>`;
            }

            showForm(value);
            customSelect.classList.remove('open');
        });
    });
}

function showForm(value) {
    const forms = ['form-estedad', 'form-bonyad', 'form-researcher', 'form-estedad-test'];
    forms.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = 'none';
    });

    if (value === 'estedad') {
        showWithAnimation('form-estedad-test');
    } else if (value === 'bonyad') {
        showWithAnimation('form-bonyad');
    } else if (value === 'researcher') {
        showWithAnimation('form-researcher');
    } else {
        showWithAnimation('form-' + value);
    }
}

function showWithAnimation(id) {
    const target = document.getElementById(id);
    if (!target) return;

    target.style.display = 'block';
    target.style.opacity = '0';
    target.style.transform = 'translateY(10px)';
    requestAnimationFrame(() => {
        target.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        target.style.opacity = '1';
        target.style.transform = 'translateY(0)';
    });
}