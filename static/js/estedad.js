// ==========================================
// تعریف فرم‌ها
// ==========================================
const formConfigs = {
    maghaleh: {
        title: 'ماده -1 انتشار مقاله',
        itemLabel: 'مقاله',
        allowMultiple: true,
        disc: 'در این بخش اطلاعات مقالات علمی منتشر شده خود را وارد کنید.',
        fields: [{
                name: 'type',
                label: 'نوع مقاله',
                type: 'select',
                required: true,
                options: [{
                        value: 'wos',
                        label: 'Web of Science / PubMed / Medline'
                    },
                    {
                        value: 'scopus',
                        label: 'Scopus'
                    },
                    {
                        value: 'internal',
                        label: 'مجله علمی پژوهشی داخلی'
                    },
                ]
            },
            {
                name: 'impact_factor',
                label: 'Impact Factor مجله',
                type: 'number',
                required: false,
                tooltip: 'اگر مقاله شما در Web of Science نمایه شده است، مقدار Impact Factor را وارد کنید.',
                dependsOn: {
                    field: 'type',
                    value: ['wos']
                },
                placeholder: 'مثلاً 3',
                min: 0,
            },
            {
                name: 'authors_count',
                label: 'تعداد کل نویسندگان',
                type: 'select',
                required: true,
                options: [{
                        value: '1',
                        label: '۱ نفر'
                    },
                    {
                        value: '2',
                        label: '۲ نفر'
                    },
                    {
                        value: '3',
                        label: '۳ نفر'
                    },
                    {
                        value: '4',
                        label: '۴ نفر'
                    },
                    {
                        value: '5',
                        label: '۵ نفر'
                    },
                    {
                        value: '6',
                        label: '۶ نفر و بیشتر'
                    },
                ]
            },
            {
                name: 'position',
                label: 'جایگاه شما در میان نویسندگان',
                type: 'select',
                required: true,
                tooltip: 'نویسنده مسئول مشابه نویسنده اول در نظر گرفته می‌شود.',
                options: [{
                        value: 'first',
                        label: 'نویسنده اول'
                    },
                    {
                        value: 'corresponding',
                        label: 'نویسنده مسئول'
                    },
                    {
                        value: 'other',
                        label: 'سایر نویسندگان'
                    },
                ]
            },
            {
                name: 'is_thesis',
                label: 'آیا این مقاله حاصل پایان‌نامه شما است؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            {
                name: 'affiliation_type',
                label: 'افیلیشن (وابستگی سازمانی) شما در این مقاله چیست؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'none',
                        label: 'افیلیشن کمیته ندارم'
                    },
                    {
                        value: 'committee',
                        label: 'افیلیشن کمیته تحقیقات دانشجویی دانشگاه'
                    },
                    {
                        value: 'committee_student_pi',
                        label: 'افیلیشن کمیته + مجری دانشجویی طرح'
                    },
                ]
            },
        ],

        // ─── بلاک امتیازدهی ───────────────────────────────────────────
        scoring: {
            maxScore: null, // بدون سقف برای این ماده

            /**
             * محاسبه امتیاز یک مقاله
             * فرمول کلی:
             *   score = (baseScore + IF×2) × authorShareRatio × maxMultiplier
             *
             * جدول سهم نویسندگان:
             *   n=1 → اول:100%
             *   n=2 → اول:60%  , سایر:90%
             *   n=3 → اول:50%  , سایر:80%
             *   n=4 → اول:40%  , سایر:70%
             *   n=5 → اول:30%  , سایر:60%
             *   n≥6 → اول:50%  , سایر:25%
             */
            calculate(fields) {
                // ── جدول توزیع امتیاز (تبصره 2) ──
                const AUTHOR_SHARE = {
                    1: {
                        first: 1.00,
                        other: 0.00
                    },
                    2: {
                        first: 0.90,
                        other: 0.60
                    },
                    3: {
                        first: 0.80,
                        other: 0.50
                    },
                    4: {
                        first: 0.70,
                        other: 0.40
                    },
                    5: {
                        first: 0.60,
                        other: 0.30
                    },
                    6: {
                        first: 0.50,
                        other: 0.25
                    }, // 6 نفر و بیشتر
                };

                // ── 1) امتیاز پایه ──
                const type = fields.type;
                const impactFactor = parseFloat(fields.impact_factor) || 0;
                let baseScore = 0;

                if (type === 'wos') {
                    // 25 + (IF × 2)
                    baseScore = 25 + impactFactor * 2;
                } else if (type === 'scopus') {
                    baseScore = 20;
                } else if (type === 'internal') {
                    baseScore = 10;
                }

                // ── 2) ضریب جایگاه نویسنده ──
                const authorsCount = parseInt(fields.authors_count) || 1;
                const position = fields.position; // 'first' | 'corresponding' | 'other'
                const tableKey = authorsCount >= 6 ? 6 : authorsCount;
                const shareTable = AUTHOR_SHARE[tableKey];

                // تبصره 3: نویسنده مسئول = امتیاز نفر اول
                // تبصره 10: مقالات پرنویسنده (>100) فقط اول یا مسئول
                let authorRatio = 0;
                if (position === 'first' || position === 'corresponding') {
                    authorRatio = shareTable.first;
                } else {
                    // اگر تعداد نویسندگان بیشتر از 100 است و نویسنده اول/مسئول نیست → 0
                    authorRatio = authorsCount > 100 ? 0 : shareTable.other;
                }

                let score = baseScore * authorRatio;

                // ── 3) ضرایب تبصره‌های 5، 6، 7 (تبصره 9: بیشترین اعمال می‌شود) ──
                const isThesis = fields.is_thesis === 'yes';
                const affiliationType = fields.affiliation_type;

                const multipliers = [];
                if (isThesis) multipliers.push(1.2); // تبصره 5
                if (affiliationType === 'committee') multipliers.push(1.5); // تبصره 6
                if (affiliationType === 'committee_student_pi') multipliers.push(2.0); // تبصره 7

                const maxMultiplier = multipliers.length > 0 ? Math.max(...multipliers) : 1;
                score = score * maxMultiplier;

                return {
                    baseScore: parseFloat(baseScore.toFixed(2)),
                    authorRatio,
                    multiplierApplied: maxMultiplier,
                    finalScore: parseFloat(score.toFixed(2)),
                    breakdown: `امتیاز پایه: ${baseScore.toFixed(2)} × سهم نویسنده: ${(authorRatio * 100).toFixed(0)}% × ضریب: ${maxMultiplier}`
                };
            }
        }
    },


    // ──────────────────────────────────────────────────────────────────
    payannameh: {
        title: 'ماده -2 پايان نامه',
        itemLabel: 'پایان‌نامه',
        allowMultiple: false,
        disc: 'منظور از پایان نامه، طرح تحقیقاتی پایان نامه مصوب دارای کد اخلاق دانشجو در آخرین مقطع تحصیلی می باشد.',
        fields: [{
            name: 'is_defended',
            label: 'آیا از پایان نامه خود با موفقیت دفاع کرده‌اید؟',
            type: 'select',
            required: true,
            options: [{
                    value: 'yes',
                    label: 'بله'
                },
                {
                    value: 'no',
                    label: 'خیر'
                },
            ]
        }],

        scoring: {
            maxScore: 5,

            /**
             * هر نوع پایان‌نامه = ۵ امتیاز ثابت
             */
            calculate(fields) {
                const defended = fields.is_defended === 'yes';
                return {
                    finalScore: defended ? 5 : 0,
                    breakdown: defended ? 'دفاع موفق از پایان‌نامه: ۵ امتیاز' : 'بدون امتیاز'
                };
            }
        }
    },


    // ──────────────────────────────────────────────────────────────────
    maghale_congress: {
        title: 'ماده -3 ارائه خلاصه مقالات در کنگره‌ها و سمینارها',
        itemLabel: 'خلاصه مقاله',
        allowMultiple: true,
        disc: 'کنگره یا سمینار باید دارای فراخوان و کتابچه خلاصه مقالات باشد و نام دانشجو می بایست جز نویسندگان خلاصه مقاله باشد.',
        fields: [{
                name: 'presentation_type',
                label: 'نوع ارائه شما در همایش چه بوده است؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'lecture',
                        label: 'سخنرانی'
                    },
                    {
                        value: 'poster',
                        label: 'پوستر'
                    },
                    {
                        value: 'isi_abstract',
                        label: 'Abstract Meeting نمایه شده در ISI'
                    },
                    {
                        value: 'isi_proceeding',
                        label: 'Proceeding نمایه شده در ISI'
                    },
                ]
            },
            {
                name: 'event_level',
                label: 'سطح همایش چیست؟',
                type: 'select',
                required: false,
                dependsOn: {
                    field: 'presentation_type',
                    value: ['lecture', 'poster']
                },
                options: [{
                        value: 'internal',
                        label: 'داخلی'
                    },
                    {
                        value: 'external',
                        label: 'خارجی'
                    },
                ]
            },
            {
                name: 'is_top_article',
                label: 'آیا این به عنوان «مقاله برتر» انتخاب شده است؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            /* {
                            name: 'top_article_level',
                            label: 'نوع همایش برای مقاله برتر چیست؟',
                            type: 'select',
                            required: false,
                            dependsOn: {
                                field: 'is_top_article',
                                value: ['yes']
                            },
                            options: [{
                                    value: 'internal',
                                    label: 'داخلی'
                                },
                                {
                                    value: 'external',
                                    label: 'خارجی'
                                },
                            ]
                        }, */
            {
                name: 'is_national_student_congress',
                label: 'آیا این ارائه در «کنگره سراسری دانشجویی کمیته تحقیقات و فناوری کشور» ارائه شده است؟',
                tooltip: 'این کنگره ها توسط کمیته تحقیقات و فناوری دانشگاه های علوم پزشکی برگزار میشود.',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'event_level',
                    value: ['internal']
                },
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
        ],

        scoring: {
            maxScore: 15, // سقف کل ماده 3

            /**
             * امتیاز پایه بر اساس نوع ارائه:
             *   سخنرانی داخلی: 1 | خارجی: 3
             *   پوستر داخلی: 0.5 | خارجی: 1
             *   ISI Abstract: 2
             *   ISI Proceeding: 3
             *
             * امتیاز اضافه مقاله برتر (تبصره 2):
             *   داخلی: +2 | خارجی: +3
             *
             * کنگره سراسری دانشجویی (تبصره 4): × 1.2
             */
            calculate(fields) {
                const type = fields.presentation_type;
                const level = fields.event_level; // 'internal' | 'external'
                const isTop = fields.is_top_article === 'yes';
                const topLevel = fields.top_article_level; // 'internal' | 'external'
                const isNational = fields.is_national_student_congress === 'yes';

                // ── 1) امتیاز پایه (تبصره 1: فقط یک مورد) ──
                let baseScore = 0;
                if (type === 'isi_proceeding') baseScore = 3;
                else if (type === 'isi_abstract') baseScore = 2;
                else if (type === 'lecture') baseScore = level === 'external' ? 3 : 1;
                else if (type === 'poster') baseScore = level === 'external' ? 1 : 0.5;

                // ── 2) امتیاز اضافه مقاله برتر (تبصره 2) ──
                let bonusScore = 0;
                if (isTop) {
                    bonusScore = topLevel === 'external' ? 3 : 3;
                }

                // ── 3) ضریب کنگره سراسری دانشجویی (تبصره 4) ──
                let total = (baseScore + bonusScore) * (isNational ? 1.2 : 1);

                return {
                    baseScore,
                    bonusScore,
                    nationalMultiplier: isNational ? 1.2 : 1,
                    finalScore: parseFloat(total.toFixed(2)),
                    breakdown: `پایه: ${baseScore} + برتر: ${bonusScore} × ضریب سراسری: ${isNational ? '1.2' : '1'}`
                };
            }
        }
    },


    // ──────────────────────────────────────────────────────────────────
    davari: {
        title: 'ماده -4 داوري طرح هاي تحقيقاتي، خلاصه مقالات كنگره ها و مقالات ژورنال هاي معتبر',
        itemLabel: 'داوری',
        allowMultiple: false,
        disc: 'داوري طرح هاي تحقيقاتي، خلاصه مقالات كنگره ها و مقالات ژورنال هاي معتبر می بایست دارای گواهی داوری معتبر باشد که به تایید معاونت پژوهش و فناوری دانشگاه مربوطه رسیده باشد.',
        fields: [{
                name: 'abstract_review_count',
                label: 'چند مورد داوری ابستراکت در کنگره‌های سالیانه انجام داده‌اید؟',
                type: 'number',
                required: true,
                placeholder: 'مثلاً 3',
                min: 0,
            },
            {
                name: 'proposal_review_count',
                label: 'چند مورد داوری طرح تحقیقاتی انجام داده‌اید؟',
                type: 'number',
                required: true,
                placeholder: 'مثلاً 3',
                min: 0,
            },
            {
                name: 'journal_review_count',
                label: 'چند مورد داوری مقاله در ژورنال‌های معتبر (داخلی یا خارجی) انجام داده‌اید؟',
                type: 'number',
                required: true,
                placeholder: 'مثلاً 3',
                min: 0,
            },
        ],

        scoring: {
            maxScore: 5,

            /**
             *   داوری ابستراکت کنگره:   هر مورد × 0.1
             *   داوری طرح تحقیقاتی:     هر مورد × 0.2
             *   داوری مقاله ژورنال:      هر مورد × 0.5
             *   سقف کل: 5 امتیاز
             */
            calculate(fields) {
                const abstracts = parseInt(fields.abstract_review_count) || 0;
                const proposals = parseInt(fields.proposal_review_count) || 0;
                const journals = parseInt(fields.journal_review_count) || 0;

                const fromAbstracts = abstracts * 0.1;
                const fromProposals = proposals * 0.2;
                const fromJournals = journals * 0.5;

                const total = fromAbstracts + fromProposals + fromJournals;

                return {
                    breakdown: {
                        abstracts: parseFloat(fromAbstracts.toFixed(2)),
                        proposals: parseFloat(fromProposals.toFixed(2)),
                        journals: parseFloat(fromJournals.toFixed(2)),
                    },
                    rawScore: parseFloat(total.toFixed(2)),
                    finalScore: parseFloat(Math.min(total, 5).toFixed(2)),
                    capped: total > 5,
                };
            }
        }
    },


    // ──────────────────────────────────────────────────────────────────
    ketab: {
        title: 'ماده -5 انتشار کتاب',
        itemLabel: 'کتاب',
        allowMultiple: true,
        disc: 'منظور از انتشار کتاب، تالیف، ترجمه و گردآوری کتابی است که نام دانشجو جز نویسندگان آن بوده و به تایید معاونت پژوهشی یا آموزشی دانشگاه رسیده باشد.',
        fields: [{
                name: 'book_category',
                label: 'نوع اثر شما چیست؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'full_book',
                        label: 'کتاب کامل'
                    },
                    {
                        value: 'book_chapter',
                        label: 'فصل کتاب (Book Chapter)'
                    },
                ]
            },
            // ─── فیلدهای مخصوص کتاب کامل ───
            {
                name: 'full_book_role',
                label: 'نقش شما در این کتاب چه بوده است؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'book_category',
                    value: ['full_book']
                },
                options: [{
                        value: 'authoring',
                        label: 'تألیف کتاب'
                    },
                    {
                        value: 'translation',
                        label: 'ترجمه کتاب'
                    },
                    {
                        value: 'compilation',
                        label: 'گردآوری کتاب'
                    },
                ]
            },
            {
                name: 'full_book_language',
                label: 'زبان کتاب چیست؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'full_book_role',
                    value: ['authoring', 'compilation']
                },
                options: [{
                        value: 'persian',
                        label: 'فارسی'
                    },
                    {
                        value: 'foreign',
                        label: 'زبان خارجی'
                    },
                ]
            },
            {
                name: 'full_book_approved',
                label: 'آیا این کتاب توسط شورای انتشارات دانشگاه تأیید شده است؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'book_category',
                    value: ['full_book']
                },
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            {
                name: 'full_book_isbn',
                label: 'آیا کتاب شابک (ISBN) دارد؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'book_category',
                    value: ['full_book']
                },
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            // ─── فیلدهای مخصوص فصل کتاب ───
            {
                name: 'chapter_language',
                label: 'زبان فصل کتاب چیست؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'book_category',
                    value: ['book_chapter']
                },
                options: [{
                        value: 'persian',
                        label: 'فارسی'
                    },
                    {
                        value: 'foreign',
                        label: 'زبان خارجی'
                    },
                ]
            },
            {
                name: 'chapter_international_publisher',
                label: 'آیا این فصل کتاب توسط ناشر بین‌المللی معتبر منتشر شده است؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'book_category',
                    value: ['book_chapter']
                },
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            {
                name: 'chapter_indexed',
                label: 'آیا این فصل کتاب در پایگاه‌های علمی نمایه شده است؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'book_category',
                    value: ['book_chapter']
                },
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            {
                name: 'chapter_count',
                label: 'چند فصل از این کتاب را نوشته‌اید؟',
                type: 'number',
                required: true,
                dependsOn: {
                    field: 'book_category',
                    value: ['book_chapter']
                },
                placeholder: 'مثلاً 1',
                min: 1,
            },
        ],

        scoring: {
            maxScore: null,

            /**
             * کتاب کامل:
             *   تألیف فارسی: 20 | خارجی: 20 × 1.3 = 26
             *   ترجمه:       15 (فقط فارسی)
             *   گردآوری فارسی: 10 | خارجی: 10 × 1.3 = 13
             *
             * فصل کتاب خارجی (تبصره 3 و 4):
             *   اگر نمایه‌سازی شده → طبق ماده 1 محاسبه شود (flag برمی‌گرداند)
             *   1 فصل  → معادل ترجمه دانشگاهی: 15
             *   >1 فصل → معادل تألیف: 20
             *
             * شرط اعتبار (تبصره 1): شابک + تأیید شورا الزامی است
             */
            calculate(fields) {
                const category = fields.book_category;

                if (category === 'full_book') {
                    const approved = fields.full_book_approved === 'yes';
                    const hasISBN = fields.full_book_isbn === 'yes';

                    // شرط اعتبار (تبصره 1)
                    if (!approved || !hasISBN) {
                        return {
                            finalScore: 0,
                            breakdown: 'کتاب بدون تأیید شورای انتشارات یا فاقد شابک امتیاز ندارد.',
                            invalid: true
                        };
                    }

                    const role = fields.full_book_role;
                    const language = fields.full_book_language;
                    const isForeign = language === 'foreign';

                    let score = 0;
                    if (role === 'authoring') score = isForeign ? 20 * 1.3 : 20;
                    else if (role === 'translation') score = 15; // ترجمه فقط فارسی
                    else if (role === 'compilation') score = isForeign ? 10 * 1.3 : 10;

                    return {
                        finalScore: parseFloat(score.toFixed(2)),
                        breakdown: `${role} ${isForeign ? 'خارجی (×1.3)' : 'فارسی'}: ${score.toFixed(2)} امتیاز`
                    };
                }

                if (category === 'book_chapter') {
                    const language = fields.chapter_language;
                    const intlPublisher = fields.chapter_international_publisher === 'yes';
                    const isIndexed = fields.chapter_indexed === 'yes';
                    const chapterCount = parseInt(fields.chapter_count) || 1;

                    if (language === 'persian' || !intlPublisher) {
                        return {
                            finalScore: 0,
                            breakdown: 'فصل کتاب فارسی یا بدون ناشر بین‌المللی امتیاز مستقل ندارد.',
                            invalid: true
                        };
                    }

                    // تبصره 4: فصل کتاب خارجی نمایه‌شده → طبق ماده 1
                    if (isIndexed) {
                        return {
                            finalScore: 0,
                            requiresArticleCalculation: true,
                            breakdown: 'این فصل کتاب نمایه‌شده خارجی است. لطفاً طبق ماده ۱ (مقالات) امتیازدهی شود.'
                        };
                    }

                    // تبصره 3: فصل کتاب خارجی نمایه‌نشده
                    const score = chapterCount > 1 ? 20 : 15;
                    return {
                        finalScore: score,
                        breakdown: chapterCount > 1 ?
                            `${chapterCount} فصل از یک کتاب (بیش از یک فصل = معادل تألیف): 20 امتیاز` : '۱ فصل کتاب خارجی ناشر بین‌المللی (معادل ترجمه): 15 امتیاز'
                    };
                }

                return {
                    finalScore: 0,
                    breakdown: 'نامشخص'
                };
            }
        }
    },


    // ──────────────────────────────────────────────────────────────────
    tahghighat: {
        title: 'ماده -6 مجری یا همکاری در اجرای طرح‌های تحقیقاتی',
        itemLabel: 'طرح تحقیقاتی',
        allowMultiple: true,
        disc: 'نام دانشجو باید در جدول همکاران اصلی یا مجری طرح مصوب شورای پژوهشی دانشگاه آورده شود و طرح تحقیقاتی دارای کد اخلاق بوده و می بایست تاییدیه پایان طرح را داشته باشد.',
        fields: [{
                name: 'role',
                label: 'نقش شما در این طرح تحقیقاتی چه بوده است؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'pi',
                        label: 'مجری طرح'
                    },
                    {
                        value: 'collaborator',
                        label: 'همکار طرح'
                    },
                ]
            },
            {
                name: 'project_type',
                label: 'نوع طرح تحقیقاتی چیست؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'single',
                        label: 'طرح عادی (تک مرکز)'
                    },
                    {
                        value: 'multi_domestic',
                        label: 'طرح چندمرکزی داخلی'
                    },
                    {
                        value: 'multi_foreign',
                        label: 'طرح چندمرکزی خارجی'
                    },
                ]
            },
            {
                name: 'is_innovation',
                label: 'آیا این طرح در حوزه نوآوری و فناوری بوده است؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            {
                name: 'is_student_committee_approved',
                label: 'آیا این طرح مصوب کمیته تحقیقات و فناوری دانشجویی بوده است؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
        ],

        scoring: {
            maxScore: 30,

            /**
             * امتیاز پایه:
             *   مجری:  5
             *   همکار: 3
             *
             * ضرایب (تبصره 1: بیشترین اعمال می‌شود):
             *   چندمرکزی داخلی: × 1.2
             *   چندمرکزی خارجی: × 1.3
             *   نوآوری/فناوری:  × 1.4
             *   مصوب کمیته:     × 1.5
             *
             * سقف: 30 امتیاز
             */
            calculate(fields) {
                const role = fields.role;
                const projectType = fields.project_type;
                const isInno = fields.is_innovation === 'yes';
                const isCommittee = fields.is_student_committee_approved === 'yes';

                const baseScore = role === 'pi' ? 5 : 3;

                const multipliers = [];
                if (projectType === 'multi_domestic') multipliers.push(1.2);
                if (projectType === 'multi_foreign') multipliers.push(1.3);
                if (isInno) multipliers.push(1.4);
                if (isCommittee) multipliers.push(1.5);

                const maxMultiplier = multipliers.length > 0 ? Math.max(...multipliers) : 1;
                const raw = baseScore * maxMultiplier;

                return {
                    baseScore,
                    multiplierApplied: maxMultiplier,
                    rawScore: parseFloat(raw.toFixed(2)),
                    finalScore: parseFloat(Math.min(raw, 30).toFixed(2)),
                    breakdown: `پایه (${role === 'pi' ? 'مجری' : 'همکار'}): ${baseScore} × ${maxMultiplier}`
                };
            }
        }
    },


    // ──────────────────────────────────────────────────────────────────
    faulit: {
        title: 'ماده -7 فعالیت در کمیته تحقیقات و فناوری دانشجویی',
        itemLabel: 'فعالیت',
        allowMultiple: true,
        disc: 'هر گونه فعالیت در کمیته تحقیقات و فناوری دانشگاه که دارای گواهی مورد تایید از سرپرست کمیته تحقیقات و فناوری باشد.',
        fields: [{
                name: 'activity_type',
                label: 'نوع فعالیت شما در کمیته تحقیقات و فناوری دانشجویی چیست؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'secretary',
                        label: 'دبیر کمیته تحقیقات دانشجویی'
                    },
                    {
                        value: 'council_member',
                        label: 'عضویت در شورای مرکزی کمیته'
                    },
                    {
                        value: 'executive',
                        label: 'همکاری یا مسئولیت اجرایی در رویدادهای علمی'
                    },
                    {
                        value: 'teaching',
                        label: 'تدریس در کارگاه‌های پژوهش و فناوری'
                    },
                ]
            },
            // ─── دبیر ───
            {
                name: 'secretary_years',
                label: 'چند سال به عنوان دبیر کمیته تحقیقات دانشجویی فعالیت داشته‌اید؟',
                type: 'number',
                required: true,
                dependsOn: {
                    field: 'activity_type',
                    value: ['secretary']
                },
                placeholder: 'مثلاً 2',
                min: 0,
                max: 100,
            },
            // ─── عضو شورا ───
            {
                name: 'council_years',
                label: 'چند سال عضو شورای مرکزی کمیته تحقیقات دانشجویی بوده‌اید؟',
                type: 'number',
                required: true,
                dependsOn: {
                    field: 'activity_type',
                    value: ['council_member']
                },
                placeholder: 'مثلاً 2',
                min: 0,
            },
            // ─── مسئولیت اجرایی ───
            {
                name: 'event_level',
                label: 'سطح رویداد چیست؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'activity_type',
                    value: ['executive']
                },
                options: [{
                        value: 'university',
                        label: 'دانشگاهی'
                    },
                    {
                        value: 'regional',
                        label: 'کلان منطقه‌ای'
                    },
                    {
                        value: 'national',
                        label: 'کشوری'
                    },
                ]
            },
            {
                name: 'event_count',
                label: 'تعداد دفعات همکاری یا مسئولیت اجرایی در رویداد',
                type: 'number',
                required: true,
                dependsOn: {
                    field: 'activity_type',
                    value: ['executive']
                },
                placeholder: 'مثلاً 2',
                min: 1,
            },
            // ─── تدریس ───
            {
                name: 'teaching_hours',
                label: 'چند ساعت در کارگاه‌های برگزار شده توسط کمیته تدریس کرده‌اید؟',
                type: 'number',
                required: true,
                dependsOn: {
                    field: 'activity_type',
                    value: ['teaching']
                },
                placeholder: 'مثلاً 5',
                min: 0,
            },
        ],

        scoring: {
            maxScore: 25,

            /**
             *   دبیر:       سال × 6
             *   عضو شورا:   سال × 3
             *   اجرایی:     تعداد × امتیاز_سطح (دانشگاهی:1، منطقه ای:2، کشوری:3)
             *   تدریس:      ساعت × 0.2
             *
             *   سقف کل: 25 امتیاز
             */
            calculate(fields) {
                const type = fields.activity_type;
                let score = 0;
                let breakdown = '';

                if (type === 'secretary') {
                    const years = parseFloat(fields.secretary_years) || 0;
                    score = years * 6;
                    breakdown = `دبیری: ${years} سال × 6 = ${score}`;
                } else if (type === 'council_member') {
                    const years = parseFloat(fields.council_years) || 0;
                    score = years * 3;
                    breakdown = `عضو شورا: ${years} سال × 3 = ${score}`;
                } else if (type === 'executive') {
                    const levelScores = {
                        university: 1,
                        regional: 2,
                        national: 3
                    };
                    const baseScore = levelScores[fields.event_level] || 1;
                    const count = parseFloat(fields.event_count) || 1;

                    score = baseScore * count;
                    const levelLabel = fields.event_level === 'university' ? 'دانشگاهی' :
                        fields.event_level === 'regional' ? 'کلان منطقه‌ای' : 'کشوری';

                    breakdown = `رویداد ${levelLabel}: ${count} مورد × ${baseScore} امتیاز = ${score}`;
                } else if (type === 'teaching') {
                    const hours = parseFloat(fields.teaching_hours) || 0;
                    score = hours * 0.2;
                    breakdown = `تدریس: ${hours} ساعت × 0.2 = ${score}`;
                }

                return {
                    rawScore: parseFloat(score.toFixed(2)),
                    finalScore: parseFloat(Math.min(score, 25).toFixed(2)),
                    breakdown
                };
            }
        }
    },



    // ──────────────────────────────────────────────────────────────────
    ekhtera: {
        title: 'ماده -8 الف - اختراع، اکتشاف',
        itemLabel: 'اختراع',
        allowMultiple: true,
        disc: 'اختراعاتی که دارای گواهی ثبت اختراع داخلی یا خارجی بوده و همچنین به تایید کمیته ابداعات و اختراعات دانشگاه رسیده و توسط آن کمیته امتیاز دهی شده باشد',
        fields: [{
                name: 'registration_type',
                label: 'وضعیت ثبت اختراع شما چیست؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'legal',
                        label: 'ثبت حقوقی در اداره ثبت اسناد و مرکز مالکیت‌های معنوی'
                    },
                    {
                        value: 'authority',
                        label: 'ثبت در مراجع ذیصلاح (سازمان پژوهش‌های علمی و صنعتی / بنیاد ملی نخبگان / وزارت بهداشت)'
                    },
                    {
                        value: 'foreign',
                        label: 'ثبت اختراع در خارج از کشور'
                    },
                ]
            },
            {
                name: 'participation_share',
                label: 'سهم مشارکت شما در این اختراع چند درصد است؟',
                type: 'number',
                required: true,
                placeholder: 'مثلاً 50',
                min: 1,
                max: 100,
                tooltip: 'عددی بین ۱ تا ۱۰۰ وارد کنید.'
            },
            {
                name: 'has_both_registrations',
                label: 'آیا این اختراع هم در داخل و هم در خارج از کشور ثبت شده است؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'registration_type',
                    value: ['legal', 'authority']
                },
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
        ],

        scoring: {
            maxScore: null,

            /**
             * امتیاز = ضریب_نوع × (سهم_مشارکت / 100)
             *
             *   ثبت حقوقی داخلی:        10 × سهم
             *   مراجع ذیصلاح:           20 × سهم
             *   خارج از کشور:           30 × سهم
             *
             * تبصره 2: ثبت همزمان داخلی+خارجی → فقط یک تأییدیه (بالاترین)
             */
            calculate(fields) {
                let typeMultiplier = {
                    legal: 10,
                    authority: 20,
                    foreign: 30,
                } [fields.registration_type] || 0;

                // اگر ثبت همزمان داخلی و خارجی وجود داشت،
                // امتیاز بالاتر یعنی 30 لحاظ شود
                if (fields.has_both_registrations === 'yes') {
                    typeMultiplier = 30;
                }
                const impactFactor = parseFloat(fields.impact_factor) || 0;
                const share = Math.min(
                    Math.max(parseFloat(fields.participation_share) || 0, 0),
                    100
                );

                const shareRatio = share / 100;
                const score = typeMultiplier * shareRatio;

                return {
                    typeMultiplier,
                    participationShare: share,
                    finalScore: parseFloat(score.toFixed(2)),
                    breakdown: `${typeMultiplier} × ${share}% = ${score.toFixed(2)}`,
                    note: fields.has_both_registrations === 'yes' ?
                        'ثبت همزمان داخلی و خارجی: فقط تأییدیه با امتیاز بالاتر محاسبه می‌شود.' : ''
                };
            }

        }
    },


    // ──────────────────────────────────────────────────────────────────
    noavari: {
        title: 'ماده -8 ب - کارآفرینی و فناوری',
        itemLabel: 'کارآفرینی',
        allowMultiple: true,
        disc: 'فعالیت های کارآفرینانه مانند ثبت شرکت دانش بنیان و یا تجاری سازی محصول و برپایی غرفه در نمایشگاه که دارای مستندات لازم باشد',
        fields: [{
                name: 'entrepreneurship_type',
                label: 'نوع فعالیت شما چیست؟',
                type: 'select',
                required: true,
                options: [{
                        value: 'incubator',
                        label: 'استقرار در مرکز رشد یا فناوری سلامت'
                    },
                    {
                        value: 'knowledge',
                        label: 'تأسیس شرکت دانش‌بنیان'
                    },
                    {
                        value: 'commercial',
                        label: 'تجاری‌سازی محصول'
                    },
                    {
                        value: 'exhibition',
                        label: 'حضور در نمایشگاه‌های فناوری'
                    },
                ]
            },
            // ─── استقرار در مرکز رشد ───
            {
                name: 'incubator_confirmed',
                label: 'آیا شرکت/تیم شما در مرکز رشد یا فناوری سلامت دانشگاه مستقر شده است؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'entrepreneurship_type',
                    value: ['incubator']
                },
                tooltip: 'مستندات: تأییدیه مرکز رشد / تصویر قرارداد استقرار / اساسنامه شرکت',
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            // ─── شرکت دانش‌بنیان ───
            {
                name: 'knowledge_is_founder',
                label: 'آیا شما مدیر یا مؤسس شرکت دانش‌بنیان هستید؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'entrepreneurship_type',
                    value: ['knowledge']
                },
                tooltip: 'مستندات: مجوز معاونت علمی و فناوری / تأییدیه پارک علم و فناوری / اساسنامه شرکت',
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            // ─── تجاری‌سازی ───
            {
                name: 'commercial_has_contract',
                label: 'آیا محصول شما قرارداد فروش یا حداقل یک فاکتور فروش دارد؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'entrepreneurship_type',
                    value: ['commercial']
                },
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
            // ─── نمایشگاه ───
            {
                name: 'exhibition_has_booth',
                label: 'آیا شرکت شما در نمایشگاه‌های فناوری داخلی یا خارجی غرفه داشته است؟',
                type: 'select',
                required: true,
                dependsOn: {
                    field: 'entrepreneurship_type',
                    value: ['exhibition']
                },
                tooltip: 'مستندات: گواهی یا تقدیرنامه از نمایشگاه / تأییدیه دفتر توسعه فناوری سلامت',
                options: [{
                        value: 'yes',
                        label: 'بله'
                    },
                    {
                        value: 'no',
                        label: 'خیر'
                    },
                ]
            },
        ],

        scoring: {
            maxScore: null,

            /**
             *   استقرار مرکز رشد:        10
             *   شرکت دانش‌بنیان:         20
             *   تجاری‌سازی:              15
             *   نمایشگاه:                5
             */
            calculate(fields) {
                const type = fields.entrepreneurship_type;

                const scoreMap = {
                    incubator: {
                        field: 'incubator_confirmed',
                        score: 10
                    },
                    knowledge: {
                        field: 'knowledge_is_founder',
                        score: 20
                    },
                    commercial: {
                        field: 'commercial_has_contract',
                        score: 15
                    },
                    exhibition: {
                        field: 'exhibition_has_booth',
                        score: 5
                    },
                };

                const config = scoreMap[type];
                const isConfirmed = config && fields[config.field] === 'yes';
                const finalScore = isConfirmed ? config.score : 0;

                return {
                    finalScore,
                    breakdown: isConfirmed ?
                        `${type}: ${finalScore} امتیاز` : 'شرایط احراز نشده است.'
                };
            }
        }
    },


    // ──────────────────────────────────────────────────────────────────
    jashnvare: {
        title: 'ماده -9 برگزیدگان جشنواره‌های مورد تأیید کمیته تحقیقات و فناوری دانشجویی',
        itemLabel: 'جشنواره',
        allowMultiple: true,
        disc: 'جشنواره های مورد تایید کمیته تحقیقات و فناوری که دارای گواهی معتبر از سمت برگزار کننده باشد.',
        fields: [{
                name: 'festival_type',
                label: 'در کدام جشنواره به عنوان برگزیده انتخاب شده‌اید؟',
                type: 'select',
                required: true,
                tooltip: 'مستندات مورد نیاز: تصویر گواهی رسمی کسب رتبه از دبیرخانه جشنواره.',
                options: [{
                        value: 'razi',
                        label: 'برگزیده بخش دانشجویی جشنواره ملی تحقیقات و فناوری رازی'
                    },
                    {
                        value: 'national',
                        label: 'برگزیده جشنواره ملی پژوهش و فناوری دانشجویان دانشگاه‌های علوم پزشکی (جشنواره سالیانه کمیته‌ها)'
                    },
                    {
                        value: 'tech_market',
                        label: 'برگزیده جشنواره‌های فن‌بازار ملی سلامت، استارتاپ‌ویکند یا سایر رویدادهای وزارتخانه'
                    },
                ]
            },
            {
                name: 'festival_number',
                /*  برای این قسمت کد محاسبه نمره قرار نگرفته شده */
                label: 'چندبار در جشنواره مورد نظر برگزیده شده اید؟',
                type: 'number',
                required: true,
                placeholder: 'مثلاً 2',
                max: 10,
                min: 0,
            },
        ],

        scoring: {
            maxScore: 10,

            /**
             *   رازی:           10
             *   ملی دانشجویی:    8
             *   فن‌بازار / استارتاپ:  5 (ولی سقف 10)
             */
            calculate(fields) {

                const scoreMap = {
                    razi: {
                        score: 10,
                        max: 10
                    },
                    national: {
                        score: 8,
                        max: 8
                    },
                    tech_market: {
                        score: 5,
                        max: 10
                    },
                };

                const festival_number = parseFloat(fields.festival_number) || 0;

                const selected = scoreMap[fields.festival_type] || {
                    score: 0,
                    max: 10
                };

                // ضرب تعداد در امتیاز هر جشنواره
                const rawScore = selected.score * festival_number;

                // اعمال سقف مجاز
                const finalScore = Math.min(rawScore, selected.max);

                return {
                    rawScore,
                    finalScore: parseFloat(Math.min(score, 10).toFixed(2)),
                    breakdown: `جشنواره ${fields.festival_type}: ${finalScore} امتیاز`
                };
            }

        }

    },
};