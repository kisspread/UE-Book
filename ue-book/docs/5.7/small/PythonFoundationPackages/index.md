# Python Foundation Packages

> Common Python packages such as NumPy and PyTorch used by engine plugins

| 属性 | 值 |
|---|---|
| 中文名 | Python 基础包 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（第三方 Python 包：NumPy, PyTorch, 等） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonFoundationPackages) | |

## 用途

Python Foundation Packages 是一个**纯内容插件**，为 Unreal Engine 的 Python 脚本环境（通过 `PythonScriptPlugin` 提供）预先打包并安装了常用的科学计算和数据科学 Python 库。它解决了以下问题：

- **开发者不需要手动安装** NumPy、PyTorch 等重型 Python 包到引擎的嵌入式 Python 环境中。
- **版本兼容性**：提供经过 Epic 测试并确认与 UE 特定版本兼容的包版本，避免依赖冲突或 API 不匹配。
- **支持机器学习工作流**：为 ML Deformer、Learning Agents 等机器学习相关插件提供底层依赖（NumPy、PyTorch、MLflow 等）。

> 该插件本身不包含任何 C++ 模块或蓝图节点；所有功能通过 Python 脚本调用。

## 使用场景

- 你需要在 UE 中使用 **NumPy** 进行高效数组运算、数学变换或数据预处理。
- 你正在开发或使用 **ML Deformer**、**Learning Agents** 等需要 PyTorch 的机器学习插件。
- 你需要通过 Python 脚本在编辑器或运行时执行科学计算（例如读取 CSV、矩阵运算）。
- 你希望避免手动管理嵌入式 Python 的 site-packages，直接获得一个“开箱即用”的 Python 科学环境。

## 蓝图用法

该插件不提供任何蓝图暴露的节点或函数。所有功能只能通过 Python 脚本访问。在 Blueprint 中，你可以通过 **Execute Python Script** 节点调用 Python 代码。

### 在蓝图中使用 Python 调用 NumPy

创建一个 `Execute Python Script` 节点，将以下脚本填入命令参数：

```python
import numpy as np
arr = np.array([1, 2, 3])
print(arr.mean())  # 输出均值
```

然后通过字符串输出或其他方式获取结果。

## C++ 用法

该插件不包含 C++ 模块，也没有头文件。如果你在 C++ 中需要调用 Python，请依赖 `PythonScriptPlugin` 模块，并通过 `PythonScriptLibrary` 执行脚本。示例：

```cpp
#include "PythonScriptLibrary.h"

void YourFunction()
{
    FString Script = TEXT("import numpy as np\nprint(np.__version__)");
    UPythonScriptLibrary::ExecuteConsoleCommand(GetWorld(), Script, true);
}
```

## Demo 示例

无（纯依赖包，无需创建项目）。启用插件后，即可在 UE Python 控制台或脚本中测试：

```python
# 在 UE 编辑器 -> 窗口 -> 开发者工具 -> Python 控制台
import numpy
print(numpy.__version__)

import torch
print(torch.__version__)
```

如果打印出版本号，说明包已成功加载。

## 模块依赖

该插件不包含任何 C++ 模块，因此无需在 `Build.cs` 中添加依赖。但是，要使用其提供的 Python 包，您必须同时启用：

| 插件/模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | 提供 UE 内部 Python 3 解释器环境 |
| （间接）`ML Deformer` 或 `Learning Agents` | 如果需要使用这些机器学习插件，它们会依赖本插件 |

**注意**：您自己的插件如果需要在 C++ 中调用 Python，需在 `Build.cs` 中添加 `PythonScriptPlugin` 依赖（Runtime 类型）。

## 维护状态

### 近期更新

| 日期 | Hash | Commit |
|---|---|---|
| 2025-06-20 | `35f8ecb8` | 将 PyTorch 要求移入独立的 `PythonMLPackages` 插件（拆分） |
| 2025-03-28 | `bb99a74d` | 更新 numpy 至 1.26.4，torch 至 2.5.1 |
| 2025-02-25 | `b591fbf2` | 更新兼容的 charset-normalizer（2.1.×） |
| 2025-02-20 | `5ff67eb5` | 为 Learning Agents 添加 MLflow 作为日志/实验跟踪选项 |
| 2024-08-29 | `5dc1d36d` | 更新 torch 至 v2.4.0 以兼容 ML Deformer |

### 维护评价

- **创建时间**：2024-08（约 1 年前），属于较新的插件。
- **更新频率**：活跃。近半年有 4 次实质性更新（包括版本升级和功能拆分）。
- **活跃维护**：是。Epic 正在持续跟进 Python 生态变化（如将 PyTorch 独立出去加强模块化）。
- **已知问题/限制**：作为 Experimental 插件，API/包版本可能随引擎迭代变化；部分包（如 PyTorch）体积较大，会增加引擎包体积。
- **推荐使用**：✅ 推荐。如果你需要 NumPy / PyTorch 等科学计算，这是最佳（甚至唯一）的官方方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PythonFoundationPackages)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/scripting-with-python-in-unreal-engine/)（通用 Python 脚本指南）
- [PythonScriptPlugin 文档](https://docs.unrealengine.com/5.7/en-US/python-scripting-in-unreal-engine/)