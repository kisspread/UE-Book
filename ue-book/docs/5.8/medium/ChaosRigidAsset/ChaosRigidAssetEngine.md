# Chaos Rigid Asset

> Rigid Asset plugin for creating and utilising collections of rigid bodies

| 属性 | 值 |
|---|---|
| 中文名 | 混沌刚体资产 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosRigidAssetEditor` (Editor), `ChaosRigidAssetNodes` (Runtime), `ChaosRigidAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset) | |

## 用途

ChaosRigidAsset 插件的核心目的是通过 **Dataflow（数据流图）** 的方式，程序化地创建和操作 `UPhysicsAsset`（物理资产）。传统物理资产的创建依赖于物理资产编辑器手动设置骨骼体（Body）、约束（Constraint）和碰撞几何体，过程繁琐且难以参数化。此插件将这一过程抽象为节点化的数据流，允许用户通过图形化的方式定义和修改物理资产的结构，特别适用于需要重复生成、参数化调整或程序化衍生物理资产的场景。

插件解决了以下问题：
1.  **程序化生成物理资产**：无需进入物理资产编辑器，通过连接数据流节点即可生成完整的物理资产。
2.  **参数化控制**：通过调整数据流图中的参数，可以动态地改变物理资产的构成（如骨骼体大小、约束角度）。
3.  **工作流集成**：在数据流编辑器中直接预览物理资产效果，并可以选择性地绕过传统的物理资产编辑器。

## 使用场景

-   **你正在开发一款需要大量不同体型NPC的游戏**，且这些NPC的物理碰撞体需要根据其身形参数（如胖瘦、高矮）动态生成 → 使用此插件，在数据流图中连接一个“身体参数”输入，通过节点计算并生成对应的物理资产。
-   **你正在制作一个可破坏环境系统**，需要为不同形状和材质的物体创建破碎后的物理模拟数据 → 使用此插件，根据物体网格体程序化生成带有合理碰撞体和约束的物理资产。
-   **你需要为AI训练环境快速生成大量具有细微差别的物理代理** → 使用此插件，通过数据流的随机种子或参数输入，批量创建物理资产变体。

## 蓝图用法

该插件的蓝图交互主要集中在预览场景的控制上，用于在数据流编辑器中调试物理模拟。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Apply Solver Config` | 应用一个 `FChaosSolverConfiguration` 结构体，用于配置预览场景中的物理求解器参数。 | `UPreviewSceneControllerComponent` |
| `Enable Async Tick` | 启用预览场景的异步 Tick，并指定其 Delta Time (`InAsyncDt`)。 | `UPreviewSceneControllerComponent` |
| `Disable Async Tick` | 禁用预览场景的异步 Tick。 | `UPreviewSceneControllerComponent` |

### 使用示例（蓝图描述）

1.  在数据流编辑器的预览场景中，找到或添加一个拥有 `UPreviewSceneControllerComponent` 组件的 Actor。
2.  在事件图表中，可以调用 `Apply Solver Config` 节点，传入一个自定义的求解器配置（如迭代次数、子步长等）来调整模拟精度。
3.  为了流畅地预览物理模拟，可以调用 `Enable Async Tick` 节点，设置一个合适的 `AsyncDt`（如 0.02s）。当需要停止模拟时，调用 `Disable Async Tick`。

## C++ 用法

该插件主要通过扩展数据流系统来工作。使用者通常需要创建自定义的“附件（Attachment）”和“内容（Content）”类。

### 头文件引入

```cpp
#include "PhysicsAssetDataflowAttachment.h"
```

### 基本用法

创建一个自定义的数据流附件，使其能够管理 `UPhysicsAsset` 的数据流内容。你需要继承 `UPhysicsAssetDataflowAttachment` 或实现 `IDataflowContentOwner` 接口。

**文件路径**：`Engine/Plugins/Experimental/ChaosRigidAsset/Source/ChaosRigidAssetEngine/Public/PhysicsAssetDataflowAttachment.h`

```cpp
// 自定义一个用于特定游戏逻辑的物理资产数据流附件
UCLASS()
class UMyGamePhysicsAssetAttachment : public UPhysicsAssetDataflowAttachment
{
    GENERATED_BODY()

public:
    // 可以在此处重写父类的方法，例如 CreateDataflowContent，
    // 以返回自定义的 UPhysicsAssetDataflowContent 子类。
    // 也可以添加游戏特定的数据读写逻辑。
    
