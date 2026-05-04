# Physics Toolsets

> AI-callable toolsets for working with Unreal Engine physics.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PhysicsToolsets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PhysicsToolsets) | |

## 用途

PhysicsToolsets 是 Unreal Engine AI 助手工具集系统的一部分，为 AI 提供操作物理资产（Physics Asset）的结构化接口。它将物理资产中的刚体（Body）、碰撞形状（Shape）和约束（Constraint）抽象为标准化的数据结构，使 AI 能够以编程方式查询和修改骨骼网格体的物理设置。

这个插件存在的意义是：物理资产的编辑通常需要在编辑器中手动操作，而通过 Toolset 接口，AI 助手可以自动化这些操作——例如批量修改碰撞形状类型、调整刚体的物理模式、或配置约束的运动限制。

## 使用场景

- 你需要通过 AI 助手批量调整角色骨骼的碰撞体形状 → 用 PhysicsToolsets
- 你需要自动化物理资产的配置流程（如将所有刚体设为 Kinematic） → 用 PhysicsToolsets
- 你需要在 AI 工作流中查询物理约束的当前状态 → 用 PhysicsToolsets

## 蓝图用法

本插件主要通过 Toolset 系统暴露给 AI，而非直接面向蓝图用户。以下枚举和结构体在蓝图中可用：

### 核心枚举

| 枚举 | 说明 |
|---|---|
| `EPhysicsShapeType` | 碰撞图元类型：Sphere（球体）、Capsule（胶囊体）、Box（盒体） |
| `EBodyPhysicsMode` | 刚体物理模式：Default（跟随组件状态）、Kinematic（运动学）、Simulated（始终模拟） |
| `EConstraintMotion` | 约束轴运动方式：Free（自由）、Limited（受限）、Locked（锁定） |

### 核心结构体

| 结构体 | 说明 |
|---|---|
| `FPhysicsShapeInfo` | 描述物理刚体上的单个碰撞图元，包含形状类型、位置、旋转、尺寸等属性 |

### FPhysicsShapeInfo 属性

| 属性 | 类型 | 说明 |
|---|---|---|
| `ShapeName` | `FString` | 形状的唯一标识名称 |
| `ShapeType` | `EPhysicsShapeType` | 碰撞图元类型 |
| `Center` | `FVector` | 骨骼局部空间中的中心位置（厘米） |
| `Rotation` | `FRotator` | 骨骼局部空间中的朝向（Capsule 的 Z 轴为长轴） |
| `Radius` | `float` | 半径（厘米），Sphere 和 Capsule 使用 |
| `HalfExtent` | `FVector` | 半尺寸（厘米），Box 使用 |
| `HalfHeight` | `float` | 胶囊体半高（厘米），Capsule 使用 |

## C++ 用法

### 头文件引入

```cpp
#include "PhysicsToolsets/PhysicsAssetToolset.h"
```

### 基本用法

```cpp
// 创建一个碰撞形状描述
FPhysicsShapeInfo ShapeInfo;
ShapeInfo.ShapeName = TEXT("head_sphere");
ShapeInfo.ShapeType = EPhysicsShapeType::Sphere;
ShapeInfo.Center = FVector(0.f, 0.f, 10.f);  // 骨骼局部空间偏移
ShapeInfo.Radius = 8.f;

// 创建胶囊体形状
FPhysicsShapeInfo CapsuleInfo;
CapsuleInfo.ShapeName = TEXT("spine_capsule");
CapsuleInfo.ShapeType = EPhysicsShapeType::Capsule;
CapsuleInfo.Center = FVector::ZeroVector;
CapsuleInfo.Rotation = FRotator(0.f, 0.f, 90.f);  // Z 轴为长轴
CapsuleInfo.Radius = 5.f;
CapsuleInfo.HalfHeight = 15.f;

// 创建盒体形状
FPhysicsShapeInfo BoxInfo;
BoxInfo.ShapeName = TEXT("pelvis_box");
BoxInfo.ShapeType = EPhysicsShapeType::Box;
BoxInfo.Center = FVector(0.f, 0.f, -5.f);
BoxInfo.HalfExtent = FVector(10.f, 8.f, 12.f);
```

### 进阶用法

结合枚举类型配置物理刚体的行为模式和约束：

```cpp
// 配置刚体物理模式
EBodyPhysicsMode BodyMode = EBodyPhysicsMode::Kinematic;  // 始终跟随动画

// 配置约束运动限制
EConstraintMotion SwingMotion = EConstraintMotion::Limited;
EConstraintMotion TwistMotion = EConstraintMotion::Locked;
```

## Demo 示例

```cpp
// PhysicsToolsetExample.h
#pragma once

#include "CoreMinimal.h"
#include "PhysicsToolsets/PhysicsAssetToolset.h"

class FPhysicsToolsetExample
{
public:
    /** 为角色头部创建标准碰撞球体 */
    static FPhysicsShapeInfo CreateHeadCollision()
    {
        FPhysicsShapeInfo Shape;
        Shape.ShapeName = TEXT("head");
        Shape.ShapeType = EPhysicsShapeType::Sphere;
        Shape.Center = FVector(0.f, 0.f, 8.f);
        Shape.Radius = 10.f;
        return Shape;
    }

    /** 为躯干创建胶囊体碰撞 */
    static FPhysicsShapeInfo CreateSpineCollision()
    {
        FPhysicsShapeInfo Shape;
        Shape.ShapeName = TEXT("spine");
        Shape.ShapeType = EPhysicsShapeType::Capsule;
        Shape.Center = FVector::ZeroVector;
        Shape.Rotation = FRotator(0.f, 0.f, 90.f);
        Shape.Radius = 12.f;
        Shape.HalfHeight = 25.f;
        return Shape;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | AI 工具集注册系统，本插件通过它将物理操作暴露给 AI |

## 维护状态

### 近期更新

```
- 2026-04-18 6471b168 [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools
- 2026-04-17 8c911af5 [Backout] - CL52878047
- 2026-04-17 9404cd3e [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools
- 2026-04-01 27afb6e8 [AI Assistant Toolsets] Move toolset tests under AI.Toolsets
- 2026-03-26 b2e45b7d Add Physics asset toolset
```

### 维护评价

- **创建时间**：2026-03-26，非常新的插件
- **活跃度**：创建后一个月内有多次更新，包括功能调整和回退操作，说明仍在积极开发迭代中
- **状态**：实验性（IsExperimentalVersion=true），默认未启用（EnabledByDefault=false）
- **风险提示**：API 可能频繁变动（从 git 历史可见有 backout 操作），不建议在生产环境使用
- **推荐**：适合关注 AI 辅助开发工作流的早期探索者，生产项目建议等待稳定版本

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PhysicsToolsets)
- [ToolsetRegistry 依赖插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)