# Level Snapshots

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 关卡快照 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LevelSnapshots` (Runtime), `LevelSnapshotsEditor` (Runtime), `LevelSnapshotFilters` (Runtime), `FoliageSupport` (Runtime), `nDisplaySupport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 是一个关卡状态快照与回滚系统，用于捕获关卡（UWorld）在某一时刻的完整状态，并在需要时将关卡回滚到该状态。与编辑器内置的撤销系统（Undo/Transaction）不同，Level Snapshots 将整个关关的状态持久化到资产文件（ULevelSnapshot）中，可以跨编辑器会话保存，并支持**选择性恢复**——用户可以挑选哪些 Actor、哪些属性需要恢复。

核心工作流程：
1. **拍摄快照**：序列化整个 World 中所有 Actor、组件及其属性到 `ULevelSnapshot` 资产
2. **对比差异**：将快照与当前关卡进行 Diff，识别新增/删除/修改的 Actor 和属性
3. **选择性恢复**：通过 Filter 系统选择要恢复的属性，然后应用到编辑器世界

系统内部为每个 Actor 计算哈希（CRC32/MD5），在对比阶段可以跳过未变化的 Actor 以提升性能。快照数据使用 Oodle 压缩，支持多种压缩级别和算法。插件提供大量接口允许外部模块自定义序列化行为、属性比较逻辑和 Actor 恢复策略。

## 使用场景

- 你在 Virtual Production 中进行复杂的关卡布景，需要保存多个版本的关卡状态并在它们之间切换 → 用 Level Snapshots
- 你需要对关卡中特定 Actor 的特定属性进行回滚，而不是整体撤销 → 用 Level Snapshots 的 Filter 和 PropertySelection 系统
- 你正在开发需要自定义序列化逻辑的对象（如自定义组件），需要将其纳入快照系统 → 实现 `ICustomObjectSnapshotSerializer` 接口并注册到模块
- 你需要在蓝图中监听快照拍摄/恢复事件 → 通过 `ULevelSnapshotsEngineSubsystem` 的动态多播委托

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TakeLevelSnapshot` | 拍摄当前关卡的快照，返回 ULevelSnapshot 资产 | `ULevelSnapshotsFunctionLibrary` |
| `ApplySnapshotToWorld` | 将快照应用到当前世界，可选传入 Filter | `ULevelSnapshotsFunctionLibrary` |
| `SetSnapshotName` | 设置快照的用户自定义名称 | `ULevelSnapshot` |
| `SetSnapshotDescription` | 设置快照的描述文本 | `ULevelSnapshot` |
| `GetMapPath` | 获取快照拍摄时的地图路径 | `ULevelSnapshot` |
| `GetCaptureTime` | 获取快照拍摄时间 | `ULevelSnapshot` |
| `GetSnapshotName` | 获取快照名称 | `ULevelSnapshot` |
| `GetSnapshotDescription` | 获取快照描述 | `ULevelSnapshot` |

### 事件委托（ULevelSnapshotsEngineSubsystem）

| 委托 | 说明 |
|---|---|
| `OnPreTakeSnapshot` | 拍摄快照前触发 |
| `OnPostTakeSnapshot` | 拍摄快照后触发 |
| `OnPreApplySnapshot` | 应用快照到世界前触发 |
| `OnPostApplySnapshot` | 应用快照到世界后触发 |

### 使用示例（蓝图描述）

**拍摄快照**：从任意蓝图调用 `TakeLevelSnapshot` 节点，指定 `WorldContextObject`（通常用 Self 引用）、快照名称和描述。返回的 `ULevelSnapshot` 可以保存到变量或存入资产引用。

**应用快照**：调用 `ApplySnapshotToWorld` 节点，传入之前拍摄的 `ULevelSnapshot` 引用。`OptionalFilter` 参数留空则恢复所有数据，传入 Filter 资产则按规则选择性恢复。

**监听事件**：获取 `UEngineSubsystem` 的子类实例 `ULevelSnapshotsEngineSubsystem`，绑定 `OnPreTakeSnapshot` / `OnPostApplySnapshot` 等委托，可在快照生命周期各阶段执行自定义逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "ILevelSnapshotsModule.h"
#include "LevelSnapshotsFunctionLibrary.h"
#include "LevelSnapshotsFilteringLibrary.h"
#include "Data/LevelSnapshot.h"
```

