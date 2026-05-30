# Foliage Support (Level Snapshots)

> （Description 为空，基于源码分析生成文档）

| 属性 | 值 |
|---|---|
| 中文名 | 植被快照支持 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时逻辑） |
| 模块 | `FoliageSupport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

本模块为 `LevelSnapshots` 插件提供了对虚幻引擎内置植被系统（`AInstancedFoliageActor`）的全面支持。它解决了在使用 `LevelSnapshots` 进行场景状态保存（快照）与恢复（回滚）时，植被实例（Foliage Instances）这一特殊、复杂对象无法被正确序列化和反序列化的问题。

具体来说，它通过实现 `ICustomObjectSnapshotSerializer` 等接口，接管了植被Actor的序列化流程，确保植被类型（`UFoliageType`）、实例位置、旋转、缩放等数据能够被可靠地捕获到快照中，并在恢复时能正确应用回编辑器世界，处理了组件冲突、子对象识别等棘手问题。

## 使用场景

- **虚拟制片**：在影视拍摄中，需要频繁保存和恢复不同拍摄镜头对应的完整场景状态，包括大量精心布置的植被。
- **关卡设计迭代**：关卡设计师在布局植被后，可以创建快照作为“检查点”。如果后续修改不满意，可以一键回滚到快照状态，无需手动重新放置。
- **多人协作与场景同步**：在版本控制或多用户协作编辑场景时，此模块确保了植被状态在同步和合并过程中的可靠性。

## 蓝图用法

此模块主要通过 C++ 接口与 `LevelSnapshots` 主模块交互，未提供直接的蓝图可调用函数（`UFUNCTION(BlueprintCallable)`）。其功能在用户执行快照或恢复操作时由引擎内部调用。

### 控制台变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `AllowFoliageDataPre5dot1` | 是否允许应用5.1之前版本保存的、可能格式不正确的植被数据。仅在确定数据兼容时启用。 | `false` |

### 使用示例（蓝图描述）

1.  **保存快照**：在关卡编辑器中，选中包含 `AInstancedFoliageActor` 的关卡或Actor，使用 `LevelSnapshots` 面板创建快照。此模块会自动处理植被数据的序列化。
2.  **恢复快照**：在 `LevelSnapshots` 面板中选择一个之前的快照，点击“Apply”或“Restore”。此模块会自动处理植被数据的反序列化，并将其正确应用到编辑器世界中的 `AInstancedFoliageActor` 上。

## C++ 用法

本模块的功能主要通过实现一组特定接口来融入 `LevelSnapshots` 系统，供引擎内部调用。开发者通常无需直接调用其函数，而是理解其集成机制。

### 头文件引入

```cpp
#include "ILevelSnapshotsModule.h"
#include "Interfaces/ISnapshotRestorabilityOverrider.h"
#include "Interfaces/ICustomObjectSnapshotSerializer.h"
#include "Interfaces/IRestorationListener.h"
```

### 基本用法（模块注册）

在 `FoliageSupportModule` 的 `StartupModule` 中，将支持类注册到 `LevelSnapshots` 模块。
（来源：`Private/FoliageSupportModule.cpp`，推测）

```cpp
void FFoliageSupportModule::StartupModule()
{
    // 获取 LevelSnapshots 模块实例
    ILevelSnapshotsModule* LevelSnapshotsModule = FModuleManager::GetModulePtr<ILevelSnapshotsModule>(TEXT("LevelSnapshots"));
    if (LevelSnapshotsModule)
    {
        // 注册植被支持，使 LevelSnapshots 系统知道如何处理 AInstancedFoliageActor
        UE::LevelSnapshots::Foliage::Private::FFoliageSupport::Register(*LevelSnapshotsModule);
    }
}
```

### 进阶用法（理解核心接口实现）

`FFoliageSupport` 类同时实现了多个关键接口，定义了植被在快照生命周期中的行为：

1.  **`ISnapshotRestorabilityOverrider`**：决定哪些Actor（如 `AInstancedFoliageActor`）在快照捕获时是“需要”的。
2.  **`ICustomObjectSnapshotSerializer`**：核心接口，定义了如何将植被Actor及其内部数据（`FFoliageInfoData`, `FInstancedFoliageActorData`）序列化到快照档案（`FArchive`）中，以及如何从档案中读取数据并应用到世界中的对象。
3.  **`IRestorationListener`**：在快照恢复的各个阶段（如应用前、应用后、Actor重建前后）提供回调，用于处理植被组件的刷新、冲突解决等后置逻辑。
4.  **`IActorSnapshotFilter`**：在更细粒度上控制是否允许修改或重建匹配的植被Actor。

## Demo 示例

以下示例展示了如何创建一个简化的、集成 `LevelSnapshots` 并特别处理自定义Actor的框架。`FoliageSupport` 的实现是更复杂、专门针对植被的版本。

**MyCustomActorSnapshotSupport.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Interfaces/ICustomObjectSnapshotSerializer.h"
#include "Interfaces/ISnapshotRestorabilityOverrider.h"

class UMyCustomComponent;
class ILevelSnapshotsModule;

class FMyCustomActorSnapshotSupport : public ICustomObjectSnapshotSerializer, public ISnapshotRestorabilityOverrider
{
public:
    static void Register(ILevelSnapshotsModule& Module);

    // ISnapshotRestorabilityOverrider
    virtual ERestorabilityOverride IsActorDesirableForCapture(const AActor* Actor) override;

    // ICustomObjectSnapshotSerializer
    virtual void OnTakeSnapshot(UObject* EditorObject, ICustomSnapshotSerializationData& DataStorage) override;
    virtual UObject* FindOrRecreateSubobjectInSnapshotWorld(UObject* SnapshotObject, const ISnapshotSubobjectMetaData& ObjectData, const ICustomSnapshotSerializationData& DataStorage) override;
    virtual void PostApplyToEditorObject(UObject* Object, const ICustomSnapshotSerializationData& DataStorage, const FPropertySelectionMap& SelectionMap) override;
    // ... 其他接口方法可返回 nullptr 或空实现
};
```

