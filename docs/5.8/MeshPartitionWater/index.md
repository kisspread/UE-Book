# Mesh Partition Water

> Interoperability of Mesh Partition with the Water plugin.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshPartitionWater` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater) | |

## 用途

该插件为 Mesh Partition（网格分区/大网格地形）系统与 Water（水体）系统之间提供互操作层。它解决的核心问题是：当使用 Mesh Partition 生成大规模地形网格时，如何让地形自动适配水体（湖泊、海洋、河流）的形状——包括在水体边缘进行高度衰减、生成权重图用于材质混合，以及处理多个水体 modifier 之间的重叠混合。

简单来说，这个插件让 Mesh Partition 地形能够"感知"水体的存在，并自动在水体周围进行地形变形和材质权重分配，使得水岸过渡自然。

## 使用场景

- 你正在使用 Mesh Partition 系统构建大型地形，同时场景中有 Water 插件生成的湖泊、海洋或河流 → 需要此插件让地形自动适配水体形状
- 你需要地形在河流/湖泊边缘自动下沉，形成自然的河床/湖床效果 → 使用对应的 Lake/River/Ocean Modifier
- 场景中有多条河流交汇或河流汇入湖泊，需要平滑的权重混合 → 插件内置了内部水体权重通道处理重叠

## 蓝图用法

所有 Modifier 组件均标记为 `BlueprintSpawnableComponent`，可在蓝图中直接添加到 Actor。

### 核心组件

| 组件 | 说明 | 适用水体 |
|---|---|---|
| `ULakeModifier` | 湖泊地形变形 Modifier | 湖泊 (Lake) |
| `URiverModifier` | 河流地形变形 Modifier | 河流 (River) |
| `UOceanModifier` | 海洋地形变形 Modifier | 海洋 (Ocean) |

### 可编辑属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `MaxZDistance` | `double` | Modifier 影响地形的最大垂直距离（默认 10000） | `UWaterModifier` |

### 使用示例（蓝图描述）

1. 在你的 Mesh Partition Actor 上，添加 `ULakeModifier`（或 `URiverModifier` / `UOceanModifier`）组件
2. 组件会自动关联场景中对应的 Water Body Actor（通过 `WaterBrushActorInterface`）
3. 调整 `MaxZDistance` 控制地形受水体影响的最大垂直范围
4. 地形在构建时会自动根据水体形状进行高度变形和权重图生成

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionWaterModifier.h"  // 基类 UWaterModifier
```

> 注意：`ULakeModifier`、`URiverModifier`、`UOceanModifier` 的头文件位于 Private 目录，通常不需要直接 include。通过基类 `UWaterModifier` 和 Mesh Partition 的 Modifier 系统进行交互。

### 基本用法

该插件主要通过组件系统工作，核心交互方式是在 Mesh Partition 的 Modifier 框架中使用水体 Modifier：

```cpp
// UWaterModifier 提供的辅助方法，用于获取关联的水体信息
AWaterBody* WaterActor = WaterModifier->GetWaterBodyActor();
UWaterBodyComponent* WaterComponent = WaterModifier->GetWaterBodyComponent();
UWaterSplineComponent* WaterSpline = WaterModifier->GetWaterSpline();

// 检查 Modifier 是否启用
bool bEnabled = WaterModifier->IsEnabled();

// 设置最大影响距离
WaterModifier->SetMaxZDistance(5000.0);
```

### 进阶用法

`UWaterModifier` 提供了静态辅助函数，用于自定义水体混合计算：

```cpp
// 计算顶点的高度衰减权重
// 参数：是否在水体内、水体高度、到样条线距离、目标高度、网格Z值、高度图设置、曲线设置
float FalloffHeight = UWaterModifier::CalculateVertexFalloffHeight(
    InternalBlendWeight,  // 内部混合权重（会被修改）
    bIsInside,            // 顶点是否在水体内部
    WaterHeight,          // 水面高度
    DistanceFromSpline,   // 到水体样条线的距离
    TargetHeight,         // 目标高度
    MeshZ,                // 网格顶点Z值
    HeightmapSettings,    // 水体高度图设置
    CurveSettings         // 水体曲线设置
);

// 计算顶点的权重图 alpha 值（不包含调制纹理）
float Weight = UWaterModifier::CalculateVertexWeight(
    bIsInside,            // 是否在水体内部
    DistanceFromSpline,   // 到样条线距离
    WeightmapSettings     // 权重图设置
);

// 注册水体权重图到实例信息
UWaterModifier::RegisterWaterWeightmaps(WeightMaps, Instance);
```

## Demo 示例

以下展示如何创建一个自定义的水体 Modifier 组件：

```cpp
// MyWaterModifier.h
#pragma once

#include "CoreMinimal.h"
#include "MeshPartitionWaterModifier.h"
#include "MyWaterModifier.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyWaterModifier : public UE::MeshPartition::UWaterModifier
{
    GENERATED_BODY()

public:
    // 创建后台构建操作
    virtual TSharedPtr<const MeshPartition::IModifierBackgroundOp> 
    CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const override;

    // 返回代码版本标识，用于缓存失效
    virtual FGuid GetCodeVersionKey() const override;
};
```

```cpp
// MyWaterModifier.cpp
#include "MyWaterModifier.h"

TSharedPtr<const MeshPartition::IModifierBackgroundOp> 
UMyWaterModifier::CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const
{
    // 创建并返回后台操作，用于在构建线程中执行地形变形
    // 参考 ULakeModifier / URiverModifier 的实现
    return nullptr; // 需要实现具体的 FBackgroundOp
}

FGuid UMyWaterModifier::GetCodeVersionKey() const
{
    // 当此 GUID 变化时，缓存的构建结果会失效并重新构建
    return FGuid(0x12345678, 0x12345678, 0x12345678, 0x12345678);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshPartition` | 网格分区系统，提供 `UModifierComponent` 基类和构建框架 |
| `Water` | 水体系统，提供 `WaterBrushActorInterface`、`UWaterBodyComponent`、`UWaterSplineComponent` 等 |

## 维护状态

### 近期更新

```
- 2026-04-01 d41ed57e Updating Ground Truth Meshes for Remesh and Boolean Modifiers
- 2026-03-20 4f6ea1be [Mesh Partition]
- 2026-03-13 a0b73b93 add an internal water weight channel and use it to more cleanly blend different water modifiers together
- 2026-03-05 29f7cf7b [Mesh Partition]（初始提交）
```

### 维护评价

该插件创建于 2026 年 3 月，是一个非常新的实验性插件。从 git 历史来看，在创建后的一个月内有 4 次提交，包括功能增强（内部水体权重通道用于多水体混合）和测试资源更新，表明处于**活跃开发**阶段。

**注意事项**：
- 标记为 `IsExperimentalVersion: true`，API 可能随时变化
- `EnabledByDefault: false`，需要手动在插件设置中启用
- 依赖 Mesh Partition 和 Water 两个插件，确保它们已启用
- 作为实验性功能，建议在生产环境中谨慎使用

**推荐**：如果你正在使用 Mesh Partition 构建地形并需要水体交互，这是官方推荐的互操作方案。虽然是实验性阶段，但由 Epic Games 维护，质量有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain#usingwaterbodytools)