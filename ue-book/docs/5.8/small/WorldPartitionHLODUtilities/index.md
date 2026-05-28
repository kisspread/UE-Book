# World Partition HLOD Utilities

> Editor utility classes & HLOD layer asset types

| 属性 | 值 |
|---|---|
| 中文名 | 世界分区HLOD工具 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WorldPartitionHLODUtilities` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2022-01-12 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WorldPartitionHLODUtilities) | |

## 用途

该插件是 World Partition HLOD 系统的**核心构建引擎**。World Partition 本身提供了 HLOD 的概念框架（HLOD Layer、HLOD Actor），但如何将源 Actor 的网格体转化为低细节的 HLOD 表现形式，则由本插件提供具体实现。

**核心功能：**

1. **HLOD 构建器（Builders）**：提供多种网格体合并/简化策略，将数十个高细节静态网格体合并为一个低细节 HLOD 网格体
2. **重建策略（Rebuild Policies）**：智能判断 HLOD 是否需要重新构建，避免不必要的全量重建
3. **修改器（Modifiers）**：在 HLOD 构建过程中插入自定义逻辑（如破碎系统集成）

没有这个插件，World Partition 的 HLOD 系统将无法执行实际的网格体构建操作。它默认启用，是开放世界项目的必备组件。

## 使用场景

- 你正在开发开放世界游戏，使用 World Partition 管理大型地图 → 需要此插件来构建 HLOD
- 你希望远距离降低渲染的 Actor 数量以提升性能 → 配置 HLOD Layer 选择合适的构建策略
- 你需要不同精度等级的 HLOD 选项 → 根据性能/质量需求选择 MeshMerge、MeshSimplify 或 MeshApproximate
- 你使用了 Nanite 网格体但需要非 Nanite 的 HLOD → 使用 Instancing 构建器并禁用 Nanite
- 你希望 HLOD 只在源数据实际变化时才重建 → 选择 HashCompare 或 ImageCompare 策略

## 蓝图用法

本插件主要是编辑器工具层，大部分操作通过编辑器 UI 完成（在 HLOD Layer 资产中选择构建器类型）。以下是可通过蓝图配置的设置类。

### 构建器设置类

| 设置类 | 说明 | 构建器 |
|---|---|---|
| `UHLODBuilderMeshMergeSettings` | 合并网格体设置，包含材质合并选项 | `UHLODBuilderMeshMerge` |
| `UHLODBuilderMeshSimplifySettings` | 简化网格体设置，使用 Proxy 生成 | `UHLODBuilderMeshSimplify` |
| `UHLODBuilderMeshApproximateSettings` | 近似网格体设置，自动代理生成 | `UHLODBuilderMeshApproximate` |
| `UHLODBuilderInstancingSettings` | 实例化设置，支持尺寸过滤和 Nanite 控制 | `UHLODBuilderInstancing` |
| `UHLODBuilderCustomHLODActorSettings` | 自定义 HLOD Actor 设置 | `UHLODBuilderCustomHLODActor` |

### 实例化构建器的关键配置

| 属性 | 类型 | 说明 |
|---|---|---|
| `bDisallowNanite` | bool | 禁用 Nanite，使用最后 LOD（强制 LOD 被 Nanite 忽略） |
| `InstanceFilteringType` | EInstanceFilteringType | 实例过滤方式：无/最小范围/最小面积/最小体积 |
| `MinimumExtent` | double | 最小范围阈值（Unreal 单位） |
| `MinimumArea` | double | 最小面积阈值（uu²） |
| `MinimumVolume` | double | 最小体积阈值（uu³） |

### 使用示例

1. **在编辑器中创建 HLOD Layer 资产**：右键 Content Browser → Miscellaneous → HLOD Layer
2. **选择构建器类型**：如 "Mesh Merge"、"Mesh Simplify"、"Instancing" 等
3. **配置构建器设置**：如合并材质、简化参数、Nanite 开关等
4. **应用到 World Partition 子级别**：将 HLOD Layer 赋予特定 Grid 的 HLOD 设置
5. **构建 HLOD**：World Partition 窗口 → Build HLOD

## C++ 用法

### 头文件引入

```cpp
#include "WorldPartition/HLOD/Utilities/WorldPartitionHLODUtilities.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderMeshMerge.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderMeshSimplify.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderMeshApproximate.h"
#include "WorldPartition/HLOD/Builders/HLODBuilderInstancing.h"
#include "WorldPartition/HLOD/RebuildPolicies/HLODRebuildPolicyHashCompare.h"
#include "WorldPartition/HLOD/RebuildPolicies/HLODRebuildPolicyImageCompare.h"
```

### 基本用法

获取 HLOD 工具接口并查询构建器：

```cpp
// 获取 HLOD 工具模块
IWorldPartitionHLODUtilitiesModule& HLODUtilitiesModule = 
    FModuleManager::Get().LoadModuleChecked<IWorldPartitionHLODUtilitiesModule>("WorldPartitionHLODUtilities");
IWorldPartitionHLODUtilities* HLODUtilities = HLODUtilitiesModule.GetUtilities();

// 根据 HLOD Layer 获取对应的构建器类
const UHLODLayer* HLODLayer = /* your HLOD Layer asset */;
TSubclassOf<UHLODBuilder> BuilderClass = HLODUtilities->GetHLODBuilderClass(HLODLayer);

// 创建构建器设置
UHLODBuilderSettings* Settings = HLODUtilities->CreateHLODBuilderSettings(
    const_cast<UHLODLayer*>(HLODLayer)
);
```

### 构建 HLOD

```cpp
// 构建 HLOD（由编辑器内部调用）
FHLODBuildParams BuildParams;
BuildParams.WorldPartition = WorldPartition;
BuildParams.HLODLayer = HLODLayer;
// ... 设置其他参数

