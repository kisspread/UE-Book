# Mesh Partition Water

> Interoperability of Mesh Partition with the Water plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 网格分区水域 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图可放置组件） |
| 模块 | `MeshPartitionWater` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater) | |

## 用途

该插件是 **Mesh Partition（网格分区/MegaMesh）** 系统与 **Water** 插件之间的桥接层。它提供了一组修改器组件（Modifier），用于在 MegaMesh 地形上自动处理水体与地形的交互——即让河流、湖泊、海洋等水体能够正确地变形、混合和融合其下方的地形网格。

简单来说：如果你同时使用了 Mesh Partition 地形系统和 Water 水体系统，没有这个插件，两者无法配合工作。它解决的核心问题是：**水体需要在地形上"挖出"河床/湖床，并在水陆交界处产生自然的高度过渡和权重混合**。

## 使用场景

- 你使用 MegaMesh（网格分区）系统构建大型地形，同时需要用 Water 插件放置河流、湖泊、海洋 → 启用此插件让两者协同工作
- 你需要河流沿岸有自然的高度衰减和材质混合过渡，而不是水体与地形之间出现明显的硬切边 → 河流修改器自动沿样条计算衰减
- 你需要多个水体（如河流汇入湖泊）之间有正确的权重混合，避免地形变形冲突 → 内部水体权重通道处理重叠

## 蓝图用法

所有修改器组件均标记为 `BlueprintSpawnableComponent`，可直接作为组件添加到 Actor 上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaxZDistance` | 设置修改器影响地形的最大垂直距离 | `UWaterModifier` |
| `IsEnabled` | 查询修改器是否启用 | `UWaterModifier` |
| `GetWaterBodyActor` | 获取关联的水体 Actor | `UWaterModifier` |
| `GetWaterBodyComponent` | 获取水体组件 | `UWaterModifier` |
| `GetWaterSpline` | 获取水体样条组件 | `UWaterModifier` |

### 三种修改器组件

| 组件类 | 用途 |
|---|---|
| `ULakeModifier` | 为湖泊类型的水体执行基于高度的 MegaMesh 变形 |
| `URiverModifier` | 为河流类型的水体执行基于高度的 MegaMesh 变形（沿样条衰减） |
| `UOceanModifier` | 为海洋类型的水体执行基于高度的 MegaMesh 变形 |

### 使用示例（蓝图描述）

1. 在场景中放置一个 Water Body Actor（如河流）
2. 为其添加对应的修改器组件：选中 Water Body → Add Component → `ULakeModifier` / `URiverModifier` / `UOceanModifier`
3. 在组件详情面板中调整 `MaxZDistance` 属性，控制地形受影响的最大高度范围
4. 构建 MegaMesh 时，修改器会自动计算地形顶点的混合权重和高度变形

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionWaterModifier.h"
```

### 基本用法

从源码分析，主要涉及自定义修改器组件的创建和水体高度计算。

```cpp
// 获取水体修改器的基本信息（基于 UWaterModifier 公开接口）
UWaterModifier* WaterMod = FindComponentByClass<UWaterModifier>();
if (WaterMod && WaterMod->IsEnabled())
{
    // 设置地形受影响的最大垂直距离
    WaterMod->SetMaxZDistance(15000.0);
    
    // 获取关联的水体 Actor
    AWaterBody* WaterBody = WaterMod->GetWaterBodyActor();
    UWaterSplineComponent* Spline = WaterMod->GetWaterSpline();
}
```

### 进阶用法

重写修改器背景操作，自定义地形变形逻辑：

```cpp
// 继承 UWaterModifier 创建自定义水体修改器
UCLASS(meta = (BlueprintSpawnableComponent))
class UMyWaterModifier : public MeshPartition::UWaterModifier
{
    GENERATED_BODY()
public:
    virtual TSharedPtr<const MeshPartition::IModifierBackgroundOp> 
        CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const override;
    
    virtual FGuid GetCodeVersionKey() const override;
    virtual TArray<FBox> ComputeBounds() const override;
};
```

