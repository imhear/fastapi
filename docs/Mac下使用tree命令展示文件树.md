
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(.venv) wutaodeMacBook-Pro:fastapi wutao$ 
tree -I '.venv|docs|docs_src|tests|__pycache__'
.
├── CITATION.cff
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── fastapi
│   ├── __init__.py
│   ├── __main__.py
│   ├── _compat
│   │   ├── __init__.py
│   │   ├── shared.py
│   │   └── v2.py
│   ├── applications.py
│   ├── background.py
│   ├── cli.py
│   ├── concurrency.py
│   ├── datastructures.py
│   ├── dependencies
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── encoders.py
│   ├── exception_handlers.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── middleware
│   │   ├── __init__.py
│   │   ├── asyncexitstack.py
│   │   ├── cors.py
│   │   ├── gzip.py
│   │   ├── httpsredirect.py
│   │   ├── trustedhost.py
│   │   └── wsgi.py
│   ├── openapi
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── docs.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── param_functions.py
│   ├── params.py
│   ├── py.typed
│   ├── requests.py
│   ├── responses.py
│   ├── routing.py
│   ├── security
│   │   ├── __init__.py
│   │   ├── api_key.py
│   │   ├── base.py
│   │   ├── http.py
│   │   ├── oauth2.py
│   │   ├── open_id_connect_url.py
│   │   └── utils.py
│   ├── staticfiles.py
│   ├── templating.py
│   ├── testclient.py
│   ├── types.py
│   ├── utils.py
│   └── websockets.py
├── fastapi-slim
│   └── README.md
├── pyproject.toml
├── scripts
│   ├── contributors.py
│   ├── coverage.sh
│   ├── deploy_docs_status.py
│   ├── doc_parsing_utils.py
│   ├── docs.py
│   ├── format.sh
│   ├── general-llm-prompt.md
│   ├── label_approved.py
│   ├── lint.sh
│   ├── mkdocs_hooks.py
│   ├── notify_translations.py
│   ├── people.py
│   ├── playwright
│   │   ├── cookie_param_models
│   │   │   └── image01.py
│   │   ├── header_param_models
│   │   │   └── image01.py
│   │   ├── json_base64_bytes
│   │   │   └── image01.py
│   │   ├── query_param_models
│   │   │   └── image01.py
│   │   ├── request_form_models
│   │   │   └── image01.py
│   │   ├── separate_openapi_schemas
│   │   │   ├── image01.py
│   │   │   ├── image02.py
│   │   │   ├── image03.py
│   │   │   ├── image04.py
│   │   │   └── image05.py
│   │   └── sql_databases
│   │       ├── image01.py
│   │       └── image02.py
│   ├── sponsors.py
│   ├── test-cov-html.sh
│   ├── test.sh
│   ├── topic_repos.py
│   ├── translate.py
│   └── translation_fixer.py
└── uv.lock

17 directories, 86 files
(.venv) wutaodeMacBook-Pro:fastapi wutao$ pwd
/Users/wutao/code/fastapi
(.venv) wutaodeMacBook-Pro:fastapi wutao$ 

