# LevelSnapshots - nDisplay Support

> Level Snapshot support for nDisplay.

| 属性 | 值 |
|---|---|
| 中文名 | 虚幻显示快照支持 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LevelSnapshots` (Runtime), `LevelSnapshotFilters` (Runtime), `LevelSnapshotsEditor` (Runtime), `nDisplaySupport` (Runtime), `FoliageSupport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots/Source/nDisplaySupport) | |

## 用途

`nDisplaySupport` 模块是 `LevelSnapshots` 插件的一个扩展模块，专门为 **nDisplay**（虚幻引擎的多显示器/集群渲染系统）提供支持。它解决了核心 `LevelSnapshots` 模块无法正确处理 `ADisplayClusterRootActor` 及其复杂配置数据（如 `UDisplayClusterConfigurationData`）的子对象（Subobject）序列化与比较问题。

nDisplay 的配置涉及大量在运行时动态创建的对象（如视口配置节点 `UDisplayClusterConfigurationClusterNode`），默认的序列化器无法识别和保存这些对象。此模块通过实现 `ICustomObjectSnapshotSerializer` 和 `IPropertyComparer` 接口，为这些特殊对象提供了自定义的快照拍摄、查找和比较逻辑，确保在虚拟制片环境中，nDisplay 集群的复杂配置可以被准确地保存和恢复。

## 使用场景

- **虚拟制片流程中**：你在使用 nDisplay 系统配置多屏幕LED墙或投影系统时，需要保存当前的集群配置状态以便后续恢复或比较。
- **迭代内容开发**：对关卡内的 nDisplay 配置进行修改后，希望使用 Level Snapshot 功能快速比对修改前后的差异，或一键回退到之前的配置。
- **自动化测试**：需要验证 nDisplay 配置在序列化/反序列化过程中的正确性。

## 蓝图用法

此模块主要提供 C++ 层的底层序列化支持，没有直接暴露给蓝图使用的 `UFUNCTION` 或 `UPROPERTY`。其功能通过 `LevelSnapshots` 编辑器界面间接使用：当用户拍摄或应用一个包含 `ADisplayClusterRootActor` 的关卡快照时，此模块会在后台自动工作。

## C++ 用法

### 头文件引入

```cpp
#include "nDisplaySupportModule.h"
#include "Interfaces/ILevelSnapshotsModule.h"
```

### 基本用法 - 注册自定义序列化器

此模块的核心是向 `LevelSnapshots` 模块注册一系列自定义的序列化器和属性比较器。通常在模块 `StartupModule` 中完成。

```cpp
// 来源: Private/nDisplaySupportModule.cpp (推断)
void FnDisplaySupportModule::StartupModule()
{
    ILevelSnapshotsModule* LevelSnapshotsModule = FModuleManager::GetModulePtr<ILevelSnapshotsModule>(TEXT("LevelSnapshots"));
    if (LevelSnapshotsModule)
    {
        // 注册 DisplayClusterRootActor 的子对象序列化器和属性比较器
        FDisplayClusterRootActorSerializer::Register(*LevelSnapshotsModule);
        // 注册 DisplayClusterConfigurationData 的子对象序列化器
        FDisplayClusterConfigurationDataSerializer::Register(*LevelSnapshotsModule);
        // ... 注册其他 ClusterNode， Cluster 等 Map 子对象序列化器
        // FDisplayClusterConfigurationClusterNodeSerializer::Register(*LevelSnapshotsModule);
        // FDisplayClusterConfigurationClusterSerializer::Register(*LevelSnapshotsModule);
        
        // 注册材质覆盖属性的比较器
        FDisplayMaterialOverrideFix::Register(*LevelSnapshotsModule);
    }
}
```

### 进阶用法 - 自定义序列化器实现

`TReferenceSubobjectSerializer` 和 `TMapSubobjectSerializer` 是两个辅助模板，用于简化常见的序列化模式。

```cpp
// 示例：为自己的 Actor 类型实现一个简单的引用子对象序列化器
// 来源: Private/Helpers/ReferenceSubobjectSerializer.h
class FMyActorComponentSerializer
    : public TReferenceSubobjectSerializer<FMyActorComponentSerializer>
{
    // 1. 定义要支持的 Owner 类
    static UClass* GetSupportedClass() { return AMyActor::StaticClass(); }

    // 2. 实现查找子对象的逻辑
    UObject* FindSubobject(UObject* Owner) const
    {
        if (AMyActor* MyActor = Cast<AMyActor>(Owner))
        {
            return MyActor->GetMySpecialComponent(); // 返回需要序列化的子对象
        }
        return nullptr;
    }

public:
    // 3. 提供静态注册函数
    static void Register(ILevelSnapshotsModule& Module)
    {
        // 注册序列化器，并可选择标记某些属性不支持
        Module.RegisterCustomObjectSnapshotSerializer(GetSupportedClass(), MakeShared<FMyActorComponentSerializer>());
    }
};

// 在模块的 StartupModule 中调用：
// FMyActorComponentSerializer::Register(*LevelSnapshotsModule);
```

