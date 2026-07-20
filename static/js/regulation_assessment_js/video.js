// ==========================================
// ذخیره‌سازی اطلاعات کاربر
// ==========================================


function logUserData(action) {
    console.log(formData.firstName);
    console.log(formData.lastName);
    console.log(formData.phone);
    console.log(formData.email);
    console.group(`📊 لاگ اطلاعات کاربر - ${action}`);
    console.log("🎯 امتیاز کل:", userData.totalScore);
    console.log("📂 جزئیات امتیازات:", userData.breakdown);

    console.log("⏰ زمان:", userData.timestamp);
    console.groupEnd();
}


// ==========================================
// بانک اطلاعات ویدیوها
// ==========================================
const VIDEO_DATABASE = {
    olampiad_elmi: [{
            id: 'ola_001',
            title: 'المپیاد کارآفرینی دوره 18',
            category: 'olampiad_elmi',
            shortDesc: 'دوره آموزش و منتورینگ المپیاد کارآفرینی',
            longDesc: 'دوره هجدهم المپیاد کارآفرینی، فرصتی است برای تجربه‌ی واقعی کار تیمی، حل مسئله و نوآوری در فضای علوم پزشکی. \n در این مسیر، شرکت‌کنندگان هم‌زمان با آموزش مفاهیم کلیدی نوآوری، بیزنس‌مدل و طراحی راه‌حل، از منتورینگ شخصی متناسب با پروژه خود بهره‌مند می‌شوند. تمرکز اصلی دوره، انتقال مهارت‌هایی است که مستقیماً در عمل به کار می‌آید – از ایده‌پردازی تا ارائه نهایی.',
            stars: 5,
            duration: '30 ساعت',
            mainPrice: '1,875,000',
            discountPrice: '1,680,000',
            percentage: '10',
            instructor: 'جمعی از مدال آوران',
            thumbnail: '/media/image_card/IMG_20260506_215201.jpg',
            videoLink: 'https://example.com',
            active: true
        },
        {
            id: 'ola_002',
            title: 'المپیاد هنر و رسانه دوره 18',
            category: 'olampiad_elmi',
            shortDesc: 'دوره آموزش و منتورینگ المپیاد هنر و رسانه',
            longDesc: 'دوره آموزش و منتورینگ المپیاد هنر و رسانه در المپیاد علمی دانشجویی علوم پزشکی، فرصتی برای آشنایی با نقش هنر و رسانه در آموزش سلامت، فرهنگ‌سازی و انتقال مؤثر پیام‌های حوزه پزشکی است. در این دوره شرکت‌کنندگان با مفاهیم تولید محتوای خلاقانه، روایت‌سازی در سلامت و طراحی پیام‌های اثرگذار آشنا می‌شوند و در کنار آموزش، با همراهی منتورها ایده‌های خود را توسعه می‌دهند.',
            stars: 5,
            duration: '25 ساعت',
            mainPrice: '1,850,000',
            discountPrice: '1,660,000',
            percentage: '10',
            instructor: 'جمعی از مدال آوران',
            thumbnail: '/media/image_card/IMG_20260506_215206.jpg',
            videoLink: 'https://example.com',
            active: true
        },
        {
            id: 'ola_003',
            title: 'المپیاد مدیریت در نظام سلامت دوره 18',
            category: 'olampiad_elmi',
            shortDesc: 'دوره آموزش و منتورینگ المپیاد مدیریت در نظام سلامت',
            longDesc: 'دوره آموزش و منتورینگ المپیاد مدیریت در نظام سلامت فرصتی است برای آشنایی عمیق‌تر با پشت‌صحنه اداره نظام سلامت؛ از مدیریت بیمارستان و مراکز درمانی تا برنامه‌ریزی منابع و سیاست‌گذاری. در این دوره، مفاهیم کلیدی مدیریت، سازمان‌دهی، تصمیم‌گیری و حل مسئله در نظام سلامت به‌صورت کاربردی آموزش داده می‌شود و شرکت‌کنندگان با همراهی منتورها روی مسائل واقعی و سناریوهای شبیه‌سازی‌شده کار می‌کنند.',
            stars: 5,
            duration: '25  ساعت',
            mainPrice: '1,780,000',
            discountPrice: '1,600,000',
            percentage: '10',
            instructor: 'جمعی از مدال آوران',
            thumbnail: '/media/image_card/IMG_20260506_215211.jpg',
            videoLink: 'https://example.com',
            active: true
        },
        {
            id: 'ola_004',
            title: 'المپیاد نانو دانشجویی دوره 15',
            category: 'olampiad_elmi',
            shortDesc: 'دوره آموزش و منتورینگ المپیاد نانو دانشجویی',
            longDesc: 'دوره آموزش و منتورینگ المپیاد نانو دانشجویی (دوره ۱۵) فرصتی برای یادگیری عمیق مفاهیم فناوری نانو و آماده‌سازی هدفمند برای حضور در این رقابت علمی است. در این دوره، مباحث پایه و کاربردی نانو از جمله اصول نانومواد، روش‌های ساخت و شناسایی، و کاربردهای نانو در حوزه‌های مختلف علمی به‌صورت ساختارمند آموزش داده می‌شود. علاوه بر آموزش مفهومی، تمرکز دوره بر تقویت مهارت حل مسئله و تحلیل سوالات المپیادی است تا شرکت‌کنندگان بتوانند در فضای رقابتی المپیاد عملکرد بهتری داشته باشند. \n در کنار آموزش، شرکت‌کنندگان از منتورینگ تخصصی بهره‌مند می‌شوند؛ منتورها با تجربه حضور در المپیاد، مسیر مطالعه، تمرین و آمادگی علمی شما را هدایت می‌کنند و با بررسی نقاط قوت و ضعف، کمک می‌کنند برنامه یادگیری مؤثرتری داشته باشید. این ترکیب آموزش هدفمند و راهنمایی مستمر، باعث می‌شود شرکت‌کنندگان با آمادگی علمی و ذهنی بالاتری وارد رقابت شوند',
            stars: 5,
            duration: '30 ساعت',
            mainPrice: '2,100,000',
            discountPrice: '1,890,000',
            percentage: '10',
            instructor: 'جمعی از مدال آوران',
            thumbnail: '/media/image_card/549fd6a7-9a20-4a94-be1e-52a6659cc8da.png.jpeg',
            videoLink: 'https://example.com',
            active: true
        },
        {
            id: 'ola_005',
            title: 'المپیاد پرستاری دوره 5',
            category: 'olampiad_elmi',
            shortDesc: 'دوره آموزش و منتورینگ المپیاد پرستاری',
            longDesc: 'دوره آموزش و منتورینگ المپیاد پرستاری (دوره ۵) فرصتی برای آشنایی عمیق‌تر با مباحث علمی و مهارتی حوزه پرستاری و آمادگی هدفمند برای حضور در المپیاد علمی دانشجویی است. در این دوره، موضوعات کلیدی پرستاری با رویکرد تحلیلی و مسئله‌محور مرور می‌شوند تا شرکت‌کنندگان بتوانند علاوه بر تقویت دانش نظری، مهارت تحلیل سناریوهای بالینی و تصمیم‌گیری حرفه‌ای را نیز توسعه دهند. \n در کنار آموزش، مسیر یادگیری شرکت‌کنندگان با منتورینگ تخصصی همراه است؛ منتورها با تجربه حضور در المپیاد، در برنامه‌ریزی مطالعه، مرور منابع و تمرین سؤالات راهنمایی لازم را ارائه می‌دهند تا هر شرکت‌کننده بتواند با آمادگی علمی و ذهنی بیشتری در این رقابت شرکت کند.',
            stars: 5,
            duration: '25 ساعت',
            mainPrice: '1,950,000',
            discountPrice: '1,650,000',
            percentage: '15',
            instructor: 'جمعی از مدال آوران',
            thumbnail: '/media/image_card/IMG_20260506_215220.jpg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
    ],


    tahghighat: [{
        id: 'tah_001',
        title: 'پروپوزال نویسی مقدماتی',
        category: 'tahghighat',
        shortDesc: 'نحوه نگارش استاندارد پروپوزال پژوهشی',
        longDesc: 'دوره پروپوزال‌نویسی مقدماتی، نقشه راه علمی شما برای تبدیل یک «ایده پژوهشی» به یک «طرح استاندارد و قابل‌اجرا» است. در این دوره، اصول ساختاری نگارش پروپوزال، از تعریف دقیق مسئله و مرور متون گرفته تا طراحی روش‌شناسی (Methodology) و بیان ضرورت‌های پژوهش، به صورت گام‌به‌گام آموزش داده می‌شود. این آموزش به شما کمک می‌کند تا با اعتمادبه‌نفس، پروپوزال‌های پژوهشی مستحکمی بنویسید که استانداردهای دانشگاهی و داوری را با موفقیت پشت سر بگذارند.',
        stars: 5,
        duration: '15  ساعت',
        mainPrice: '1,250,000',
        discountPrice: '1,060,000',
        percentage: '15',
        instructor: 'دپارتمان پژوهشی',
        thumbnail: '/media/image_card/IMG_20232506_215701.jpeg',
        videoLink: 'https://example.com',
        active: true
    }, ],



    maghaleh: [{
            id: 'mag_001',
            title: 'مقاله نویسی مقدماتی',
            category: 'maghaleh',
            shortDesc: 'نحوه نگارش و سابمیت مقاله در مجلات داخلی',
            longDesc: 'دوره مقاله‌نویسی مقدماتی برای دانشجویانی طراحی شده است که می‌خواهند با اصول نگارش و ارسال مقالات علمی در مجلات داخلی آشنا شوند. در این دوره، ساختار استاندارد مقاله پژوهشی — از چکیده و مقدمه تا روش‌ کار، نتایج و بحث — به صورت کاربردی و مرحله‌به‌مرحله آموزش داده می‌شود. همچنین روند انتخاب مجله مناسب، آماده‌سازی فایل‌ها و اصول سابمیت حرفه‌ای مقاله نیز مرور خواهد شد تا شرکت‌کنندگان بتوانند اولین تجربه انتشار علمی خود را با اطمینان طی کنند.',
            stars: 5,
            duration: '20 ساعت',
            mainPrice: '2,450,000',
            discountPrice: '2,080,000',
            percentage: '15',
            instructor: 'دپارتمان پژوهشی',
            thumbnail: '/media/image_card/IMG_20260506_215224.jpg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
        {
            id: 'mag_002',
            title: 'مقاله نویسی پیشرفته',
            category: 'maghaleh',
            shortDesc: 'نحوه نگارش و سابمیت مقاله در مجلات ISI ',
            longDesc: 'دوره مقاله‌نویسی پیشرفته برای پژوهشگرانی طراحی شده است که قصد دارند سطح نگارش علمی خود را به استانداردهای بین‌المللی ارتقا دهند و مقالات خود را در مجلات ISI منتشر کنند. در این دوره، نکات دقیق ساختار مقاله‌های بین‌المللی، نحوه انتخاب مجله مناسب، شناخت شاخص‌های اعتبارسنجی (Impact Factor، Quartile)، اصلاح علمی و زبانی متن، و اصول حرفه‌ای سابمیت و مکاتبه با داوران آموزش داده می‌شود. علاوه بر آموزش فنی، شرکت‌کنندگان یاد می‌گیرند چگونه مقاله خود را برای پذیرش بالاتر بهینه‌سازی کنند.',
            stars: 5,
            duration: '25 ساعت',
            mainPrice: '4,990,000',
            discountPrice: '4,490,000',
            percentage: '10',
            instructor: 'دپارتمان پژوهشی',
            thumbnail: '/media/image_card/71f2f4b2-bee2-4a3e-9bc4-aa7dca42dd4b.png.jpeg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
    ],


    maghale_congress: [{
            id: 'con_001',
            title: 'طراحی پوستر کنگره',
            category: 'maghale_congress',
            shortDesc: 'نحوه طراحی پوستر جهت ارائه خلاصه مقالات',
            longDesc: 'دوره آموزشی طراحی پوستر در کنگره با هدف توانمندسازی پژوهشگران و دانشجویان برای ارائه بصری و حرفه‌ای دستاوردهای علمی طراحی شده است. ارائه پوستر، یکی از رایج‌ترین و در عین حال چالش‌برانگیزترین بخش‌های هر همایش علمی است؛ چرا که شما باید بتوانید حاصل ماه‌ها پژوهش و نگارش مقاله را در یک فضای محدود و با رعایت استانداردهای گرافیکی به مخاطب منتقل کنید. در این دوره، شما یاد می‌گیرید که چگونه از ساختار سنتی و متنی فاصله بگیرید و خلاصه مقالات خود را به یک محتوای بصری جذاب تبدیل کنید که در نگاه اول، توجه داوران و شرکت‌کنندگان را به خود جلب کند. \n در این مسیر، مباحثی همچون اصول چیدمان علمی (Layout)، انتخاب پالت رنگی مناسب برای محیط‌های نمایشگاهی، تایپوگرافی خوانا، و نحوه تبدیل جداول و نمودارهای پیچیده به اینفوگرافیک‌های ساده و گویا آموزش داده می‌شود. همچنین، تفاوت‌های طراحی برای پوسترهای چاپی و الکترونیک (E-Poster) بررسی شده و ابزارهای کاربردی برای طراحی سریع و استاندارد معرفی می‌گردند. هدف نهایی این دوره این است که شما بیاموزید چگونه میان «دقت علمی» و «زیبایی بصری» تعادل برقرار کنید تا پیام اصلی پژوهش شما به شکلی اثرگذار و ماندگار در ذهن مخاطبان کنگره ثبت شود',
            stars: 4,
            duration: '5 ساعت',
            mainPrice: '999,000',
            discountPrice: '799,000',
            percentage: '20',
            instructor: 'دپارتمان پژوهشی',
            thumbnail: '/media/image_card/1778095626950.jpg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
        {
            id: 'con_002',
            title: ': دوره اورژانسی کنگره ملی پژوهش و فناوری ',
            category: 'maghale_congress',
            shortDesc: 'تدوین خلاصه مقاله جهت حضور در کنگره سالیانه در کمتر از یک هفته',
            longDesc: 'دوره اورژانسی کنگره ملی پژوهش و فناوری برای دانشجویان و پژوهشگرانی طراحی شده که قصد دارند در زمان محدود، خلاصه مقاله (Abstract) خود را برای ارسال به کنگره آماده کنند. بسیاری از افراد ایده یا داده‌های پژوهشی ارزشمندی دارند، اما به دلیل کمبود زمان یا آشنایی نداشتن با ساختار استاندارد خلاصه مقاله، فرصت ارسال اثر خود را از دست می‌دهند. این دوره با یک برنامه فشرده و هدفمند طراحی شده تا به شما کمک کند در کمتر از یک هفته، مسیر تدوین و آماده‌سازی خلاصه مقاله را به‌صورت اصولی طی کنید. \n در طول دوره، ساختار استاندارد یک خلاصه مقاله علمی شامل مقدمه، هدف، روش مطالعه، نتایج و جمع‌بندی به‌صورت کاربردی آموزش داده می‌شود. همچنین نکات مهمی مانند انتخاب عنوان مناسب، خلاصه‌نویسی دقیق، رعایت محدودیت تعداد کلمات، و تطبیق متن با قالب موردنظر کنگره بررسی خواهد شد. در کنار آموزش، شرکت‌کنندگان می‌توانند با راهنمایی منتورها و بازخوردهای اصلاحی، متن خود را مرحله‌به‌مرحله بهبود دهند تا در نهایت نسخه‌ای آماده برای ارسال به کنگره در اختیار داشته باشند.',
            stars: 4,
            duration: '7 ساعت',
            mainPrice: '1,100,000',
            discountPrice: '935,000',
            percentage: '15',
            instructor: 'دپارتمان پژوهشی',
            thumbnail: '/media/image_card/1778096846187.jpg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
        {
            id: 'con_003',
            title: 'ارائه علمی درکنگره',
            category: 'maghale_congress',
            shortDesc: 'آمادگی جهت ارائه خلاصه مقالات در کنگره ملی پژوهش و فناوری',
            longDesc: 'دوره ارائه علمی در کنگره برای پژوهشگرانی طراحی شده که می‌خواهند خلاصه‌مقاله خود را نه فقط «ارائه کنند»، بلکه به شکلی حرفه‌ای، جذاب و اثرگذار در کنگره ملی پژوهش و فناوری نمایش دهند. ارائه شفاهی در کنگره، یکی از مهم‌ترین لحظات مسیر پژوهشی هر فرد است؛ جایی که باید بتوانید در چند دقیقه کوتاه، ماه‌ها تلاش علمی را به‌صورت دقیق، منسجم و قابل فهم برای داوران و مخاطبان ارائه کنید.  \nدر این دوره یاد می‌گیرید چگونه از یک خلاصه‌مقاله معمولی، یک ارائه قوی و قابل دفاع بسازید. ساختار استاندارد ارائه شفاهی، نحوه استخراج پیام‌های کلیدی از مقاله، تبدیل داده‌ها به اسلایدهای حرفه‌ای، مدیریت زمان، کنترل استرس، فن بیان علمی، شروع و پایان تأثیرگذار، و نحوه پاسخ به پرسش‌های داوران به‌صورت عملی آموزش داده می‌شود. علاوه بر این، استانداردهای ویژه کنگره ملی پژوهش و فناوری نیز بررسی می‌شود تا مطمئن شوید ارائه شما با انتظارات علمی و فرمی این رویداد کاملاً همخوان است.',
            stars: 4,
            duration: '2 ساعت',
            instructor: 'دپارتمان پژوهشی',
            thumbnail: '/media/image_card/1778095626950.jpg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
    ],



    ketab: [{
        id: 'ket_001',
        title: 'مقدمات تالیف کتاب',
        category: 'ketab',
        shortDesc: 'آَشنایی با اصول اولیه تالیف کتاب در حوزه تخصصی',
        longDesc: 'دوره مقدمات تألیف کتاب برای افرادی طراحی شده که دانش، تجربه یا تخصص ارزشمندی در یک حوزه مشخص دارند اما نمی‌دانند چگونه آن را به شکل یک کتاب منسجم و قابل انتشار ارائه کنند. بسیاری از متخصصان، پژوهشگران و مدرسان ایده نوشتن کتاب را در ذهن دارند، اما به دلیل ناآشنایی با ساختار تألیف، انتخاب موضوع مناسب، یا مسیر انتشار، این ایده هرگز عملی نمی‌شود. در این دوره، شما با اصول پایه و استانداردهای تألیف کتاب در حوزه تخصصی خود آشنا می‌شوید و یاد می‌گیرید چگونه از یک ایده خام به یک طرح اولیه قابل اجرا برسید. \n در طول دوره، موضوعاتی مانند انتخاب عنوان و مخاطب هدف، طراحی ساختار فصل‌بندی، تفاوت کتاب آموزشی، دانشگاهی و تخصصی، اصول نگارش علمی و روان، و جلوگیری از پراکندگی محتوا آموزش داده می‌شود. همچنین با نکات اولیه و ضروری مربوط به ویرایش، رعایت حقوق معنوی، استناددهی و مسیرهای انتشار (انتشارات دانشگاهی، ناشران عمومی یا چاپ شخصی) آشنا می‌شوید. هدف این دوره این است که در پایان، شما یک نقشه راه شفاف برای شروع تألیف کتاب داشته باشید و بدانید قدم بعدی چیست و چگونه باید نوشتن را به‌صورت اصولی آغاز کنید.',
        stars: 4,
        duration: '2 ساعت',
        instructor: 'محمدرضا علیمردانی',
        thumbnail: '/media/image_card/b85d4f94-4fed-402a-a849-f3bae0c1bafc.jpeg',
        videoLink: 'https://example.com',
        active: true
    }, ],


    ekhtera: [{
            id: 'ekh_001',
            title: 'ثبت اختراع داخلی',
            category: 'ekhtera',
            shortDesc: 'نحوه نوشتن اظهار نامه و گرفتن گواهی ثبت اختراع داخلی',
            longDesc: 'دوره ثبت اختراع داخلی به شما کمک می‌کند تا ایده یا نوآوری خود را به‌صورت رسمی در قالب یک پتنت قابل ثبت تبدیل کنید. در این دوره با فرآیند شناسایی نوآوری، جستجوی پیشینه اختراع، نگارش اصولی اظهارنامه ثبت اختراع و مراحل ثبت در سامانه مالکیت فکری آشنا می‌شوید. همچنین نکات مهمی درباره ساختار ادعاها (Claims)، توصیف فنی اختراع و مراحل پیگیری پرونده تا دریافت گواهی ثبت اختراع آموزش داده می‌شود.',
            stars: 5,
            duration: '20 ساعت',
            mainPrice: '4,500,000',
            discountPrice: '3,600,000',
            percentage: '20',
            instructor: 'دپارتمان ثبت اختراع',
            thumbnail: '/media/image_card/071349cf-65dd-4aea-889a-65c551d4a62f.jpeg',
            videoLink: 'https://example.com',
            active: true
        },
        {
            id: 'ekh_002',
            title: 'ثبت اختراع بین المللی',
            category: 'ekhtera',
            shortDesc: 'نحوه ثبت اختراع به صورت بین المللی (US patent)',
            longDesc: ': دوره ثبت اختراع بین‌المللی به شما کمک می‌کند تا نوآوری خود را فراتر از مرزهای کشور ثبت و محافظت کنید. در این دوره با اصول ثبت پتنت در سطح بین‌المللی، به‌ویژه فرآیند ثبت در سیستم پتنت آمریکا (US Patent) آشنا می‌شوید. مباحثی مانند جستجوی پیشینه اختراع در پایگاه‌های جهانی، نگارش حرفه‌ای توضیحات فنی و ادعاهای اختراع (Claims)، انتخاب مسیر مناسب ثبت و آشنایی با مراحل بررسی و پیگیری پرونده به صورت کاربردی آموزش داده می‌شود.',
            stars: 5,
            duration: '30 ساعت',
            mainPrice: '13,500,000',
            discountPrice: '12,150,000',
            percentage: '10',
            instructor: 'دپارتمان ثبت اختراع',
            thumbnail: '/media/image_card/IMG_20260506_232826.jpeg',
            videoLink: 'https://example.com',
            active: true
        },
    ],


    noavari: [{
            id: 'nov_001',
            title: 'راه اندازی استارتاپ های حوزه سلامت',
            category: 'noavari',
            shortDesc: 'صفر تا صد چگونگی راه اندازی استارتاپ های سلامت محور',
            longDesc: 'دوره راه‌اندازی استارتاپ‌های حوزه سلامت یک مسیر جامع و مرحله‌به‌مرحله برای افرادی است که می‌خواهند ایده‌های سلامت‌محور خود را به یک کسب‌وکار واقعی و پایدار تبدیل کنند. حوزه سلامت، به دلیل حساسیت بالا، قوانین خاص، و ارتباط مستقیم با جان و کیفیت زندگی افراد، نیازمند رویکردی متفاوت نسبت به سایر استارتاپ‌هاست. در این دوره، از مرحله شکل‌گیری ایده و اعتبارسنجی نیاز بازار گرفته تا طراحی مدل کسب‌وکار، توسعه محصول، مسائل حقوقی و جذب سرمایه، همه چیز به‌صورت کاربردی و ساختارمند آموزش داده می‌شود. \n شما یاد می‌گیرید چگونه یک مسئله واقعی در نظام سلامت را شناسایی کنید، برای آن راهکار نوآورانه طراحی کنید و با استفاده از ابزارهایی مانند Lean Canvas یا طراحی مدل کسب‌وکار، ایده خود را قابل ارائه و سرمایه‌پذیر کنید. همچنین چالش‌های خاص این حوزه مانند مجوزها، تعامل با نهادهای درمانی، محرمانگی داده‌های سلامت و اعتمادسازی در بازار بررسی می‌شود. این دوره صرفاً تئوری نیست؛ بلکه با مثال‌های واقعی از استارتاپ‌های موفق و تحلیل تجربه‌های عملی، مسیر راه‌اندازی را شفاف و قابل اجرا می‌کند.',
            stars: 5,
            duration: '20 ساعت',
            mainPrice: '5,750,000',
            discountPrice: '4,900,000',
            percentage: '15 ',
            instructor: 'دپارتمان نوآوری و کارآفرینی',
            thumbnail: '/media/image_card/1778094301755.jpg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
        {
            id: 'nov_002',
            title: 'ثبت شرکت در مرکز رشد',
            category: 'noavari',
            shortDesc: 'نحوه ثبت شرکت و استقرار در مرکز رشد دانشگاه',
            longDesc: 'دوره آموزشی ثبت شرکت در مرکز رشد، راهنمای جامع و گام‌به‌گامی است برای دانشجویان، فناوران و نخبگانی که می‌خواهند ایده‌های نوآورانه خود را در قالب یک شخصیت حقوقی رسمی و با حمایت مستقیم دانشگاه به بازار عرضه کنند. استقرار در مراکز رشد، در واقع پلی میان محیط آکادمیک و بازار تجاری است؛ اما ورود به این مراکز و بهره‌مندی از خدمات آن‌ها، نیازمند آگاهی دقیق از قوانین اداری، نحوه نگارش طرح کسب‌وکار (Business Plan) حرفه‌ای و موفقیت در جلسات داوری تخصصی است. در این دوره، شما با تمامی مراحل فرآیند پذیرش، از نحوه تدوین پروپوزال‌های فناورانه تا جزئیات مربوط به مصاحبه‌های استقرار آشنا می‌شوید تا احتمال پذیرش ایده خود را به عنوان یک واحد فناور به حداکثر برسانید. \n علاوه بر جنبه‌های فنی پذیرش، این دوره به بررسی دقیق مزایای استقرار در مراکز رشد می‌پردازد؛ خدماتی از جمله بهره‌مندی از فضاهای اداری و کارگاهی، استفاده از خدمات منتورینگ و مشاوره تخصصی، معافیت‌های مالیاتی و تسهیلات مالی، و همچنین استفاده از برند معتبر دانشگاه برای اعتباربخشی به کسب‌وکار. ما در این دوره، ابهامات مربوط به مراحل قانونی ثبت شرکت، انتخاب نوع شرکت (سهامی خاص یا مسئولیت محدود) و تفاوت‌های میان استقرار به عنوان «هسته فناور» یا «واحد فناور» را به‌صورت شفاف تبیین می‌کنیم. هدف نهایی این است که شما نه تنها شرکت خود را ثبت کنید، بلکه از پتانسیل‌های حمایتی مرکز رشد برای تسریع رشد استارتاپ خود و کاهش ریسک‌های اولیه کسب‌وکار به بهترین شکل ممکن استفاده نمایید.',
            stars: 4,
            duration: '3 ساعت',
            mainPrice: '500,000',
            discountPrice: '350,000',
            percentage: '30',
            instructor: 'حسن اسماعیلی',
            thumbnail: '/media/image_card/d763e9f4-17fb-4f4c-9c3e-d77bf08ba4ff.jpeg',
            videoLink: 'https://example.com',
            active: true
        },
        {
            id: 'nov_003',
            title: 'ساخت محصولات سلامت دیجیتال بدون کدنویسی',
            category: 'noavari',
            shortDesc: 'طراحی و ساخت محصولات سلامت دیجیتال با متدولوژی Low code & No code',
            longDesc: 'دوره ساخت محصولات سلامت دیجیتال بدون کدنویسی برای افرادی طراحی شده که می‌خواهند ایده‌های سلامت‌محور خود را بدون درگیر شدن با پیچیدگی‌های برنامه‌نویسی، به یک محصول دیجیتال واقعی تبدیل کنند. در این دوره با رویکرد Low‑Code / No‑Code یاد می‌گیرید چگونه اپلیکیشن‌ها، وب‌اپ‌ها و ابزارهای دیجیتال حوزه سلامت را با استفاده از پلتفرم‌های آماده و استاندارد طراحی و پیاده‌سازی کنید. این رویکرد به شما اجازه می‌دهد تمرکز اصلی خود را روی حل مسئله، تجربه کاربر و ارزش بالینی محصول بگذارید، نه نوشتن کد. \n در طول دوره، از ایده‌پردازی و طراحی اولیه محصول (MVP) شروع می‌کنید و به‌صورت گام‌به‌گام با ابزارهای نوکد برای طراحی رابط کاربری، ساخت منطق‌های کاربردی، اتصال به پایگاه‌های داده و تست محصول آشنا می‌شوید. همچنین ملاحظات مهم حوزه سلامت مانند امنیت اطلاعات بیماران، محرمانگی داده‌ها، استانداردهای اولیه سلامت دیجیتال و تطابق محصول با نیاز کاربران واقعی بررسی می‌شود. هدف دوره این است که شما در پایان، بتوانید یک نمونه اولیه قابل ارائه از محصول سلامت دیجیتال خود بسازید که آماده تست بازار، ارائه به مرکز رشد یا جذب سرمایه اولیه باشد.',
            stars: 5,
            duration: '12 ساعت',
            mainPrice: '1,999,000',
            discountPrice: '1,800,000',
            percentage: '10',
            instructor: 'پوریا فتح الله زاده',
            thumbnail: '/media/image_card/22f6ecb4-44d4-44ba-95c7-f09f711f1c46.jpeg',
            videoLink: 'https://example.com',
            active: true  /* false */
        },
    ],

    jashnvare: [{
            id: 'jash_001',
            title: 'آمادگی برای استارتاپ ویکندهای کشوری',
            category: 'jashnvare',
            shortDesc: 'چگونگی ایده پردازی و مقام آوری در استارتاپ ویکند ',
            longDesc: 'دوره آمادگی برای استارتاپ ویکندهای کشوری برای افرادی طراحی شده که می‌خواهند با آمادگی واقعی و ذهنیت برنده وارد رویدادهای رقابتی استارتاپ ویکند شوند. استارتاپ ویکند تنها یک رویداد ۵۴ ساعته نیست؛ بلکه میدانی فشرده از ایده‌پردازی، تیم‌سازی، ارائه ارزش پیشنهادی و تصمیم‌گیری سریع است. در این دوره یاد می‌گیرید چگونه در زمان محدود، یک ایده خام را به یک طرح قابل دفاع و جذاب برای داوران تبدیل کنید و از همان ساعات ابتدایی رویداد، مسیر رقابت را به نفع خودتان جلو ببرید. \n تمرکز اصلی دوره بر ایده‌پردازی هدفمند و مقام‌آور است؛ از شناسایی مسئله واقعی و تحلیل نیاز بازار گرفته تا طراحی ارزش پیشنهادی، انتخاب مدل کسب‌وکار مناسب و آماده‌سازی برای پیچ دک (Pitch). همچنین تکنیک‌های تشکیل تیم مؤثر، تقسیم نقش‌ها، مدیریت زمان در طول رویداد و نکات کلیدی ارائه نهایی آموزش داده می‌شود. با بررسی تجربه‌های واقعی برگزیدگان استارتاپ ویکندهای کشوری، شما با اشتباهات رایج شرکت‌کنندگان و راه‌های متمایز شدن در نگاه داوران آشنا می‌شوید تا حضور شما در رویداد، صرفاً مشارکت نباشد بلکه یک تجربه موفق و نتیجه‌محور باشد.',
            stars: 4,
            duration: '3 ساعت',
            mainPrice: '600,000',
            discountPrice: '510,000',
            percentage: '15',
            instructor: 'محمد محسن خدابنده',
            thumbnail: '/media/image_card/1778096277918.jpg',
            videoLink: 'https://example.com',
            active: true
        },
        {
            id: 'jash_002',
            title: 'ایده پردازی فناورانه',
            category: 'jashnvare',
            shortDesc: 'روش های ایده پردازی فناورانه در حوزه سلامت',
            longDesc: 'دوره ایده‌پردازی فناورانه در حوزه سلامت برای افرادی طراحی شده که می‌خواهند یاد بگیرند چگونه از دل چالش‌های واقعی نظام سلامت، به ایده‌هایی برسند که قابلیت تبدیل به محصول، خدمت یا استارتاپ را داشته باشند. حوزه سلامت به‌دلیل پیچیدگی‌های ساختاری، قوانین خاص، نیازهای حساس و سرعت بالای تغییرات، یکی از دشوارترین اما جذاب‌ترین بسترها برای نوآوری است. در این دوره شما یاد می‌گیرید چگونه به‌جای ایده‌پردازی تصادفی، از متدولوژی‌های علمی و سیستماتیک استفاده کنید و با تحلیل گپ‌های بالینی، مسیر بیمار، داده‌های سلامت، و روندهای فناورانه مانند تله‌مدیسین، هوش مصنوعی و سلامت دیجیتال، به ایده‌هایی دقیق، کاربردی و ارزش‌آفرین برسید. \n در این دوره علاوه بر معرفی تکنیک‌های شناخته‌شده مانند SCAMPER، Design Thinking، TRIZ و تحلیل مشکلات بالینی (Clinical Problem Solving)، مسیر ایده‌پردازی در حوزه سلامت به‌صورت مرحله‌به‌مرحله آموزش داده می‌شود؛ از مشاهده مسئله در محیط واقعی تا کشف نیازهای پنهان، تعریف مسئله به زبان درست، اعتبارسنجی اولیه ایده و تحلیل اینکه آیا ایده قابلیت اجرا، مقیاس‌پذیری و کسب مجوز دارد یا نه. همچنین با مثال‌های واقعی از نوآوری‌های موفق سلامت، یاد می‌گیرید چه عواملی باعث می‌شود یک ایده ساده به یک نوآوری تأثیرگذار تبدیل شود',
            stars: 4,
            duration: '2 ساعت',
            instructor: 'ایمان رجائی',
            thumbnail: '/media/image_card/1ea0ff8a-359f-41e0-87cb-bb6bd6156658.jpeg',
            videoLink: 'https://example.com',
            active: true
        },
    ],



    bedone_dastebandi: [{
        id: 'bedone_001',
        title: 'آشنایی با بند ک استعداد درخشان',
        category: 'bedone_dastebandi',
        shortDesc: 'آشنایی با ماده های مختلف بند ک استعدادهای درخشان',
        longDesc: 'دوره آشنایی با بند «ک» استعدادهای درخشان برای دانشجویانی طراحی شده که قصد دارند از مزایای آیین‌نامه‌های ویژه استعدادهای درخشان در ادامه تحصیل، ورود به مقاطع بالاتر، یا بهره‌مندی از تسهیلات آموزشی و پژوهشی استفاده کنند، اما از جزئیات این آیین‌نامه‌ها آگاهی کامل ندارند. بسیاری از دانشجویان نمی‌دانند دقیقاً چه شرایطی لازم است، چه امتیازاتی قابل دریافت است، چه مدارکی باید تهیه شود و کدام مواد آیین‌نامه بیشترین تاثیر را روی مسیر تحصیلی آن‌ها دارد. \n در این دوره، بند «ک» و تمام مواد مرتبط با آن به زبان ساده تشریح می‌شود. شما با مفاهیم اصلی مانند شرایط احراز استعداد درخشان، امتیازهای پژوهشی، امتیازهای آموزشی، نحوه محاسبه امتیازات، سهمیه‌ها، معافیت‌ها، تسهیلات ورود بدون آزمون یا با امتیازات ویژه به مقاطع بالاتر، همچنین محدودیت‌ها و الزامات اداری آشنا می‌شوید.',
        stars: 4,
        duration: '2 ساعت',
        instructor: 'ستاره شهسواری',
        thumbnail: '/media/image_card/images-3.jpeg',
        videoLink: 'https://example.com',
        active: true
    }, ]

};
// ==========================================
// تابع تولید پیشنهادات ویدیو
// ==========================================
function generateVideoSuggestions(breakdown) {
    console.group('🎬 تولید پیشنهادات ویدیو');
    
    // مرتب‌سازی بخش‌ها بر اساس کمترین امتیاز کسب‌شده کاربر
    const sortedSections = Object.entries(breakdown)
        .map(([key, data]) => ({
            key,
            title: data.title,
            userScore: data.finalSectionScore, // امتیاز واقعی کاربر
            maxScore: formConfigs[key]?.scoring?.maxScore || 0
        }))
        .filter(section => {
            // فقط بخش‌هایی که ویدیو دارند
            const hasVideos = VIDEO_DATABASE[section.key] && VIDEO_DATABASE[section.key].length > 0;
            if (!hasVideos) {
                console.warn(`⚠️ ${section.title} ویدیو ندارد، حذف می‌شود`);
            }
            return hasVideos;
        })
        .sort((a, b) => a.userScore - b.userScore); // کمترین امتیاز اول (صعودی)
    
    console.log('📊 بخش‌ها مرتب‌شده بر اساس امتیاز کاربر (کمترین → بیشترین):');
    sortedSections.forEach((s, i) => {
        console.log(`  ${i + 1}. ${s.title}: ${s.userScore} امتیاز`);
    });
    
    const selectedVideos = [];
    const TARGET_VIDEO_COUNT = 20;
    
    // مرحله 1: توزیع اولیه بر اساس اولویت (کمترین امتیاز = بیشترین ویدیو)
    let remainingSlots = TARGET_VIDEO_COUNT;
    const sectionAllocations = [];
    
    for (let i = 0; i < sortedSections.length && remainingSlots > 0; i++) {
        const section = sortedSections[i];
        const availableVideos = VIDEO_DATABASE[section.key];
        
        // محاسبه تعداد ویدیو: بخش‌های اولیه (کم‌امتیازتر) سهم بیشتری می‌گیرند
        const remainingSections = sortedSections.length - i;
        const baseAllocation = Math.max(1, Math.ceil(remainingSlots / remainingSections));
        const allocation = Math.min(baseAllocation, availableVideos.length, remainingSlots);
        
        sectionAllocations.push({
            section,
            allocation,
            availableCount: availableVideos.length
        });
        
        remainingSlots -= allocation;
    }
    
    console.log('📋 توزیع اولیه:');
    sectionAllocations.forEach(({ section, allocation }) => {
        console.log(`  ${section.title}: ${allocation} ویدیو (امتیاز کاربر: ${section.userScore})`);
    });
    
    // مرحله 2: انتخاب ویدیوها از هر بخش
    for (const { section, allocation } of sectionAllocations) {
        const availableVideos = VIDEO_DATABASE[section.key];
        
        // مرتب‌سازی بر اساس ستاره (بالاترین کیفیت اول)
        const sortedVideos = [...availableVideos].sort((a, b) => b.stars - a.stars);
        const selectedFromSection = sortedVideos.slice(0, allocation);
        
        selectedVideos.push(...selectedFromSection.map(v => ({
            ...v,
            sectionTitle: section.title,
            sectionKey: section.key,
            userScore: section.userScore,
            priority: section.userScore // برای ردیابی اولویت
        })));
        
        console.log(`✅ ${selectedFromSection.length} ویدیو از ${section.title} انتخاب شد`);
    }
    
    // مرحله 3: تکمیل تا 20 ویدیو (اگر نیاز باشد)
    if (selectedVideos.length < TARGET_VIDEO_COUNT) {
        console.log(`🔄 ${TARGET_VIDEO_COUNT - selectedVideos.length} ویدیوی دیگر نیاز است`);
        
        // دوباره از اول بخش‌ها (کم‌امتیازترین‌ها) شروع کن
        for (const { section } of sectionAllocations) {
            if (selectedVideos.length >= TARGET_VIDEO_COUNT) break;
            
            const availableVideos = VIDEO_DATABASE[section.key];
            const alreadySelected = selectedVideos.filter(v => v.sectionKey === section.key).length;
            
            if (alreadySelected < availableVideos.length) {
                const sortedVideos = [...availableVideos].sort((a, b) => b.stars - a.stars);
                const additionalVideos = sortedVideos.slice(alreadySelected);
                
                const needed = TARGET_VIDEO_COUNT - selectedVideos.length;
                const toAdd = additionalVideos.slice(0, needed);
                
                selectedVideos.push(...toAdd.map(v => ({
                    ...v,
                    sectionTitle: section.title,
                    sectionKey: section.key,
                    userScore: section.userScore,
                    priority: section.userScore
                })));
                
                console.log(`➕ ${toAdd.length} ویدیوی اضافی از ${section.title} اضافه شد`);
            }
        }
    }
    
    console.log(`🎯 مجموع ویدیوهای انتخاب‌شده: ${selectedVideos.length}`);
    
    // ==========================================
    // اضافه کردن مرتب‌سازی بر اساس فعال بودن ویدیو
    // ==========================================
    selectedVideos.sort((a, b) => {
        // اگر هر دو وضعیت یکسانی دارند، ترتیب فعلی (بر اساس اولویت امتیاز) حفظ شود
        if (a.active === b.active) {
            return a.priority - b.priority;
        }
        // ویدیوهای فعال (true) بالاتر از غیرفعال (false) قرار بگیرند
        return a.active ? -1 : 1;
    });

    console.log('📑 ترتیب نهایی ویدیوها:');
    selectedVideos.slice(0, TARGET_VIDEO_COUNT).forEach((v, i) => {
        console.log(`  ${i + 1}. [${v.active ? 'فعال' : 'در حال تدوین'}] ${v.sectionTitle} (امتیاز: ${v.userScore}) - ${v.title}`);
    });
    console.groupEnd();
    
    return selectedVideos.slice(0, TARGET_VIDEO_COUNT);
}




// ==========================================
// رندر کارت ویدیو
// ==========================================
function renderVideoCard(video) {
    const stars = '⭐'.repeat(video.stars);
    const statusBadge = video.active 
        ? '<span class="video-status-badge active">فعال</span>' 
        : '<span class="video-status-badge inactive">در حال تدوین</span>';
    
    // بررسی وجود قیمت
    const hasPricing = video.mainPrice && video.discountPrice;
    const pricingHTML = hasPricing 
        ? `
            <div class="proposal-video-pricing">
                <span class="proposal-video-price-original">${video.mainPrice}</span>
                <span class="proposal-video-price-discount">${video.discountPrice}</span>
                <span class="proposal-video-price-currency">تومان</span>
            </div>
        `
        : `
            <div class="proposal-video-pricing">
                <span class="proposal-video-price-free">رایگان</span>
            </div>
        `;
    
    return `
        <div class="proposal-video-card" data-video-id="${video.id}">
            <div class="proposal-video-thumbnail">
                <img src="${video.thumbnail}" alt="${video.title}">
                <div class="proposal-video-play">▶</div>
                <span class="proposal-video-duration">${video.duration}</span>
                ${statusBadge}
            </div>
            <div class="proposal-video-content">
                <div class="proposal-video-category">${video.sectionTitle}</div>
                <h4 class="proposal-video-title">${video.title}</h4>
                <p class="proposal-video-desc">${video.shortDesc}</p>
                <div class="proposal-video-meta">
                    <span class="proposal-video-stars">${stars}</span>
                    <span class="proposal-video-instructor">${video.instructor}</span>
                </div>
                ${pricingHTML}
            </div>
        </div>
    `;
}




// ==========================================
// نمایش ویدیوها در Step 5
// ==========================================
function displayVideoSuggestions(breakdown) {
    const container = document.querySelector('.proposal-videos-list');
    
    if (!container) {
        console.error('❌ .proposal-videos-list پیدا نشد');
        return;
    }
    
    const videos = generateVideoSuggestions(breakdown);
    
    if (videos.length === 0) {
        container.innerHTML = '<p class="no-videos">ویدیویی برای نمایش وجود ندارد.</p>';
        return;
    }
    
    container.innerHTML = videos.map(video => renderVideoCard(video)).join('');
    
    // افزودن event listener برای کلیک روی ویدیو
    container.querySelectorAll('.proposal-video-card').forEach(card => {
        card.addEventListener('click', function() {
            const videoId = this.dataset.videoId;
            openVideoModal(videoId);
        });
    });
}


// ==========================================
// باز کردن مودال ویدیو
// ==========================================
function openVideoModal(videoId) {
    // پیدا کردن ویدیو از دیتابیس
    let foundVideo = null;
    let sectionKey = null;
    
    for (const category in VIDEO_DATABASE) {
        const video = VIDEO_DATABASE[category].find(v => v.id === videoId);
        if (video) {
            foundVideo = video;
            sectionKey = category;
            break;
        }
    }
    
    if (!foundVideo) {
        console.error('ویدیو پیدا نشد:', videoId);
        return;
    }
    
    // محاسبه sectionTitle از breakdown یا formConfigs
    const sectionTitle = formConfigs[sectionKey]?.title || foundVideo.category;
    
    // ثبت کلیک کاربر
    /* trackVideoClick(foundVideo); */
    
    // بررسی وجود قیمت
    const hasPricing = foundVideo.mainPrice && foundVideo.discountPrice;
    const pricingBoxHTML = hasPricing 
        ? `
            <div class="video-modal-pricing-box">
                <div class="video-modal-pricing-content">
                    <span class="video-modal-price-label">قیمت دوره:</span>
                    <div class="video-modal-prices">
                        <span class="video-modal-price-original">${foundVideo.mainPrice}</span>
                        <div class="video-modal-price-final">
                            <span class="video-modal-price-discount">${foundVideo.discountPrice}</span>
                            <span class="video-modal-price-currency">تومان</span>
                        </div>
                    </div>
                </div>
            </div>
        `
        : `
            <div class="video-modal-pricing-box">
                <div class="video-modal-pricing-content">
                    <span class="video-modal-price-free-large">رایگان</span>
                </div>
            </div>
        `;
    
    // ساخت مودال
    const modalHTML = `
        <div class="video-modal-overlay" id="videoModalOverlay">
            <div class="video-modal-container">
                <button class="video-modal-close" onclick="closeVideoModal()">✕</button>
                
                <div class="video-modal-content">
                    
                    <div class="video-modal-body">
                        <div class="video-modal-thumbnail">
                            <img src="${foundVideo.thumbnail}" alt="${foundVideo.title}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect fill=%22%23ddd%22 width=%22400%22 height=%22300%22/%3E%3Ctext fill=%22%23999%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E${foundVideo.title}%3C/text%3E%3C/svg%3E'">
                            <div class="proposal-video-play">▶</div>
                        </div>

                        <div class="video-modal-header">
                            <h2 class="video-modal-title">${foundVideo.title}</h2>
                            <div class="video-modal-meta">
                                <span class="video-modal-stars">${'⭐'.repeat(foundVideo.stars)}</span>
                            </div>
                        </div>
                        
                        <div class="video-modal-info">
                            <div class="video-modal-info-row">
                                <span class="video-modal-label">دسته‌بندی:</span>
                                <span class="video-modal-value">${sectionTitle}</span>
                            </div>
                            <div class="video-modal-info-row">
                                <span class="video-modal-label">مدرس:</span>
                                <span class="video-modal-value">${foundVideo.instructor}</span>
                            </div>
                            <div class="video-modal-info-row">
                                <span class="video-modal-label">مدت زمان:</span>
                                <span class="video-modal-value">${foundVideo.duration}</span>
                            </div>
                        </div>
                        
                        ${pricingBoxHTML}
                        
                        <div class="video-modal-description">
                            <h3>توضیحات دوره</h3>
                            <p>${foundVideo.longDesc}</p>
                        </div>
                        
                        ${foundVideo.active ? `
                            <div class="video-modal-actions">
                                <button class="video-modal-btn-primary" onclick="watchVideo('${foundVideo.videoLink}')">
                                    شرکت در دوره
                                </button>
                            </div>
                        ` : `
                            <div class="video-modal-inactive">
                                <p class="video-modal-inactive-text">این ویدیو در حال تدوین است</p>
                                <p class="video-modal-inactive-subtext">به زودی منتشر خواهد شد</p>
                            </div>
                        `}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // حذف مودال قبلی اگر وجود دارد
    const existingModal = document.getElementById('videoModalOverlay');
    if (existingModal) {
        existingModal.remove();
    }
    
    // اضافه کردن مودال به body
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // جلوگیری از اسکرول صفحه
    document.body.style.overflow = 'hidden';
    
    // بستن مودال با کلیک روی overlay
    document.getElementById('videoModalOverlay').addEventListener('click', function(e) {
        if (e.target === this) {
            closeVideoModal();
        }
    });
}




// ==========================================
// بستن مودال ویدیو
// ==========================================
function closeVideoModal() {
    const modal = document.getElementById('videoModalOverlay');
    if (modal) {
        modal.classList.add('closing');
        setTimeout(() => {
            modal.remove();
            document.body.style.overflow = '';
        }, 300);
    }
}

// ==========================================
// مشاهده ویدیو (انتقال به لینک)
// ==========================================
// اضافه کردن این کد به فایل JavaScript موجود

// تابع watchVideo را به این صورت تغییر دهید:
function watchVideo(videoLink) {
    const modalOverlay = document.getElementById('videoModalOverlay');
    const titleElement = modalOverlay.querySelector('.video-modal-title');
    const courseTitle = titleElement ? titleElement.textContent : '';

    const userData = {
        firstName: formData.firstName,
        lastName: formData.lastName,
        phone: formData.phone,
        email: formData.email,
        totalScore: scoreData.totalScore || 0,
        breakdown: scoreData.breakdown || {},
        courseTitle: courseTitle
    };

    // به‌جای آدرس هاردکد، از متغیری که از تمپلیت پاس داده شده استفاده کن
    fetch(window.SAVE_VIDEO_INTEREST_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            closeVideoModal();
            window.location.href = window.THANK_YOU_URL || '/thank-you/';
        } else {
            alert('خطا در ثبت اطلاعات: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('خطا در ارتباط با سرور');
    });
}


// ==========================================
// بستن مودال با کلید ESC
// ==========================================
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeVideoModal();
    }
});
