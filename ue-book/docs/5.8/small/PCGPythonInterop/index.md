# PCG Python Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Editor Python Interpreter.

| 属性 | 值 |
|---|---|
| 中文名 | PCG Python互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `PCGPythonInteropEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop) | |

## 用途

该插件是 **程序化内容生成框架 (PCG)** 与 **编辑器 Python 解释器** 之间的桥梁。它解决了在 PCG 图中需要编写复杂、自定义或非标准逻辑时，必须使用 C++ 编写自定义 PCG 节点的局限性。通过此插件，用户可以直接在 PCG 节点中编写或引用 Python 脚本，从而获得 Python 语言的灵活性、庞大的第三方库支持以及快速原型开发的能力。

其核心功能是提供两个新的 PCG 节点：
1.  **`Execute Python Script`**：执行一个简单的 Python 脚本，主要用于生成或修改 PCG 数据。
2.  **`Python Data Processor`**：执行一个 Python 脚本，并直接接收和返回 `FPCGDataCollection`，为 Python 脚本提供对 PCG 数据结构（如属性、元数据）的完整读写访问权限。

这允许用户利用 Python 来处理程序化生成中的复杂算法、文件I/O、API调用或其他现有工具链。

## 使用场景

- **快速原型与迭代**：在不编写和编译 C++ 插件的情况下，快速测试新的程序化生成逻辑。
- **复杂算法集成**：在 PCG 管线中集成使用 NumPy、SciPy 等 Python 科学计算库实现的算法。
- **工具链复用**：调用已有的、用 Python 编写的资产处理、关卡设计或数据分析工具。
- **数据后处理**：使用 Python 的丰富文本处理能力（如正则表达式、JSON解析）来修改 PCG 生成的数据。
- **流程自动化**：结合 Unreal 的 Python 脚本能力，自动化 PCG 图的设置、运行和结果收集。

## 蓝图用法

该插件的核心功能通过两个 PCG 节点暴露，这些节点在 PCG 图中作为设置（`UCLASS`）存在，而非传统的蓝图函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Python Script` | 执行一个简单的 Python 脚本，用于生成输出数据。脚本可以从输入属性、内联编辑或外部 `.py` 文件加载。 | `UPCGExecutePythonScriptSettings` |
| `Python Data Processor` | 执行一个 Python 脚本，直接操作 `FPCGDataCollection`。支持动态输入/输出引脚，允许 Python 脚本接收和返回任意类型的 PCG 数据集合。 | `UPCGPythonDataProcessorSettings` |

### 使用示例（蓝图描述）

1.  **添加节点**：在 PCG 图编辑器中，右键搜索 “Execute Python Script” 或 “Python Data Processor”，将其拖入图表。
2.  **配置脚本来源**：
    *   **Input**：选择一个输入 PCG 数据的属性（如 String 属性）作为脚本源。该属性的值将被当作 Python 代码执行。
    *   **Inline**：直接在节点的属性面板中编写 Python 代码。
    *   **File**：指定一个本地 `.py` 文件的路径。
3.  **连接数据**：
    *   对于 `Execute Python Script`：通常将 PCG 数据（如点数据、属性数据）连接到输入引脚 `In`，Python 脚本可以处理这些数据并生成新的数据输出到 `Out` 引脚。
    *   对于 `Python Data Processor`：可以添加任意数量的动态输入引脚。Python 脚本通过 `UPCGPythonDataBridge` 对象访问所有输入数据，并构建一个包含所需输出数据的 `FPCGDataCollection` 设置回去。
4.  **编写 Python 逻辑**：在脚本中，你可以通过 `pcg` 模块或直接通过桥接对象与 PCG 数据交互。例如，在 Python Data Processor 中，你可以这样访问输入并设置输出：
    ```python
    import unreal
    # 查找当前执行创建的桥接对象（名字是动态生成的）
    bridge = unreal.find_object(None, "PCGPythonDataBridge_XX")
    if bridge:
        input_collection = bridge.get_input_collection()
        # ... 处理 input_collection ...
        new_data = # ... 创建新的 UPCGData 对象 ...
        bridge.add_to_collection(new_data, "OutputPinName", [])
    ```

## C++ 用法

此插件主要用于编辑器扩展，其 C++ API 主要是其节点类的接口，通常在实现自定义 PCG 元素或扩展插件功能时使用。

### 头文件引入

```cpp
#include "Elements/PCGExecutePythonScript.h"
#include "Elements/PCGPythonDataProcessor.h"
```

### 基本用法

以下示例展示了如何在代码中动态创建并配置一个 `ExecutePythonScript` 节点。

*注意：此代码片段基于插件提供的类接口推断，用于说明典型用法。*

