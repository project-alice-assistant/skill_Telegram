#Telegram skill

## What it does
This skill allows you to chat with Alice or send her commands, with your phone, using the highly privacy centered Telegram app. The app is free and available for both Android and IOS.
In addition to this, A recent feature also adds the ability to send a emergency contact a Telegram message if you request help
(please see "Emergency help" section below)

## What it does not
Obviously, this skill replaces your physical voice, so it won't add new actions to Alice, but simply bridge your text messages to Alice.

## Install

### On your mobile device
- Go to your app store
- Download Telegram: [Android](https://play.google.com/store/apps/details?id=org.telegram.messenger), [IOS](https://apps.apple.com/app/telegram-messenger/id686449807)
- Once installed, open the app,search for a user named **BotFather** and start chatting with him.
- Send the message **/newbot** and answer the questions asked.
- At the end, you'll get a *token* which you need to insert in the Telegram skill settings. Don't want to type that long string by hand? Easy:
   - Go to [https://web.telegram.org/](https://web.telegram.org/)
   - Open the chat you had with **BotFather** and voilà!
- Navigate to Alice's interface skill page and open the Telegram skill settings
- Insert your token and save
- You can now search your bot in Telegram and start chatting with her!

### Permissions
You don't want people to find your bot and start messing with your home do you? So, by default, there's no user allowed. Text something to Alice. Alice will detect it, but won't let it through but will ask you if you allow that new user.

### I have audio inactive on my main unit, how to I add my permissions?
Text something to Alice, and head for your logs on the interface. She should have alerted you that someone unknown is texting her, giving you a username and user id combo, something like `Psycho/12345678`. Copy that combo and go for the skill settings. Paste it in the whitelist setting.

### What now?
Well.. Now you can just send message from your app or your browser to Alice, even when you're out in the wild! Want your bath ready when you get home? Text her from work before you leave! Enjoy!

### What's next
- Better multisession

### Emergency Help
The skill now has a feature that allows you to ask Alice for help if you have fallen and can't get back up to grab your phone etc

To use this feature:

From the skill settings...
- In the emergency contact list, add your contacts username/chatId. You can add as many as you like, just seperate them with a comma, 
example : Sue/12345678, Bob/87654321
- Enable "Confirm Emergency call" if you'd like to be asked confirmation regarding sending a emergency message.

If the unfortunate happens and you take a fall or need help. You can now ask Alice things such as :
- help me please
- Will you help me ?
- Help, call my emergency contact
