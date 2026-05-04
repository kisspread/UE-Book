# World Partition HLOD Utilities

> Editor utility classes & HLOD layer asset types

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | WorldPartitionHLODUtilities (Editor) |
| 创建时间 | 2022-01-12 |
| 年龄标签 | 🆕 (4 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Editor/WorldPartitionHLODUtilities) | |

## 用途

WorldPartitionHLODUtilities 是 UE5 World Partition HLOD 系统的核心实现插件，提供了将 World Partition 中的大量 Actor 生成为 HLOD（Hierarchical Level of Detail）表示的所有 Builder 和工具类。

HLOD 解决的核心问题是：在开放世界中，当摄像机远离某个区域时，需要将该区域内成百上千个 Actor 替换为一个低面数的替代物，以大幅降低渲染开销。这个插件就是那个「替代物」的生成器。

它不只做简单的网格合并——它提供了 6 种不同的 HLOD 构建策略（从简单复制到网格合并到几何近似），支持自定义 Builder 扩展，并且管理 HLOD 的 Hash 计算以实现增量构建（只重建有变化的 HLOD）。

## 使用场景

- **开放世界项目**：使用 World Partition 管理大地图，需要 HLOD 来优化远处区域的渲染 → 在 HLOD Layer 资产中选择构建策略，然后通过 World Partition HLODs Builder 面板构建
- **大量重复静态网格体**（如森林、城市街道家具）→ 使用 **Instancing** 类型，将相同网格体的实例合并为 ISM，极大减少 draw call
- **需要保留视觉精度的近景 HLOD** → 使用 **MeshSimplify** 或 **MeshApproximate**，在减少面数的同时保留大致形状
- **允许最大简化的远景 HLOD** → 使用 **MeshMerge**，将所有网格体合并为一个并烘焙材质纹理
- **自定义 HLOD Actor** → 使用 **CustomHLODActor** 类型，让你的自定义 Actor 直接作为 HLOD 表示

## 蓝图用法

此插件是纯编辑器工具类，**没有 BlueprintCallable 函数**。所有交互通过编辑器 UI（HLOD Layer 资产的属性面板）和 World Partition HLODs Builder 命令完成。

### HLOD Layer 属性编辑

HLOD Layer 资产中可配置的 Builder Settings 属性（通过 Details 面板编辑）：

#### Mesh Merge 设置 (`UHLODBuilderMeshMergeSettings`)

| 属性 | 类型 | 说明 |
|---|---|---|
| `MeshMergeSettings` | `FMeshMergingSettings` | 合并网格体的详细设置（LOD、材质烘焙参数等） |
| `HLODMaterial` | `UMaterialInterface` | 不合并材质时使用的 HLOD 材质 |

#### Mesh Simplify 设置 (`UHLODBuilderMeshSimplifySettings`)

| 属性 | 类型 | 说明 |
|---|---|---|
| `MeshSimplifySettings` | `FMeshProxySettings` | 简化网格体的设置（目标面数、误差容限等） |
| `HLODMaterial` | `UMaterialInterface` | HLOD 材质 |

#### Mesh Approximate 设置 (`UHLODBuilderMeshApproximateSettings`)

| 属性 | 类型 | 说明 |
|---|---|---|
| `MeshApproximationSettings` | `FMeshApproximationSettings` | 几何近似设置（体素大小、法线计算等） |
| `HLODMaterial` | `UMaterialInterface` | HLOD 材质 |

#### Instancing 设置 (`UHLODBuilderInstancingSettings`)

| 属性 | 类型 | 说明 |
|---|---|---|
| `bDisallowNanite` | `bool` | 禁用 Nanite（需要使用 forced LOD 时必须关闭 Nanite） |
| `InstanceFilteringType` | `EInstanceFilteringType` | 实例过滤类型：不过滤 / 按最小范围 / 按最小面积 / 按最小体积 |
| `MinimumExtent` | `double` | 最小范围阈值（Unreal 单位） |
| `MinimumArea` | `double` | 最小面积阈值（uu²） |
| `MinimumVolume` | `double` | 最小体积阈值（uu³） |

