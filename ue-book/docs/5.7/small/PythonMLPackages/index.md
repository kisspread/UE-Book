# Python ML Package

> Auto-install Pytorch and related ML packages used by engine plugins

| 属性 | 值 |
|---|---|
| 中文名 | Python 机器学习包 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯配置插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonMLPackages) | |

## 用途

本插件是 UE5 的 **Python 机器学习包自动管理器**。它不提供任何可调用的功能或 UI，而是在引擎启动时自动检测并安装 PyTorch 及其主要依赖（如 torchvision、torchaudio 等），为其他依赖 Python ML 能力的 Editor Utility 或插件提供运行环境。

其核心价值在于：

- **零手动配置**：开发者无需在目标机器上手动 pip install PyTorch，插件会在引擎首次使用 ML 功能时自动完成安装。
- **依赖隔离**：将机器学习包的安装逻辑与具体使用 ML 的插件（如 "Python Foundation Packages"）分离，降低耦合。
- **版本控制**：通过插件内的 Python 需求文件（`requirements.txt`）固定 PyTorch 版本，确保所有使用该环境的功能一致性。

## 使用场景

- **开发 AI 驱动的编辑器工具**：例如图像生成、场景理解、自动 Logo 放置等需要运行时调用 PyTorch 模型的功能。
- **集成第三方 ML 插件**：如果需要让用户一键启用基于 PyTorch 的 Python 脚本，本插件是前置条件。
- **团队协作标准化**：确保所有团队成员和 CI 机器上安装的 PyTorch 版本一致，避免“在我机器上能跑”问题。

## 蓝图用法

本插件无暴露给蓝图的 C++ 函数或属性。启用后，Python 脚本环境（`DeveloperTools > Python Console`）将自动可用 PyTorch 包。

### Python 脚本示例（在编辑器控制台运行）

```python
import torch
print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
```

如果安装成功，将输出类似：
```
PyTorch version: 2.4.0
CUDA available: False
```

## C++ 用法

本插件不提供 C++ API。它是一个纯配置/内容插件，所有逻辑通过 Python 脚本和引擎的包管理基础设施实现。

### 头文件引入

不需要额外头文件。只需在 `Build.cs` 中添加模块依赖。

### 模块依赖

如果要让你的插件在 Python ML 包可用时执行操作，需要在 `Build.cs` 中依赖 `PythonMLPackages` 模块并监听可用性事件（如果插件将来提供 C++ 入口）。**但当前版本无此能力**。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin`（隐式） | Python 脚本宿主，本插件的包安装成功后，用户可直接在该环境中使用 ML 库 |

本插件无 C++ 代码，因此对其他模块无编译期依赖。

## 维护状态

### 近期更新

- 2025-12-18 `b4bafcd3` Merge fix for extra download dir to support pytorch download wheel filtering.
- 2025-06-20 `35f8ecb8` PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin

### 维护评价

插件创建至今不足一年，已有一个功能性修复提交，说明团队在持续关注。作为实验性插件，功能单一但稳定，适合作为其他 ML 相关插件的前置依赖。

**⚠️ 注意事项**：
- 自动安装可能因网络环境失败（需要访问 `pypi.org` / `download.pytorch.org`），建议在内网环境中准备离线 wheel 缓存。
- 该插件目前仅支持编辑器环境，打包后的游戏无法使用。
- 不保证与所有 Python 包版本兼容，如果遇到冲突，可在 `Engine/Plugins/Experimental/PythonMLPackages/Python/requirements.txt` 中调整版本号后重启编辑器。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonMLPackages)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-scripting-in-unreal-engine)（UE5 Python 脚本通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonMLPackages/Tests)（如果存在）