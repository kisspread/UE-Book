# Editor Telemetry

> Plugin that emits common telemetry events from the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器遥测 |
| 分类 | Telemetry |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RuntimeTelemetry` (RuntimeAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RuntimeTelemetry) | |

## 用途

该插件提供一个轻量级的 C++ 接口，用于从编辑器代码中发射常见的遥测事件。通过 `FRuntimeTelemetry` 单例，开发者可以方便地记录 I/O 存储按需加载（IoStoreOnDemand）和内存 LLM 标签（MemoryLLM）等事件，无需直接操作底层的分析提供器（`IAnalyticsProvider`）。它简化了编辑器遥测数据的收集，便于 Epic 内部和插件开发者追踪编辑器性能和使用模式。

## 使用场景

- 你在开发编辑器模块或工具，需要记录特定操作（如资源加载、内存分配）的发生次数或耗时。
- 你想为分析系统添加自定义的 LLM 分组标签，以便在 Insights 中可视化内存分布。
- 你需要快速将编辑器中的性能指标发送到遥测后端，而无需手动管理分析会话。

## 蓝图用法

该插件**仅提供 C++ 接口**，未暴露任何 `UFUNCTION(BlueprintCallable)` 或 `UProperty`，因此无法在蓝图中直接使用。若需在蓝图项目中记录遥测，请通过 C++ 包装函数（如自定义 `UBlueprintFunctionLibrary`）调用 `FRuntimeTelemetry` 接口。

## C++ 用法

### 头文件引入

```cpp
#include "RuntimeTelemetry.h"
```

### 基本用法

以下示例演示如何获取单例、启动会话、记录事件并结束会话。建议在编辑器模块的 `StartupModule` 和 `ShutdownModule` 中调用 `StartSession`/`EndSession`。

```cpp
// RuntimeTelemetryExample.h
#pragma once

#include "CoreMinimal.h"

class FRuntimeTelemetryExample
{
public:
    static void RunExample();
};
```

```cpp
// RuntimeTelemetryExample.cpp
#include "RuntimeTelemetryExample.h"
#include "RuntimeTelemetry.h"
#include "Interfaces/IAnalyticsProvider.h"

void FRuntimeTelemetryExample::RunExample()
{
    FRuntimeTelemetry& Telemetry = FRuntimeTelemetry::Get();

    // 启动遥测会话（通常在模块启动时调用）
    Telemetry.StartSession();

    // 记录 IoStoreOnDemand 事件，传入上下文和可选属性
    TArray<FAnalyticsEventAttribute> Attributes;
    Attributes.Add(FAnalyticsEventAttribute(TEXT("PackageName"), TEXT("/Game/Example")));
    Telemetry.RecordEvent_IoStoreOnDemand(TEXT("OnDemandLoad"), Attributes);

    // 记录 MemoryLLM 事件，可附加自定义 LLM 标签
    Telemetry.RecordEvent_MemoryLLM(TEXT("UObjectAllocation"), {});

    // 结束会话（通常在模块关闭时调用）
    Telemetry.EndSession();
}
```

> **来源文件**：`Engine/Plugins/Experimental/RuntimeTelemetry/Source/Public/RuntimeTelemetry.h`

### 进阶用法

结合 LLM 标签系统，在 Insights 中区分不同 UObject 类的分配来源。以下示例来自最新提交的典型用法（伪代码）：

```cpp
// 在 UObject 分配路径中嵌入 LLM 标签
#if LLM_ALLOWED
    FRuntimeTelemetry::Get().RecordEvent_MemoryLLM(TEXT("UObjectClass"), 
        { FAnalyticsEventAttribute(TEXT("ClassName"), TEXT("UMyBlueprintGeneratedClass")) });
#endif
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何将遥测记录嵌入任意编辑器模块。

**ExampleModule.h**  
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FExampleModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**ExampleModule.cpp**  
```cpp
#include "ExampleModule.h"
#include "RuntimeTelemetry.h"

void FExampleModule::StartupModule()
{
    // 启动遥测会话
    FRuntimeTelemetry::Get().StartSession();

    // 记录模块启动事件
    FRuntimeTelemetry::Get().RecordEvent_IoStoreOnDemand(TEXT("ModuleStart"), {});
}

void FExampleModule::ShutdownModule()
{
    // 记录模块关闭事件
    FRuntimeTelemetry::Get().RecordEvent_MemoryLLM(TEXT("ModuleShutdown"), {});

    // 结束会话
    FRuntimeTelemetry::Get().EndSession();
}

IMPLEMENT_MODULE(FExampleModule, ExampleModule);
```

## 模块依赖

以下依赖项是使用本插件时需要引入的（不含标准 Core/Engine/Slate 等）。在你的模块 `Build.cs` 中添加：

| 模块 | 用途 |
|---|---|
| `Analytics` | 提供 `IAnalyticsProvider` 和 `IAnalyticsTracer` 接口，用于发射事件 |

其余依赖（如 `CoreUObject`、`Engine`）为隐式标准依赖，无需额外声明。

## 维护状态

### 近期更新

- 2025-05-13 1521eda1 Rework on the UObjectClasses new TagSet for Insights to remove the necessity of adding `#if LLM_ALLOWED` guards
- 2025-05-12 b212d510 [Backout] - CL42506291
- 2025-05-12 c87333f6 Rework on the UObjectClasses new TagSet for Insights to remove the necessity of adding `#if LLM_ALLOWED` guards
- 2025-04-29 a873c04d Add a new set of LLM tags for the UObject scope to better see where the allocated memory comes from.
- 2025-04-23 6ae57335 Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i

### 维护评价

- **创建时间**：2025-04-23（距今约 1 个月）
- **更新频率**：创建后一个月内有多次功能提交，涉及 LLM 标签优化和回退调整，说明团队在积极打磨。
- **活跃度**：非常活跃，最新提交在 2025-05-13，属于 6 个月内的正常维护。
- **已知问题**：无公开的已知限制。
- **推荐使用**：✅ 推荐。该插件为官方提供，用于替代直接操作分析提供器的繁琐流程，特别适合需要在编辑器内发射遥测事件的模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RuntimeTelemetry)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RuntimeTelemetry/Tests)（若存在，当前目录未发现测试文件）