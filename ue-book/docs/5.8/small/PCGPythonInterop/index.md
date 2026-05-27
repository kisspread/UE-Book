# Procedural Content Generation Framework (PCG) Python Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Editor Python Interpreter.

| 属性 | 值 |
|---|---|
| 中文名 | PCG Python 互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PCGPythonInteropEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop) | |

## 用途

该插件在 PCG（程序化内容生成）框架与 Editor Python Script Plugin 之间架起桥梁，允许用户在 PCG 图表中直接执行 Python 脚本来处理程序化数据。

它解决了以下问题：PCG 框架的数据处理节点通常局限于蓝图或内置算法，无法灵活地利用 Python 生态系统的能力（如数学库、数据科学工具、自定义算法原型等）。通过此插件，用户可以在 PCG 管线中嵌入 Python 脚本节点，直接读写 PCG 数据集合，实现高度自定义的程序化生成逻辑。

插件提供两种节点：
1. **Execute Python Script** — 将 PCG 数据序列化为 JSON 传入脚本，脚本输出 JSON 回传（适合简单的数据转换）
2. **Python Data Processor** — 通过 UObject 桥接对象让 Python 直接访问 `FPCGDataCollection`，并支持动态引脚（适合复杂的多输入/多输出数据处理）

## 使用场景

- 你需要在 PCG 图表中执行自定义的数据变换算法（如噪声生成、几何处理）但不想写 C++ 节点 → 用 Execute Python Script 节点
- 你需要从 Python 调用外部库（NumPy、SciPy 等）来处理 PCG 数据 → 用 Python Data Processor 节点
- 你需要快速原型化 PCG 处理逻辑，先用 Python 验证再移植到 C++ → 两个节点都适用
- 你需要在 PCG 图中根据条件动态修改点云属性或空间数据 → 用 Python 脚本实现自定义逻辑

## 蓝图用法

> ⚠️ 该插件主要在 PCG 图表编辑器中使用，不涉及传统蓝图节点。以下为 PCG 图表中的节点属性配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute Python Script` | 执行 Python 脚本，PCG 数据以 JSON 形式传入/传出 | `UPCGExecutePythonScriptSettings` |
| `Python Data Processor` | 执行 Python 脚本，直接访问 PCG 数据集合，支持动态引脚 | `UPCGPythonDataProcessorSettings` |

### 节点属性配置

两个节点共享以下核心属性：

| 属性 | 说明 |
|---|---|
| `ScriptInputMethod` | 脚本来源：`Input`（从输入引脚或内联）或 `File`（从 .py 文件） |
| `ScriptSource` | 当 ScriptInputMethod 为 Input 时，选择哪个属性作为脚本源 |
| `ScriptPath` | 当 ScriptInputMethod 为 File 时，选择 .py 文件路径 |
| `bMuteEditorToast` | 是否静默编辑器通知（高级选项） |

### 使用示例（PCG 图表描述）

**Execute Python Script 节点基本用法：**
1. 在 PCG 图表中添加 "Execute Python Script" 节点
2. 将上游数据节点（如 Surface Sampler）的输出连接到输入引脚
3. 设置 `ScriptInputMethod` 为 `Input`，在默认值中编写 Python 脚本
4. 脚本接收 JSON 格式的 PCG 数据，输出 JSON 格式的结果数据
5. 将输出引脚连接到下游节点（如 Static Mesh Spawner）

**Python Data Processor 节点动态引脚用法：**
1. 添加 "Python Data Processor" 节点
2. 该节点支持动态添加/重命名输入和输出引脚
3. 每个输入引脚可接收任意 PCG 数据类型，支持多连接和多数据
4. Python 脚本通过 `unreal.find_object()` 获取桥接对象，直接读取输入集合并写入输出集合

## C++ 用法

> ⚠️ 该插件为 Editor 专用，不面向运行时 C++ 代码。以下为在编辑器工具或自定义 PCG 节点中的集成用法。

### 头文件引入

```cpp
#include "Elements/PCGExecutePythonScript.h"
#include "Elements/PCGPythonDataProcessor.h"
#include "Helpers/PCGPythonDataBridge.h"
#include "Helpers/PCGPythonHelpers.h"
```

### 基本用法：访问 Python 数据桥接对象

在 Python Data Processor 节点的执行逻辑中，桥接对象用于在 C++ 和 Python 之间传递 `FPCGDataCollection`。桥接对象在每次执行时以唯一名称创建，Python 端通过 `unreal.find_object()` 查找。

```cpp
// 来源: Source/PCGPythonInteropEditor/Public/Helpers/PCGPythonDataBridge.h