    // 示例：重写内容创建方法以注入默认设置
    virtual TObjectPtr<UDataflowBaseContent> CreateDataflowContent() override
    {
        TObjectPtr<UPhysicsAssetDataflowContent> Content = NewObject<UPhysicsAssetDataflowContent>(this);
        // 对 Content 进行默认设置...
        return Content;
    }
};
```

### 进阶用法

组合使用附件（Attachment）和内容（Content）类，实现对物理资产数据流的完全控制。以下示例展示了如何设置内容对象，以将特定的骨骼网格体和物理资产用于数据流预览。

**文件路径**：`Engine/Plugins/Experimental/ChaosRigidAsset/Source/ChaosRigidAssetEngine/Private/PhysicsAssetDataflowContent.h`

```cpp
// 假设你已经创建了一个附件实例 `MyAttachment`
TObjectPtr<UMyGamePhysicsAssetAttachment> MyAttachment = ...;

// 获取或创建数据流内容
TObjectPtr<UPhysicsAssetDataflowContent> Content = 
    Cast<UPhysicsAssetDataflowContent>(MyAttachment->CreateDataflowContent());

// 设置预览所需的资源
Content->SetSkeletalMesh(MyCharacterMesh);
Content->SetPhysicsAsset(MyCharacterPhysAsset);

// 现在可以将此内容传递给数据流系统进行计算和预览
```

## Demo 示例

一个最小的 C++ 示例，演示如何创建一个自定义的物理资产数据流附件类。

**MyPhysicsAssetGenerator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "PhysicsAssetDataflowAttachment.h"
#include "MyPhysicsAssetGenerator.generated.h"

/**
 * 用于生成特定敌人物理资产的自定义附件。
 */
UCLASS()
class MYGAME_API UMyPhysicsAssetGenerator : public UPhysicsAssetDataflowAttachment
{
    GENERATED_BODY()

public:
    // 可在此处重写 ReadDataflowContent/WriteDataflowContent，
    // 以处理敌人特有的参数（例如，护甲部位对应更强的碰撞体）。
    virtual void WriteDataflowContent(const TObjectPtr<UDataflowBaseContent>& DataflowContent) const override;
    virtual void ReadDataflowContent(const TObjectPtr<UDataflowBaseContent>& DataflowContent) override;

    // 可以添加敌人类型等标识信息。
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Generator")
    FName EnemyType;
};
```

**MyPhysicsAssetGenerator.cpp**
```cpp
#include "MyPhysicsAssetGenerator.h"

void UMyPhysicsAssetGenerator::WriteDataflowContent(const TObjectPtr<UDataflowBaseContent>& DataflowContent) const
{
    Super::WriteDataflowContent(DataflowContent);

    // 将 EnemyType 等自定义数据写入 DataflowContent 对象中，
    // 以便数据流图中的节点可以读取。
    // 例如，设置一个在数据流中可读取的参数。
}

void UMyPhysicsAssetGenerator::ReadDataflowContent(const TObjectPtr<UDataflowBaseContent>& DataflowContent)
{
    Super::ReadDataflowContent(DataflowContent);

    // 从计算后的 DataflowContent 中读取结果（如生成的物理资产），
    // 并应用到当前生成器或目标 Actor 上。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Dataflow` | 核心数据流框架，提供节点、图和执行环境。 |
| `GeometryProcessing` | 提供几何体处理功能（如网格体操作、凸分解），用于生成碰撞几何体。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `1a41cebd` | Dataflow : fix Dataflow nodes not properly referencing the node when outputing error messages causin | 修复了数据流节点输出错误消息时引用不正确的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-10 | `36646cb9` | Rigid asset - Update rigid asset asset to use the unified dataflow menu command so that the user exp | 更新刚体资产以使用统一的数据流菜单命令，提升用户体验。 |
| 2026-04-10 | `5c4d7272` | Dataflow : added an API to dataflow attachment to get the preview actor path for the Dataflow Editor | 为数据流附件添加了获取预览 Actor 路径的 API。 |
| 2026-04-07 | `b7596b26` | Fixup docs on rigid caching node | 修复了刚体缓存节点的文档说明。 |

### 维护评价

-   **状态**：**活跃维护中**。插件创建于 2025 年 8 月，截至 2026 年 4 月底仍有功能性更新和错误修复。
-   **频率**：更新较为频繁，近期主要集中在修复数据流集成问题、统一操作体验和改进文档上。
-   **风险**：作为实验性（`IsExperimentalVersion=true`）且默认禁用的插件，其 API 和功能可能会发生变化。目前版本号为 0.1，处于早期开发阶段。
-   **推荐**：**推荐有特定需求的开发者关注和试用**。如果你需要高度程序化和数据驱动的物理资产创建流程，该插件是 UE5 生态中一个有价值的选择。但应做好应对 API 变更的准备，并密切关注其更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosRigidAsset)
-   [官方文档]() （暂无）
-   [测试用例]() （插件内未发现独立的测试用例目录）