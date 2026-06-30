// ذخیره اطلاعات فرم در LocalStorage
function saveTestData() {
    const data = {
        degree: document.getElementById('degree-select').value,
        university: document.getElementById('uni-select').value,
        gpa: document.getElementById('gpa-input').value,
        checkboxes: Array.from(document.querySelectorAll('input[type="checkbox"][name="research[]"]:checked')).map(cb => cb.value)
    };
    localStorage.setItem('estedadTestData', JSON.stringify(data));
}

// بازیابی اطلاعات فرم از LocalStorage هنگام لود صفحه
function loadTestData() {
    const dataStr = localStorage.getItem('estedadTestData');
    if (dataStr) {
        const data = JSON.parse(dataStr);
        if (data.degree) document.getElementById('degree-select').value = data.degree;
        if (data.university) document.getElementById('uni-select').value = data.university;
        if (data.gpa) document.getElementById('gpa-input').value = data.gpa;
        if (data.checkboxes) {
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name="research[]"]');
            checkboxes.forEach(cb => {
                cb.checked = data.checkboxes.includes(cb.value);
            });
        }
    }
}

// فعال‌سازی ذخیره خودکار هنگام تغییر مقادیر
document.addEventListener('DOMContentLoaded', () => {
    loadTestData();      // مقداردهی از LocalStorage
    updateMinScore();   // ✅ محاسبه MIN_SCORE با مقادیر لود شده

    const formInputs = document.querySelectorAll(
        '#form-estedad-test select, #form-estedad-test textarea, #form-estedad-test input[type="checkbox"]'
    );

    formInputs.forEach(input => {
        input.addEventListener('change', saveTestData);
        input.addEventListener('input', saveTestData);
    });
});


function submitEstadadTest() {
    const MINIMUM_GPA = 15;
    const gpaInput = document.getElementById('gpa-input');
    const gpa = parseFloat(gpaInput.value);

    const testForm = document.getElementById('form-estedad-test');
    const testFormShow = document.getElementById('form-estedad-test-show');
    const progressContainer = document.getElementById('progress-container');

    // قبل از اعتبارسنجی اطلاعات را برای اطمینان ذخیره می‌کنیم
    saveTestData();

    testFormShow.style.display = 'none';

    // تنها شرط قبولی: معدل باید بزرگتر یا مساوی 15 باشد
    if (!isNaN(gpa) && gpa >= MINIMUM_GPA) {
        // ✅ قبول شد
        if (testForm) {
            showTestSuccess(testForm);

            setTimeout(() => {
                testForm.style.transition = 'opacity 0.3s ease';
                testForm.style.opacity = '0';

                if (progressContainer) progressContainer.style.display = 'block';
                if (typeof openWizardStep === 'function') openWizardStep(0);

                setTimeout(() => {
                    testForm.remove();
                }, 300);

            }, 1500);
        }
    } else {
        // ❌ رد شد
        showTestError(gpa, MINIMUM_GPA);
    }
}

function showTestSuccess(testForm) {
    const oldError = document.getElementById('test-error-msg');
    if (oldError) oldError.remove();

    const oldSuccess = document.getElementById('test-success-msg');
    if (oldSuccess) oldSuccess.remove();

    const msg = document.createElement('div');
    msg.id = 'test-success-msg';
    msg.style.cssText = `
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 16px;
        color: #155724;
        font-size: 14px;
        direction: rtl;
        text-align: right;
        font-weight: bold;
    `;
    msg.innerHTML = `✅ تبریک! معدل شما شرایط لازم را دارد. در حال انتقال...`;
    testForm.appendChild(msg);
}

function showTestError(gpa, minimum) {
    const old = document.getElementById('test-error-msg');
    if (old) old.remove();

    const testForm = document.getElementById('form-estedad-test');
    if (!testForm) return;

    const msg = document.createElement('div');
    msg.id = 'test-error-msg';
    msg.style.cssText = `
        transition: all 0.2s ease;
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 16px;
        color: #856404;
        font-size: 14px;
        direction: rtl;
        text-align: right;
    `;

    const displayGpa = isNaN(gpa) ? "نامعتبر" : gpa;

    msg.innerHTML = `
        ⚠️ متأسفانه معدل وارد شده "<strong>${displayGpa}</strong>" کمتر از حداقل مورد نیاز "<strong>${minimum}</strong>" است.
        <br>برای ورود به این بخش، معدل شما باید بیشتر از 15 باشد.
    `;
    testForm.appendChild(msg);
}