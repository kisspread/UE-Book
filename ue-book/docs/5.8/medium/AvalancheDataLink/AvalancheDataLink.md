# Motion Design Data Link Integration

> （.uplugin Description 字段为空）

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计数据链接 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `AvalancheDataLink` (Runtime), `AvalancheDataLinkEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheDataLink) | |

## 用途

AvalancheDataLink 是 Motion Design（Avalanche）系统与 DataLink 数据框架之间的桥梁插件。它的核心作用是：**让 Motion Design 场景中的 Actor 能够消费外部数据源，并通过 Remote Control 将数据驱动到场景属性上**。

具体来说：
- `AAvaDataLinkActor` 持有一个或多个 `UAvaDataLinkInstance`，每个实例封装了一个 DataLink 数据管线
- 每个实例可以配置输出处理器（`OutputProcessors`），其中 `UAvaDataLinkRCProcessor` 负责将 DataLink 的输出字段映射到 Remote Control Preset 中的控制器
- 这使得虚拟制片场景中的动态设计元素可以被实时数据驱动，例如从外部数据源获取数值后自动更新材质参数、变换等

插件从 Experimental 迁移至 VirtualProduction 目录，当前为 Beta 状态。

## 使用场景

- 你在做虚拟制片（Virtual Production），需要让 Motion Design 场景中的图形元素被外部实时数据（如数据表格、API 返回值）驱动 → 用 AvalancheDataLink
- 你需要将 DataLink 数据管线的输出映射到 Remote Control Preset 的控制器上，实现数据驱动的属性编辑 → 用 UAvaDataLinkRCProcessor
- 你想在场景开始时自动执行数据链接，让画面元素根据数据自动更新 → 在 AAvaDataLinkActor 上勾选 `bExecuteOnBeginPlay`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecuteDataLinkInstances` | 启动所有已配置的数据链接实例 | `AAvaDataLinkActor` |
| `StopDataLinkInstances` | 停止所有正在运行的数据链接实例 | `AAvaDataLinkActor` |

### 属性编辑

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `DataLinkInstances` | `TArray<UAvaDataLinkInstance>` | 数据链接实例数组（Instanced，可内联编辑） | `AAvaDataLinkActor` |
| `bExecuteOnBeginPlay` | `bool` | 是否在 BeginPlay 时自动执行 | `AAvaDataLinkActor` |
| `DataLinkInstance` | `FDataLinkInstance` | 底层 DataLink 实例配置 | `UAvaDataLinkInstance` |
| `OutputProcessors` | `TArray<UDataLinkProcessor>` | 输出处理器数组 | `UAvaDataLinkInstance` |
| `ControllerMappings` | `TArray<FAvaDataLinkControllerMapping>` | 输出字段到 RC 控制器的映射 | `UAvaDataLinkRCProcessor` |

### 使用示例（蓝图描述）

1. **放置 Actor**：在场景中放置一个 `AAvaDataLinkActor`（搜索 "Motion Design Data Link Actor"）
2. **配置实例**：在 Details 面板中，展开 `DataLinkInstances` 数组，添加新元素。每个元素是 `UAvaDataLinkInstance`（显示为 "Motion Design Data Link Instance"）
3. **配置数据源**：在实例内配置 `DataLinkInstance`，选择数据链接类型和参数
4. **添加输出处理器**：在 `OutputProcessors` 中添加 `UAvaDataLinkRCProcessor`（显示为 "Motion Design Data Link Remote Control Processor"）
5. **映射字段**：在处理器的 `ControllerMappings` 中，配置 `OutputFieldName`（数据输出字段名）和 `TargetController`（目标 Remote Control 控制器 ID）
6. **执行**：勾选 `bExecuteOnBeginPlay` 实现自动执行，或在运行时调用 `ExecuteDataLinkInstances` 手动触发

## C++ 用法

### 头文件引入

```cpp
#include "AvaDataLinkActor.h"
#include "AvaDataLinkInstance.h"
#include "AvaDataLinkControllerMapping.h"
```

### 基本用法

创建数据链接 Actor 并手动执行（基于 `AAvaDataLinkActor` 公共 API）：