**MyCustomActorSnapshotSupport.cpp**
```cpp
#include "MyCustomActorSnapshotSupport.h"
#include "MyCustomActor.h" // 假设的自定义Actor头文件
#include "ILevelSnapshotsModule.h"

void FMyCustomActorSnapshotSupport::Register(ILevelSnapshotsModule& Module)
{
    // 注册此支持类，使其处理 AMyCustomActor 类型的Actor
    Module.RegisterCustomSnapshotSerializer(AMyCustomActor::StaticClass(), MakeShared<FMyCustomActorSnapshotSupport>());
    Module.RegisterActorSnapshotFilter(AMyCustomActor::StaticClass(), MakeShared<FMyCustomActorSnapshotSupport>());
}

ERestorabilityOverride FMyCustomActorSnapshotSupport::IsActorDesirableForCapture(const AActor* Actor)
{
    // 只捕获我们的自定义Actor
    return Cast<AMyCustomActor>(Actor) ? ERestorabilityOverride::Desirable : ERestorabilityOverride::DontCare;
}

void FMyCustomActorSnapshotSupport::OnTakeSnapshot(UObject* EditorObject, ICustomSnapshotSerializationData& DataStorage)
{
    AMyCustomActor* MyActor = Cast<AMyCustomActor>(EditorObject);
    if (MyActor && MyActor->MyCustomComponent)
    {
        // 将自定义组件的某些关键数据（如计数器）序列化到快照存储中
        int32 CounterValue = MyActor->MyCustomComponent->GetCounter();
        DataStorage.AddCustomData(TEXT("CounterKey"), FMemoryWriter(CounterValue));
    }
}

UObject* FMyCustomActorSnapshotSupport::FindOrRecreateSubobjectInSnapshotWorld(UObject* SnapshotObject, const ISnapshotSubobjectMetaData& ObjectData, const ICustomSnapshotSerializationData& DataStorage)
{
    // 为快照世界中的Actor重建子对象（如果需要）
    return nullptr;
}

void FMyCustomActorSnapshotSupport::PostApplyToEditorObject(UObject* Object, const ICustomSnapshotSerializationData& DataStorage, const FPropertySelectionMap& SelectionMap)
{
    AMyCustomActor* MyActor = Cast<AMyCustomActor>(Object);
    if (MyActor && MyActor->MyCustomComponent)
    {
        // 从快照存储中读取数据并应用到编辑器世界的对象
        const TArray<uint8>* Data = DataStorage.FindCustomData(TEXT("CounterKey"));
        if (Data)
        {
            int32 CounterValue;
            FMemoryReader Reader(*Data);
            Reader << CounterValue;
            MyActor->MyCustomComponent->SetCounter(CounterValue);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | 用于获取植被相关的编辑器工具类和数据结构，以支持植被实例的操作。 |
| `LevelSnapshots` | 核心模块，提供快照系统的接口（`ILevelSnapshotsModule`, `ICustomSnapshotSerializationData` 等）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下导致双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复了关于虚拟制作资产可能未包含在项目中的相关警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整了虚拟制作资产的分类和存储路径。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将模块内的日志宏从 `UE_LOG` 迁移到新的 `UE_LOGF` 格式。 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为调试跟踪通道和其他地方添加了描述信息。 |

### 维护评价

- **状态**：**维护中**。最近一次实质性提交在2026年5月，表明该模块仍在被主动维护和更新。
- **活跃度**：更新频率稳定，近期的提交主要集中在编译警告修复、资产组织和日志标准化，属于常规维护和改进。
- **建议**：该模块作为 `LevelSnapshots` 的关键扩展，为虚拟制作中的植被管理提供了必不可少的功能。鉴于其仍在维护且解决了核心痛点，**推荐在需要进行复杂植被状态管理的虚拟制作或关卡设计项目中使用**。需注意其标记为**实验性**（`IsBetaVersion: true`），使用时应关注后续版本的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [官方文档]() （.uplugin 未提供 DocsURL）
- [测试用例]() （未在提供的模块文件列表中发现明确测试文件）