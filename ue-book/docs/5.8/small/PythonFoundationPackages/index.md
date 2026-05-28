# Python Foundation Packages

> Common Python packages such as NumPy and PyTorch used by engine plugins

| 属性 | 值 |
|---|---|
| 中文名 | 基础 Python 包 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 库） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-11-08 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonFoundationPackages) | |

## 用途

Python Foundation Packages 插件本身不包含任何 C++ 或蓝图逻辑代码。它的核心作用是充当一个**Python 依赖包分发容器**。它预置和打包了数据科学及机器学习领域常用的 Python 库（例如 NumPy, PyTorch），并确保这些库版本兼容、依赖正确。

**解决的问题**：当使用 Unreal Engine 的 Python 脚本环境（如 Python Editor Script Plugin）或相关的机器学习插件（如 Learning Agents）时，用户可能需要使用 NumPy 进行数值计算、使用 PyTorch 进行模型训练和推理。手动在操作系统中安装和配置这些 Python 环境繁琐且容易出现版本冲突。此插件通过 Engine 内置的方式，简化了这些基础库的部署和管理。

**为什么存在**：它是 UE5 Python 及 ML 生态系统的**基石插件**，为其他高级脚本或 AI/ML 插件提供运行时所依赖的 Python 库。

## 使用场景

- 你希望在 Unreal Editor 的 Python 控制台中，使用 NumPy 数组进行高效的矩阵或科学计算。
- 你正在使用 `Learning Agents` 插件来训练游戏 AI，其中涉及基于 PyTorch 的强化学习或模仿学习模型。
- 你编写的自定义 Python 脚本需要处理复杂数据，需要用到 Pandas（通常依赖 NumPy）等数据分析库。
- 任何需要在 UE5 内部 Python 环境中使用数据科学相关第三方库的场景。

## 蓝图用法

本插件是纯内容（Python 库）插件，**不包含任何蓝图节点或蓝图可调用函数**。
它的作用是为其他插件（如 `PythonScriptPlugin`， `LearningAgents`）的蓝图功能提供底层 Python 库支持。例如，当 `LearningAgents` 蓝图节点需要调用 PyTorch 时，依赖的就是本插件提供的运行时。

## C++ 用法

本插件不包含任何 C++ 模块或源代码。它作为内容依赖，被其他 C++ 模块或蓝图在运行时间接引用。
通常，开发者在项目的 `Build.cs` 中不会直接依赖此插件，而是依赖需要它的上层插件（如 `PythonScriptPlugin`， `LearningAgents`），这些上层插件会处理对 Python 环境及此基础包插件的隐式依赖。

## Demo 示例

由于本插件无自身代码，示例展示如何在其上层插件 `PythonScriptPlugin` 中使用它提供的库。

### 头文件引入

```cpp
// 使用 Python 脚本引擎的头文件
#include "IPythonScriptPlugin.h"
```

### 基本用法（C++ 中执行使用了 NumPy 的 Python 脚本）

```cpp
// 在某个 Actor 的 BeginPlay 中执行一段使用了 NumPy 的 Python 脚本
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    if (IPythonScriptPlugin* PythonPlugin = IPythonScriptPlugin::Get())
    {
        const FString PythonScript = TEXT(R"(
import numpy as np
# 创建一个 NumPy 数组
arr = np.array([1, 2, 3, 4, 5])
# 计算平均值
mean_val = np.mean(arr)
print(f"NumPy array: {arr}, Mean: {mean_val}")
)");

        PythonPlugin->ExecPythonCommand(*PythonScript);
    }
}
// 代码逻辑：通过 IPythonScriptPlugin 接口执行包含 `import numpy as np` 的 Python 代码。
// NumPy 库即由 PythonFoundationPackages 插件提供。
```

### 进阶用法（与上层插件 Learning Agents 结合）

本插件的典型使用场景是作为 `LearningAgents` 等插件的隐式依赖。开发者在使用这些高级插件的功能时，会自动用到此处的 Python 库。
例如，当使用 `LearningAgents` 训练一个使用神经网络的 AI 代理时，其底层训练循环会调用 `PythonFoundationPackages` 中的 PyTorch。

## 模块依赖

本插件自身是纯内容插件，**无特殊依赖（仅标准 Core/Engine/Slate 等）**。

对于**使用此插件的开发者**，你的项目或模块通常需要间接依赖：
| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | 用于在 UE 内运行 Python 脚本，本插件为其提供运行时库 |
| （其他上层插件） | 如 `LearningAgents`，它会在内部依赖此插件以使用 PyTorch 等库 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 及其依赖拆分到新的 PythonMLPackages 插件中 |
| 2025-03-28 | `bb99a74d` | PythonFoundationPackages: Update to numpy 1.26.4 and torch 2.5.1 | 更新 NumPy 到 1.26.4， PyTorch 到 2.5.1 |
| 2025-02-25 | `b591fbf2` | PythonFoundationPackages: Updated foundation packages to include compatible charset-normalizer (2.1. | 更新基础包以包含兼容版本的 charset-normalizer (2.1.x) |
| 2024-08-29 | `5dc1d36d` | PythonFoundationPackages: Update torch to v2.4.0 to work correctly with ML Deformer. | 更新 PyTorch 到 v2.4.0 以兼容 ML Deformer 插件 |

### 维护评价

- **活跃维护**：插件创建于 2021 年末，但维护状态非常活跃。最近一次实质性更新（库版本更新和依赖拆分）发生在 **2025 年 6 月**，距今仅约 2 个月。
- **评价**：作为 UE5 Python/ML 生态系统的底层依赖包管理器，Epic Games 持续为其更新第三方 Python 库的版本，以兼容新的引擎功能（如 ML Deformer）并修复安全或兼容性问题。它是一个关键的基础插件，推荐在需要 UE 内置 Python 数据科学生态时使用。需要注意，它默认是**实验性**且**默认不启用**，需要手动在插件管理器中开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PythonFoundationPackages) (纯内容插件，主要包含库文件和配置)
- 官方文档：无
- 测试用例：无独立测试用例，其功能通过依赖它的上层插件（如 LearningAgents）进行间接验证。