```cpp
// 在已有 World 中 Spawn 一个 DataLink Actor
FActorSpawnParameters SpawnParams;
AAvaDataLinkActor* DataLinkActor = World->SpawnActor<AAvaDataLinkActor>(SpawnParams);

// 配置完成后手动触发执行
DataLinkActor->ExecuteDataLinkInstances();

// 需要停止时
DataLinkActor->StopDataLinkInstances();
```

### 进阶用法

通过 C++ 配置控制器映射，将数据链接输出字段绑定到 Remote Control 控制器：

```cpp
// 假设已获取 AAvaDataLinkActor* DataLinkActor
UAvaDataLinkInstance* LinkInstance = NewObject<UAvaDataLinkInstance>(DataLinkActor);
DataLinkActor->DataLinkInstances.Add(LinkInstance);

// 创建 RC 输出处理器
UAvaDataLinkRCProcessor* RCProcessor = NewObject<UAvaDataLinkRCProcessor>(LinkInstance);
LinkInstance->OutputProcessors.Add(RCProcessor);

// 配置字段到控制器的映射
FAvaDataLinkControllerMapping Mapping;
Mapping.OutputFieldName = TEXT("ColorValue");
Mapping.TargetController = FAvaRCControllerId(/* 目标控制器 ID */);
RCProcessor->ControllerMappings.Add(Mapping);
```

## Demo 示例

```cpp
// MyDataLinkActor.h
#pragma once

#include "AvaDataLinkActor.h"
#include "MyDataLinkActor.generated.h"

UCLASS()
class AMyDataLinkActor : public AAvaDataLinkActor
{
    GENERATED_BODY()

public:
    AMyDataLinkActor();

    UFUNCTION(BlueprintCallable, Category="My Data Link")
    void ReExecuteWithDelay(float DelaySeconds);
};
```

```cpp
// MyDataLinkActor.cpp
#include "MyDataLinkActor.h"
#include "TimerManager.h"

AMyDataLinkActor::AMyDataLinkActor()
{
    // 默认在 BeginPlay 时自动执行
    bExecuteOnBeginPlay = true;
}

void AMyDataLinkActor::ReExecuteWithDelay(float DelaySeconds)
{
    // 先停止当前执行
    StopDataLinkInstances();

    // 延迟后重新执行
    FTimerHandle TimerHandle;
    GetWorldTimerManager().SetTimer(TimerHandle, [this]()
    {
        ExecuteDataLinkInstances();
    }, DelaySeconds, false);
}
```

## 模块依赖

从插件依赖的其他插件推断，AvalancheDataLink 需要以下非标准模块：

| 模块 | 用途 |
|---|---|
| `Avalanche` | Motion Design 核心模块，提供 `IAvaSceneInterface` |
| `DataLink` | 数据链接框架，提供 `FDataLinkInstance`、`FDataLinkExecutor`、`UDataLinkProcessor` |
| `RemoteControl` | Remote Control 功能，提供 `URemoteControlPreset`、`URCController`、`FAvaRCControllerId` |

> 注意：该插件标记为 `Installed: false`，使用时需在插件设置中手动启用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF 格式 |
| 2025-08-27 | `f25e96ca` | Motion Design: set the scene state and data link plugins to beta | 将插件标记为 Beta 状态 |
| 2025-08-27 | `94f96138` | Motion Design: Moved scene state and data link plugins out of experimental into virtualproduction | 从 Experimental 迁移到 VirtualProduction 目录 |

### 维护评价

- **年龄**：约 1 年，属于较新的插件
- **维护频率**：初始创建后仅有少量维护性提交（日志宏迁移），无功能性更新
- **Beta 状态**：`IsBetaVersion=true`，接口可能发生变化
- **迁移历史**：从 Experimental 迁移而来，说明 Epic 在逐步稳定该功能，但尚未正式发布
- **已废弃 API**：`ControllerMappings_DEPRECATED` 已被标记为 UE 5.7 废弃，建议使用 `OutputProcessors` 替代

**评价**：该插件处于 Beta 阶段，功能相对稳定但接口仍可能调整。适合在虚拟制片项目中探索性使用，不建议在生产环境的关键路径中依赖。最近一次实质性更新（日志迁移）距离当前约 3 个月，维护不算活跃但也不算废弃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/AvalancheDataLink)
- [Avalanche 插件（Motion Design 核心）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [DataLink 插件（数据链接框架）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/DataLink)