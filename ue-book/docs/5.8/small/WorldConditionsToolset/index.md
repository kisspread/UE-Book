# WorldConditionsToolset

> Toolset for WorldConditions Inspection

| 属性 | 值 |
|---|---|
| 中文名 | 世界条件工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WorldConditionsToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/WorldConditionsToolset) | |

## 用途

该插件为 `WorldConditions` 插件提供了一套编辑器内使用的检查与转换工具，其核心是作为 AI 工具集（`UToolsetDefinition`）的一部分，集成到 `ToolsetRegistry` 系统中。它解决了在 AI 系统（如 AI 助手）中检查、序列化和转换世界条件（`FWorldConditionQueryDefinition`）的特定需求。

它主要提供两大功能：
1.  **人类可读的条件描述**：能够将复杂的 `FWorldConditionQueryDefinition` 或单个 `FWorldConditionBase` 结构体转换成可读的文本描述，便于调试和理解 AI 行为规则。
2.  **JSON 转换器**：提供了一个专门的 `FToolsetJsonConverter`，用于将世界条件查询定义序列化为 JSON 格式。这对于 AI 工具集（AI Toolsets）系统持久化存储或传输条件定义至关重要。

该插件本身不直接暴露给游戏逻辑，而是作为编辑器开发工具存在。

## 使用场景

- **AI 行为调试与开发**：在编辑器中检查某个 NPC 或系统使用的世界条件，快速了解其触发逻辑。
- **AI 工具集集成**：开发需要利用世界条件的 AI 工具时，此插件提供了必要的序列化/反序列化支持。
- **自动化内容审查**：通过 JSON 格式，可以脚本化地批量检查或修改世界条件定义。

## 蓝图用法

该插件的功能主要通过 `UToolsetDefinition` 子类暴露给 AI 工具集系统。`UWorldConditionTools` 类中的函数被标记为 `AICallable`，这意味着它们可以被 AI 工具集管道调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetQueryDescription` | 返回一个世界条件查询（`FWorldConditionQueryDefinition`）的可读文本描述。 | `UWorldConditionTools` |
| `GetConditionDescription` | 返回一个封装在 `FInstancedStruct` 中的单个世界条件的可读文本描述。 | `UWorldConditionTools` |

**注意**：这些函数未标记为 `BlueprintCallable`，无法在普通蓝图中直接调用。它们是为 AI 工具集系统设计的 `UFUNCTION(meta=(AICallable))`。

### 使用示例（AI 工具集调用）

1.  在 AI 工具集定义中，引用 `UWorldConditionTools`。
2.  工具集系统会将 `GetQueryDescription` 等函数注册为可用的 AI 工具。
3.  AI 助手或相关系统可以调用这些工具，传入一个 `FWorldConditionQueryDefinition` 对象，获取其文本描述。

## C++ 用法

### 头文件引入

```cpp
#include "WorldConditionsToolset.h" // 包含模块接口
// 主要工具函数定义在私有头文件中，通常通过工具集系统间接使用
```

### 基本用法

调用静态函数获取条件描述。

```cpp
// 假设你已经有一个 FWorldConditionQueryDefinition 对象
FWorldConditionQueryDefinition MyQueryDef;
// ... 初始化 MyQueryDef ...

// 获取其文本描述
FText Description = UWorldConditionTools::GetQueryDescription(MyQueryDef);
if (!Description.IsEmpty())
{
    UE_LOG(LogTemp, Log, TEXT("World Condition Query Description: %s"), *Description.ToString());
}
```

### 进阶用法：使用 JSON 转换器

`FWorldConditionQueryConverter` 是该插件的核心，它处理了条件定义与 JSON 之间的相互转换。以下是其接口方法的示例用途（通常由 `ToolsetRegistry` 管理，此处展示逻辑）：

```cpp
// 获取转换器实例（通常从注册表获取）
// UE::WorldConditionsToolset::FWorldConditionQueryConverter Converter;

