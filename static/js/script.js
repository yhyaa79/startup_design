


document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.rs-alert');

    alerts.forEach(function (alert) {
        // انیمیشن ورود
        requestAnimationFrame(function () {
            alert.classList.add('rs-alert-show');
        });

        // بسته شدن خودکار بعد از ۵ ثانیه
        setTimeout(function () {
            dismissAlert(alert);
        }, 5000);

        // بسته شدن با دکمه
        const closeBtn = alert.querySelector('.btn-close-alert');
        if (closeBtn) {
            closeBtn.addEventListener('click', function (e) {
                e.preventDefault();
                dismissAlert(alert);
            });
        }
    });

    function dismissAlert(alert) {
        alert.classList.remove('rs-alert-show');
        alert.classList.add('rs-alert-hide');
        setTimeout(function () {
            alert.remove();
        }, 400);
    }
});







const menuToggle = document.getElementById('menuToggle');
const sidebar = document.getElementById('sidebar');
const main = document.getElementById('main');

menuToggle.addEventListener('click', () => {
    sidebar.classList.toggle('closed');
    main.classList.toggle('full');
});