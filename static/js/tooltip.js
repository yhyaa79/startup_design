function initTooltips() {
    document.querySelectorAll('.tooltip-icon').forEach(icon => {
        icon.onclick = null;
        icon.addEventListener('click', (e) => {
            e.stopPropagation();
            const wrapper = icon.closest('.tooltip-wrapper');
            document.querySelectorAll('.tooltip-wrapper.active').forEach(el => {
                if (el !== wrapper) el.classList.remove('active');
            });
            wrapper.classList.toggle('active');
        });
    });
}

// بستن با کلیک خارج
document.addEventListener('click', () => {
    document.querySelectorAll('.tooltip-wrapper.active').forEach(el => {
        el.classList.remove('active');
    });
});