### 基本用法

```cpp
// 引擎子系统暴露了蓝图事件，C++ 中也可以通过模块接口注册监听

// 检查模块是否可用
if (UE::LevelSnapshots::ILevelSnapshotsModule::IsAvailable())
{
    UE::LevelSnapshots::ILevelSnapshotsModule& Module = UE::LevelSnapshots::ILevelSnapshotsModule::Get();
    
    // 注册快照拍摄前的监听
    Module.OnPreTakeSnapshot().AddLambda([](const UE::LevelSnapshots::FPreTakeSnapshotEventData& Data)
    {
        UE_LOG(LogTemp, Log, TEXT("快照即将拍摄，目标世界: %s"), *Data.World->GetName());
    });
    
    // 注册快照拍摄后的监听
    Module.OnPostTakeSnapshot().AddLambda([](const UE::LevelSnapshots::FPostTakeSnapshotEventData& Data)
    {
        UE_LOG(LogTemp, Log, TEXT("快照已拍摄: %s"), *Data.Snapshot->GetSnapshotName().ToString());
    });
}
```

### 进阶用法

**自定义属性比较器**：当默认的属性比较逻辑不满足需求时（例如需要忽略浮点精度误差或自定义对象等价性判断），可以注册 `IPropertyComparer`：

```cpp
// 来源：ILevelSnapshotsModule.h - RegisterPropertyComparer
auto Comparer = MakeShared<FMyPropertyComparer>();
Module.RegisterPropertyComparer(AMyActor::StaticClass(), Comparer);

// 取消注册时使用同一实例
Module.UnregisterPropertyComparer(AMyActor::StaticClass(), Comparer);
```

**自定义对象序列化器**：对于需要手动管理子对象生命周期的对象，注册 `ICustomObjectSnapshotSerializer`：

```cpp
// 来源：ICustomObjectSnapshotSerializer.h
auto Serializer = MakeShared<FMyCustomSerializer>();
Module.RegisterCustomObjectSerializer(
    UMyCustomClass::StaticClass(),
    Serializer,
    true  // 是否包含蓝图子类
);
```

**注册全局 Actor 过滤器**：控制哪些 Actor 可以被修改、重建或删除：

```cpp
// 来源：IActorSnapshotFilter.h
auto Filter = MakeShared<FMyActorFilter>();
Module.RegisterGlobalActorFilter(Filter);
// 之后不再使用时
Module.UnregisterGlobalActorFilter(Filter);
```

**注册恢复监听器**：在快照恢复的各个阶段插入自定义逻辑：

```cpp
// 来源：IRestorationListener.h
auto Listener = MakeShared<FMyRestorationListener>();
Module.RegisterRestorationListener(Listener);
```

**快照滤镜扩展器**：在过滤阶段添加额外属性或修改对象状态：

```cpp
// 来源：ISnapshotFilterExtender.h
auto Extender = MakeShared<FMyFilterExtender>();
Module.RegisterSnapshotFilterExtender(Extender);
```

## Demo 示例

以下示例展示如何在 C++ 中实现一个简单的恢复监听器，用于在 Actor 被重建后执行自定义初始化：

