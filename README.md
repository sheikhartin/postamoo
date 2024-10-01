## Postamoo

![GitHub repo status](https://img.shields.io/badge/status-active-green?style=flat)
![GitHub license](https://img.shields.io/github/license/sheikhartin/postamoo)
![GitHub contributors](https://img.shields.io/github/contributors/sheikhartin/postamoo)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/sheikhartin/postamoo)
![GitHub repo size](https://img.shields.io/github/repo-size/sheikhartin/postamoo)

Users can post multimedia content and interact with others.

### How to Use

Install the dependencies:

```
poetry install
```

Test it first:

```
poetry run pytest -rSp
```

Run the Postamoo and [Shenase](https://github.com/sheikhartin/shenase) servers:

```
poetry run uvicorn postamoo.main:app --reload --port 9507 --log-config log_config.json
```

Then navigate to http://127.0.0.1:9507/docs.

### License

This project is licensed under the Apache License 2.0 found in the [LICENSE](LICENSE) file in the root directory of this repository.
