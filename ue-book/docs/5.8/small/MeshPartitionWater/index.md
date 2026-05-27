# Mesh Partition Water

> Interoperability of Mesh Partition with the Water plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 网格分区水域 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MeshPartitionWater` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater) | |

## 用途

这个插件是 **Mesh Partition（网格分区地形）** 和 **Water（水体系统）** 之间的桥梁。Mesh Partition 是 UE5 的网格化地形系统（MegaMesh），而 Water 插件提供了湖泊、河流、海洋等水体工具。

此插件的核心功能是：**让水体能够影响网格地形的高度和混合权重**。具体来说：
- 湖泊（Lake）会根据水体边界对地形进行凹陷和高度混合
- 河流（River）会沿样条线对地形进行切削，形成河床
- 海洋（Ocean）会将地形拉低到海平面以下区域

如果没有这个插件，Mesh Partition 生成的网格地形将无法响应 Water 插件的水体工具，水体边缘会出现地形穿模或不匹配的问题。

## 使用场景

- 你使用 Mesh Partition 网格地形系统，同时场景中有 Water 水体（湖泊、河流、海洋）→ 需要此插件来实现地形与水体的正确交互
- 你需要地形在水体边界处自动产生过渡混合效果（高度衰减、权重图混合）→ 使用对应的 Modifier 组件

## 蓝图用法

本插件提供三个可直接放置的组件，分别对应三种水体类型。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ULakeModifier` | 湖泊水体地形修饰器，处理湖泊区域的地形变形 | `ULakeModifier` |
| `URiverModifier` | 河流水体地形修饰器，沿河流样条线削切地形 | `URiverModifier` |
| `UOceanModifier` | 海洋水体地形修饰器，处理海洋区域的地形变形 | `UOceanModifier` |

### 继承关系

所有三个组件均继承自 `UWaterModifier`，而 `UWaterModifier` 继承自 `MeshPartition::UModifierComponent`：

```
MeshPartition::UModifierComponent
  └─ UWaterModifier（抽象基类）
       ├─ ULakeModifier（湖泊）
       ├─ URiverModifier（河流）
       └─ UOceanModifier（海洋）
```

### 使用示例

1. **启用插件**：在 Edit → Plugins 中启用 MeshPartitionWater（需同时启用 Water 和 MeshPartition）
2. **添加组件**：在使用 Mesh Partition 地形的 Actor 上，添加 `LakeModifier`、`RiverModifier` 或 `UOceanModifier` 组件
3. **配置参数**：在组件详情面板中设置 `MaxZDistance`（最大垂直影响距离，默认 10000），控制修饰器在多大高度范围内影响地形
4. **自动交互**：组件会自动检测父级 Water Body Actor 的配置，根据水体样条线和高度图设置进行地形变形

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionWaterModifier.h"  // UWaterModifier 基类
```

### 基本用法

UWaterModifier 提供了静态辅助函数用于水体权重计算：

```cpp
// 来源: MeshPartitionWaterModifier.h
// 计算顶点高度衰减
float Alpha;
float WaterHeight = 500.0f;
float DistanceFromSpline = 100.0f;
float TargetHeight = 450.0f;
float MeshZ = 480.0f;

float FalloffHeight = UWaterModifier::CalculateVertexFalloffHeight(
    Alpha,           // [out] 内部混合权重
    bIsInside,       // 是否在水体内
    WaterHeight,     // 水面高度
    DistanceFromSpline, // 距样条线距离
    TargetHeight,    // 目标高度
    MeshZ,           // 网格当前Z值
    HeightmapSettings, // 高度图设置
    CurveSettings    // 曲线设置
);

// 计算顶点权重图 Alpha
float Weight = UWaterModifier::CalculateVertexWeight(
    bIsInside,
    DistanceFromSpline,
    WeightmapSettings
);
```

### 进阶用法

可以通过继承 `UWaterModifier` 创建自定义水体修饰器：

```cpp
// 创建自定义修饰器（参考 UOceanModifier 的简洁实现）
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

## Demo 示例

```cpp
// MyWaterTerrainModifier.h
#pragma once

#include "CoreMinimal.h"
#include "MeshPartitionWaterModifier.h"

UCLASS(meta = (BlueprintSpawnableComponent))
class UMyCustomWaterModifier : public MeshPartition::UWaterModifier
{
    GENERATED_BODY()

public:
    UMyCustomWaterModifier();

    // 自定义边界计算
    virtual TArray<FBox> ComputeBounds() const override;
    
    // 创建后台操作
    virtual TSharedPtr<const MeshPartition::IModifierBackgroundOp> 
        CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const override;
    
    // 版本标识
    virtual FGuid GetCodeVersionKey() const override;
};
```

```cpp
// MyWaterTerrainModifier.cpp
#include "MyWaterTerrainModifier.h"

UMyCustomWaterModifier::UMyCustomWaterModifier()
{
    MaxZDistance = 5000.0; // 设置较小的影响范围
}

TArray<FBox> UMyCustomWaterModifier::ComputeBounds() const
{
    // 委托给基类处理
    return Super::ComputeBounds();
}

TSharedPtr<const MeshPartition::IModifierBackgroundOp> 
UMyCustomWaterModifier::CreateBackgroundOp(const MeshPartition::EBuildType InBuildType) const
{
    // 实现自定义后台地形变形逻辑
    return nullptr;
}

FGuid UMyCustomWaterModifier::GetCodeVersionKey() const
{
    // 返回版本标识，用于缓存失效检测
    return FGuid(0x12345678, 0, 0, 0);
}
```

## 模块依赖

本插件依赖以下插件（非标准模块）：

| 模块 | 用途 |
|---|---|
| `Water` | 水体系统插件，提供 AWaterBody、UWaterBodyComponent、UWaterSplineComponent 等水体基础设施 |
| `MeshPartition` | 网格分区系统插件，提供 UModifierComponent 基类和 MegaMesh 地形框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `d41ed57e` | Updating Ground Truth Meshes for Remesh and Boolean Modifiers | 更新重网格和布尔修饰器的基准网格数据 |
| 2026-03-20 | `4f6ea1be` | [Mesh Partition] | Mesh Partition 系统通用更新 |
| 2026-03-13 | `a0b73b93` | add an internal water weight channel and use it to more cleanly blend different water modifiers together | 新增内部水体权重通道，改善多水域修饰器间的混合过渡 |
| 2026-03-05 | `29f7cf7b` | [Mesh Partition] Moved plugins into experimental. | 创建插件，移入实验性目录 |

### 维护评价

- **状态**：🆕 新创建插件（约 1 个月），正处于活跃开发期
- **更新频率**：创建后持续有功能性更新（权重通道混合优化等）
- **实验性**：`IsExperimentalVersion=true`，`Installed=false`，需要手动启用
- **成熟度**：API 尚在演进中，不建议在生产环境使用
- **建议**：适合对 Mesh Partition + Water 交互有需求的开发者提前调研，等待正式发布后用于生产

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain#usingwaterbodytools)