// 创建桥接对象并初始化输入数据
UPCGPythonDataBridge* Bridge = NewObject<UPCGPythonDataBridge>();
Bridge->Initialize(InputDataCollection);

// 执行 Python 脚本后，检查是否有输出
if (Bridge->HasOutputCollection())
{
    const FPCGDataCollection& Output = Bridge->GetOutputCollection();
    // 使用输出数据...
}
```

### 进阶用法：Python 端操作桥接对象

Python 脚本通过 Unreal Python API 访问桥接对象：

```python
# Python 端（在 PCG 节点中执行的脚本）
import unreal

# 查找桥接对象（名称由 C++ 端按执行 ID 生成）
bridge = unreal.find_object("PCGPythonDataBridge_<ExecutionID>")

# 读取输入数据集合
input_collection = bridge.get_input_collection()

# 处理数据后设置输出
bridge.set_output_collection(output_collection)

# 或者逐个添加数据到输出
bridge.add_to_collection(data, pin_label, tags)
```

### 进阶用法：错误信息提取

```cpp
// 来源: Source/PCGPythonInteropEditor/Public/Helpers/PCGPythonHelpers.h

FString PythonTraceback = TEXT("Traceback (most recent call last):\n  File \"script.py\", line 5\n    result = 1/0\nZeroDivisionError: division by zero");

// 从完整 traceback 中提取简要错误信息
FString ErrorSummary = PCG::Python::Helpers::ExtractErrorSummary(PythonTraceback);
// ErrorSummary == "ZeroDivisionError: division by zero"
```

## Demo 示例

### 自定义 PCG Python 数据处理节点（C++ 端扩展示例）

```cpp
// MyCustomPCGPythonNode.h
#pragma once

#include "CoreMinimal.h"
#include "Elements/PCGPythonDataProcessor.h"
#include "MyCustomPCGPythonNode.generated.h"

/**
 * 自定义节点：基于 PCG Python Data Processor，添加额外的预处理逻辑
 */
UCLASS(MinimalAPI, BlueprintType, ClassGroup = (Procedural))
class UMyCustomPCGPythonNodeSettings : public UPCGPythonDataProcessorSettings
{
    GENERATED_BODY()

public:
#if WITH_EDITOR
    virtual FName GetDefaultNodeName() const override { return TEXT("MyCustomPythonNode"); }
    virtual FText GetDefaultNodeTitle() const override
    {
        return NSLOCTEXT("MyCustom", "Title", "Custom Python Processor");
    }
#endif

    /** 自定义参数，可在 Python 脚本中通过桥接对象访问 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings)
    float ScaleFactor = 1.0f;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 核心框架，提供 `UPCGSettings`、`FPCGDataCollection` 等基础类型 |
| `PythonScriptPlugin` | Editor Python 解释器，提供 Python 脚本执行环境和 Unreal Python API |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `d47477a3` | [PCG] Python Data Processor Node | 新增 Python Data Processor 节点，支持动态引脚直接访问数据集合 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-02-25 | `c0dd9731` | StringBuilder: Removing construction of TStringBuilderBase<T> | 重构字符串构建器构造方式 |
| 2025-08-22 | `2de17507` | [PCG] Fixed bug causing Inline Constant not to respect required pin | 修复内联常量不遵守必需引脚约束的 bug |
| 2025-07-14 | `002e7b67` | [PCG] Python Interop Plugin and Execute Python Script Node | 初始提交：创建插件并实现 Execute Python Script 节点 |

### 维护评价

- **状态**: 🟢 活跃维护中
- **创建时间**: 2025 年 7 月，约 1 年历史，属于较新的插件
- **更新频率**: 2025 年 4 月仍有功能性更新（新增 Python Data Processor 节点），约每 1-2 个月有提交
- **实验性标记**: 插件标记为 Beta（`IsBetaVersion=true`），且默认禁用（`EnabledByDefault=false`），API 可能发生变化
- **已知限制**: 
  - `FPCGPythonDataBridge` 的存在是因为 `PythonScriptPlugin` 的 `PyConversion` 头文件为 Private，未来可能被移除
  - Python 脚本必须在主线程执行（`CanExecuteOnlyOnMainThread = true`），不支持并行
  - 节点不可缓存（`IsCacheable = false`），每次执行都会重新运行脚本
- **推荐**: 适合实验和快速原型开发，暂不建议用于生产管线（Beta 状态）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCGInterops/PCGPythonInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)