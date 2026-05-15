# Physics Toolsets

> AI-callable toolsets for working with Unreal Engine physics.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 物理工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PhysicsToolsets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PhysicsToolsets) | |

## 用途

此插件提供了一套专门供 AI 助手调用的工具集，用于以编程方式操作 Unreal Engine 的物理资产（`UPhysicsAsset`）。它封装了创建、查询、修改和删除物理资产中刚体（`SkeletalBodySetup`）、碰撞形状以及约束的复杂逻辑，使得 AI 能够通过简单的函数调用来完成这些操作，而无需深入理解底层的编辑器 API。

核心解决的问题是：**让 AI 助手能够程序化地创建和编辑骨骼网格体的物理资产（如布娃娃系统）**。

## 使用场景

- 你的 AI 助手需要根据角色骨骼自动创建或优化布娃娃物理资产。
- 你需要在自动化流程中批量为多个骨骼网格体生成物理资产。
- AI 在调整角色动画后，需要同步更新其物理碰撞体。

## 蓝图用法

本插件所有功能均通过 `UPhysicsAssetToolset` 类的静态函数暴露，这些函数都标记了 `AICallable` 元数据，表明其为 AI 可调用接口。以下按功能分组列出核心节点。

### 核心节点

#### 创建与查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateFromMesh` | 从指定路径的骨骼网格体创建一个新的物理资产，并可选择是否将其分配给该网格体。 | `UPhysicsAssetToolset` |
| `GetBodyNames` | 获取物理资产中所有刚体的骨骼名称列表。 | `UPhysicsAssetToolset` |
| `GetBodyShapes` | 获取指定骨骼对应刚体上的所有碰撞形状信息。 | `UPhysicsAssetToolset` |
| `GetBodyPhysicsMode` | 查询指定骨骼对应刚体的物理模拟模式（默认、运动学、模拟）。 | `UPhysicsAssetToolset` |
| `GetBodyMassScale` | 查询指定骨骼对应刚体的质量缩放倍率。 | `UPhysicsAssetToolset` |
| `GetConstraints` | 获取物理资产中所有约束及其当前角度限制。 | `UPhysicsAssetToolset` |

#### 形状管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSphere` | 为指定骨骼的刚体添加或替换一个球形碰撞体。 | `UPhysicsAssetToolset` |
| `SetCapsule` | 为指定骨骼的刚体添加或替换一个胶囊体碰撞体。 | `UPhysicsAssetToolset` |
| `SetBox` | 为指定骨骼的刚体添加或替换一个盒体碰撞体。 | `UPhysicsAssetToolset` |
| `RemoveShape` | 根据名称从指定骨骼的刚体上移除一个碰撞形状。 | `UPhysicsAssetToolset` |

#### 刚体管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddBody` | 为指定骨骼添加一个空的刚体。 | `UPhysicsAssetToolset` |
| `RemoveBody` | 移除指定骨骼对应的刚体及其相关约束。 | `UPhysicsAssetToolset` |
| `SetBodyPhysicsMode` | 设置指定骨骼对应刚体的物理模拟模式。 | `UPhysicsAssetToolset` |
| `SetBodyMassScale` | 设置指定骨骼对应刚体的质量缩放倍率。 | `UPhysicsAssetToolset` |

#### 约束管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddConstraint` | 在两个已有的刚体之间添加一个新的约束。 | `UPhysicsAssetToolset` |
| `SetConstraintLimits` | 更新现有约束的角度限制。 | `UPhysicsAssetToolset` |
| `RemoveConstraint` | 移除两个刚体之间的约束。 | `UPhysicsAssetToolset` |

### 使用示例（蓝图描述）

