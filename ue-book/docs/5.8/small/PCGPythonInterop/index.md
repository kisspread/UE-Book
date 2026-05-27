# Procedural Content Generation Framework (PCG) Python Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Editor Python Interpreter.

| 属性 | 值 |
|---|---|
| 中文名 | PCG Python 互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，测试资源） |
| 模块 | `PCGPythonInteropEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop) | |

## 用途

该插件为 Unreal Engine 的 PCG（程序化内容生成）框架提供 Python 互操作性，允许在 PCG 图的执行过程中运行 Python 脚本。它主要解决在 PCG 工作流中集成 Python 脚本能力的问题，让用户能够利用 Python 的灵活性和庞大的生态系统来处理或生成程序化数据。

具体来说，插件提供了两个核心 PCG 节点：
1.  **Execute Python Script**: 允许在 PCG 图中执行一段 Python 脚本（支持从属性输入、内联编辑或外部 `.py` 文件加载）。
2.  **Python Data Processor**: 提供一个更高级的节点，允许 Python 脚本通过一个轻量级的“桥接”对象（`UPCGPythonDataBridge`）直接访问和操作 PCG 的 `FPCGDataCollection`，支持动态输入输出引脚。

## 使用场景

-   **在 PCG 图中执行 Python 脚本**: 当标准的 PCG 节点无法满足复杂的数据生成或处理逻辑时，可以使用 Python 脚本节点。
-   **利用 Python 处理 PCG 数据**: 需要 Python 脚本直接读取 PCG 的输入数据集，并输出处理后的数据集到后续 PCG 节点。
-   **集成外部 Python 工具或库**: 将已有的 Python 脚本（如用于数据解析、算法计算）接入 PCG 工作流。
-   **需要快速原型验证**: 使用 Python 脚本快速迭代 PCG 数据生成逻辑。

## 蓝图用法

该插件主要面向 Python 脚本使用，其 C++ 类提供了一些供 Python 脚本调用的蓝图函数接口。

### 核心节点（Python 脚本中调用）

| 函数 | 说明 | 所在类 |
|---|---|---|
| `GetInputCollection` | 获取当前 PCG 执行的输入数据集合。 | `UPCGPythonDataBridge` |
| `SetOutputCollection` | 设置经 Python 脚本处理后的输出数据集合。 | `UPCGPythonDataBridge` |
| `AddToCollection` | 向输出数据集合中添加一条数据，并指定其引脚标签和标签。 | `UPCGPythonDataBridge` |

### 使用示例（在 Python 脚本中）

在 `Execute Python Script` 或 `Python Data Processor` 节点执行的 Python 脚本中，可以通过桥接对象（通常命名为 `pcg_bridge`）与 PCG 数据交互：

```python
import unreal

# 获取桥接对象
bridge = unreal.PCGPythonDataBridge.find_object("pcg_bridge")

# 获取输入数据
input_collection = bridge.get_input_collection()

# 处理数据（示例：简单地将输入数据传递到输出）
output_collection = input_collection

# 设置输出数据
bridge.set_output_collection(output_collection)

# 或者，使用 add_to_collection 逐步构建输出
# bridge.add_to_collection(some_data, "OutputPin", ["tag1"])
```

## C++ 用法

该插件的核心类均为 Editor 模块，主要供 PCG 框架内部及 Python 脚本调用，不直接供游戏运行时 C++ 代码使用。

### 头文件引入

```cpp
#include "Elements/PCGExecutePythonScript.h"
#include "Elements/PCGPythonDataProcessor.h"
```

### 基本用法（创建与配置节点）

以下示例展示了如何在 C++ 中获取或创建 `Execute Python Script` 节点的设置对象，并配置其属性。通常这些节点是通过编辑器 UI 放置到 PCG 图中的，代码仅用于说明其内部结构。

```cpp
// 假设我们有一个 UPCGGraph* MyPCGGraph
UPCGExecutePythonScriptSettings* ScriptSettings = NewObject<UPCGExecutePythonScriptSettings>();

// 设置脚本输入方式为“输入”（从某个属性读取脚本）
ScriptSettings->ScriptInputMethod = EPCGPythonScriptInputMethod::Input;
// 假设有一个属性选择器来指定包含脚本的属性
// ScriptSettings->ScriptSource = ...;

