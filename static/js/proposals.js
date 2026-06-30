// -------------------------
// پیشنهادات ویژه هر ماده
// -------------------------

const SUGGESTIONS = {

    /* ماده 1 */
    maghaleh: [{
            text: "ماده 1: انتشار مقاله نمایه شده در ISI",
            score: 25
        },
        {
            text: "ماده 1: انتشار مقاله نمایه شده در SCOPUS ",
            score: 20
        },
        {
            text: "ماده 1: انتشار مقاله نمایه شده در علمی پژوهشی داخل کشور ",
            score: 10
        },
    ],

    /* ماده 2 */
    payannameh: [{
        text: "ماده 2: دفاع از پایان نامه ",
        score: 5
    }, ],

    /* ماده 3 */
    maghale_congress: [{
            text: "ماده 3: ارائه خلاصه مقالات به صورت سخنرانی در همایش های داخلی ",
            score: 1
        },
        {
            text: "ماده 3: ارائه خلاصه مقالات به صورت سخنرانی در همایش های خارجی ",
            score: 3
        },
        {
            text: "ماده 3: ارائه خلاصه مقالات به صورت پوستر در همایش های داخلی ",
            score: 0.5
        },
        {
            text: "ماده 3: ارائه خلاصه مقالات به صورت پوستر در همایش های خارجی ",
            score: 1
        },
    ],

    /* ماده 4 */
    davari: [{
            text: "ماده 4: داوری ابسترکت در کنگره های سالیانه",
            score: 0.1
        },
        {
            text: "ماده 4: داوری طرح تحقیقاتی",
            score: 0.2
        },
        {
            text: "ماده 4: داوری مقاله در ژورنال های داخلی و خارجی ",
            score: 0.5
        },
    ],

    /* ماده 5 */
    ketab: [{
            text: "ماده 5: تالیف کتاب مرتبط با رشته تحصیلی ",
            score: 20
        },
        {
            text: "ماده 5: ترجمه کتاب مرتبط با رشته تحصیلی ",
            score: 15
        },
        {
            text: "ماده 5: گردآوری کتاب مرتبط با رشته تحصیلی ",
            score: 10
        },
    ],

    /* ماده 6 */
    tahghighat: [{
            text: "ماده 6: همکار طرح تحقیقاتی",
            score: 3
        },
        {
            text: "ماده 6: مجری طرح تحقیقاتی ",
            score: 5
        },
    ],

    /* ماده 7 */
    faulit: [{
            text: "ماده 7: دبیر کل کمیته تحقیقات و فناوری دانشگاه یا دانشکده",
            score: 8
        },
        {
            text: "ماده 7: عضویت در شورای مرکزی کمیته تحقیقات و فناوری دانشگاه یا دانشکده",
            score: 4
        },
        {
            text: "ماده 7: همکار یا مسئول اجرایی در برگزاری رویداد، همایش، ژورنال کلاب و استارتاپ ویکند ",
            score: 1
        },
        {
            text: "ماده 7: هر یک ساعت تدریس در کارگاه های کمیته تحقیقات و فناوری دانشجویی ",
            score: 0.2
        },
    ],

    /* ماده 8 الف */
    ekhtera: [{
            text: "ماده 8 الف: ثبت اختراع با تاییدیه مرکز مالکیتهای معنوی",
            score: 10
        },
        {
            text: "ماده 8 الف: ثبت اختراع با تاییدیه بنیاد ملی نخبگان یا وزارت بهداشت ",
            score: 20
        },
        {
            text: "ماده 8 الف: ثبت اختراع در خارج از کشور ",
            score: 30
        },
    ],

    /* ماده 8 ب */
    noavari: [{
            text: "ماده 8 ب: استقرار در مرکز رشد دانشگاه به عنوان مدیر یا عضو هیئت مدیره یک شرکت ",
            score: 10
        },
        {
            text: "ماده 8 ب: استقرار در مرکز رشد دانشگاه به عنوان مدیر یا عضو هیئت مدیره یک واحد فناور ",
            score: 10
        },
        {
            text: "ماده 8 ب: تاسیس شرکت دانش بنیان به عنوان مدیر یا عضو هیئت مدیره",
            score: 20
        },
        {
            text: "ماده 8 ب: تجاری سازی و فروش محصول ",
            score: 15
        },
        {
            text: "ماده 8 ب: شرکت و برپایی غرفه در رویدادها و نمایشگاه های فناورانه ",
            score: 5
        },
    ],

    /* ماده 9 */
    jashnvare: [{
            text: "ماده 9: برگزیده بخش دانشجویی جشنواره ملی رازی",
            score: 10
        },
        {
            text: "ماده 9: برگزیده جشنواره ملی پژوهش و فناوری دانشجویان علوم پزشکی کشور ",
            score: 8
        },
        {
            text: "ماده 9: برگزیده جشنواره های فن بازار سلامت و استارتاپ ویکند کشوری ",
            score: 5
        },
    ],

    /* المپیاد علمی */
    olampiad_elmi: [{
            text: "مدال آوری در المپیاد های علمی وزارت بهداشت — عضویت در استعداد درخشان",
        },
    ]
};