// 序列化为 JSON
FWorldConditionQueryDefinition QueryToSerialize;
// ... 填充 QueryToSerialize ...
// bool bSuccess = Converter.PropertyToJsonData(Property, &QueryToSerialize);

// 从 JSON 反序列化
TSharedPtr<FJsonValue> JsonData; // 来自之前的 JSON 解析
FWorldConditionQueryDefinition DeserializedQuery;
// bool bSuccess = Converter.JsonDataToProperty(JsonData, Property, &DeserializedQuery, OuterObject);
```

## Demo 示例

以下示例展示了如何在一个编辑器模块中注册并使用该工具集定义。

**MyEditorTools.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyEditorToolsModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyEditorTools.cpp**
```cpp
#include "MyEditorTools.h"
#include "WorldConditionsToolset.h" // 包含工具集定义类
#include "UObject/UObjectGlobals.h"

#define LOCTEXT_NAMESPACE "FMyEditorToolsModule"

void FMyEditorToolsModule::StartupModule()
{
    // 示例：在工具集系统中注册一个包含 WorldConditions 工具的工具集定义
    // 实际注册通过 ToolsetRegistry 自动处理，此处仅为演示获取类信息
    UClass* ToolsClass = UWorldConditionTools::StaticClass();
    if (ToolsClass)
    {
        UE_LOG(LogTemp, Log, TEXT("Found WorldConditionTools class: %s"), *ToolsClass->GetName());
        // 这里可以进一步使用 ToolsClass，例如获取其 UFunction 信息等
    }
}

void FMyEditorToolsModule::ShutdownModule()
{
    // 清理工作
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorToolsModule, MyEditorTools)
```

**说明**：此插件的主要功能通过 `UToolsetDefinition` 子类和 `FToolsetJsonConverter` 子类实现，并在 `StartupModule` 中向 `ToolsetRegistry` 注册。上层使用者通常通过工具集系统间接使用，而非直接调用 `UWorldConditionTools`。

## 模块依赖

从插件 `.uplugin` 文件分析，该插件依赖于以下其他插件：

| 插件 | 用途 |
|---|---|
| `WorldConditions` | 提供核心的世界条件定义（`FWorldConditionQueryDefinition`）和运行时系统。 |
| `ToolsetRegistry` | 提供 AI 工具集（`UToolsetDefinition`）的注册和管理框架。 |

该插件自身的 `Build.cs` 仅依赖 `Core` 模块，无特殊模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `8b443338` | Fix a crash where the FToolsetReferenceConverter cannot find the correct Outer to create a new insta | 修复了一个导致崩溃的bug，该bug与转换器无法找到正确的外部对象有关。 |
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 调整了工具集定义如何判断哪些UFunction是工具函数的逻辑。 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回滚了一次提交。 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 调整了工具集定义识别工具函数的逻辑。 |
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 将所有工具集的加载阶段移至引擎初始化后，以简化在工具集注册表可用时的注册流程。 |

### 维护评价

这是一个**非常新**的实验性插件，创建于 2026 年 4 月。从近期提交记录来看，它处于**活跃的早期开发与调整阶段**。最近的更新集中在修复崩溃、调整工具识别逻辑和优化初始化流程。

- **优势**：功能聚焦，与最新的 AI 工具集系统紧密结合，有 Epic Games 持续维护。
- **风险与限制**：
    1.  标记为**实验性** (`IsExperimentalVersion=true`) 且**默认未启用** (`EnabledByDefault=false`)，API 和行为可能在未来版本中发生不兼容的变化。
    2.  文档和示例较少，需要参考源码和 AI 工具集系统的用法。
    3.  仅适用于编辑器 (`EditorOnly=true`)。

**结论**：推荐有 AI 工具集开发需求的高级用户或团队尝试使用，但应密切关注版本更新，做好 API 变更的准备。不建议用于需要长期稳定性的生产项目的核心功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/WorldConditionsToolset)
- [官方文档]() （无）
- [测试用例]() （未发现）