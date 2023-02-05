Template Telegram Bot with Webhooks, CaptchaProtect, Throttling, AdminPanel, I18n internationalization
==================================================

### How to start

1. Edit code in a correspoing way

2. Upadte `pip` and `setuptools` packages

```shell
pip install -U setuptools pip 
```

3. Install bot

```shell
pip install .
```

And also install requirements.txt

```shell
pip install -r requirements.txt
```

4. Create and fill `.env` file ([example](env_example))

5. Edit your `.po` files with languages and compile them

```shell
pybabel compile -d bot/locales -D messages
```

6. Add a 2 services to your linux machine ([example](tg_bot.example.service)) ([example](tg_captcha.example.service))

7. Turn on services

```shell
systemctl enable tg_bot
systemctl enable tg_captcha
```

8. Start bot to check

```shell
systemctl start tg_bot
```

9. Use, edit
