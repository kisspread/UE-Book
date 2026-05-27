# Mesh Partition Water

> Interoperability of Mesh Partition with the Water plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 网格分区水体兼容 |
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPartitionWater` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater) | |

## 用途

本插件的核心功能是为 **Mesh Partition（网格分区/巨型网格）** 地形系统与 **Water（水体）** 插件提供互操作性。它允许水体（如河流、湖泊、海洋）在基于网格分区生成的地形上正确地交互，实现地形变形（例如河床凹陷、湖岸坡度）和材质混合（如水边沙滩、岸边过渡）。插件提供了一系列修改器组件，用于在网格分区构建过程中处理水体对地形的影响。

## 使用场景

- 你正在使用 **Mesh Partition** 插件生成大规模地形，并且地形中包含了使用官方 **Water** 插件创建的河流、湖泊或海洋。
- 你希望水体能够自动、正确地塑造下方或周围的网格分区地形，例如让河流河床低于周围地形，让湖泊拥有平缓的岸边坡度。
- 你需要在水体与地形的交界处实现自然的材质权重过渡（例如水边沙地）。

## 蓝图用法

插件主要提供组件形式，需要在水体或网格分区的Actor中添加相应的修改器组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Max Z Distance` | 设置此水体修改器影响地形的最大垂直距离。 | `UWaterModifier` |
| `Is Enabled` | 查询此水体修改器是否启用。 | `UWaterModifier` |

### 使用示例（蓝图描述）

1.  在你的 `WaterBody` Actor（如 `WaterBody_River` 或 `WaterBody_Lake`）上，添加一个对应的修改器组件（如 `URiverModifier` 或 `ULakeModifier`）。
2.  在组件的细节面板中，调整 `Max Z Distance` 属性，以控制水体对地形的变形影响范围。
3.  当网格分区系统构建地形时，这些修改器组件会自动参与计算，根据水体的形状（通过 `WaterSpline`）和设置对网格分区地形的顶点和权重进行变形和混合。

## C++ 用法

本插件主要作为编辑器和构建时工具使用，其核心类是 `UWaterModifier` 及其子类。

### 头文件引入

```cpp
// 根据具体修改器类型引入对应头文件
#include "MeshPartitionWaterModifier.h" // UWaterModifier 基类
#include "MeshPartitionRiverModifier.h" // URiverModifier
#include "MeshPartitionLakeModifier.h"  // ULakeModifier
```

### 基本用法

创建一个继承自 `UWaterModifier` 的自定义修改器组件，以实现特定的水体交互逻辑。
```cpp
// MyCustomWaterModifier.h
#pragma once

#include "MeshPartitionWaterModifier.h"
#include "MyCustomWaterModifier.generated.h"

UCLASS(ClassGroup=(MeshPartition), meta=(BlueprintSpawnableComponent))
class UMyCustomWaterModifier : public MeshPartition::UWaterModifier
{
    GENERATED_BODY()

public:
    // 覆写核心方法，定义你的自定义地形修改逻辑
    virtual void PostProcessSection(AActor* InSection) override;

    // 覆写背景操作创建方法，用于多线程地形构建
    virtual TSharedPtr<const MeshPartition::IModifierBackgroundOp> CreateBackgroundOp(
        const MeshPartition::EBuildType InBuildType) const override;

    // 返回一个版本Key，当你的逻辑改变时更新它，以强制地形重新构建
    virtual FGuid GetCodeVersionKey() const override;
};
```

### 进阶用法

在自定义修改器的 `CreateBackgroundOp` 中，创建一个后台操作对象，该对象将在构建线程中执行实际的顶点处理。
```cpp
// 在 UMyCustomWaterModifier 的 .cpp 中
TSharedPtr<const MeshPartition::IModifierBackgroundOp> UMyCustomWaterModifier::CreateBackgroundOp(
    const MeshPartition::EBuildType InBuildType) const
{
    // 创建一个后台操作实例，并将必要的设置（如 MaxZDistance）传递进去
    auto BackgroundOp = MakeShared<FMyCustomWaterBackgroundOp>();
    BackgroundOp->MaxZDistance = this->MaxZDistance;
    BackgroundOp->WaterSpline = GetWaterSpline(); // 调用基类的辅助函数获取水样条线
    return BackgroundOp;
}
```

## Demo 示例

一个最小化的自定义水体湖修改器示例。

```cpp
// SimpleLakeModifier.h
#pragma once

#include "MeshPartitionLakeModifier.h"
#include "SimpleLakeModifier.generated.h"

UCLASS(ClassGroup=(MeshPartition), meta=(BlueprintSpawnableComponent))
class USimpleLakeModifier : public MeshPartition::ULakeModifier
{
    GENERATED_BODY()

public:
    // 使用父类的所有默认实现，仅通过属性进行配置
    // 例如，你可以在蓝图中设置 MaxZDistance
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshPartition` | 核心的网格分区/地形构建系统。 |
| `Water` | 官方的水体插件，提供水体Actor、样条线和渲染系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `d41ed57e` | Updating Ground Truth Meshes for Remesh and Boolean Modifiers | 更新了用于重网格化和布尔运算修改器的基准网格数据。 |
| 2026-03-20 | `4f6ea1be` | [Mesh Partition] | 常规的网格分区系统更新。 |
| 2026-03-13 | `a0b73b93` | add an internal water weight channel and use it to more cleanly blend different water modifiers toge | 新增了内部水体权重通道，用于更干净地混合多个水体修改器。 |
| 2026-03-05 | `29f7cf7b` | [Mesh Partition] | 插件的首次提交，移入实验性文件夹。 |

### 维护评价

- **状态**：实验性插件，创建时间很短（约1年），处于**活跃开发**阶段。
- **更新频率**：近期有功能更新（如权重通道混合优化），表明核心功能仍在完善。
- **推荐使用**：**推荐在需要实现 Mesh Partition 地形与 Water 水体交互的项目中使用**。由于是实验性插件，其API和功能在未来版本中可能发生变化。在正式项目中使用前，建议进行充分的测试和验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartitionWater)
- [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain#usingwaterbodytools)（介绍 Mesh Partition 地形使用水体工具的部分）