```cpp
// MyRestorationListener.h
#pragma once

#include "Restorability/Interfaces/IRestorationListener.h"

class FMyRestorationListener : public UE::LevelSnapshots::IRestorationListener
{
public:
    // Actor 重建后的回调
    virtual void PostRecreateActor(AActor* RecreatedActor) override
    {
        UE_LOG(LogTemp, Log, TEXT("Actor 已从快照重建: %s"), *RecreatedActor->GetName());
    }

    // 应用属性到 Actor 前的回调
    virtual void PreApplySnapshotToActor(const UE::LevelSnapshots::FApplySnapshotToActorParams& Params) override
    {
        UE_LOG(LogTemp, Log, TEXT("即将对 Actor 应用快照数据: %s, 是否重建: %s"),
            *Params.Actor->GetName(),
            Params.bWasRecreated ? TEXT("是") : TEXT("否"));
    }

    // 整个快照应用完成后的回调
    virtual void PostApplySnapshot(const UE::LevelSnapshots::FPostApplySnapshotParams& Params) override
    {
        UE_LOG(LogTemp, Log, TEXT("快照应用完成"));
    }

    virtual ~FMyRestorationListener() = default;
};
```

```cpp
// MySnapshotSubsystem.cpp
#include "ILevelSnapshotsModule.h"
#include "MyRestorationListener.h"

void UMySnapshotSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    if (UE::LevelSnapshots::ILevelSnapshotsModule::IsAvailable())
    {
        UE::LevelSnapshots::ILevelSnapshotsModule& Module = UE::LevelSnapshots::ILevelSnapshotsModule::Get();
        
        // 注册自定义恢复监听器
        Listener = MakeShared<FMyRestorationListener>();
        Module.RegisterRestorationListener(Listener);
        
        // 注册能否拍摄快照的委托
        Module.AddCanTakeSnapshotDelegate(
            FName("MyGameplayCheck"),
            UE::LevelSnapshots::ILevelSnapshotsModule::FCanTakeSnapshot::CreateLambda(
                [](const UE::LevelSnapshots::FPreTakeSnapshotEventData& Data) -> bool
                {
                    // 例如：仅在编辑模式下允许拍摄快照
                    return Data.World && Data.World->WorldType == EWorldType::Editor;
                })
        );
    }
}

void UMySnapshotSubsystem::Deinitialize()
{
    if (UE::LevelSnapshots::ILevelSnapshotsModule::IsAvailable())
    {
        UE::LevelSnapshots::ILevelSnapshotsModule& Module = UE::LevelSnapshots::ILevelSnapshotsModule::Get();
        
        if (Listener)
        {
            Module.UnregisterRestorationListener(Listener);
            Listener.Reset();
        }
        
        Module.RemoveCanTakeSnapshotDelegate(FName("MyGameplayCheck"));
    }
    
    Super::Deinitialize();
}
```

## 模块依赖

以下模块不列出（属于标准 Core/Engine/Slate 依赖）：`Core`, `CoreUObject`, `Engine`, `Slate`, `SlateCore`。

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | FoliageSupport 子模块用于支持植被 Actor 的快照捕获与恢复 |
| 无其他特殊依赖（LevelSnapshots 核心模块仅依赖标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复虚拟制片中 EngineAssetDefinitions 插件未被包含的警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将虚拟制片资产迁移到不同的资产分类中 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为 Trace Channel 和其他位置添加描述 |

### 维护评价

- **状态**：实验性/Beta 版本（`.uplugin` 中 `IsBetaVersion: true`）
- **创建时间**：2021 年 2 月，约 4 年历史
- **更新频率**：近期（2026 年 4-5 月）有持续更新，但主要为编译警告修复和代码风格迁移，无功能性改动
- **活跃度**：作为 Virtual Production 工作流的核心组件，处于维护状态但未见重大新功能引入
- **注意事项**：默认未启用（`EnabledByDefault: false`），需在项目设置中手动启用。Beta 标记意味着 API 可能发生变化，生产环境使用需谨慎
- **推荐程度**：适合在 Virtual Production 项目中用于关卡版本管理，但需关注 Beta 状态带来的潜在不稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots)
- 官方文档（无）