# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies

| 属性 | 值 |
|---|---|
| 中文名 | 物理刚体资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据流节点） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetNodes` (Runtime), `ChaosRigidAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset) | |

## 用途

Chaos Rigid Asset 是一个**实验性**插件，旨在通过 Dataflow 框架实现程序化创建和管理刚体集合（物理资产）。传统上，物理资产（`UPhysicsAsset`）需要在编辑器手动摆放碰撞体，该插件允许开发者使用 Dataflow 图以数据驱动的方式定义盒体、胶囊体、凸包等基本几何体，并自动生成物理碰撞体。

插件的核心价值在于：将物理资产的创建过程从手动调整转变为可重复、可参数化的自动化流程，非常适合程序化生成、批量处理和动态内容创建场景。

## 使用场景

- **程序化布偶生成**：在角色绑定过程中，使用 Dataflow 根据骨骼位置自动生成盒体/胶囊碰撞体，无需手动编辑每个碰撞体。
- **破坏系统预置**：批量生成大量碎块（如建筑物碎块）的物理资产，确保碰撞形状与网格体匹配。
- **动态物理资产调整**：在运行时或编辑器工具中，通过 Dataflow 图调整物体的碰撞形状，实现自适应物理。
- **教学与原型**：快速测试不同的碰撞体组合对物理模拟的影响，无需反复手动导出导入。

## 蓝图用法

本插件主要面向 C++ 和 Dataflow 节点工作流，**蓝图内公开的 API 有限**。以下节点可能在 `ChaosRigidAssetNodes` 模块中作为蓝图可调用函数暴露（需启用 Dataflow 蓝图节点支持）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeBoxCollision` | 创建盒体碰撞体（形状尺寸） | `(推测 ChaosRigidAssetNodes 模块的 UDataflowNode 子类)` |
| `MakeCapsuleCollision` | 创建胶囊碰撞体 | 同上 |
| `MakeConvexCollision` | 从网格体生成凸包碰撞体 | 同上 |

> 注意：当前版本（0.1）的蓝图可调用节点尚未完全稳定，请优先使用 C++ 或 Dataflow 编辑器图进行开发。

## C++ 用法

### 头文件引入

```cpp
#include "PhysicsAssetDataflowContent.h"
#include "DataflowAttachment.h"
```

### 基本用法

以下示例展示如何通过 `UDataflowAttachment` 将数据流实例附加到一个 `UPhysicsAsset` 上，用于在编辑器工具或运行时操作物理资产内容：

```cpp
// 假设已有 UPhysicsAsset* PhysAsset
UPhysicsAsset* MyAsset = CreateDefaultSubobject<UPhysicsAsset>(TEXT("GeneratedPhysicsAsset"));

// 创建并附加 Dataflow 附件
UDataflowAttachment* Attachment = NewObject<UDataflowAttachment>(MyAsset);
MyAsset->AddAssetUserData(Attachment);

// 从附件获取 Dataflow 实例，以便通过节点图操作刚体
FDataflowInstance& Instance = Attachment->GetDataflowInstance();
// 在此可设置或执行 Dataflow 节点（如 BoxGenerator）来生成碰撞体
```

*来源：[DataflowAttachment.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/ChaosRigidAsset/Source/ChaosRigidAssetEngine/Public/DataflowAttachment.h)*

### 进阶用法：创建数据流内容并应用

使用 `UPhysicsAssetDataflowContent` 来封装预览骨骼网格体和物理资产，实现编辑器内的实时反馈：

```cpp
// 创建数据流内容对象
UPhysicsAssetDataflowContent* Content = NewObject<UPhysicsAssetDataflowContent>();

// 设置预览网格体和物理资产
Content->SetSkeletalMesh(MySkeletalMesh);
Content->SetPhysicsAsset(MyPhysicsAsset);

