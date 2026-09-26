# LinkedIn project draft

## English

How useful is high accuracy when a model misses every event we care about?

Our Data Analytics for Business project explores unusual monthly increases in Gaza's Consumer Price Index using official data from the Palestinian Central Bureau of Statistics (PCBS).

The repository includes data validation, exploratory analysis, lagged and rolling features, and a Logistic Regression experiment evaluated with a chronological train/test split. We compare it with two simple rules and examine how the results change under 5%, 10% and 20% spike definitions.

For the primary definition—a monthly increase of at least 10%—Logistic Regression identified 21 of 25 spikes in the held-out year:
• Recall: 84%
• Precision: 35.6%
• F1: 0.50

It also produced 38 false alarms. Meanwhile, predicting “no spike” every time achieved about 84% accuracy while detecting none of the spikes.

That tradeoff is the main takeaway: accuracy alone can hide poor event detection, and a more complex method must earn its place against simple baselines.

The repository contains the executed notebook, plots, prediction tables, methodology, limitations and instructions to reproduce the analysis. The dataset is short and affected by major disruptions, so these findings are an academic analysis rather than a production forecasting claim.

Project team: **Misk Elayan, Asil Khalil and Sandra Shwamreh**.
Data source: **PCBS**.
Study data: December 2022–February 2026; held-out evaluation: March 2025–February 2026.

[View the project](https://github.com/miskelayan/palestine-cpi-spike-analysis)

#DataAnalytics #Python #TimeSeries #EconomicData #Palestine

## العربية

هل تكفي دقة عالية إذا كان النموذج لا يلتقط الحالات التي نهتم بها؟

في مشروعنا لمساق Data Analytics for Business، درسنا الارتفاعات الشهرية الحادة في مؤشر أسعار المستهلك في غزة باستخدام بيانات الجهاز المركزي للإحصاء الفلسطيني PCBS.

المستودع يتضمن فحص البيانات وتحليلها، وتجهيز متغيرات من الأشهر السابقة، وتجربة Logistic Regression بتقسيم زمني للتدريب والاختبار، مع المقارنة بقواعد بسيطة وفحص عتبات 5% و10% و20%.

عند تعريف الارتفاع الحاد بزيادة شهرية لا تقل عن 10%، التقط النموذج 21 من أصل 25 حالة في سنة الاختبار:
• Recall: 84%
• Precision: 35.6%
• F1: 0.50

لكنه أعطى أيضًا 38 إنذارًا خاطئًا. في المقابل، حققت قاعدة «لا يوجد ارتفاع حاد دائمًا» دقة تقارب 84%، مع أنها لم تلتقط أي حالة.

أهم ما توضحه التجربة هو أن Accuracy وحدها قد تكون مضللة، وأن مقارنة النموذج بقواعد بسيطة وشرح أخطائه جزء أساسي من التحليل.

المشروع متاح مع الدفتر المنفذ والرسوم والجداول والمنهجية وخطوات إعادة التشغيل. النتائج محدودة بقصر السلسلة وظروف البيانات، وليست نظام توقعات جاهزًا للاستخدام العملي.

فريق المشروع: **Misk Elayan، Asil Khalil، Sandra Shwamreh**.
المصدر: **PCBS**.
فترة البيانات: ديسمبر 2022–فبراير 2026. الاختبار: مارس 2025–فبراير 2026.

[رابط المشروع](https://github.com/miskelayan/palestine-cpi-spike-analysis)

#تحليل_البيانات #Python #DataAnalytics #فلسطين