```cpp
// 创建一个 UPCGExecutePythonScriptSettings 实例
UPCGExecutePythonScriptSettings* ScriptSettings = NewObject<UPCGExecutePythonScriptSettings>();

// 配置脚本输入方式为内联
ScriptSettings->ScriptInputMethod = EPCGPythonScriptInputMethod::Input;

// 设置内联脚本内容（注意：实际属性为私有，通常通过节点UI设置，这里仅为演示）
// 在实际场景中，可能通过序列化或特定方法设置。
FString Script = TEXT("print('Hello from PCG Python!')");

// 创建执行元素
FPCGElementPtr Element = ScriptSettings->CreateElement();
if (Element.IsValid())
{
    // 准备执行上下文 (FPCGContext)，这通常由 PCG 框架管理
    // FPCGContext* Context = ...
    // Element->Execute(Context);
}
```

### 进阶用法

更复杂的用法涉及与 `PythonDataProcessor` 和桥接对象 `UPCGPythonDataBridge` 交互，这通常发生在需要扩展或调试节点行为时。主要流程是：
1.  理解 `UPCGPythonDataProcessorSettings` 如何管理动态引脚 (`FPCGDynamicPinContainer`)。
2.  在元素执行（`FPCGPythonDataProcessorElement::ExecuteInternal`）时，框架会创建一个 `UPCGPythonDataBridge` 对象，用当前的输入 `FPCGDataCollection` 初始化它，并让 Python 脚本通过该对象读写数据。
3.  执行结束后，元素从桥接对象中取出输出集合，继续 PCG 流水线。

## Demo 示例

以下是一个最简单的自定义元素示例，演示了如何基于 `UPCGExecutePythonScriptSettings` 创建一个功能类似但名字不同的设置类。

**PCGSimplePythonNode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Elements/PCGExecutePythonScript.h"
#include "PCGSimplePythonNode.generated.h"

UCLASS(MinimalAPI, BlueprintType, ClassGroup = (Procedural))
class UPCGSimplePythonNodeSettings : public UPCGExecutePythonScriptSettings
{
    GENERATED_BODY()

public:
#if WITH_EDITOR
    // 重写默认节点名称和标题
    virtual FName GetDefaultNodeName() const override { return TEXT("SimplePythonNode"); }
    virtual FText GetDefaultNodeTitle() const override { return NSLOCTEXT("PCGSimplePythonNode", "NodeTitle", "Simple Python Node"); }
#endif // WITH_EDITOR
};
```

**PCGSimplePythonNode.cpp**
```cpp
#include "PCGSimplePythonNode.h"

// 实现创建元素的方法，直接使用父类的元素
FPCGElementPtr UPCGSimplePythonNodeSettings::CreateElement() const
{
    // 由于功能与父类完全相同，直接返回父类创建的元素。
    // 如果需要修改执行逻辑，可以创建自定义的 FPCGElement 子类。
    return MakeShared<FPCGExecutePythonScriptElement>();
}
```

## 模块依赖

该插件自身依赖于其他插件。在你的项目中使用它，需要确保这些插件已启用。

| 模块/插件 | 用途 |
|---|---|
| `PCG` | 基础程序化内容生成框架 |
| `PythonScriptPlugin` | 提供编辑器内的 Python 解释器和脚本执行能力 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `d47477a3` | [PCG] Python Data Processor Node | 新增 Python Data Processor 节点，支持直接操作 PCG 数据集合。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统更新，将宏替换为新格式。 |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 代码重构，优化字符串构建器的初始化。 |
| 2025-08-22 | `2de17507` | [PCG] Fixed bug causing Inline Constant not to respect required pin | 修复一个 Bug，该 Bug 导致内联常量不遵守必填引脚的设置。 |
| 2025-07-14 | `002e7b67` | [PCG] Python Interop Plugin and Execute Python Script Node | 插件创建，包含首个 Execute Python Script 节点。 |

### 维护评价

该插件于 2025 年 7 月创建，至今约 1 年，处于**活跃维护**状态。最近的提交（2026年4月）增加了重要的新功能节点 (`Python Data Processor`)，表明 Epic 正在积极开发和完善它。

**注意事项**：
1.  **实验性 (Beta)**：插件在 `.uplugin` 中明确标记为 `IsBetaVersion: true`，并且默认未启用 (`EnabledByDefault: false`)。这意味着其 API 和功能在未来版本中可能会发生不兼容的变更。
2.  **编辑器专用**：这是一个仅编辑器 (`Editor`) 插件，不能在打包的游戏中使用。
3.  **依赖关系**：需要同时启用 `PCG` 和 `PythonScriptPlugin` 插件。

**推荐使用**：非常适合用于编辑器工具、快速原型开发和自定义 PCG 逻辑的编写。但在生产环境中用于需要长期稳定的 PCG 图时，需谨慎评估其 Beta 状态带来的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/) (PCG 框架文档，包含此插件的用法)