## C++ 用法

### 头文件引入

```cpp
// HLOD 工具主类
#include "WorldPartition/HLOD/Utilities/WorldPartitionHLODUtilities.h"

// Builder 头文件（按需引入）
#include "WorldPartition/HLOD/Builders/HLODBuilderMeshMerge.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderMeshSimplify.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderMeshApproximate.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderInstancing.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderCustomHLODActor.h"

// Modifier
#include "WorldPartition/HLOD/Modifiers/HLODModifierMeshDestruction.h"
```

### HLOD Builder 架构

所有 Builder 继承自 `UHLODBuilder`，核心接口：

```cpp
class UHLODBuilder : public UObject
{
    // 获取该 Builder 对应的 Settings 类
    virtual TSubclassOf<UHLODBuilderSettings> GetSettingsClass() const;

    // 构建 HLOD 组件，返回生成的组件列表
    virtual TArray<UActorComponent*> Build(
        const FHLODBuildContext& InHLODBuildContext,
        const TArray<UActorComponent*>& InSourceComponents) const;

    // 计算 HLOD Hash（用于增量构建判断）
    virtual void ComputeHLODHash(FHLODHashBuilder& InHashBuilder) const;
};
```

### 自定义 HLOD Builder

要创建自定义的 HLOD 构建策略，需要创建两个类：

```cpp
// 1. Settings 类 - 定义可配置参数
UCLASS(Blueprintable, Config = Engine, PerObjectConfig)
class UMyHLODBuilderSettings : public UHLODBuilderSettings
{
    GENERATED_UCLASS_BODY()

    virtual void ComputeHLODHash(FHLODHashBuilder& InHashBuilder) const override;

    UPROPERTY(EditAnywhere, Category = HLOD)
    float MySimplificationRatio = 0.5f;
};

// 2. Builder 类 - 实际构建逻辑
UCLASS(MinimalAPI, HideDropdown)
class UMyHLODBuilder : public UHLODBuilder
{
    GENERATED_UCLASS_BODY()

public:
    virtual TSubclassOf<UHLODBuilderSettings> GetSettingsClass() const override
    {
        return UMyHLODBuilderSettings::StaticClass();
    }

    virtual TArray<UActorComponent*> Build(
        const FHLODBuildContext& InHLODBuildContext,
        const TArray<UActorComponent*>& InSourceComponents) const override;
};
```

然后在 HLOD Layer 中选择 `Custom` 类型并指定你的 Builder 类。

### 自定义 HLOD Modifier

Modifier 在 Builder 构建前后插入自定义逻辑（如破坏效果）：

```cpp
UCLASS(MinimalAPI)
class UMyHLODModifier : public UWorldPartitionHLODModifier
{
    GENERATED_UCLASS_BODY()

    // 判断该 Modifier 是否可以应用于当前 Builder
    virtual bool CanModifyHLOD(TSubclassOf<UHLODBuilder> InHLODBuilderClass) const override;

    // 在 HLOD 构建开始前调用
    virtual void BeginHLODBuild(const FHLODBuildContext& InHLODBuildContext) override;

    // 在 HLOD 构建完成后调用，可以修改生成的组件
    virtual void EndHLODBuild(TArray<UActorComponent*>& InOutComponents) override;
};
```

### HLOD Hash 增量构建

`FWorldPartitionHLODUtilities::BuildHLOD()` 内部会自动计算 HLOD Hash，只在内容变化时才真正重建。Hash 计算包含：

- 基础版本 Key（全局重建时更新）
- 源 Actor 列表及其引用
- 最小可见距离
- 各组件的几何 Hash
- Builder Settings 的 Hash

可以通过 `ComputeHLODHash()` 在不执行构建的情况下计算预期 Hash。

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `wp.Editor.HLOD.UseLegacy32BitNameHash` | `false` | 使用旧的 32 位 Hash 生成 HLOD Actor 名称。切换到 64 位会导致新的 Actor 文件 |

## Demo 示例

### 最小自定义 Builder 示例

