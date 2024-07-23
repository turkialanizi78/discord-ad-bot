# Arabic 
# بوت الإعلانات في ديسكورد

هذا البوت يسمح للمستخدمين بإنشاء وجدولة الإعلانات داخل سيرفرات ديسكورد. يوفر واجهة تفاعلية لإنشاء الإعلانات، ويدعم إرفاق الصور، ويتضمن نظام أذونات قائم على الأدوار لإنشاء الإعلانات.

## الميزات

- إنشاء إعلانات بعناوين وأوصاف قابلة للتخصيص
- جدولة الإعلانات للنشر في المستقبل
- دعم إرفاق صور متعددة لكل إعلان
- نظام أذونات قائم على الأدوار لإنشاء الإعلانات
- واجهة تفاعلية لاختيار القناة
- إطارات بألوان باستيل للصور المرفقة

## المتطلبات الأساسية

- بايثون 3.8 أو أحدث
- مكتبة discord.py
- مكتبة Pillow لمعالجة الصور

## التثبيت

1. استنسخ هذا المستودع:
   ```
   git clone https://github.com/turkialanizi78/discord-ad-bot.git
   cd discord-ad-bot
   ```

2. قم بتثبيت المكتبات المطلوبة:
   ```
   pip install -r requirements.txt
   ```

3. أنشئ ملف `config.json` في المجلد الرئيسي وأضف توكن بوت ديسكورد الخاص بك:
   ```json
   {
     "TOKEN": "your_discord_bot_token_here"
   }
   ```

## الإعداد

1. افتح ملف `main.py` وابحث عن قائمة `AUTHORIZED_ROLE_IDS`.
2. أضف معرفات الأدوار التي يجب أن تمتلك صلاحية إنشاء الإعلانات:
   ```python
   AUTHORIZED_ROLE_IDS = [1219669909366116463, 1234567890123456789]  # أضف المزيد من معرفات الأدوار حسب الحاجة
   ```

## الاستخدام

1. قم بتشغيل البوت:
   ```
   python main.py
   ```

2. في ديسكورد، استخدم الأمر `/create_ad` لفتح واجهة إنشاء الإعلان.

3. اتبع التعليمات لـ:
   - اختيار قناة للإعلان
   - إدخال عنوان وتفاصيل الإعلان
   - إرفاق الصور (اختياري)

4. سيقوم البوت بنشر الإعلان في القناة المحددة أو جدولته للنشر في المستقبل.

## الأوامر

- `/create_ad`: يفتح واجهة إنشاء إعلان جديد
- `/remove_command <اسم_الأمر>`: يزيل أمر سلاش محدد (للمشرفين فقط)

## جدولة الإعلانات

لجدولة إعلان للنشر في المستقبل:

1. استخدم الأمر `/create_ad`.
2. في نموذج الجدولة، حدد التاريخ والوقت لنشر الإعلان.
3. سيقوم البوت تلقائيًا بنشر الإعلان في الوقت المحدد.

## الأذونات

فقط المستخدمون الذين لديهم الأدوار المحددة في `AUTHORIZED_ROLE_IDS` يمكنهم استخدام الأمر `/create_ad`. تأكد من أن البوت الخاص بك لديه الأذونات اللازمة في سيرفر ديسكورد، بما في ذلك:

- إرسال الرسائل
- تضمين الروابط
- إرفاق الملفات
- إضافة ردود الفعل
- استخدام الإيموجي الخارجية
- إدارة الرسائل (لإزالة ردود الفعل)

## المساهمة

المساهمات مرحب بها! لا تتردد في تقديم طلب سحب.

## الترخيص

هذا المشروع مرخص بموجب رخصة MIT - راجع ملف [LICENSE](LICENSE) للحصول على التفاصيل.

## الدعم

 

إذا واجهت أي مشاكل أو كانت لديك أسئلة، يرجى الانضمام إلى سيرفر الدعم الخاص بنا على ديسكورد:

[![Discord](https://img.shields.io/discord/1164455943451459645?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/ZZC8JVuyb6)

You can also open an issue on the GitHub repository.

# English
# Discord Advertisement Bot

This Discord bot allows users to create and schedule advertisements within Discord servers. It provides an interactive interface for creating ads, supports image attachments, and includes role-based permissions for ad creation.

## Features

- Create advertisements with customizable titles and descriptions
- Schedule advertisements for future posting
- Support for multiple image attachments per advertisement
- Role-based permission system for ad creation
- Interactive channel selection interface
- Pastel color framing for attached images

## Prerequisites

- Python 3.8 or higher
- discord.py library
- Pillow library for image processing

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/turkialanizi78/discord-ad-bot.git
   cd discord-ad-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `config.json` file in the root directory with your Discord bot token:
   ```json
   {
     "TOKEN": "your_discord_bot_token_here"
   }
   ```

## Configuration

1. Open `main.py` and locate the `AUTHORIZED_ROLE_IDS` list.
2. Add the role IDs that should have permission to create ads:
   ```python
   AUTHORIZED_ROLE_IDS = [1219669909366116463, 1234567890123456789]  # Add more role IDs as needed
   ```

## Usage

1. Start the bot:
   ```
   python main.py
   ```

2. In Discord, use the `/create_ad` command to open the ad creation interface.

3. Follow the prompts to:
   - Select a channel for the ad
   - Enter the ad title and details
   - Attach images (optional)

4. The bot will post the ad in the selected channel or schedule it for future posting.

## Commands

- `/create_ad`: Opens the interface to create a new advertisement
- `/remove_command <command_name>`: Removes a specified slash command (admin only)

## Scheduling Advertisements

To schedule an ad for future posting:

1. Use the `/create_ad` command.
2. In the scheduling form, specify the date and time for the ad to be posted.
3. The bot will automatically post the ad at the scheduled time.

## Permissions

Only users with roles specified in `AUTHORIZED_ROLE_IDS` can use the `/create_ad` command. Ensure that your bot has the necessary permissions in the Discord server, including:

- Send Messages
- Embed Links
- Attach Files
- Add Reactions
- Use External Emojis
- Manage Messages (for removing reactions)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please join our Discord support server:

[![Discord](https://img.shields.io/discord/1164455943451459645?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/ZZC8JVuyb6)

You can also open an issue on the GitHub repository.