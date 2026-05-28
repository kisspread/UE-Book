# Editor Telemetry

> Plugin that emits common telemetry events from the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 运行时遥测 |
| 分类 | Telemetry |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RuntimeTelemetry` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RuntimeTelemetry) | |

## 用途

该插件提供了一个标准化的运行时遥测数据收集框架，专门用于记录来自游戏客户端和服务器构建的关键事件。尽管其描述中提到“Editor Telemetry”，但其核心是 `RuntimeAndProgram` 类型的模块，其设计目标是在游戏运行时采集底层系统的关键指标（如 `IoStore` 按需加载、内存 `LLM` 标签等），并将这些事件数据发送到 `StudioTelemetry` 进行汇总和分析。它解决了在非编辑器环境下对特定系统行为进行数据化监控和问题诊断的需求。

## 使用场景

- 你的游戏使用了 `IoStore` 按需加载功能，需要监控其加载成功率和性能数据。
- 你需要跟踪特定内存分配标签（如 `UObject` 作用域）的使用情况，以便进行内存优化。
- 你需要在游戏服务器和客户端的运行时收集特定的行为或状态数据，用于分析线上问题或用户行为。

## 蓝图用法

该插件提供的核心类 `FRuntimeTelemetry` 是一个 C++ 单例，其公开接口均为 `UE_API` 函数，但未标记为 `BlueprintCallable`。因此，其主要使用方式是通过 C++ 代码在游戏逻辑中进行调用，而非直接在蓝图中操作。

## C++ 用法

### 头文件引入

```cpp
#include "RuntimeTelemetry.h"
```

### 基本用法

该插件提供了一个单例 `FRuntimeTelemetry` 来管理会话和事件记录。通常在游戏会话开始和结束时调用其方法。

```cpp
// 获取遥测单例
FRuntimeTelemetry& Telemetry = FRuntimeTelemetry::Get();

// 在游戏或服务器启动时开始会话
Telemetry.StartSession();

// ... 游戏运行中 ...

// 记录一个 IoStore 按需加载相关的事件
TArray<FAnalyticsEventAttribute> Attributes;
Attributes.Add(FAnalyticsEventAttribute(TEXT("LoadPath"), TEXT("/Game/Maps/MainMap")));
Telemetry.RecordEvent_IoStoreOnDemand(TEXT("LoadSuccess"), Attributes);

// 在游戏或服务器关闭时结束会话
Telemetry.EndSession();
```
**来源**：基于 `Source/Public/RuntimeTelemetry.h` 中的接口设计。

### 进阶用法

你可以组合多个事件来记录一个复杂流程的不同阶段。

```cpp
FRuntimeTelemetry& Telemetry = FRuntimeTelemetry::Get();

// 开始一个会话（例如，一个游戏局）
Telemetry.StartSession();

// 1. 记录一个内存 LLM 标签事件，用于标记某个系统初始化
TArray<FAnalyticsEventAttribute> InitAttribs;
InitAttribs.Add(FAnalyticsEventAttribute(TEXT("System"), TEXT("PhysicsWorld")));
Telemetry.RecordEvent_MemoryLLM(TEXT("SystemInit"), InitAttribs);

// 2. 执行某些操作...
// ...

// 3. 在操作完成后，记录另一个内存事件以分析增量
TArray<FAnalyticsEventAttribute> PostAttribs;
PostAttribs.Add(FAnalyticsEventAttribute(TEXT("DeltaBytes"), TEXT("102400")));
Telemetry.RecordEvent_MemoryLLM(TEXT("AfterHeavyLoad"), PostAttribs);

// 会话结束时，所有未被单独记录的事件可能会被批量发送
Telemetry.EndSession();
```
**来源**：综合 `FRuntimeTelemetry` 的公开接口及典型遥测插件的使用模式。

## Demo 示例

以下是一个在 `UGameInstance` 子类中集成 `RuntimeTelemetry` 的最小示例。

**MyGameInstance.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class MYPROJECT_API UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

private:
    void RecordGameplayStartEvent();
};
```

**MyGameInstance.cpp**
```cpp
#include "MyGameInstance.h"
#include "RuntimeTelemetry.h" // 引入插件头文件

void UMyGameInstance::Init()
{
    Super::Init();

    // 开始运行时遥测会话
    FRuntimeTelemetry::Get().StartSession();
}

void UMyGameInstance::Shutdown()
{
    // 结束运行时遥测会话
    FRuntimeTelemetry::Get().EndSession();

    Super::Shutdown();
}

void UMyGameInstance::RecordGameplayStartEvent()
{
    // 在游戏玩法开始时记录一个自定义属性
    TArray<FAnalyticsEventAttribute> Attributes;
    Attributes.Add(FAnalyticsEventAttribute(TEXT("GameMode"), TEXT("BattleRoyale")));
    Attributes.Add(FAnalyticsEventAttribute(TEXT("Map"), TEXT("Island")));
    // 可以复用插件提供的函数，例如内存事件
    FRuntimeTelemetry::Get().RecordEvent_MemoryLLM(TEXT("GameplayStart"), Attributes);
}
```

## 模块依赖

根据插件的 `Build.cs` 文件，要在你的项目中使用此插件，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `StudioAnalytics` | 插件遥测数据的核心传输和处理模块 |
| `Analytics` | 引擎的通用分析框架，提供 `FAnalyticsEventAttribute` 等基础类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统日志宏迁移至新的 UE_LOGF 宏。 |
| 2025-05-13 | `1521eda1` | Rework on the UObjectClasses new TagSet for Insights to remove the necessity of adding `#if LLM_ALLO` | 为 Insights 重构 UObject 类的标签集，以去除添加 `#if LLM_ALLO` 宏的必要性。 |
| 2025-05-12 | `b212d510` | [Backout] - CL42506291 | 回退了提交 CL42506291。 |
| 2025-05-12 | `c87333f6` | Rework on the UObjectClasses new TagSet for Insights to remove the necessity of adding `#if LLM_ALLO` | （与 1521eda1 重复）重构 UObject 类的标签集。 |
| 2025-04-29 | `a873c04d` | Add a new set of LLM tags for the UObject scope to better see where the allocated memory comes from. | 为 UObject 作用域添加一套新的 LLM 标签，以便更好地了解内存分配来源。 |

### 维护评价

该插件自 2024 年 10 月创建以来，持续有更新，最近一次更新在 2026 年 4 月。近期的更新主要集中在底层日志系统和内存标签（LLM）的适配与改进上，表明其仍在维护中且与引擎核心功能保持同步。目前没有发现已知的废弃标记或重大限制。**推荐使用**，它是一个用于收集运行时关键系统指标的实用工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RuntimeTelemetry)
- [初始提交](https://github.com/EpicGames/UnrealEngine/commit/09ae5fcafcca27b5053f307412fd86745866f140)