# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies

| 属性 | 值 |
|---|---|
| 中文名 | 刚体资产插件 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流节点、生成器、C++构建器） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetNodes` (Runtime), `ChaosRigidAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset) | |

---

## 用途

Chaos Rigid Asset 是一个基于 **Dataflow 框架**的物理资产（Physics Asset）创作工具。它允许用户在数据流图表中以节点化、可复现的方式定义物理体的碰撞形状、刚体链和约束，并最终生成 `UPhysicsAsset`。

该插件解决了传统手动为骨骼网格体创建物理资产时的痛点：
- **传统方式**：在“Physics Asset”编辑器中手动摆放碰撞体、调整约束，操作繁琐、难以迭代、不易复用。
- **Dataflow 方式**：将物理资产构建过程分解为多个可配置的节点（如选择骨骼、生成几何体、添加约束），通过连线组合形成完整的管道。修改任意输入节点即可快速重新生成整个物理资产，适合程序化内容生成（PCG）和频繁迭代的场景。

核心价值：**将物理资产创建过程以数据流方式可视化、参数化、可复用**。

---

## 使用场景

- **程序化生成角色物理资产**：当你有大量同构或异构的骨骼网格体角色时，可以通过相同的 Dataflow 图表自动生成其物理碰撞体和约束，避免手动调整每个角色。
- **快速原型与迭代**：在游戏开发早期，物理参数需要频繁调整，使用 Dataflow 节点可以立即看到修改效果，无需等待编辑器刷新。
- **与已有 Dataflow 管线集成**：如果项目中已经使用 Dataflow 处理其他资产（如 ProceduralMesh、毛发），可以将物理资产生成作为管线的一部分。
- **内容可复用性**：将物理生成逻辑保存为 Dataflow 资产，分享给团队或跨项目复用。

---

## 蓝图用法

该插件目前**不暴露任何蓝图可调用函数**。其功能完全通过 **Dataflow 图表节点** 在编辑器中使用。蓝图开发者可以通过操作 Dataflow 资产来间接使用，但无法在蓝图事件图表中直接调用。

---

## C++ 用法

C++ 开发者可以使用该插件提供的核心构建器 `FPhysicsAssetBuilder` 以编程方式生成物理资产，或通过 Dataflow 节点编写自定义生成逻辑。

### 头文件引入

```cpp
#include "PhysicsAssetBuilder.h"         // 核心构建器
#include "Generators/BoneGeometryGenerators.h"  // 骨骼几何生成器
#include "Generators/ConstraintGenerators.h"    // 约束生成器
#include "BoneSelection.h"                // 骨骼选择
#include "PhysicsAssetDataflowState.h"    // 数据流状态
```

### 基本用法：使用 FPhysicsAssetBuilder 构建物理资产

示例取自 `PhysicsAssetBuilder.h` 的公共 API。

```cpp
// 1. 创建构建器，指定目标骨架
UE::Chaos::RigidAsset::FPhysicsAssetBuilder Builder =
    UE::Chaos::RigidAsset::FPhysicsAssetBuilder::Make(TargetSkeleton);

// 2. 添加刚体（骨骼体）
USkeletalBodySetup* BodySetup = NewObject<USkeletalBodySetup>();
// ... 配置 BodySetup 的碰撞几何体
Builder.Body(BodySetup);

// 3. 添加约束（连接两刚体）
UPhysicsConstraintTemplate* Constraint = NewObject<UPhysicsConstraintTemplate>();
Constraint->DefaultInstance.ProfileInstance.LinearLimit.bSoftConstraint = false;
// ... 其他约束设置
Builder.Joint(Constraint);

// 4. 为最后添加的两个刚体之间添加约束
Builder.JoinLast(Constraint);

// 5. 指定输出路径或目标资产
Builder.Path(TEXT("/Game/Physics/MyPhysicsAsset"));

// 6. 最终构建
UPhysicsAsset* NewAsset = Builder.Build();
```

### 进阶用法：自定义 Dataflow 节点

你可以继承 `FRigidDataflowNode` 或 `UConstraintGenerator` 来扩展新的生成节点。

```cpp
// 实现自定义约束生成器
UCLASS()
class UMyCustomConstraintGenerator : public UConstraintGenerator
{
    GENERATED_BODY()

public:
    virtual TArray<TObjectPtr<UPhysicsConstraintTemplate>> Build(
        TObjectPtr<UPhysicsConstraintTemplate> ConstraintTemplate,
        FRigidAssetBoneSelection Bones) const override
    {
        TArray<TObjectPtr<UPhysicsConstraintTemplate>> Result;
        // 自定义逻辑：例如为每对相邻骨骼创建约束
        for (int32 i = 0; i < Bones.SelectedBones.Num() - 1; ++i)
        {
            UPhysicsConstraintTemplate* NewConstraint = DuplicateObject(ConstraintTemplate, nullptr);
            // 设置约束的两个物体为骨骼 i 和 i+1
            NewConstraint->DefaultInstance.ConstraintBone1 = Bones.SelectedBones[i].Name;
            NewConstraint->DefaultInstance.ConstraintBone2 = Bones.SelectedBones[i+1].Name;
            Result.Add(NewConstraint);
        }
        return Result;
    }
};
```

然后将该生成器通过 `FMakeSwingTwistConstraintGenerator` 类似的节点暴露到 Dataflow 图表中。

### 使用 Dataflow 节点（C++）

数据流节点可通过 `Dataflow` 插件直接用于编辑器。以下是一个使用 `FDataflowPhysicsAssetMakeState` 和形状构建节点的示例：

