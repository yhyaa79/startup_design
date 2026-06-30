/* steps.js */

let currentStep = 0;
// متغیر گلوبال برای ذخیره داده‌ها
let formData = {
    firstName: '',
    lastName: '',
    phone: '',
    email: ''
};



// ذخیره‌سازی خودکار فیلدها در localStorage
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.step.active .content');
    const inputs = form.querySelectorAll('input, select');
    
    // بارگذاری داده‌های ذخیره شده
    inputs.forEach(input => {
        const savedValue = localStorage.getItem(input.name || input.placeholder);
        if (savedValue) {
            input.value = savedValue;
        }
        
        // ذخیره خودکار هنگام تغییر
        input.addEventListener('input', function() {
            localStorage.setItem(this.name || this.placeholder, this.value);
        });
    });
});



// محدودیت ورودی شماره همراه
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.querySelector('input[type="tel"]');
    
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // فقط اعداد
            this.value = this.value.replace(/[^0-9]/g, '');
            
            // حداکثر ۱۱ رقم
            if (this.value.length > 11) {
                this.value = this.value.slice(0, 11);
            }
        });
        
        phoneInput.addEventListener('keydown', function(e) {
            const allowedKeys = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'Tab'];
            if (!allowedKeys.includes(e.key) && !/[0-9]/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
});

// محدودیت ورودی ایمیل (فقط انگلیسی)
document.addEventListener('DOMContentLoaded', function() {
    const emailInput = document.querySelector('input[type="email"]');
    
    if (emailInput) {
        emailInput.addEventListener('input', function(e) {
            // حذف کاراکترهای فارسی
            this.value = this.value.replace(/[\u0600-\u06FF]/g, '');
        });
    }
});

// محدودیت ورودی ترم (۱ تا ۱۴)
document.addEventListener('DOMContentLoaded', function() {
    const termInput = document.querySelector('input[type="number"]');
    
    if (termInput) {
        termInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
            
            const num = parseInt(this.value);
            if (num > 14) this.value = 14;
            if (num < 1 && this.value !== '') this.value = 1;
        });
    }
});





function nextStep(index, btn) {
    let currentStep = btn.closest(".step");
    let next = currentStep.nextElementSibling;

    let inputs = [];

    if (index === 0) {
        inputs = currentStep.querySelectorAll(".required");
        
        // اعتبارسنجی مرحله اول
        if (!validateStep1()) {
            return;
        }
    } else if (index === 1) {
        let selected = document.getElementById("selected-bylaw").value;
        if (selected === "") {
            alert("لطفاً یک آیین‌نامه انتخاب کنید");
            return;
        }
        let visibleForm = document.getElementById("form-" + selected);
        if (visibleForm) inputs = visibleForm.querySelectorAll(".required");
    } else {
        inputs = currentStep.querySelectorAll(".required");
    }

    let allFilled = true;
    inputs.forEach(input => {
        if (input.value.trim() === "") {
            allFilled = false;
            input.classList.add("error");
        } else {
            input.classList.remove("error");
        }
    });

    if (!allFilled) {
        alert("لطفاً فیلدهای اجباری را کامل کنید");
        return;
    }

    let loader = document.getElementById("loading-overlay");
    loader.classList.add("active");
    btn.disabled = true;

    setTimeout(() => {
        btn.innerHTML = "تأیید شد ✔";

        const selectTrigger = document.getElementById("select-trigger");

        if (index === 1 && selectTrigger) {
            selectTrigger.style.pointerEvents = "none";
            selectTrigger.style.opacity = "0.6";
            selectTrigger.classList.add("disabled");
        }

        const modalBodies = document.querySelectorAll(".modal-body");

        if (index === 1 && modalBodies.length > 0) {
            modalBodies.forEach(el => {
                el.style.pointerEvents = "none";
                el.style.opacity = "0.6";
                el.classList.add("disabled");
            });
        }

        const labelOpenModals = document.querySelectorAll(".label-open-modal");

        if (index === 1 && labelOpenModals.length > 0) {
            labelOpenModals.forEach(el => {
                el.style.pointerEvents = "none";
                el.style.opacity = "0.6";
                el.classList.add("disabled");
            });
        }

        currentStep.querySelectorAll("textarea, input:not([type=hidden])").forEach(el => {
            el.disabled = true;
        });

        if (index === 0) {
            currentStep.classList.add("step-hide");
            setTimeout(() => currentStep.remove(), 600);
        } else {
            currentStep.classList.add("step-locked");
        }

        currentStepIndex = index + 1;
        updateProgress(currentStepIndex);

        // Skip container div if exists
        let nextStep = next;
        while (nextStep && !nextStep.classList.contains("step")) {
            nextStep = nextStep.nextElementSibling;
        }

        if (next && next.classList.contains("step")) {
            next.classList.add("active");
            setTimeout(() => {
                next.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }, 100);
        }

        loader.classList.remove("active");
    }, 900);
}

// تابع اعتبارسنجی مرحله اول
function validateStep1() {
    const inputs = document.querySelectorAll('.step.active .form-input.required');
    let isValid = true;
    let errors = [];
    
    inputs.forEach(input => {
        const value = input.value.trim();
        const label = input.previousElementSibling?.textContent.replace('*', '').trim() || 'فیلد';
        
        // بررسی خالی بودن
        if (!value) {
            isValid = false;
            errors.push(`${label} الزامی است`);
            input.classList.add('error');
            return;
        }
        
        // اعتبارسنجی نام و نام خانوادگی
        if (input.type === 'text' && (input.placeholder.includes('نام') || input.name === 'firstName' || input.name === 'lastName')) {
            const namePattern = /^[\u0600-\u06FFa-zA-Z\s]+$/;
            if (!namePattern.test(value)) {
                isValid = false;
                errors.push(`${label} فقط باید شامل حروف باشد`);
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        }
        
        // اعتبارسنجی شماره همراه
        if (input.type === 'tel') {
            const phonePattern = /^0[0-9]{10}$/;
            if (value.length !== 11) {
                isValid = false;
                errors.push('شماره همراه باید دقیقاً ۱۱ رقم باشد');
                input.classList.add('error');
            } else if (!phonePattern.test(value)) {
                isValid = false;
                errors.push('شماره همراه باید با ۰ شروع شود و فقط شامل اعداد باشد');
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        }
        
        // اعتبارسنجی ایمیل
        if (input.type === 'email') {
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailPattern.test(value)) {
                isValid = false;
                errors.push('فرمت ایمیل معتبر نیست (مثال: user@example.com)');
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        }
    });
    
    if (isValid) {
        // ذخیره مقادیر در متغیر گلوبال
        formData.firstName = document.querySelector('input[name="firstName"]').value.trim();
        formData.lastName = document.querySelector('input[name="lastName"]').value.trim();
        formData.phone = document.querySelector('input[name="phone"]').value.trim();
        formData.email = document.querySelector('input[name="email"]').value.trim();
        
    } else {
        alert(errors.join('\n'));
    }
    
    return isValid;
}



// Initial progress
updateProgress(0);


function updateProgress(activeIndex) {
    document.querySelectorAll('.progress-step').forEach((step, i) => {
        step.classList.remove('active', 'done');
        if (i < activeIndex) step.classList.add('done');
        else if (i === activeIndex) step.classList.add('active');
    });
}

function shakeButton(btn) {
    if (!btn) return;
    btn.classList.add('shake');
    setTimeout(() => btn.classList.remove('shake'), 500);
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'flex';
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
}