1.  **创建物理资产**：调用 `CreateFromMesh` 节点，输入骨骼网格体的路径（如 `/Game/Characters/SKM_Hero`），并设置 `bAssignToMesh` 为 `true`。返回值即为新创建的物理资产对象。
2.  **添加碰撞体**：获取到物理资产后，调用 `SetSphere` 节点，依次传入物理资产对象、骨骼名称（如 `"head"`）、形状名称（如 `"head_sphere"`）、中心位置、半径。
3.  **配置约束**：调用 `GetConstraints` 获取约束列表，或用 `AddConstraint` 创建新约束。使用 `SetConstraintLimits` 节点，传入一个填充好 `Bone1Name`、`Bone2Name` 及 `Swing1Motion`、`Swing1LimitDegrees` 等参数的 `FPhysicsConstraintInfo` 结构体来设置限制。

## C++ 用法

所有函数均为静态函数，可直接通过类名调用。主要用于在自定义工具、编辑器实用程序或 AI 脚本中操作物理资产。

### 头文件引入

```cpp
#include "PhysicsToolsets/PhysicsAssetToolset.h"
```

### 基本用法

以下示例展示了如何通过代码创建物理资产并为其骨骼添加一个球形碰撞体。

```cpp
// 假设已获得一个骨骼网格体的路径
FString MeshPath = TEXT("/Game/Characters/SKM_Hero");

// 1. 创建物理资产并分配给网格体
UPhysicsAsset* NewPhysAsset = UPhysicsAssetToolset::CreateFromMesh(MeshPath, true);
if (NewPhysAsset)
{
    // 2. 为 “head” 骨骼添加一个半径为 10cm 的球形碰撞体，中心在骨骼原点
    UPhysicsAssetToolset::SetSphere(
        NewPhysAsset,
        TEXT("head"),          // 骨骼名称
        TEXT("head_sphere"),   // 形状名称，用于标识和替换
        FVector::ZeroVector,   // 骨骼局部空间的中心位置
        10.0f                  // 半径 (cm)
    );

    // 3. 查询刚体信息
    TArray<FString> BodyNames = UPhysicsAssetToolset::GetBodyNames(NewPhysAsset);
    UE_LOG(LogPhysicsToolsets, Log, TEXT("物理资产包含 %d 个刚体"), BodyNames.Num());

    // 4. 设置 “pelvis” 骨骼刚体的质量缩放
    UPhysicsAssetToolset::SetBodyMassScale(NewPhysAsset, TEXT("pelvis"), 1.5f);
}
```

### 进阶用法

组合使用约束和形状管理，为角色的腿部构建简单的物理结构。

```cpp
UPhysicsAsset* PhysAsset = ...; // 已有的物理资产

// 1. 确保 thigh 和 calf 骨骼有刚体
UPhysicsAssetToolset::AddBody(PhysAsset, TEXT("thigh"));
UPhysicsAssetToolset::AddBody(PhysAsset, TEXT("calf"));

// 2. 为它们添加碰撞体
UPhysicsAssetToolset::SetCapsule(
    PhysAsset, TEXT("thigh"), TEXT("thigh_capsule"),
    FVector(0, 0, -15), FRotator(90, 0, 0), 8.0f, 20.0f);
UPhysicsAssetToolset::SetCapsule(
    PhysAsset, TEXT("calf"), TEXT("calf_capsule"),
    FVector(0, 0, -10), FRotator(90, 0, 0), 6.0f, 15.0f);

// 3. 添加它们之间的约束并设置膝盖关节的活动范围
UPhysicsAssetToolset::AddConstraint(PhysAsset, TEXT("calf"), TEXT("thigh"));

FPhysicsConstraintInfo KneeConstraint;
KneeConstraint.Bone1Name = TEXT("calf"); // 子骨骼
KneeConstraint.Bone2Name = TEXT("thigh"); // 父骨骼
KneeConstraint.Swing1Motion = EConstraintMotion::Limited;
KneeConstraint.Swing1LimitDegrees = 45.0f; // 限制摆动1轴（Y轴）角度
KneeConstraint.Swing2Motion = EConstraintMotion::Locked; // 锁定摆动2轴（Z轴）
KneeConstraint.TwistMotion = EConstraintMotion::Limited;
KneeConstraint.TwistLimitDegrees = 10.0f; // 限制扭转轴（X轴）角度
UPhysicsAssetToolset::SetConstraintLimits(PhysAsset, KneeConstraint);
```

