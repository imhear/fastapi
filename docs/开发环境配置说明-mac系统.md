# 开发环境配置说明-mac系统
Author:Wu Tao  
Status:Active  
Type:Informational  
Created:2026-02-24  
Post-History:2026-03-10 

## 前置条件
### mac系统
```
1.github克隆上游代码仓库：fastapi，为自己master，并建立develop分支
2.mac电脑生成ssh密钥，复制公钥内容，在GitHub后端设置中新增配置1个ssh公钥，可配多个
3.git检出项目代码到mac目录/Use[fastapi](../../fastapi)rs/wutao/code/：git clone -b develop git@github.com:imhear/fastapi.git  
4.IDE中，右键/Users/wutao/code/fastapi/fastapi -> Mark Directory As -> Sources Root  
5.下载并安装mac版数据库软件:终端中先安装Homebrew，再使用Homebrew安装PostgreSQL服务
6.确认已上一步附带安装可视化数据库操作软件:pgAdmin 4（首次打开设置超级管理员密码，后面要用）
7.下载并安装IDE：PyCharm 2024.3.4 (Community Edition)  
8.使用pyenv下载并安装python：python-3.13.12
```

## 第1步：新建虚拟环境并激活
### pycharm命令行中
```在终端执行

前置步骤：删除当前目录的版本配置文件（推荐，临时生效）
# 进入fastapi目录（你已在该目录）
cd /Users/wutao/code/fastapi
# 删除强制指定3.11版本的文件
rm .python-version

一、先激活 pyenv 的 3.13.12 版本
pyenv 需要显式指定使用哪个版本，才能调用对应的 Python，步骤如下：
bash
运行
# 步骤1：在fastapi目录下，指定当前目录使用3.13.12（仅当前目录生效）
pyenv local 3.13.12

# 步骤2：验证pyenv是否切换成功
pyenv versions
# 输出应该是：
#   system
# * 3.13.12 (set by /Users/wutao/code/fastapi/.python-version)
# 注意*号要在3.13.12前面，说明已切换

# 步骤3：刷新shell，让版本生效
exec $SHELL

# 步骤4：验证Python版本（此时python3.13会指向pyenv的3.13.12）
python3 --version   # 应该输出 Python 3.13.12
python3.13 --version # 同样输出 Python 3.13.12
二、创建 3.13 的虚拟环境（此时已生效）
bash
运行
# 步骤1：用pyenv激活的3.13创建虚拟环境
python3 -m venv venv  # 因为已切换到3.13，直接用python3即可（等价于python3.13）

# 步骤2：激活虚拟环境
source venv/bin/activate

# 步骤3：最终验证（激活后终端前缀是(venv)）
python --version  # 必须输出 Python 3.13.12

# 实际执行结果
Last login: Tue Mar 10 14:53:30 on ttys001
wutao@wutaodeMacBook-Pro ~ % cd code/fastapi
wutao@wutaodeMacBook-Pro ~ % rm .python-version
wutao@wutaodeMacBook-Pro fastapi % pyenv local 3.13.12
wutao@wutaodeMacBook-Pro fastapi % pyenv versions
  system
* 3.13.12 (set by /Users/wutao/code/fastapi/.python-version)
wutao@wutaodeMacBook-Pro fastapi % exec $SHELL
wutao@wutaodeMacBook-Pro fastapi % python3 --version
Python 3.13.12
wutao@wutaodeMacBook-Pro fastapi % python3.13 --version
Python 3.13.12
wutao@wutaodeMacBook-Pro fastapi % python3 -m venv venv
wutao@wutaodeMacBook-Pro fastapi % source venv/bin/activate
(venv) wutao@wutaodeMacBook-Pro fastapi % python --version
Python 3.13.12
```

### 在IDE中，为项目配置新python解释器
PyCharm - Settings - Project:fastapi - Python Interpreter - Add Interpreter - Add Local Interpreter - 解释器选择：/Users/wutao/code/fastapi/.venv/Scripts/python.exe - Apply - OK

