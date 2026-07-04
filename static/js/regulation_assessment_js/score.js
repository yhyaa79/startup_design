/* score.js */


// تعریف حداقل نمره به عنوان متغیر

const SCORE_TABLE = {
    tier1: {
        bachelor: 60,
        master: 80,
        general_doctorate: 100,
        specialty_doctorate: 80,
        PHD: 120
    },
    tier2: {
        bachelor: 54,
        master: 72,
        general_doctorate: 90,
        specialty_doctorate: 72,
        PHD: 108
    },
    tier3: {
        bachelor: 48,
        master: 64,
        general_doctorate: 80,
        specialty_doctorate: 64,
        PHD: 96
    }
};


let scoreData = {
    totalScore: 0,
    breakdown: {},
};



let MIN_SCORE = 85;

function updateMinScore() {
    const degree = document.getElementById("degree-select").value;
    const tier = document.getElementById("uni-select").value;

    if (degree && tier && SCORE_TABLE[tier] && SCORE_TABLE[tier][degree]) {
        MIN_SCORE = SCORE_TABLE[tier][degree];
    } else {
        MIN_SCORE = 85;
    }

    document.getElementById('min-score').textContent = MIN_SCORE;

    console.log("MIN_SCORE =", MIN_SCORE);
}


document.getElementById("degree-select").addEventListener("change", updateMinScore);
document.getElementById("uni-select").addEventListener("change", updateMinScore);

updateMinScore();



// نمایش حداقل نمره در HTML
document.getElementById('min-score').textContent = MIN_SCORE;