## Demo 示例

一个演示如何创建物理资产并配置基本布娃娃的最小示例。

**PhysicsDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "PhysicsDemo.generated.h"

UCLASS()
class UPhysicsDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    /** 运行物理资产创建和配置演示 */
    UFUNCTION(Exec, Category = "PhysicsDemo")
    void RunPhysicsAssetDemo();

private:
    void SetupRagdollPart(UPhysicsAsset* PhysAsset, const FString& BoneName,
                          const FString& ShapeName, const FVector& Center, float Radius);
};
```

**PhysicsDemo.cpp**
```cpp
#include "PhysicsDemo.h"
#include "PhysicsToolsets/PhysicsAssetToolset.h"

void UPhysicsDemoSubsystem::RunPhysicsAssetDemo()
{
    // 使用一个假设的骨骼网格体路径
    FString MeshPath = TEXT("/Game/Mannequin/Characters/SK_Mannequin");
    UPhysicsAsset* PhysAsset = UPhysicsAssetToolset::CreateFromMesh(MeshPath, true);

    if (!PhysAsset) return;

    // 设置主要骨骼的碰撞体
    SetupRagdollPart(PhysAsset, TEXT("head"), TEXT("head_sphere"), FVector(0, 0, 5), 12.f);
    SetupRagdollPart(PhysAsset, TEXT("spine_01"), TEXT("spine_capsule"), FVector(0, 0, -10), 15.f);
    SetupRagdollPart(PhysAsset, TEXT("spine_02"), TEXT("spine_capsule"), FVector(0, 0, 5), 15.f);

    // 设置物理模式（可选）
    UPhysicsAssetToolset::SetBodyPhysicsMode(PhysAsset, TEXT("pelvis"), EBodyPhysicsMode::Simulated);
    UPhysicsAssetToolset::SetBodyPhysicsMode(PhysAsset, TEXT("head"), EBodyPhysicsMode::Default);

    UE_LOG(LogPhysicsToolsets, Log, TEXT("物理资产演示配置完成。"));
}

void UPhysicsDemoSubsystem::SetupRagdollPart(UPhysicsAsset* PhysAsset, const FString& BoneName,
                                              const FString& ShapeName, const FVector& Center, float Radius)
{
    // 添加刚体（如果不存在）并设置球体碰撞
    UPhysicsAssetToolset::AddBody(PhysAsset, BoneName);
    UPhysicsAssetToolset::SetSphere(PhysAsset, BoneName, ShapeName, Center, Radius);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 插件所依赖的工具集注册系统，用于将 `UPhysicsAssetToolset` 注册为 AI 可调用的工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-18 | `6471b168` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 调整了工具集定义识别可用函数的方式。 |
| 2026-04-17 | `8c911af5` | [Backout] - CL52878047 | 回滚了一次提交。 |
| 2026-04-17 | `9404cd3e` | [AIAssistant] Change how UToolsetDefinitions determine which UFunctions are tools,. | 调整了工具集定义识别可用函数的方式（与上次相同改动）。 |
| 2026-04-01 | `27afb6e8` | [AI Assistant Toolsets] Move toolset tests under AI.Toolsets. | 将工具集测试移动到 `AI.Toolsets` 分类下。 |
| 2026-03-26 | `b2e45b7d` | Add Physics asset toolset. | 首次提交，添加物理资产工具集。 |

### 维护评价

- **状态**：该插件仍处于实验阶段（`IsExperimentalVersion=true`），且默认未启用。
- **活跃度**：创建约 3 年，最近一次更新在 2026 年 4 月，主要是围绕 AI 工具集定义框架的调整，表明它仍在维护中，但更新频率较低。
- **结论**：这是一个针对特定 AI 辅助工作流的实验性插件。由于其依赖尚不稳定的 `ToolsetRegistry` 框架，且功能较为专一，**仅推荐在开发涉及 AI 自动化物理资产操作的内部工具时使用**。不建议在最终产品项目中依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/PhysicsToolsets)
- 官方文档（无）
- 测试用例（未在提供的源文件中发现）