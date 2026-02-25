# 开发环境配置说明-mac系统
Author:Wu Tao  
Status:Active  
Type:Informational  
Created:2026-02-24  
Post-History:2026-02-24 

## 前置条件
### mac系统
```
1.github克隆上游代码仓库：fastapi，为自己master，并建立develop分支
2.mac电脑生成ssh密钥，复制公钥内容，在GitHub后端设置中新增配置1个ssh公钥，可配多个
3.git检出项目代码到mac目录/Users/wutao/code/：git clone -b develop git@github.com:imhear/fastapi.git  
4.IDE中，右键/Users/wutao/code/fastapi/fastapi -> Mark Directory As -> Sources Root  
5.下载并安装mac版数据库软件:终端中先安装Homebrew，再使用Homebrew安装PostgreSQL服务
6.确认已上一步附带安装可视化数据库操作软件:pgAdmin 4（首次打开设置超级管理员密码，后面要用）
7.下载并安装IDE：PyCharm 2024.3.4 (Community Edition)  
8.使用pyenv下载并安装python：python-3.13.12
```

## 第1步：新建虚拟环境并激活
### pycharm命令行中
```pycharm命令行中
在终端执行
```

### 在IDE中，为项目配置新python解释器
PyCharm - Settings - fastapi - Python Interpreter - Add Interpreter - Add Local Interpreter - 解释器选择：/Users/wutao/code/fastapi/.venv/Scripts/python.exe - Apply - OK