## 第2步：Python虚拟环境中使用uv安装依赖
### python虚拟环境中
```python虚拟环境中

The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(venv) wutaodeMacBook-Pro:fastapi wutao$ uv sync
warning: `VIRTUAL_ENV=venv` does not match the project environment path `.venv` and will be ignored; use `--active` to target the active environment instead
Using CPython 3.13.12 interpreter at: venv/bin/python
Creating virtual environment at: .venv
Resolved 259 packages in 2ms
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 20 packages in 4.86s
Installed 240 packages in 3.12s
 + a2wsgi==1.10.10
 + ag-ui-protocol==0.1.10
 + aiohappyeyeballs==2.6.1
 + aiohttp==3.13.3
 + aiosignal==1.4.0
 + annotated-doc==0.0.4
 + annotated-types==0.7.0
 + anthropic==0.83.0
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
 + click==8.2.1
 + cloudpickle==3.1.2
 + cohere==5.20.7
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
 + execnet==2.1.2
 + executing==2.2.1
 + fakeredis==2.33.0
 + fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
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
 + huggingface-hub==1.4.1
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
 + psutil==7.2.2
 + pwdlib==0.3.0
 + py-key-value-aio==0.3.0
 + py-key-value-shared==0.3.0
 + pyasn1==0.6.2
 + pyasn1-modules==0.4.2
 + pycparser==3.0
 + pydantic==2.12.5
 + pydantic-ai==1.63.0
 + pydantic-ai-slim==1.63.0
 + pydantic-core==2.41.5
 + pydantic-evals==1.63.0
 + pydantic-graph==1.63.0
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
 + pytest-codspeed==4.3.0
 + pytest-cov==7.0.0
 + pytest-sugar==1.1.1
 + pytest-timeout==2.4.0
 + pytest-xdist==3.8.0
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
 + strawberry-graphql==0.307.1
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
 + typer==0.24.1
 + typer-slim==0.21.2
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
 + werkzeug==3.1.6
 + wrapt==1.17.3
 + xai-sdk==1.6.1
 + yarl==1.22.0
 + zipp==3.23.0
(fastapi)) wutaodeMacBook-Pro:fastapi wutao$ 
```

验证安装
安装完成后，运行测试确认一切正常：
如果所有测试通过，说明依赖安装成功，环境已准备就绪。
```bash
pytest tests/

FAILED tests/test_fastapi_cli.py::test_fastapi_cli - assert 'Path does not exist non_existent_file.py' in 'To use the fastapi command, please install "fastapi[standard]":\n\n\tpip install "fastapi[standard]"\n\n'

Results (72.15s (0:01:12)):
    3133 passed
       1 failed
         - tests/test_fastapi_cli.py:10 test_fastapi_cli
       4 xfailed
       1 skipped
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
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv pip install -e ".[standard,test]"
Resolved 42 packages in 3.31s
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 5 packages in 1.01s
Uninstalled 1 package in 6ms
Installed 11 packages in 18ms
 ~ fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
 + fastapi-cli==0.0.24
 + fastapi-cloud-cli==0.14.1
 + fastar==0.8.0
 + httptools==0.7.1
 + pydantic-extra-types==2.11.0
 + rich-toolkit==0.19.7
 + rignore==0.7.6
 + sentry-sdk==2.54.0
 + uvloop==0.22.1
 + watchfiles==1.1.1
warning: The package `fastapi @ file:///Users/wutao/code/fastapi` does not have an extra named `test`
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```

再次验证安装
安装完成后，运行测试确认一切正常：
如果所有测试通过，说明依赖安装成功，环境已准备就绪。
```bash
pytest tests/

Results (50.17s):
    3134 passed
       4 xfailed
       1 skipped
```

IDE中项目根目录下创建如下文件夹及文件
```markdown
# app/main.py
from fastapi import FastAPI
from app.core.config import settings


def create_app() -> FastAPI:

    app = FastAPI(title=settings.PROJECT_NAME)

    return app


app = create_app()