在背景操作中，可使用基类提供的静态辅助函数：

```cpp
// 计算顶点高度混合衰减（在 BackgroundOp 中调用）
float FalloffHeight = UWaterModifier::CalculateVertexFalloffHeight(
    InternalBlendWeight,
    bIsInsideWater,
    WaterHeight,
    DistanceFromSpline,
    TargetHeight,
    MeshVertexZ,
    HeightmapSettings,
    CurveSettings
);

// 计算顶点权重（用于材质混合）
float Weight = UWaterModifier::CalculateVertexWeight(
    bIsInsideWater,
    DistanceFromSpline,
    WeightmapSettings
);

// 注册水体权重图
UWaterModifier::RegisterWaterWeightmaps(WeightMaps, InstanceInfo);
```

## Demo 示例

以下展示如何创建一个自定义的湖泊修改器：

```cpp
// MyLakeModifier.h
#pragma once

#include "CoreMinimal.h"
#include "MeshPartitionWaterModifier.h"

UCLASS(meta = (BlueprintSpawnableComponent))
class MYPROJECT_API UMyLakeModifier : public MeshPartition::UWaterModifier
{
    GENERATED_BODY()

public:
    UMyLakeModifier();

    // UModifierComponent 接口
    virtual TSharedPtr<const MeshPartition::IModifierBackgroundOp> 
        CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const override;
    virtual FGuid GetCodeVersionKey() const override;
    virtual TArray<FBox> ComputeBounds() const override;
};

// MyLakeModifier.cpp
#include "MyLakeModifier.h"
#include "WaterBodyLakeActor.h"

UMyLakeModifier::UMyLakeModifier()
{
    MaxZDistance = 8000.0;
}

TArray<FBox> UMyLakeModifier::ComputeBounds() const
{
    // 使用水体组件的边界来计算影响区域
    TArray<FBox> Bounds;
    if (AWaterBody* Body = GetWaterBodyActor())
    {
        Bounds.Add(Body->GetComponentsBoundingBox().ExpandBy(FVector(0, 0, MaxZDistance)));
    }
    return Bounds;
}
```

## 模块依赖

该插件本身依赖以下 UE 插件（已在 .uplugin 中声明）：

| 模块/插件 | 用途 |
|---|---|
| `Water` | 水体系统核心，提供水体 Actor、样条、权重设置等基础功能 |
| `MeshPartition` | 网格分区/MegaMesh 地形系统，提供修改器组件基类和构建管线 |

无特殊模块依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `d41ed57e` | Updating Ground Truth Meshes for Remesh and Boolean Modifiers | 更新 Remesh 和布尔修改器的基准网格测试数据 |
| 2026-03-20 | `4f6ea1be` | [Mesh Partition] | Mesh Partition 整体更新（批量提交） |
| 2026-03-13 | `a0b73b93` | add an internal water weight channel and use it to more cleanly blend different water modifiers toge... | 新增内部水体权重通道，改进多个水体修改器之间的混合效果 |
| 2026-03-05 | `29f7cf7b` | [Mesh Partition] Moved plugins into experimental. | 首次提交，将插件移入 Experimental 目录 |

### 维护评价

该插件创建于 2026 年 3 月，距今不到 1 个月，是一个**非常新的实验性插件**。

- **活跃度**：在创建后的近一个月内有 4 次提交，开发节奏较快
- **状态**：标记为 `IsExperimentalVersion=true`，且 `Installed=false`（不默认安装），说明尚处于实验阶段
- **功能成熟度**：已具备湖泊、河流、海洋三种水体修改器，且有内部权重混合机制，功能框架已成型
- **风险提示**：作为实验性插件，API 可能会随时变更，不建议用于生产环境

**推荐程度**：如果你正在使用 Mesh Partition + Water 系统，这是必选插件；但由于实验性状态，需做好 API 变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain#usingwaterbodytools)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater/Tests)（如有）