## 第2步：Python虚拟环境中使用uv安装依赖
### python虚拟环境中
```python虚拟环境中
(.venv) wutaodeMacBook-Pro:fastapi wutao$ uv sync
Resolved 252 packages in 9ms
      Built fastapi @ file:///Users/wutao/code/fastapi
⠋ Preparing packages... (232/233)
Prepared 233 packages in 8m 13s
Installed 233 packages in 1.38s
 + a2wsgi==1.10.10
 + ag-ui-protocol==0.1.10
 + aiohappyeyeballs==2.6.1
 + aiohttp==3.13.3
 + aiosignal==1.4.0
 + annotated-doc==0.0.4
 + annotated-types==0.7.0
 + anthropic==0.78.0
 + anyio==4.12.1
 + argcomplete==3.6.3
 + argon2-cffi==25.1.0
 + argon2-cffi-bindings==25.1.0
 + asttokens==3.0.1
 + attrs==25.4.0
 + authlib==1.6.7
 + babel==2.18.0
 + backrefs==6.1
 + beartype==0.22.9
 + black==26.1.0
 + blinker==1.9.0
 + boto3==1.42.43
 + botocore==1.42.43
 + cachetools==7.0.0
 + cairocffi==1.7.1
 + cairosvg==2.8.2
 + certifi==2026.1.4
 + cffi==2.0.0
 + charset-normalizer==3.4.4
 + click==8.3.1
 + cloudpickle==3.1.2
 + cohere==5.20.4
 + colorama==0.4.6
 + coverage==7.13.3
 + croniter==6.0.0
 + cross-web==0.4.1
 + cryptography==46.0.5
 + cssselect2==0.8.0
 + cyclic==1.0.0
 + cyclopts==4.5.1
 + defusedxml==0.7.1
 + dirty-equals==0.11
 + diskcache==5.6.3
 + distro==1.9.0
 + dnspython==2.8.0
 + docstring-parser==0.17.0
 + docutils==0.22.4
 + email-validator==2.3.0
 + eval-type-backport==0.3.1
 + exceptiongroup==1.3.1
 + executing==2.2.1
 + fakeredis==2.33.0
 + fastapi==0.132.0 (from file:///Users/wutao/code/fastapi)
 + fastavro==1.12.1
 + fastmcp==2.14.5
 + filelock==3.20.3
 + flask==3.1.3
 + frozenlist==1.8.0
 + fsspec==2026.2.0
 + genai-prices==0.0.52
 + ghp-import==2.1.0
 + gitdb==4.0.12
 + gitpython==3.1.46
 + google-auth==2.48.0
 + google-genai==1.62.0
 + googleapis-common-protos==1.72.0
 + graphql-core==3.2.7
 + greenlet==3.3.1
 + griffe-typingdoc==0.3.1
 + griffe-warnings-deprecated==1.1.1
 + griffelib==2.0.0
 + groq==1.0.0
 + grpcio==1.78.0
 + h11==0.16.0
 + hf-xet==1.2.0
 + hjson==3.1.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + httpx-sse==0.4.3
 + huggingface-hub==0.36.2
 + idna==3.11
 + importlib-metadata==8.7.1
 + iniconfig==2.3.0
 + inline-snapshot==0.31.1
 + invoke==2.2.1
 + itsdangerous==2.2.0
 + jaraco-classes==3.4.0
 + jaraco-context==6.1.0
 + jaraco-functools==4.4.0
 + jieba==0.42.1
 + jinja2==3.1.6
 + jiter==0.13.0
 + jmespath==1.1.0
 + jsonref==1.1.0
 + jsonschema==4.26.0
 + jsonschema-path==0.3.4
 + jsonschema-specifications==2025.9.1
 + keyring==25.7.0
 + librt==0.7.8
 + logfire==4.22.0
 + logfire-api==4.22.0
 + lupa==2.6
 + markdown==3.10.1
 + markdown-include-variants==0.0.8
 + markdown-it-py==4.0.0
 + markupsafe==3.0.3
 + mcp==1.26.0
 + mdurl==0.1.2
 + mdx-include==1.4.2
 + mergedeep==1.3.4
 + mistralai==1.9.11
 + mkdocs==1.6.1
 + mkdocs-autorefs==1.4.3
 + mkdocs-get-deps==0.2.0
 + mkdocs-macros-plugin==1.5.0
 + mkdocs-material==9.7.1
 + mkdocs-material-extensions==1.3.1
 + mkdocs-redirects==1.2.2
 + mkdocstrings==1.0.2
 + mkdocstrings-python==2.0.3
 + more-itertools==10.8.0
 + multidict==6.7.1
 + mypy==1.19.1
 + mypy-extensions==1.1.0
 + nexus-rpc==1.2.0
 + openai==2.17.0
 + openapi-pydantic==0.5.1
 + opentelemetry-api==1.39.1
 + opentelemetry-exporter-otlp-proto-common==1.39.1
 + opentelemetry-exporter-otlp-proto-http==1.39.1
 + opentelemetry-instrumentation==0.60b1
 + opentelemetry-instrumentation-httpx==0.60b1
 + opentelemetry-proto==1.39.1
 + opentelemetry-sdk==1.39.1
 + opentelemetry-semantic-conventions==0.60b1
 + opentelemetry-util-http==0.60b1
 + orjson==3.11.7
 + outcome==1.3.0.post0
 + packaging==25.0
 + paginate==0.5.7
 + pathable==0.4.4
 + pathspec==1.0.4
 + pathvalidate==3.3.1
 + pillow==12.1.1
 + platformdirs==4.5.1
 + playwright==1.58.0
 + pluggy==1.6.0
 + prek==0.3.2
 + prometheus-client==0.24.1
 + prompt-toolkit==3.0.52
 + propcache==0.4.1
 + protobuf==6.33.5
 + pwdlib==0.3.0
 + py-key-value-aio==0.3.0
 + py-key-value-shared==0.3.0
 + pyasn1==0.6.2
 + pyasn1-modules==0.4.2
 + pycparser==3.0
 + pydantic==2.12.5
 + pydantic-ai==1.62.0
 + pydantic-ai-slim==1.62.0
 + pydantic-core==2.41.5
 + pydantic-evals==1.56.0
 + pydantic-graph==1.62.0
 + pydantic-settings==2.12.0
 + pydocket==0.17.5
 + pyee==13.0.0
 + pygithub==2.8.1
 + pygments==2.19.2
 + pyjwt==2.11.0
 + pymdown-extensions==10.20.1
 + pynacl==1.6.2
 + pyperclip==1.11.0
 + pytest==9.0.2
 + pytest-codspeed==4.2.0
 + python-dateutil==2.9.0.post0
 + python-dotenv==1.2.1
 + python-json-logger==4.0.0
 + python-multipart==0.0.22
 + python-slugify==8.0.4
 + pytokens==0.4.1
 + pytz==2025.2
 + pyyaml==6.0.3
 + pyyaml-env-tag==1.1
 + rcslice==1.1.0
 + redis==7.1.0
 + referencing==0.36.2
 + regex==2026.1.15
 + requests==2.32.5
 + rich==14.3.2
 + rich-rst==1.3.2
 + rpds-py==0.30.0
 + rsa==4.9.1
 + ruff==0.15.0
 + s3transfer==0.16.0
 + shellingham==1.5.4
 + six==1.17.0
 + smmap==5.0.2
 + sniffio==1.3.1
 + sortedcontainers==2.4.0
 + sqlalchemy==2.0.46
 + sqlmodel==0.0.32
 + sse-starlette==3.2.0
 + starlette==0.52.1
 + strawberry-graphql==0.291.2
 + super-collections==0.6.2
 + temporalio==1.20.0
 + tenacity==9.1.3
 + termcolor==3.3.0
 + text-unidecode==1.3
 + tiktoken==0.12.0
 + tinycss2==1.5.1
 + tokenizers==0.22.2
 + tqdm==4.67.3
 + trio==0.32.0
 + typer==0.21.1
 + types-orjson==3.6.2
 + types-protobuf==6.32.1.20251210
 + types-requests==2.32.4.20260107
 + types-ujson==5.10.0.20250822
 + typing-extensions==4.15.0
 + typing-inspection==0.4.2
 + ujson==5.11.0
 + urllib3==2.6.3
 + uvicorn==0.40.0
 + watchdog==6.0.0
 + wcwidth==0.5.3
 + webencodings==0.5.1
 + websockets==15.0.1
 + werkzeug==3.1.5
 + wrapt==1.17.3
 + xai-sdk==1.6.1
 + yarl==1.22.0
 + zipp==3.23.0
(.venv) wutaodeMacBook-Pro:fastapi wutao$  
```