```cpp
// MyHLODBuilder.h
#pragma once

#include "WorldPartition/HLOD/HLODBuilder.h"
#include "MyHLODBuilder.generated.h"

UCLASS(MinimalAPI, Blueprintable)
class UMyHLODBuilderSettings : public UHLODBuilderSettings
{
    GENERATED_UCLASS_BODY()

    virtual void ComputeHLODHash(FHLODHashBuilder& InHashBuilder) const override
    {
        FString BaseKey = TEXT("MY_CUSTOM_BUILDER_KEY");
        InHashBuilder.HashField(BaseKey, TEXT("MyBaseKey"));
    }
};

UCLASS(MinimalAPI, HideDropdown)
class UMyHLODBuilder : public UHLODBuilder
{
    GENERATED_UCLASS_BODY()

public:
    virtual TSubclassOf<UHLODBuilderSettings> GetSettingsClass() const override;
    virtual TArray<UActorComponent*> Build(
        const FHLODBuildContext& InHLODBuildContext,
        const TArray<UActorComponent*>& InSourceComponents) const override;
};

// MyHLODBuilder.cpp
#include "MyHLODBuilder.h"
#include "Components/StaticMeshComponent.h"

UMyHLODBuilderSettings::UMyHLODBuilderSettings(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer) {}

UMyHLODBuilder::UMyHLODBuilder(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer) {}

TSubclassOf<UHLODBuilderSettings> UMyHLODBuilder::GetSettingsClass() const
{
    return UMyHLODBuilderSettings::StaticClass();
}

TArray<UActorComponent*> UMyHLODBuilder::Build(
    const FHLODBuildContext& InHLODBuildContext,
    const TArray<UActorComponent*>& InSourceComponents) const
{
    TArray<UActorComponent*> Result;

    // 简单示例：创建一个代理网格组件
    UStaticMeshComponent* ProxyComponent = NewObject<UStaticMeshComponent>();
    // ... 设置代理网格体
    Result.Add(ProxyComponent);

    return Result;
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject"
});

PrivateDependencyModuleNames.AddRange(new string[]
{
    "Engine",
    "WorldPartitionHLODUtilities"  // 依赖 HLOD Builder 基类
});
```

## 模块依赖

此插件的 Build.cs 依赖如下（给想要扩展此插件的开发者参考）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（StaticMesh、Component 等） |
| `MaterialBaking` | MeshMerge 时烘焙材质纹理 |
| `MaterialUtilities` | 材质工具函数 |
| `MeshDescription` | 网格体描述数据 |
| `MeshMergeUtilities` | 网格体合并核心工具 |
| `StaticMeshDescription` | 静态网格体描述 |
| `WorldPartitionEditor` | World Partition 编辑器集成 |
| `GeometryProcessingInterfaces` | 几何处理接口（动态加载） |
| `MeshUtilities` | 网格体工具（动态加载） |
| `MeshReductionInterface` | 网格体减面接口（动态加载） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-10-17 | `3d31d124` | HLOD build world 改用私有 transient package，避免多个 world 连续构建时的冲突 (UE-349438) |
| 2025-10-15 | `5d7d0947` | 重构 Source Actors 加载：处理缺失的源 Actor 和重命名的 Level，在隔离 world 中加载 Actor，废弃 `UWorldPartitionLevelStreamingDynamic::LoadInEditor()` 改用 `FWorldPartitionLevelHelper::LoadActors()` (UE-295326) |
| 2025-09-29 | `70efc452` | 新增不执行重建即可计算更新后 HLOD Hash 的能力 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次实质性更新，包括架构重构和新功能
- 创建于 2022-01，已有约 4 年历史，是 UE5 World Partition 系统的核心组件
- 最近的更新集中在构建流程的稳健性改进（隔离构建环境、处理缺失资源等）
- 无废弃标记，`IsBetaVersion = false`，`EnabledByDefault = true`
- **推荐使用**：这是 UE5 World Partition HLOD 的官方实现，开放世界项目几乎必用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/WorldPartitionHLODUtilities)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/world-partition-hierarchical-level-of-detail-in-unreal-engine)
