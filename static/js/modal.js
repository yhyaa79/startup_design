/* modal.js */


// ==========================================
// تعریف مراحل ویزارد
// ==========================================
const wizardSteps = [{
        key: "maghaleh",
        title: "ماده ۱- انتشار مقاله"
    },
    {
        key: "payannameh",
        title: "ماده ۲- پايان نامه"
    },
    {
        key: "maghale_congress",
        title: "ماده ۳- ارائه خلاصه مقالات در کنگره‌ها و سمینارها"
    },
    {
        key: "davari",
        title: "ماده ۴- داوري طرح هاي تحقيقاتي، خلاصه مقالات كنگره ها و مقالات ژورنال هاي معتبر"
    },
    {
        key: "ketab",
        title: "ماده ۵- انتشاركتاب"
    },
    {
        key: "tahghighat",
        title: "ماده ۶- مجري يا همكاري در اجراي طرح هاي تحقيقاتي"
    },
    {
        key: "faulit",
        title: "ماده ۷- فعاليت در كميته تحقيقات و فناوري دانشجويي"
    },
    {
        key: "ekhtera",
        title: "ماده ۸- الف - اختراع، اکتشاف"
    },
    {
        key: "noavari",
        title: "ماده ۸- ب - کارآفرینی و فناوری"
    },
    {
        key: "jashnvare",
        title: "ماده ۹- برگزیدگان جشنواره‌های مورد تأیید کمیته تحقیقات و فناوری دانشجویی"
    }
];

let currentStepIndex = 0;

// ==========================================
// مقداردهی اولیه formsData از localStorage
// ==========================================
const formsData = {};
Object.keys(formConfigs).forEach(key => {
    const saved = localStorage.getItem(`formData_${key}`);
    formsData[key] = saved ? JSON.parse(saved) : [{}];
});

// ==========================================
// ذخیره یک مرحله در localStorage
// ==========================================
function saveToLocalStorage(formKey) {
    localStorage.setItem(`formData_${formKey}`, JSON.stringify(formsData[formKey]));
}

// ==========================================
// خواندن داده‌های کارت‌های فعلی و ذخیره
// ==========================================
function saveCurrentStep() {
    const overlay = document.getElementById('modal-overlay');
    const formKey = overlay.dataset.currentForm;
    const cards = document.querySelectorAll('#modal-bylaw .article-card');
    formsData[formKey] = [];

    cards.forEach(card => {
        const data = {};
        card.querySelectorAll('[name]').forEach(input => {
            data[input.name] = input.value;
        });
        formsData[formKey].push(data);
    });

    saveToLocalStorage(formKey);
}

// ==========================================
// باز کردن یک مرحله از ویزارد
// ==========================================
function openWizardStep(stepIndex = 0) {
    currentStepIndex = stepIndex;

    const step = wizardSteps[stepIndex];
    const config = formConfigs[step.key];
    const overlay = document.getElementById("modal-overlay");

    overlay.dataset.currentForm = step.key;
    document.querySelector("#modal-bylaw .modal-title").textContent = step.title;
    document.querySelector("#modal-bylaw .section-disc-form").textContent = config.disc || '';

    renderModalCards(step.key);
    updateProgressBar();
    updateWizardButtons();

    overlay.style.display = "flex";
}


// ==========================================
// دکمه Back — ذخیره قبل از برگشت
// ==========================================
document.getElementById('back-btn').addEventListener('click', () => {
    if (currentStepIndex > 0) {
        saveCurrentStep();
        openWizardStep(currentStepIndex - 1);
    }
});

// ==========================================
// دکمه Next — ذخیره قبل از رفتن به مرحله بعد
// ==========================================
document.getElementById('next-btn').addEventListener('click', () => {
    saveCurrentStep();
    if (currentStepIndex < wizardSteps.length - 1) {
        openWizardStep(currentStepIndex + 1);
    }
});

// ==========================================
// نوار پیشرفت
// ==========================================
function updateProgressBar() {
    const total = wizardSteps.length;
    const current = currentStepIndex + 1;
    const percent = (current / total) * 100;

    document.getElementById("progress-bar").style.width = percent + "%";
    document.getElementById("progress-text").textContent = "مرحله " + current + " از " + total;
}

// ==========================================
// کنترل نمایش دکمه‌های ویزارد
// ==========================================
function updateWizardButtons() {
    const total = wizardSteps.length;
    const isFirst = currentStepIndex === 0;
    const isLast = currentStepIndex === total - 1;

    document.getElementById("back-btn").style.display = isFirst ? "none" : "inline-block";
    document.getElementById("next-btn").style.display = isLast ? "none" : "inline-block";
    document.getElementById("button-next-step-2").style.display = isLast ? "flex" : "none";
}