from pydantic import BaseModel
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
```

IDE命令行以开发模式启动
```shell
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ fastapi dev

   FastAPI   Starting development server 🚀
 
             Searching for package file structure from directories with __init__.py files
             Importing from /Users/wutao/code/fastapi
 
    module   📁 app            
             ├── 🐍 __init__.py
             └── 🐍 main.py    
 
      code   Importing the FastAPI app object from the module with the following code:
 
             from app.main import app
 
       app   Using import string: app.main:app
 
    server   Server started at http://127.0.0.1:8000
    server   Documentation at http://127.0.0.1:8000/docs
 
       tip   Running in development mode, for production use: fastapi run
 
             Logs:
 
      INFO   Will watch for changes in these directories: ['/Users/wutao/code/fastapi']
      INFO   Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
      INFO   Started reloader process [30293] using WatchFiles
      INFO   Started server process [30298]
      INFO   Waiting for application startup.
      INFO   Application startup complete.
```

IDE命令行以生产模式启动
```shell
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uvicorn app.main:app --host 0.0.0.0 --port 8008 --reload
INFO:     Will watch for changes in these directories: ['/Users/wutao/code/fastapi']
INFO:     Uvicorn running on http://0.0.0.0:8008 (Press CTRL+C to quit)
INFO:     Started reloader process [30405] using WatchFiles
INFO:     Started server process [30409]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

安装DI容器依赖
```shell
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv add dependency-injector==4.48.3
Resolved 260 packages in 35.23s
      Built fastapi @ file:///Users/wutao/code/fastapi
      Built dependency-injector==4.48.3
Prepared 2 packages in 56.98s
Uninstalled 1 package in 13ms
Installed 2 packages in 9ms
 + dependency-injector==4.48.3
 ~ fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```

创建数据库实例
```shell
wutao@wutaodeMacBook-Pro ~ % createdb fastapi # 创建数据库
wutao@wutaodeMacBook-Pro ~ % psql -d fastapi # 验证数据库是否创建成功
psql (14.19 (Homebrew))
Type "help" for help.

fastapi=# # 进入 `fastapi=#` 提示符即成功，退出用 \q
wutao@wutaodeMacBook-Pro ~ % dropdb fastapi # 删除数据库，要先断开所有连接会话
wutao@wutaodeMacBook-Pro ~ %       
```

IDE中编辑数据库模型

安装Alembic数据库迁移工具
```shell
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv add alembic>=1.17.2
Resolved 262 packages in 3.93s
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 3 packages in 4.11s
Uninstalled 1 package in 3ms
Installed 3 packages in 7ms
 + alembic==1.18.4
 ~ fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
 + mako==1.3.10