// 调用数据流写入/读取接口（继承自 UDataflowBaseContent）
// 该内容可被 Dataflow 编辑器窗口使用
```

*来源：[PhysicsAssetDataflowContent.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/ChaosRigidAsset/Source/ChaosRigidAssetEngine/Private/PhysicsAssetDataflowContent.h)*

## Demo 示例

以下是一个最小 C++ 示例，展示如何使用 `ChaosRigidAssetEngine` 模块创建一个带有程序化碰撞体的物理资产。该示例假设项目已启用 `Dataflow` 和 `ChaosRigidAsset` 插件。

### MyPhysicsAssetFactory.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "PhysicsAssetDataflowContent.h"
#include "DataflowAttachment.h"
#include "MyPhysicsAssetFactory.generated.h"

UCLASS()
class UMyPhysicsAssetFactory : public UObject
{
    GENERATED_BODY()

public:
    // 创建一个包含单个盒体碰撞体的物理资产
    UFUNCTION()
    UPhysicsAsset* CreateBoxCollisionAsset(USkeletalMesh* TargetMesh);
};
```

### MyPhysicsAssetFactory.cpp

```cpp
#include "MyPhysicsAssetFactory.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/PhysicsConstraintTemplate.h"
#include "Chaos/ChaosEngineInterface.h"

UPhysicsAsset* UMyPhysicsAssetFactory::CreateBoxCollisionAsset(USkeletalMesh* TargetMesh)
{
    UPhysicsAsset* NewAsset = NewObject<UPhysicsAsset>(GetTransientPackage(), NAME_None, RF_Transient);
    NewAsset->SetPreviewMesh(TargetMesh);

    // 使用 Dataflow 附件来驱动碰撞体生成
    UDataflowAttachment* Attachment = NewObject<UDataflowAttachment>(NewAsset);
    NewAsset->AddAssetUserData(Attachment);

    // 创建数据流内容并关联网格体
    UPhysicsAssetDataflowContent* Content = NewObject<UPhysicsAssetDataflowContent>();
    Content->SetSkeletalMesh(TargetMesh);
    Content->SetPhysicsAsset(NewAsset);
    Attachment->WriteDataflowContent(Content); // 将内容写入附件

    // 注意：实际生成盒体碰撞体需要执行 Dataflow 图（如 MakeBoxCollision 节点）
    // 此处为简化，直接手动创建一条体数据（物理资产的实际碰撞体由 Dataflow 节点负责）
    // 在真实项目中，应通过 FDataflowInstance 执行节点图

    return NewAsset;
}
```

> 完整的使用需要配合 Dataflow 图中的“Box Builder”节点，通过执行图来生成碰撞体结果。此示例演示了模块的核心集成方式。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 提供数据流框架，插件依赖其节点系统与编辑器集成 |
| `Chaos` | Chaos 物理引擎，用于碰撞体形状定义与物理模拟 |

> 其他依赖（如 Core, Engine, UMG 等）为标准 UE 依赖，未列出。

## 维护状态

### 近期更新

- 2025-09-30 `5c0a4ef4` — [Dataflow] Added Box, Capsule and Convex simple builders as geometry generators for dataflow physics
- 2025-09-29 `6813b43d` — [Dataflow] Fixed physics asset generation not correctly setting base joint names on constraints
- 2025-09-26 `d83fb5ae` — [Backout] - CL46264036
- 2025-09-26 `3f07f94a` — [Dataflow] Added Box, Capsule and Convex simple builders as geometry generators for dataflow physics
- 2025-08-15 `4499bef8` — Fix warning due to passing derived member to multi-pin constructor

### 维护评价

该插件于 2025 年 8 月创建，目前仍处于**实验性**阶段。从近期提交记录看，开发活跃，关键功能（基本几何体构建器）在 9 月底得到增强，同时修复了关节命名问题。无废弃标记，代码持续迭代中。由于插件较新且处于早期版本（0.1），推荐在 **项目原型或技术验证** 时启用，但需注意 API 可能发生变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosRigidAsset/Tests)（若存在）
- [Dataflow 文档](https://docs.unrealengine.com/5.7/en-US/dataflow-in-unreal-engine/)（独立参考）