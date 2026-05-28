# Procedural Content Generation Framework (PCG) Python Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Editor Python Interpreter.

| 属性 | 值 |
|---|---|
| 中文名 | PCG Python 互操作插件 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `PCGPythonInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop) | |

## 用途

该插件在**程序化内容生成框架**与**编辑器 Python 脚本系统**之间架起了一座桥梁。它允许开发者和设计师在 PCG 图（Graph）中直接执行 Python 脚本，从而利用 Python 的强大灵活性和丰富的库生态来处理 PCG 数据、实现自定义的生成逻辑、算法或工作流集成。

其核心价值在于：传统 PCG 节点提供标准化的数据操作，而 Python 脚本则提供了近乎无限的自定义能力。通过此插件，用户可以在不编写 C++ 的情况下，用 Python 实现复杂的生成规则、数据处理、调用外部 API 等，极大地扩展了 PCG 的应用范围。

## 使用场景

-   你需要在 PCG 生成流程中执行复杂的、非标准的数据处理或逻辑判断（例如，基于特定算法筛选或变换点数据）。
-   你希望利用 Python 的科学计算库（如 NumPy）或外部工具来处理 PCG 数据，然后再送回 PCG 图进行后续生成。
-   你想快速原型验证新的 PCG 算法，使用 Python 脚本比用 C++ 或蓝图更快捷。
-   你需要在运行时通过 PCG 执行一些动态脚本逻辑。

## 蓝图用法

本插件主要提供两个 PCG 节点，用于在蓝图可视化脚本中集成 Python 逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Python Script` | 执行 Python 脚本。支持内联脚本、从输入属性读取脚本或从 `.py` 文件执行。 | `UPCGExecutePythonScriptSettings` |
| `Python Data Processor` | 使用 Python 脚本处理 PCG 数据集合。提供动态输入输出引脚，脚本可直接操作输入的 `FPCGDataCollection` 并生成输出集合。 | `UPCGPythonDataProcessorSettings` |

### 使用示例（蓝图描述）

1.  **基本用法（Execute Python Script）：**
    *   在 PCG 图中添加一个 `Execute Python Script` 节点。
    *   在节点的细节面板中，设置 `Script Input Method`。例如选择 `Input`，然后将一个包含 Python 代码字符串的 PCG 属性连接到 `Script Source` 引脚。也可以选择 `File` 并指定 `.py` 文件路径。
    *   节点具有固定的 `In` 和 `Out` 引脚。Python 脚本可以通过 `unreal` 模块访问引擎和 PCG API 进行操作，但其输入输出是通过固定的 `In`/`Out` 引脚传递的，无法直接访问其他 PCG 数据引脚。

2.  **高级用法（Python Data Processor）：**
    *   在 PCG 图中添加一个 `Python Data Processor` 节点。
    *   节点有动态的输入引脚。你可以右键添加新的输入引脚，它们将被映射为 Python 中的变量。
    *   在 Python 脚本中，可以通过一个名为 `DataBridge` 的对象（类型为 `UPCGPythonDataBridge`）的 `GetInputCollection()` 方法获取所有输入数据。
    *   在脚本中处理数据后，需要构建一个 `FPCGDataCollection`，并调用 `DataBridge.AddToCollection()` 或 `DataBridge.SetOutputCollection()` 来设置输出。
    *   节点也有动态的输出引脚，你可以在 Python 脚本中决定将数据输出到哪个引脚。

## C++ 用法

该插件主要面向蓝图和 Python 脚本用户，其内部 C++ API 主要用于实现节点逻辑和数据桥接。

### 头文件引入

```cpp
#include "Elements/PCGExecutePythonScript.h"
#include "Helpers/PCGPythonDataBridge.h"
```

### 基本用法

在内部，`Execute Python Script` 和 `Python Data Processor` 节点通过 `UPythonScriptPlugin` 的服务来执行 Python 代码。以下是其工作原理的简化示例：

```cpp
// 伪代码：展示 FPCGExecutePythonScriptElement::ExecuteInternal 的大致逻辑
bool FPCGExecutePythonScriptElement::ExecuteInternal(FPCGContext* InContext) const
{
    const UPCGExecutePythonScriptSettings* Settings = InContext->GetInputSettings<UPCGExecutePythonScriptSettings>();
    FString ScriptContent;

    // 根据设置获取脚本内容 (内联、属性或文件)
    if (Settings->ScriptInputMethod == EPCGPythonScriptInputMethod::File)
    {
        FFileHelper::LoadFileToString(ScriptContent, *Settings->ScriptPath.FilePath);
    }
    // ... 其他获取方式

    // 通过 PythonScriptPlugin 执行脚本
    if (FPCGPythonHelpers::ExecutePythonScript(ScriptContent))
    {
        // 执行成功，处理输出（对于 ExecutePythonScript 节点，通常只是传递输入到输出）
        return true;
    }
    else
    {
        // 错误处理
        return false;
    }
}
```