function generateSuggestionPackages(breakdown) {
    console.group("🔍 generateSuggestionPackages");

    const REQUIRED_SECTIONS = ["olampiad_elmi", "maghaleh", "ekhtera"];

    console.log("📌 مواد اجباری:", REQUIRED_SECTIONS);

    if (!breakdown || Object.keys(breakdown).length === 0) {
        console.warn("⚠️ breakdown خالی یا نادرست است");
        console.groupEnd();
        return [];
    }

    // امتیازهای هر ماده (برای وزن‌دهی پیشنهادات غیر اجباری)
    const sortedKeys = Object.entries(breakdown)
        .map(([key, sec]) => ({
            key,
            score: sec.finalSectionScore || 0
        }))
        .sort((a, b) => a.score - b.score);

    console.log("📊 sortedKeys:", sortedKeys);

    // ایجاد weighted list برای انتخاب تصادفی از مواد کم‌امتیازتر
    const weightedList = [];

    sortedKeys.forEach(item => {
        const weight = item.score === 0 ? 3 : item.score < 3 ? 2 : 1;
        for (let i = 0; i < weight; i++) {
            weightedList.push(item.key);
        }
    });

    console.log("⚖️ weightedList:", weightedList);


    const packages = [];
    const usedSuggestions = new Set();

    for (let p = 0; p < 3; p++) {
        const pack = [];
        console.group(`📦 ساخت پکیج شماره ${p + 1}`);

        // ---------------------------------------------------
        // 1) ابتدا یک پیشنهاد از مواد اجباری وارد بسته شود
        // ---------------------------------------------------
        const requiredKey = REQUIRED_SECTIONS[p % REQUIRED_SECTIONS.length]; // چرخه ۱→۴→۸→۹
        const requiredList = SUGGESTIONS[requiredKey];

        if (requiredList && requiredList.length > 0) {
            const requiredSuggestion =
                requiredList[Math.floor(Math.random() * requiredList.length)];

            pack.push({
                ...requiredSuggestion,
                section: requiredKey
            });

            usedSuggestions.add(requiredKey + "-" + requiredSuggestion.text);

            console.log(`✔ پیشنهاد اجباری اضافه شد از بخش: ${requiredKey}`);
        } else {
            console.warn(`⚠ هیچ پیشنهادی برای بخش اجباری ${requiredKey} تعریف نشده`);
        }

        // ---------------------------------------------------
        // 2) بقیه پیشنهادها از مواد با امتیاز کم‌تر انتخاب شوند
        // ---------------------------------------------------
        let safety = 0;
        while (pack.length < 3 && safety < 50) {
            safety++;

            const randKey = weightedList[Math.floor(Math.random() * weightedList.length)];
            const options = SUGGESTIONS[randKey];
            if (!options || options.length === 0) continue;

            const sug = options[Math.floor(Math.random() * options.length)];
            const sign = randKey + "-" + sug.text;

            if (!usedSuggestions.has(sign)) {
                usedSuggestions.add(sign);
                pack.push({
                    ...sug,
                    section: randKey
                });
            }
        }

        console.log("📦 پکیج نهایی:", pack);
        console.groupEnd();
        packages.push(pack);
    }

    console.log("🎁 بسته‌های نهایی:", packages);
    console.groupEnd();
    return packages;
}