bool bSuccess = HLODUtilities->BuildHLOD(BuildParams);
```

### 自定义构建器

```cpp
// 继承 UHLODBuilder 实现自定义 HLOD 构建逻辑
UCLASS()
class UMyCustomHLODBuilder : public UHLODBuilder
{
    GENERATED_UCLASS_BODY()

public:
    virtual TSubclassOf<UHLODBuilderSettings> GetSettingsClass() const override
    {
        return UMyCustomHLODBuilderSettings::StaticClass();
    }

    virtual TArray<UActorComponent*> Build(
        const FHLODBuildContext& InHLODBuildContext,
        const TArray<UActorComponent*>& InSourceComponents) const override
    {
        TArray<UActorComponent*> Result;
        // 你的自定义 HLOD 构建逻辑
        return Result;
    }
};
```

## Demo 示例

### 自定义 HLOD 构建器

```cpp
// MyHLODBuilder.h
#pragma once

#include "CoreMinimal.h"
#include "WorldPartition/HLOD/Builders/HLODBuilder.h"
#include "MyHLODBuilder.generated.h"

UCLASS(MinimalAPI, Blueprintable)
class UMyHLODBuilderSettings : public UHLODBuilderSettings
{
    GENERATED_UCLASS_BODY()

    UPROPERTY(EditAnywhere, Category = "MyHLOD")
    float SimplificationRatio = 0.5f;

    UPROPERTY(EditAnywhere, Category = "MyHLOD")
    bool bGenerateCollision = true;

    virtual void ComputeHLODHash(FHLODHashBuilder& InHashBuilder) const override
    {
        Super::ComputeHLODHash(InHashBuilder);
        InHashBuilder << SimplificationRatio << bGenerateCollision;
    }
};

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

```cpp
// MyHLODBuilder.cpp
#include "MyHLODBuilder.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

UMyHLODBuilderSettings::UMyHLODBuilderSettings(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

UMyHLODBuilder::UMyHLODBuilder(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
}

TArray<UActorComponent*> UMyHLODBuilder::Build(
    const FHLODBuildContext& InHLODBuildContext,
    const TArray<UActorComponent*>& InSourceComponents) const
{
    TArray<UActorComponent*> Result;

    const UMyHLODBuilderSettings* Settings = GetDefault<UMyHLODBuilderSettings>();

    // 收集所有源静态网格体
    TArray<UStaticMesh*> SourceMeshes;
    for (UActorComponent* Component : InSourceComponents)
    {
        if (UStaticMeshComponent* SMC = Cast<UStaticMeshComponent>(Component))
        {
            if (UStaticMesh* Mesh = SMC->GetStaticMesh())
            {
                SourceMeshes.AddUnique(Mesh);
            }
        }
    }

    if (SourceMeshes.Num() == 0)
    {
        return Result;
    }

    // 在这里实现你的自定义 HLOD 生成逻辑
    // 例如：使用 MeshMerge、MeshSimplify 等工具生成合并后的网格体

    return Result;
}
```

## 模块依赖

本插件深度集成 UE5 的 Mesh Merge/Proxy 工具链和 World Partition 系统。

| 模块 | 用途 |
|---|---|
| `MeshMergeUtilities` | 网格体合并核心工具（MeshMerge 构建器使用） |
| `MeshConversion` | 网格体转换工具 |
| `MeshDescription` | 网格体数据描述和操作 |
| `MeshBoneReduction` | 骨骼网格体简化 |
| `StaticMeshDescription` | 静态网格体描述 |
| `GeometryCore` | 几何处理核心 |
| `WorldPartitionHLOD` | HLOD 基础框架和接口 |
| `RHI` | 渲染硬件接口（用于图像捕获） |
| `RenderCore` | 渲染核心（SSIM 图像比较） |
| `ImageWriteQueue` | 图像写入队列 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `af3610de` | World Partition - HLOD: Mirror RVT volumes into BuildHLODWorld | 将RVT体积镜像到HLOD构建世界中 |
| 2026-04-29 | `8224a941` | [StandaloneHLOD] Fix duplicate entries in HLOD external resources package | 修复HLOD外部资源包中的重复条目 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到UE_LOGF新格式 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introduced replacement overloads that use a flags based parameter. | 废弃旧版对象遍历函数，引入基于标志位的新API |
| 2026-03-09 | `534017e5` | World Partition - HLOD: Make sure all materials are compiled before starting a HLOD build | 确保HLOD构建前所有材质已编译 |

### 维护评价

**✅ 活跃维护中**

- **创建时间**：2022年1月（随 UE5 一起诞生，属于 World Partition 系统核心组件）
- **更新频率**：最近2个月内有多次实质性更新，包括新功能（RVT 镜像）、bug 修复和 API 改进
- **维护状态**：该插件是 UE5 World Partition 和开放世界管线的核心组件，由 Epic 持续维护
- **已知限制**：作为编辑器插件，仅在编辑器环境下可用，运行时不可用
- **推荐度**：⭐⭐⭐⭐⭐ 如果使用 World Partition 开放世界，此插件为必备且默认启用

该插件自 UE5 发布以来持续活跃更新，是开放世界 HLOD 管线不可替代的核心组件，可放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WorldPartitionHLODUtilities)
- [World Partition 官方文档](https://docs.unrealengine.com/5.8/en-US/world-partition-in-unreal-engine/)
- [HLOD 官方文档](https://docs.unrealengine.com/5.8/en-US/hierarchical-level-of-detail-in-unreal-engine/)