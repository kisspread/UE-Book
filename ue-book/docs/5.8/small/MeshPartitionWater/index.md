# Mesh Partition Water

> Interoperability of Mesh Partition with the Water plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 网格分区水体适配 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPartitionWater` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater) | |

## 用途

该插件是 **网格分区系统 (Mesh Partition)** 与 **水体系统 (Water plugin)** 之间的桥梁。它提供了一组修改器组件（Modifier），用于控制网格分区所生成的大型地形网格（如 MegaMesh）如何响应水体（湖泊、河流、海洋）的存在。具体来说，它实现了地形网格在水体边缘的智能变形、混合和权重计算，确保地形与水体在视觉和逻辑上无缝衔接。

## 使用场景

- 你正在使用 **网格分区** 插件构建超大、连续的地形，并希望地形能够正确地与场景中的 **Water Body**（如河流、湖泊）交互。
- 你需要地形在水体边缘产生自然的凹陷（河床、湖底），并平滑过渡到水面。
- 你希望为不同类型的水体（湖、河、海）自定义地形如何被修改和混合。

## 蓝图用法

本插件的核心是几个 `UCLASS(BlueprintSpawnableComponent)` 组件，可以直接在蓝图中添加到 Actor 上使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ULakeModifier` | 为湖泊水体修改地形网格，实现高度混合。 | `ULakeModifier` |
| `URiverModifier` | 为河流水体修改地形网格，实现基于样条线的高度混合。 | `URiverModifier` |
| `UOceanModifier` | 为海洋水体修改地形网格。 | `UOceanModifier` |
| `UWaterModifier::IsEnabled()` | 检查修改器是否启用。 | `UWaterModifier` (基类) |
| `UWaterModifier::MaxZDistance` | 属性：修改器影响地形的最大垂直距离。 | `UWaterModifier` (基类) |

### 使用示例（蓝图描述）

1.  在场景中拥有一个 `Water Body` Actor（例如 `WaterBodyLake`）。
2.  创建一个 Actor（或直接在网格分区管理器的相关设置中），并添加 `ULakeModifier` 组件。
3.  将 `ULakeModifier` 组件的 `Water Body Actor` 属性指向场景中的 `WaterBodyLake` Actor。
4.  调整 `MaxZDistance` 来控制地形受影响的范围。
5.  当网格分区系统生成或更新地形时，该修改器会自动计算并应用地形变形。

## C++ 用法

### 头文件引入

```cpp
#include “MeshPartitionWaterModifier.h”
```

### 基本用法

该插件主要通过继承 `UWaterModifier` 基类来创建针对特定水体的修改器。基类提供了核心的计算逻辑和接口。

**创建自定义水体修改器 (继承自 UWaterModifier)**

```cpp
// MyCustomWaterModifier.h
#include “MeshPartitionWaterModifier.h”

UCLASS(meta=(BlueprintSpawnableComponent))
class UMyCustomWaterModifier : public MeshPartition::UWaterModifier
{
    GENERATED_BODY()
public:
    // 必须重写，用于创建后台运算对象
    virtual TSharedPtr<const MeshPartition::IModifierBackgroundOp> CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const override;
    
    // 重写以提供唯一版本标识，用于缓存失效
    virtual FGuid GetCodeVersionKey() const override;
};
```
*来源：Private/MeshPartitionLakeModifier.h, Private/MeshPartitionRiverModifier.h*

### 进阶用法

基类提供了静态辅助函数，可用于自定义后台运算中的顶点高度和权重计算。

```cpp
// 在你的 IModifierBackgroundOp::Execute 实现中
float CurrentWaterHeight = /* 计算当前水体高度 */;
float DistanceToSpline = /* 计算顶点到水样条线的距离 */;
float MeshZ = /* 获取网格顶点的高度 */;
float TargetTerrainHeight = /* 定义的目标地形高度 */;

// 计算顶点的混合权重（用于高度图混合）
float BlendWeight = 0.f;
bool bIsVertexInsideWater = /* 判断顶点是否在水体区域内 */;
float FinalHeight = UWaterModifier::CalculateVertexFalloffHeight(
    BlendWeight,
    bIsVertexInsideWater,
    CurrentWaterHeight,
    DistanceToSpline,
    TargetTerrainHeight,
    MeshZ,
    HeightmapSettings,
    CurveSettings
);

// 计算顶点的权重图 alpha（用于材质混合）
float WeightAlpha = UWaterModifier::CalculateVertexWeight(
    bIsVertexInsideWater,
    DistanceToSpline,
    WeightmapSettings
);
```
*来源：Private/MeshPartitionWaterModifier.h*

## Demo 示例

一个最小化的自定义水体修改器实现框架：

**MyOceanModifier.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “MeshPartitionWaterModifier.h”
#include “MyOceanModifier.generated.h”

UCLASS(meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyOceanModifier : public MeshPartition::UWaterModifier
{
    GENERATED_BODY()
public:
    virtual TSharedPtr<const MeshPartition::IModifierBackgroundOp> CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const override;
    virtual FGuid GetCodeVersionKey() const override;
};
```

**MyOceanModifier.cpp**
```cpp
#include “MyOceanModifier.h”

// 定义一个简单的后台运算操作
class FOceanBackgroundOp : public MeshPartition::IModifierBackgroundOp
{
public:
    virtual void Execute(/* 参数 */) const override
    {
        // 使用 UWaterModifier 的静态函数进行计算
        // ...
    }
};

TSharedPtr<const MeshPartition::IModifierBackgroundOp> UMyOceanModifier::CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const
{
    return MakeShared<FOceanBackgroundOp>();
}

FGuid UMyOceanModifier::GetCodeVersionKey() const
{
    // 返回一个代表当前实现的唯一 GUID，当代码逻辑变更时应修改此值
    static const FGuid MyVersionKey(TEXT(“ABCDEF01-2345-6789-ABCD-EF0123456789”));
    return MyVersionKey;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Water` | 核心水体插件，提供 `AWaterBody`、`UWaterBodyComponent` 等类和接口。 |
| `MeshPartition` | 核心网格分区插件，提供 `UModifierComponent`、`IModifierBackgroundOp` 等基类和接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `d41ed57e` | Updating Ground Truth Meshes for Remesh and Boolean Modifiers | 更新了重网格和布尔修改器的基准测试网格资产。 |
| 2026-03-20 | `4f6ea1be` | [Mesh Partition] | 针对网格分区系统的一般性改动或修复。 |
| 2026-03-13 | `a0b73b93` | add an internal water weight channel and use it to more cleanly blend different water modifiers toge... | 新增内部水体权重通道，用于更干净地混合多个水体修改器。 |
| 2026-03-05 | `29f7cf7b` | [Mesh Partition] | 插件初次提交，从其他位置移入实验性文件夹。 |

### 维护评价

这是一个**非常新**且**活跃维护**的实验性插件。创建于 2026 年 3 月，自创建以来有多次实质性功能更新（如混合算法改进）。作为 `IsExperimentalVersion=true` 的插件，其 API 和功能可能发生变化。目前来看，它正在被积极开发以解决网格分区与水体交互的特定问题，适合关注地形生成前沿技术的开发者尝试和跟踪。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater)
- [官方文档 (关于在 Mesh Terrain 中使用水体)](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain#usingwaterbodytools)