验证安装
安装完成后，运行测试确认一切正常：
如果所有测试通过，说明依赖安装成功，环境已准备就绪。
```
bash
pytest tests/
```

```
1项未通过

问题原因
fastapi 的 CLI 功能由 fastapi-cli 包提供，它属于 standard 可选依赖组。

你当前安装的依赖可能只包含了核心包（fastapi 本身）以及测试依赖（test 组），但未包含 standard 组。

因此运行 fastapi dev 时，系统提示安装 fastapi[standard]。

解决方案
安装 standard 组（以及可能需要的其他组，如 test 已经安装，但为了完整可一并安装）。推荐使用以下命令：

bash
# 在虚拟环境（.venv）已激活的状态下执行
uv pip install -e ".[standard,test]"
或者如果你想安装所有可选依赖（包括文档、标准、测试等），可以尝试：
```

```
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(.venv) wutaodeMacBook-Pro:fastapi wutao$ uv pip install -e ".[standard,test]"
Resolved 42 packages in 7.15s
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 11 packages in 4.81s
Uninstalled 1 package in 6ms
Installed 11 packages in 14ms
 ~ fastapi==0.132.0 (from file:///Users/wutao/code/fastapi)
 + fastapi-cli==0.0.23
 + fastapi-cloud-cli==0.13.0
 + fastar==0.8.0
 + httptools==0.7.1
 + pydantic-extra-types==2.11.0
 + rich-toolkit==0.19.4
 + rignore==0.7.6
 + sentry-sdk==2.53.0
 + uvloop==0.22.1
 + watchfiles==1.1.1
warning: The package `fastapi @ file:///Users/wutao/code/fastapi` does not have an extra named `test`
(.venv) wutaodeMacBook-Pro:fastapi wutao$
```

