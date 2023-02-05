Template telegram bot example
==============================

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

5. Add a 2 services to your linux machine ([example](tg_bot.example.service)) ([example](tg_captcha.example.service))

6. Turn on services

```shell
systemctl enable tg_bot
```

6. Start bot to check

```shell
systemctl start tg_bot
```

7. Use, edit