### 进阶用法：使用数据桥（Data Bridge）

对于 `Python Data Processor` 节点，它使用 `UPCGPythonDataBridge` 在 Python 和 C++ 之间传递复杂的 PCG 数据结构。

```cpp
// 伪代码：展示 FPCGPythonDataProcessorElement::ExecuteInternal 的大致逻辑
bool FPCGPythonDataProcessorElement::ExecuteInternal(FPCGContext* InContext) const
{
    const UPCGPythonDataProcessorSettings* Settings = ...;
    // 1. 创建数据桥对象
    UPCGPythonDataBridge* DataBridge = NewObject<UPCGPythonDataBridge>();
    // 2. 将输入的 PCG 数据集合填充到桥中
    FPCGDataCollection InputCollection = ...; // 从 InContext 中构建
    DataBridge->Initialize(InputCollection);

    // 3. 准备 Python 脚本和环境变量
    FString ScriptContent = ...; // 获取脚本
    // DataBridge 对象会通过特定的命名规则暴露给 Python

    // 4. 执行 Python 脚本
    FPCGPythonHelpers::ExecutePythonScript(ScriptContent);

    // 5. 从桥中获取 Python 脚本设置的输出数据
    if (DataBridge->HasOutputCollection())
    {
        const FPCGDataCollection& OutputCollection = DataBridge->GetOutputCollection();
        // 6. 将输出数据应用到节点的输出引脚
        // ...
    }

    return true;
}
```

## Demo 示例

以下是一个可在 Python 脚本中使用 `PCGPythonDataBridge` 的示例，用于交换 PCG 数据。

**PCG Python 脚本示例 (ExecutePythonScript节点):**
```python
import unreal

# 获取由节点创建的 PCGPythonDataBridge 对象
# 其名称在节点执行时唯一生成，但可以通过约定或设置来定位
bridge = unreal.find_object("PCGPythonDataBridge_0") # 名称为示例

if bridge:
    # 获取输入数据
    input_data = bridge.get_input_collection()
    # ... 对 input_data 进行处理 ...

    # 创建输出数据
    output_data = unreal.FPCGDataCollection()
    # ... 构建 output_data ...

    # 将处理后的数据设置为输出
    bridge.set_output_collection(output_data)

    # 或者逐个添加数据到指定的输出引脚
    # some_pcg_data = ...
    # bridge.add_to_collection(some_pcg_data, "ProcessedData", [])
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | 核心的程序化内容生成框架，提供 `UPCGSettings`, `FPCGDataCollection` 等基础类型。 |
| `PythonScriptPlugin` | UE 内置的 Python 脚本插件，负责在引擎内嵌的 Python 解释器中执行代码。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `d47477a3` | [PCG] Python Data Processor Node | 新增了 Python Data Processor 节点，提供动态引脚和直接数据访问。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移，使用新的 `UE_LOGF` 宏。 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 代码重构，优化了字符串构建器的初始化。 |
| 2025-08-22 | `2de17507` | [PCG] Fixed bug causing Inline Constant not to respect required pin | 修复了一个 bug：内联常量未正确关联到必需引脚。 |
| 2025-07-14 | `002e7b67` | [PCG] Python Interop Plugin and Execute Python Script Node | 插件初始提交，创建了 `Execute Python Script` 节点。 |

### 维护评价

该插件**创建时间很新（约 1 年）**，且**明确标记为 Beta 版本**，表明其处于积极开发阶段。从提交历史看，最近一次实质性功能更新（添加新节点）在 2 个月内，维护较为活跃。主要功能（执行脚本、数据桥接）已可用，但作为 Beta 版本，可能存在 API 变动、未处理的边缘情况或性能问题。

**建议**：由于其 Beta 状态和依赖于 `PythonScriptPlugin`，不建议在需要长期稳定性的生产环境中作为核心功能使用。非常适合用于**工具开发、原型设计、内部管线扩展**等场景。推荐在非关键任务或探索性项目中试用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop/Source/PCGPythonInteropEditor/Private/Tests/) (位于源码的 Private/Tests 目录)