```cpp
// 示例：实现属性比较器，忽略某些动态生成的差异
// 来源: Private/Material/DisplayMaterialOverrideFix.h
class FMyDynamicPropertyFix : public IPropertyComparer
{
    // 1. 找到需要特殊处理的属性
    FProperty* DynamicProperty{};

public:
    FMyDynamicPropertyFix()
    {
        // 通过属性名或反射系统找到属性
        DynamicProperty = AMyActor::StaticClass()->FindPropertyByName(GET_MEMBER_NAME_CHECKED(AMyActor, bIsDynamicValue));
    }

    static void Register(ILevelSnapshotsModule& Module)
    {
        Module.RegisterPropertyComparer(AMyActor::StaticClass(), MakeShared<FMyDynamicPropertyFix>());
    }

    // 2. 实现比较逻辑
    virtual EPropertyComparison ShouldConsiderPropertyEqual(const FPropertyComparisonParams& Params) const override
    {
        if (Params.Property == DynamicProperty)
        {
            // 假设这个动态属性的变化总是被忽略（视为相等）
            return EPropertyComparison::TreatEqual;
        }
        return EPropertyComparison::CheckDefaultComparison;
    }
};
```

## Demo 示例

一个最小的可运行模块示例，展示如何为自定义 Actor 注册序列化支持。

```cpp
// MyLevelSnapshotExtension.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyLevelSnapshotExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyLevelSnapshotExtension.cpp
#include "MyLevelSnapshotExtension.h"
#include "Interfaces/ILevelSnapshotsModule.h"
#include "Helpers/ReferenceSubobjectSerializer.h"

using namespace UE::LevelSnapshots;

// 假设我们要支持的 Actor 类
class AMyPropActor : public AActor
{
public:
    UPROPERTY()
    UStaticMeshComponent* DynamicMesh;
};

// 自定义序列化器
class FMyPropActorMeshSerializer
    : public TReferenceSubobjectSerializer<FMyPropActorMeshSerializer>
{
    static UClass* GetSupportedClass() { return AMyPropActor::StaticClass(); }
    UObject* FindSubobject(UObject* Owner) const
    {
        if (AMyPropActor* Prop = Cast<AMyPropActor>(Owner))
        {
            return Prop->DynamicMesh;
        }
        return nullptr;
    }
public:
    static void Register(ILevelSnapshotsModule& Module)
    {
        Module.RegisterCustomObjectSnapshotSerializer(GetSupportedClass(), MakeShared<FMyPropActorMeshSerializer>());
    }
};

void FMyLevelSnapshotExtensionModule::StartupModule()
{
    if (ILevelSnapshotsModule* LevelSnapshots = FModuleManager::GetModulePtr<ILevelSnapshotsModule>(TEXT("LevelSnapshots")))
    {
        FMyPropActorMeshSerializer::Register(*LevelSnapshots);
    }
}

void FMyLevelSnapshotExtensionModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyLevelSnapshotExtensionModule, MyLevelSnapshotExtension);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | `nDisplaySupport` 模块的 Build.cs 中存在对此模块的依赖，可能用于处理 nDisplay 与植被系统的交互或冲突，具体用途需查看源码实现。 |

**其他标准依赖**：此模块还依赖 `LevelSnapshots`（核心库）、`Core`、`CoreUObject`、`Engine` 等基础模块，这些是常见依赖，无需特别列出。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复虚拟制片相关插件的依赖警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 重组虚拟制片资产分类并迁移。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF（可能是为了结构化日志）。 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为跟踪通道等地方添加描述信息。 |

### 维护评价

- **创建时间**：约 5 年前创建。
- **近期更新**：最近的更新（2026年）集中在代码规范（如日志宏迁移）、编译警告修复和资产组织上，**并非功能性更新**。这表明核心功能已相对稳定。
- **维护状态**：属于 **维护中但不活跃**。代码仍在跟随引擎主分支更新，但 nDisplaySupport 模块本身没有新的功能开发或重大问题修复。
- **已知限制**：模块标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，意味着它仍处于测试阶段，可能不适用于生产环境中的关键快照功能。其功能完全依赖于 `LevelSnapshots` 核心模块和 nDisplay 系统的稳定性。
- **推荐使用**：如果你在虚拟制片流程中严重依赖 nDisplay 配置和 Level Snapshot 功能，**可以谨慎启用此模块**，但需意识到其 Beta 状态。对于不使用 nDisplay 或对快照精度要求不高的项目，无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots/Source/nDisplaySupport)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/level-snapshots-in-unreal-engine/) (Level Snapshots 插件文档，nDisplay 部分可能需查阅 nDisplay 自身文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots/Tests)