// 或者设置为从文件读取
// ScriptSettings->ScriptInputMethod = EPCGPythonScriptInputMethod::File;
// ScriptSettings->ScriptPath.FilePath = TEXT("/Game/Scripts/my_script.py");

// 将节点添加到图中
UPCGNode* NewNode = MyPCGGraph->AddNode(ScriptSettings);
```

### 进阶用法（了解动态引脚）

`Python Data Processor` 节点实现了 `IPCGDynamicPinsProvider` 接口，允许用户在编辑器中动态添加输入和输出引脚。

```cpp
// 在 Python Data Processor 的设置类中
UPCGPythonDataProcessorSettings* ProcessorSettings = NewObject<UPCGPythonDataProcessorSettings>();

// 该节点支持动态引脚
ProcessorSettings->HasDynamicPins(); // 返回 true

// 可以通过其内部容器访问和修改动态引脚定义
// FPCGDynamicPinContainer* InputContainer = ProcessorSettings->GetMutableDynamicPinContainer(EPCGPinDirection::Input);
// ... 对 InputContainer 进行操作
```

## Demo 示例

一个最小的 C++ 示例，展示如何在代码中实例化一个 `Python Data Processor` 节点并理解其主要属性。

**MyPCGScriptNode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Elements/PCGPythonDataProcessor.h"

class FMyPCGPythonNodeExample
{
public:
    void CreateAndConfigureNode();
};
```

**MyPCGScriptNode.cpp**
```cpp
#include "MyPCGScriptNode.h"

void FMyPCGPythonNodeExample::CreateAndConfigureNode()
{
    // 创建设置对象
    UPCGPythonDataProcessorSettings* Settings = NewObject<UPCGPythonDataProcessorSettings>();

    // 配置脚本来源为内联（默认）
    Settings->ScriptInputMethod = EPCGPythonScriptInputMethod::Input;

    // 获取默认的内联脚本（通常是一个简单的模板）
    // Settings->InlineScript 是 private 的，但可通过编辑器UI修改。

    // 此节点已配置为支持动态引脚和PCG数据桥接。
    // 在PCG图中添加此节点后，用户可以：
    // 1. 在节点上动态添加输入/输出引脚。
    // 2. 编写Python脚本，通过 `unreal.PCGPythonDataBridge` 对象读取输入引脚数据并写入输出引脚。

    // 此示例不直接执行节点，仅展示其创建。
    UE_LOG(LogTemp, Log, TEXT("Created a PCGPythonDataProcessorSettings object. It should be added to a PCGNode in a PCGGraph."));
}
```

## 模块依赖

该插件要求你的项目或模块必须启用并依赖以下插件（在 `.uplugin` 或 `.uproject` 中声明）：

| 模块/插件 | 用途 |
|---|---|
| `PCG` | 提供核心的程序化内容生成框架，是此插件的基础。 |
| `PythonScriptPlugin` | 提供 Unreal Editor 内的 Python 解释器环境，是执行 Python 脚本的必备插件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `d47477a3` | [PCG] Python Data Processor Node | 添加了功能更强大的 Python Data Processor 节点。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 清理了 StringBuilder 的构造逻辑。 |
| 2025-08-22 | `2de17507` | [PCG] Fixed bug causing Inline Constant not to respect required pin | 修复了内联脚本常量不尊重必需引脚的bug。 |
| 2025-07-14 | `002e7b67` | [PCG] Python Interop Plugin and Execute Python Script Node | 插件首次创建，包含 Execute Python Script 节点。 |

### 维护评价

-   **状态**: **维护中，但处于实验阶段**。插件创建于 2025 年中，至今约 1 年，且仍在持续更新和添加新功能（如最近的 Data Processor 节点）。
-   **活跃度**: 较高。最近半年有多次提交，包括功能添加和 Bug 修复。
-   **风险提示**: `.uplugin` 中明确标记为 `IsBetaVersion: true`，表明这是一个实验性/测试版功能。API 和行为在未来版本中可能发生变化。
-   **推荐度**: **推荐尝试使用，但需注意其 Beta 状态**。对于希望在 PCG 工作流中集成 Python 脚本的用户，这是目前官方提供的唯一方式。建议在非关键生产环境中先行试用，并关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/) (PCG 框架总览，该插件为扩展)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop/Tests)