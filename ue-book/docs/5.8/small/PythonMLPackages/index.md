# Python ML Package

> Auto-install Pytorch and related ML packages used by engine plugins

| 属性 | 值 |
|---|---|
| 中文名 | Python机器学习包 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（依赖包定义） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-06-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonMLPackages) | |

## 用途

**PythonMLPackages** 插件是一个专门用于管理 Python 机器学习生态系统依赖的**纯内容插件**。它本身不包含任何 C++ 代码或蓝图逻辑，其核心作用是通过配置文件，自动为 Unreal Engine 安装特定的、经过测试的机器学习 Python 库（主要是 PyTorch 及其相关依赖）。

它存在的根本原因是为了解决在 UE 环境中使用 Python 进行机器学习时常见的**版本冲突和环境配置难题**。将依赖声明集中管理，并与引擎的 Python 插件系统（PythonFoundationPackages）集成，确保了引擎内置的 ML 工具（如用于训练、数据导入或推理的插件）能够拥有一个一致、可靠且版本匹配的 Python 运行环境，避免用户手动 `pip install` 可能导致的不兼容问题。

## 使用场景

- 当你安装或启用了 Unreal Engine 中需要调用 PyTorch 等机器学习框架的插件（例如，用于计算机视觉、自然语言处理或强化学习的数据管线或训练工具）时，此插件会作为基础依赖被自动或手动启用。
- 当你开发自己的基于 Python 的机器学习工具链，并希望它能无缝集成到 UE 编辑器环境中时，可以依赖此插件提供的标准化 Python 包环境。
- 当你遇到其他插件报告 `torch` 或相关库未找到的错误时，可以检查并确保此插件已启用。

## 蓝图用法

此插件没有蓝图接口。其所有功能均在引擎启动时通过 Python 包管理系统自动执行，用户无需（也无法）在蓝图中直接操作它。相关的机器学习功能节点来自于其他依赖此环境的 ML 工具插件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 此插件不提供蓝图节点 | （无） |

### 使用示例（蓝图描述）

在蓝图中无法直接使用此插件。实际使用是隐式的：当其他包含 ML 功能的插件（如 `ScriptableToolsEditorMode` 或自定义的 Python 管线插件）被启用时，它们会自动确保此插件提供的 PyTorch 环境可用。

## C++ 用法

此插件没有 C++ 模块，因此无法在 C++ 中直接引入或调用。它为 Python 运行时环境提供基础，C++ 代码主要通过 `FPythonScriptPlugin` 或其他 Python 绑定机制来调用已安装的 Python ML 库。

### 头文件引入

不适用。

### 基本用法

不适用。但 C++ 开发者可以确保依赖此插件的 Python 环境，以便在通过 C++ 执行 Python 脚本时，这些脚本可以 `import torch`。

### 进阶用法

不适用。

## Demo 示例

此插件没有可编译的 C++ 示例。其主要“资产”是定义了要安装的 Python 包的配置文件（如 `*.requirements.txt` 或 JSON 文件）。一个最小的功能演示是确保插件被正确启用后，在引擎的 Python 控制台中运行以下命令：

```python
# 在 Unreal Editor 的 Python 控制台中执行
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```
如果输出了版本号且 CUDA 可用性状态正确，则表明此插件已成功完成其环境配置工作。

## 模块依赖

此插件本身无代码模块，但它通常与以下内容存在依赖关系：

| 模块 | 用途 |
|---|---|
| `PythonFoundationPackages` | 它是 `PythonFoundationPackages` 的子集或衍生插件，依赖其提供的 Python 解释器管理和基础包安装功能。 |
| **外部 Python 包** | 主要依赖 `torch`（PyTorch）及其关联库（如 `torchvision`, `torchaudio`）。具体版本和额外包由插件内的配置文件定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-12-11 | `cd07d004` | PythonMLPackages: Update ExtraDownloadURLs for torch to be cu-version specific (can no longer downlo | 更新了 PyTorch 的下载 URL，使其与 CUDA 版本更精确匹配，解决了可能无法下载特定版本的问题。 |
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 初始提交，将 PyTorch 的 Python 依赖从 PythonFoundationPackages 插件中分离出来，创建了此独立插件。 |

### 维护评价

- **创建时间**: 2025年6月20日，非常新的插件。
- **更新频率**: 自创建以来仅有1次实质性更新，频率很低。这符合其作为“依赖定义包”的性质，仅在底层依赖（如 PyTorch 发布新版本或需要调整下载源）变化时更新。
- **维护状态**: **活跃维护中**。最新的 commit (2025-12) 表明 Epic 仍在关注并维护此插件的兼容性，以确保引擎 ML 生态系统的正常运行。
- **已知限制**: 作为 Experimental 插件，其 API 和行为可能在未来版本中发生变化。它主要服务于 Epic 官方 ML 工具链，社区自定义用法可能需要额外适配。
- **推荐使用**: **推荐**。如果你需要使用 Unreal Engine 内置的、依赖 PyTorch 的机器学习功能，这是必不可少的底层支持插件。应保持其默认启用状态（或根据需要启用），不要手动修改其内容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonMLPackages)
- [官方文档]( ) （无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonMLPackages/Tests) （预期路径，如果存在）