```cpp
// 假设你在某个编辑器工具中手动评估 Dataflow 图表
UE::Dataflow::FEngineContext Context(Owner);
// 准备输入
FDataflowPhysicsAssetMakeState MakeStateNode(...);
// 设置输入值
TUniquePtr<UE::Dataflow::FContextThreadPolicy> ContextPolicy;
UE::Dataflow::FContext ContextObject(ContextPolicy, &Context);
// 触发评估
MakeStateNode.Evaluate(ContextObject, &MakeStateNode.State);
```

---

## Demo 示例

以下是一个完整的 C++ 示例，演示如何通过 `FPhysicsAssetBuilder` 以编程方式为一个人形骨架创建一个简单的物理资产（仅包含两个碰撞体连接）。

### RigidAssetExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "PhysicsAssetExamples.generated.h"

UCLASS()
class UPhysicsAssetExampleHelper : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION()
    static UPhysicsAsset* CreateSimplePhysicsAsset(USkeleton* Skeleton);
};
```

### RigidAssetExample.cpp

```cpp
#include "RigidAssetExample.h"
#include "PhysicsAssetBuilder.h"
#include "PhysicsEngine/BoxElem.h"
#include "PhysicsEngine/SphereElem.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "PhysicsEngine/BodySetup.h"
#include "PhysicsEngine/PhysicsAsset.h"

UPhysicsAsset* UPhysicsAssetExampleHelper::CreateSimplePhysicsAsset(USkeleton* Skeleton)
{
    using namespace UE::Chaos::RigidAsset;

    // 1. 创建构建器
    FPhysicsAssetBuilder Builder = FPhysicsAssetBuilder::Make(Skeleton);

    // 2. 创建两个刚体
    // 刚体A：盒体碰撞
    USkeletalBodySetup* BodyA = NewObject<USkeletalBodySetup>();
    FKBoxElem BoxElem;
    BoxElem.SetTransform(FTransform(FVector(0, 0, 50)));
    BoxElem.X = 20;
    BoxElem.Y = 20;
    BoxElem.Z = 100;
    BodyA->AggGeom.BoxElems.Add(BoxElem);

    // 刚体B：球体碰撞
    USkeletalBodySetup* BodyB = NewObject<USkeletalBodySetup>();
    FKSphereElem SphereElem;
    SphereElem.Center = FVector(0, 0, 150);
    SphereElem.Radius = 30;
    BodyB->AggGeom.SphereElems.Add(SphereElem);

    // 3. 添加到构建器
    Builder.Body(BodyA);
    Builder.Body(BodyB);

    // 4. 创建约束：旋转锚定（Swing/Twist 限制 45°）
    UPhysicsConstraintTemplate* Constraint = NewObject<UPhysicsConstraintTemplate>();
    Constraint->DefaultInstance.ConstraintBone1 = TEXT("root");  // 需实际匹配骨骼名
    Constraint->DefaultInstance.ConstraintBone2 = TEXT("pelvis");
    Constraint->DefaultInstance.AngularSwing1Limit = 45.0f;
    Constraint->DefaultInstance.AngularSwing2Limit = 45.0f;
    Constraint->DefaultInstance.AngularTwistLimit = 10.0f;
    Builder.JoinLast(Constraint);

    // 5. 设置保存路径并构建
    Builder.Path(TEXT("/Game/Physics/MyGeneratedAsset"));
    return Builder.Build();
}
```

**注意**：实际使用时需要确保骨骼名称与 `Skeleton` 中的骨骼匹配，并调用适当的初始化函数。

---

## 模块依赖

以下模块是 **ChaosRigidAssetNodes** 和 **ChaosRigidAssetEngine** 的独特依赖（省略标准 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `Dataflow` | 核心数据流框架，提供节点注册、图表执行等基础设施 |
| `GeometryCollection` | 提供 `ManagedArrayCollection` 等数据结构，用于内部数据处理 |
| `Chaos` | Chaos 物理引擎核心库（通过间接依赖） |

**注意**：如果要在你自己的模块中使用 `ChaosRigidAssetNodes`，请在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "ChaosRigidAssetNodes", "Dataflow" });
```

---

## 维护状态

### 近期更新

从 git log 获取最近 5 次提交（截至 2025-09-30）：

| 日期 | Hash | 提交说明（解读） |
|---|---|---|
| 2025-09-30 | `5c0a4ef4` | [Dataflow] 添加了盒体、胶囊体和凸体简单构建器作为 Dataflow 物理的几何生成器（新增 Box、Capsule、Convex 生成节点） |
| 2025-09-29 | `6813b43d` | [Dataflow] 修复物理资产生成时未正确设置基础关节名称导致约束链接失败（bug 修复） |
| 2025-09-26 | `d83fb5ae` | [Backout] - 回退提交 46264036（回滚） |
| 2025-09-26 | `3f07f94a` | [Dataflow] 添加了盒体、胶囊体和凸体简单构建器（与 5c0a4ef4 类似，可能为不同分支） |
| 2025-08-15 | `4499bef8` | 修复将派生成员传递给多引脚构造函数时的警告（工程修复） |

### 维护评价

- **创建时间**：2025-08-15，距今约 2 个月（截至 2025-10），属于**全新插件**。
- **更新频率**：2025-09 有多次功能性更新，修复了关键 bug，并增加了多种几何生成器，开发活跃。
- **版本号**：0.1，且标记为实验性，意味着功能尚未稳定，API 可能变动。
- **推荐使用**：适合探索性开发或需要先端特性时使用。**不建议在生产项目中使用**，除非你能接受意外中断和API变更。建议跟踪后续更新。

---

## 相关链接

- [源码目录（tree/5.7）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset)
- [测试用例（如果有）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset/Tests) *（该目录可能不存在，需在仓库中确认）*
- [Dataflow 官方文档（UE 5.7）](https://docs.unrealengine.com/5.7/zh-CN/dataflow-overview/) *（通用文档，非本插件专属）*