(fastapi) wutaodeMacBook-Pro:fastapi wutao$
```

初始化 alembic（生成 alembic 文件夹和配置文件）
```shell
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ alembic init alembic
  Creating directory /Users/wutao/code/fastapi/alembic ...  done
  Creating directory /Users/wutao/code/fastapi/alembic/versions ...  done
  Generating /Users/wutao/code/fastapi/alembic/script.py.mako ...  done
  Generating /Users/wutao/code/fastapi/alembic/env.py ...  done
  Generating /Users/wutao/code/fastapi/alembic/README ...  done
  Generating /Users/wutao/code/fastapi/alembic.ini ...  done
  Please edit configuration/connection/logging settings in /Users/wutao/code/fastapi/alembic.ini before proceeding.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```
清理本地 Alembic 迁移文件（从零开始）
```shell
# 1. 删除 alembic/versions 下所有迁移文件（保留文件夹）
rm -rf alembic/versions/*
```

修改alembic.ini（数据库连接）
不用改，直接改env.py就行
```shell
# alembic/env.py 最终最终可运行版
from logging.config import fileConfig
import sys
from pathlib import Path

# 1. 项目根目录加入 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

# 2. 基础导入
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# 3. 导入配置和模型
from app.config.config import settings
from app.core.database import Base

# 4. 导入所有业务模型
from app.modules.dept.models import *
from app.modules.dept_position.models import *
from app.modules.dict.models import *
from app.modules.menu.models import *
from app.modules.permission.models import *
from app.modules.position.models import *
from app.modules.role.models import *
from app.modules.user.models import *

# 配置对象
config = context.config

# 设置数据库 URL（使用正确的 DATABASE_URL）
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 关联模型 MetaData
target_metadata = Base.metadata

# 命名规范
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

# 修复：移除 literal_binds，适配 autogenerate 命令
def run_migrations_online() -> None:
    """在线迁移（Alembic 官方推荐的 autogenerate 模式）"""
    # 使用同步引擎（autogenerate 不支持异步）
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
        await connectable.dispose()

    import asyncio
    asyncio.run(run_async_migrations())

def do_run_migrations(connection):
    """同步执行迁移逻辑"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        naming_convention=NAMING_CONVENTION,
        compare_type=True,          # 检测字段类型变化
        compare_server_default=True # 检测默认值变化
        # 关键：移除 literal_binds=True，解决冲突
    )

    with context.begin_transaction():
        context.run_migrations()

# 执行迁移（使用在线模式，适配 autogenerate）
if context.is_offline_mode():
    raise Exception("离线模式不支持 autogenerate，请使用在线模式")
else:
    run_migrations_online()
```

安装 asyncpg 驱动（PostgreSQL 异步驱动）
```shell
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv add asyncpg>=0.31.0
Resolved 263 packages in 3.90s
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 2 packages in 711ms
Uninstalled 1 package in 3ms
Installed 2 packages in 7ms
 + asyncpg==0.31.0
 ~ fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```


初始化数据库
```shell
# 1. 强制将数据库版本标记为最新（忽略历史差异）
alembic stamp head

# 2. 重新生成迁移脚本（覆盖初始化）
alembic revision --autogenerate -m "init_tables"

# 3. 执行迁移（应用表结构）
alembic upgrade head
```
```shell

The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ alembic stamp head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running stamp_revision  -> 56c5a51f17c2
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ alembic revision --autogenerate -m "init_tables"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.tables
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.types
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.constraints
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.defaults
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.comments
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_dept'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_dict'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_menu'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_permission'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_position'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_role'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_user'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_dept_position'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_dict_item'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_role_menu'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_role_permission'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_dept_position_role'
INFO  [alembic.autogenerate.compare.tables] Detected added table 'sys_dept_position_user'
  Generating /Users/wutao/code/fastapi/alembic/versions/3fec0df08af3_init_tables.py ...  done
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 56c5a51f17c2 -> 3fec0df08af3, init_tables
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```

清理本地 Alembic 迁移文件（从零开始）
```shell
# 1. 删除 alembic/versions 下所有迁移文件（保留文件夹）
rm -rf alembic/versions/*
```

常用 Alembic 命令（项目迁移）
```bash
# 生成迁移脚本（检测模型变化）
alembic revision --autogenerate -m "init_tables"

# 执行增量迁移（应用到数据库）
alembic upgrade head

# 回滚最后一次迁移
alembic downgrade -1

# 查看迁移历史
alembic history --verbose
```

安装安全相关依赖
```shell
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv add python-jose>=1.1.0
Resolved 265 packages in 4.61s
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 3 packages in 320ms
Uninstalled 1 package in 1ms
Installed 3 packages in 5ms
 + ecdsa==0.19.1
 ~ fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
 + python-jose==3.5.0
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```

安装 passlib 及 bcrypt 扩展（推荐方式）
```shell
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv add "passlib[bcrypt]"
Resolved 267 packages in 988ms
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 3 packages in 19.28s
Uninstalled 1 package in 2ms
Installed 3 packages in 6ms
 + bcrypt==5.0.0
 ~ fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
 + passlib==1.7.4
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```

有问题，需要降级依赖
```shell
The default interactive shell is now zsh.
To update your account to use zsh, please run `chsh -s /bin/zsh`.
For more details, please visit https://support.apple.com/kb/HT208050.
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv add bcrypt==4.3.0
Resolved 267 packages in 6.03s
      Built fastapi @ file:///Users/wutao/code/fastapi
Prepared 2 packages in 36.81s
Uninstalled 2 packages in 6ms
Installed 2 packages in 7ms
 - bcrypt==5.0.0
 + bcrypt==4.3.0
 ~ fastapi==0.135.1 (from file:///Users/wutao/code/fastapi)
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```

检查当前依赖版本
```shell
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ uv pip show bcrypt
Name: bcrypt
Version: 4.3.0
Location: /Users/wutao/code/fastapi/.venv/lib/python3.13/site-packages
Requires:
Required-by: fastapi
(fastapi) wutaodeMacBook-Pro:fastapi wutao$ 
```