// ==========================================
// رندر یک فیلد — با پشتیبانی از مقدار ذخیره‌شده
// ==========================================
function renderField(field, savedValue = '') {
    const tooltip = field.tooltip ? `
        <span class="tooltip-wrapper">
            <span class="tooltip-icon">?</span>
            <span class="tooltip-box">${field.tooltip}</span>
        </span>` : '';

    const dependencyAttr = field.dependsOn ?
        `data-depends-on="${field.dependsOn.field}" data-depends-value='${JSON.stringify(field.dependsOn.value)}'` : '';

    const requiredClass = field.required ? 'required' : '';
    let input = '';

    if (field.type === 'select') {
        const opts = field.options.map(o =>
            `<option value="${o.value}" ${savedValue === o.value ? 'selected' : ''}>${o.label}</option>`
        ).join('');
        input = `<select class="form-input ${requiredClass}" name="${field.name}" ${dependencyAttr}>
                    <option value="" disabled ${!savedValue ? 'selected' : ''}>-- انتخاب کنید --</option>
                    ${opts}
                 </select>`;
    } else {
        const minAttr = field.min !== undefined ? `min="${field.min}"` : '';
        const maxAttr = field.max !== undefined ? `max="${field.max}"` : '';

        const onInputLimit = (field.type === 'number' && (field.min !== undefined || field.max !== undefined)) ?
            `oninput="
            if(this.value !== ''){
                if(${field.min !== undefined ? `this.value < ${field.min}` : 'false'}) this.value=${field.min};
                if(${field.max !== undefined ? `this.value > ${field.max}` : 'false'}) this.value=${field.max};
            }
        "` : '';

        input = `<input 
                type="${field.type}" 
                class="form-input ${requiredClass}"
                name="${field.name}" 
                placeholder="${field.placeholder || ''}"
                value="${savedValue}"
                ${minAttr}
                ${maxAttr}
                ${onInputLimit}
                ${dependencyAttr}
            >`;
    }


    return `
        <div class="form-group" data-field-container="${field.name}">
            <label>${field.label} ${field.required ? '<span class="required-mark">*</span>' : ''} ${tooltip}</label>
            ${input}
        </div>`;
}

// ==========================================
// رندر یک کارت — با پشتیبانی از داده‌های ذخیره‌شده
// ==========================================
function renderCard(config, index, savedData = {}) {
    // اگر allowMultiple فالس باشد، شماره نمایش نده
    const cardTitle = config.allowMultiple 
        ? `${config.itemLabel} ${index + 1}` 
        : config.itemLabel;

    return `
        <div class="article-card" data-index="${index}">
            <div class="article-card-header">
                <span class="article-card-title">${cardTitle}</span>
                ${(index > 0 && config.allowMultiple) ? `<button class="btn-remove-card" data-remove="${index}">✕</button>` : ''}
            </div>
            ${config.fields.map(f => renderField(f, savedData[f.name] || '')).join('')}
        </div>`;
}


// ==========================================
// بررسی وابستگی فیلدها
// ==========================================
function checkDependencies(cardElement) {
    cardElement.querySelectorAll('[data-depends-on]').forEach(input => {
        const targetFieldName = input.dataset.dependsOn;
        const allowedValues = JSON.parse(input.dataset.dependsValue);
        const targetInput = cardElement.querySelector(`[name="${targetFieldName}"]`);

        if (targetInput) {
            const isVisible = allowedValues.includes(targetInput.value);
            const container = input.closest('.form-group');

            input.disabled = !isVisible;
            container.style.display = isVisible ? '' : 'none';
            if (!isVisible) input.value = '';
        }
    });
}

// ==========================================
// رندر کارت‌های مودال + ذخیره real-time
// ==========================================
function renderModalCards(formKey) {
    const config = formConfigs[formKey];
    const modalBody = document.querySelector('#modal-bylaw .modal-body');
    const footer = modalBody.querySelector('.modal-footer');
    const btnAdd = document.getElementById('btn-add-new');

    btnAdd.style.display = config.allowMultiple ? 'block' : 'none';

    // حذف کارت‌های قبلی
    modalBody.querySelectorAll('.article-card').forEach(el => el.remove());
    btnAdd.textContent = " ➕ افزودن " + config.itemLabel + " جدید ";

    formsData[formKey].forEach((savedData, i) => {
        footer.insertAdjacentHTML('beforebegin', renderCard(config, i, savedData));

        const currentCard = modalBody.querySelector(`.article-card[data-index="${i}"]`);
        checkDependencies(currentCard);

        // ذخیره خودکار با هر تغییر فیلد
        currentCard.addEventListener('change', () => {
            checkDependencies(currentCard);

            const cardIndex = Number(currentCard.dataset.index);
            currentCard.querySelectorAll('[name]').forEach(input => {
                formsData[formKey][cardIndex][input.name] = input.value;
            });

            saveToLocalStorage(formKey);
        });
    });

    // رویداد حذف کارت
    modalBody.querySelectorAll('[data-remove]').forEach(btn => {
        btn.onclick = () => {
            formsData[formKey].splice(Number(btn.dataset.remove), 1);
            saveToLocalStorage(formKey);
            renderModalCards(formKey);
        };
    });
}

// ==========================================
// رویدادهای مودال
// ==========================================
function initModalEvents() {
    const overlay = document.getElementById('modal-overlay');

    // بستن مودال با کلیک روی پس‌زمینه
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.style.display = 'none';
    });

    // افزودن کارت جدید
    document.getElementById('btn-add-new').addEventListener('click', () => {
        const formKey = overlay.dataset.currentForm;
        formsData[formKey].push({});
        saveToLocalStorage(formKey);
        renderModalCards(formKey);

        const cards = document.querySelectorAll('#modal-bylaw .article-card');
        cards[cards.length - 1].scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });

    // پاک کردن اطلاعات مرحله جاری
    document.getElementById('btn-clear-step').addEventListener('click', () => {
        const formKey = overlay.dataset.currentForm;

        if (confirm('\u202B' + 'آیا از پاک کردن تمام اطلاعات این مرحله مطمئن هستید؟' + '\u202C')) {
            formsData[formKey] = [{}];
            saveToLocalStorage(formKey);
            renderModalCards(formKey);
        }
    });
}