function calculateAllScores() {
    let totalScore = 0;
    const breakdown = {};
    const scoreTitle = {};


    Object.keys(formConfigs).forEach(key => {
        const config = formConfigs[key];
        if (!config.scoring) return;

        const items = formsData[key] || [];
        let sectionScore = 0;
        const itemResults = [];

        items.forEach((itemData, index) => {
            // فقط آیتم‌هایی که حداقل یک فیلد پر شده
            const hasData = Object.values(itemData).some(v => v !== '' && v !== null && v !== undefined);
            if (!hasData) return;

            const result = config.scoring.calculate(itemData);
            itemResults.push({
                index: index + 1,
                ...result
            });
            sectionScore += result.finalScore || 0;
        });

        // اعمال سقف ماده (maxScore)
        const cappedScore = config.scoring.maxScore !== null ?
            Math.min(sectionScore, config.scoring.maxScore) :
            sectionScore;

        breakdown[key] = {
            title: config.title,
            rawSectionScore: parseFloat(sectionScore.toFixed(2)),
            finalSectionScore: parseFloat(cappedScore.toFixed(2)),
            capped: config.scoring.maxScore !== null && sectionScore > config.scoring.maxScore,
            items: itemResults,
        };

        // ذخیره اطلاعات ماده ها در یکی از متغییر های دیتابیس 
        scoreData.breakdown = Object.fromEntries(
            Object.entries(breakdown).map(([key, data]) => [
                key,
                {
                    title: data.title,
                    finalScore: data.finalSectionScore
                }
            ])
        );



        totalScore += cappedScore;

        // لاگ هر ماده
        console.group(`📋 ${config.title}`);
        console.log('امتیاز خام:', sectionScore.toFixed(2));
        if (breakdown[key].capped) {
            console.warn(`⚠️ سقف اعمال شد: ${sectionScore.toFixed(2)} → ${cappedScore.toFixed(2)}`);
        }
        itemResults.forEach(r => {
            console.log(`  آیتم ${r.index}:`, r.breakdown || r);
        });
        console.groupEnd();
    });

    console.group('🏆 نتیجه نهایی');
    console.table(
        Object.fromEntries(
            Object.entries(breakdown).map(([k, v]) => [v.title, v.finalSectionScore])
        )
    );
    console.log('مجموع کل:', parseFloat(totalScore.toFixed(2)));
    console.groupEnd();

    return {
        totalScore: parseFloat(totalScore.toFixed(2)),
        breakdown
    };
}
document.getElementById('btn-next-2').addEventListener('click', function () {
    console.group("▶️ کلیک روی btn-next-2");

    const {
        totalScore,
        breakdown
    } = calculateAllScores();
    console.log("🏁 totalScore:", totalScore);
    console.log("📂 breakdown خروجی calculateAllScores:", breakdown);

    // ذخیره امتیاز کاربر در scoreData
    scoreData.totalScore = totalScore;



    // نمایش امتیاز کاربر
    document.getElementById('your-score').textContent = totalScore;

    const yourScoreCard = document.getElementById('your-score-card');
    const remainScoreCard = document.getElementById('remain-score-card');
    const resultText = document.getElementById('result-text');

    if (totalScore >= MIN_SCORE) {
        console.log("✅ امتیاز کافی است، نمایش پیشنهادات اختیاری است (ولی ما باز هم تست می‌کنیم)");

        yourScoreCard.style.background = '#d1f2d6';
        yourScoreCard.style.border = '2px solid #63d27b';
        yourScoreCard.style.color = '#03a819';
        remainScoreCard.style.display = 'none';

        resultText.textContent = 'تبریک! امتیاز شما از حداقل نمره مورد نیاز بیشتر است و شرایط لازم را دارید.';
        resultText.style.borderRightColor = '#22c55e';
    } else {
        console.log("⚠️ امتیاز کافی نیست، باید پیشنهادات نمایش داده شود");

        yourScoreCard.style.background = '#ffd7cd';
        yourScoreCard.style.border = '2px solid #ff7b78';
        yourScoreCard.style.color = '#c21904';
        remainScoreCard.style.display = 'block';

        const remain = parseFloat((MIN_SCORE - totalScore).toFixed(2));
        document.getElementById('remain-score').textContent = remain.toLocaleString('en-US');

        resultText.textContent = 'بر اساس بررسی اطلاعات شما، امتیاز کسب‌شده از حداقل نمره مورد نیاز کمتر است. برای دریافت تأییدیه این آیین‌نامه لازم است امتیاز خود را از طریق پیشنهادات مرحله بعد افزایش دهید.';
        resultText.style.borderRightColor = '#ef4444';
    }

    // ---- از اینجا به بعد: پیشنهادات ----
    const container = document.querySelector(".proposals-list");
    console.log("🧩 container (.proposals-list):", container);

    if (!container) {
        console.error("❌ .proposals-list در DOM پیدا نشد. HTML را چک کن.");
    } else {
        // همیشه برای تست، پیشنهاد بسازیم (چه قبول شده چه رد شده)
        const suggestionPackages = generateSuggestionPackages(breakdown);

        console.log("📦 suggestionPackages:", suggestionPackages);

        container.innerHTML = ""; // حذف قبلی‌ها

        if (!suggestionPackages || suggestionPackages.length === 0) {
            console.warn("⚠️ suggestionPackages خالی است، چیزی برای نمایش وجود ندارد");
            container.innerHTML = `<div class="proposal-item">پیشنهادی یافت نشد. لطفاً تنظیمات SUGGESTIONS یا breakdown را بررسی کنید.</div>`;
        } else {
            suggestionPackages.forEach((pack, i) => {
                const box = document.createElement("div");
                box.className = "proposal-box";

                // لاگ داخلی هر پکیج
                console.log(`📦 رندر پکیج ${i + 1}:`, pack);

                box.innerHTML = `
                <p>بسته پیشنهادی ${i + 1}</p>
                    <ul class="proposal-item-ul">
                        ${
                            pack.map(p =>
                                `<li class="proposal-item">${p.text}${p.score !== undefined ? ` — امتیاز: ${p.score}` : ''}</li>`
                            ).join("")
                        }
                    </ul>
                `;
                container.appendChild(box);
            });

        }
    }

    // نمایش ویدیوهای پیشنهادی
    displayVideoSuggestions(breakdown);

    console.groupEnd();
    nextStep(1, this);
});