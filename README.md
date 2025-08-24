# Telegram Support Bot

यह Telegram बॉट किसी भी यूज़र के मैसेज को Admin तक पहुँचाता है और Admin का रिप्लाई उसी यूज़र तक भेज देता है।

## Deploy on Render
1. इस repo को fork/clone कीजिए।
2. Render पर New → Web Service → GitHub से कनेक्ट कीजिए।
3. Environment Variables में डालें:
   - BOT_TOKEN = आपका BotFather वाला टोकन
   - ADMIN_ID = आपका Telegram numeric ID
4. Build Command:
