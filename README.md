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

5. To use mulit-language, run the `run.bat` file after you've worked through the whole bot

It will create a `.pot` file with a translation template, then create a compiled translation using a program, such as `Poedit`

6. Start bot to check

```shell
python3 app.py
```

7. Use, edit
