# Skeletal Mesh Editing Tools

> Create skeletons, paint skin weights and edit skeletal meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼网格体编辑工具 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器模式工具，UI控件） |
| 模块 | `SkeletalMeshModelingTools` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/SkeletalMeshModelingTools) | |

## 用途

该插件为 **Skeletal Mesh Editor** 提供了一整套内嵌的 **3D 建模与编辑工具链**。它的核心作用是突破传统骨骼网格体编辑器“仅调整参数和预览”的局限，允许美术人员在编辑器视口内直接对网格体几何体、骨架、形态目标（Morph Target）和蒙皮权重进行可视化的交互式编辑。

简而言之，它将 UE 的建模模式工具（Modeling Tools）深度集成到了骨骼网格体资产编辑器中，解决了**高保真角色模型制作**和**动画资源迭代**中的核心痛点：需要在外部 DCC 软件（如 Maya、Blender）中调整模型或蒙皮，然后反复导入导出，流程繁琐且难以实时预览动画效果。通过此插件，大部分此类工作可以直接在 UE 编辑器内完成。

## 使用场景

- **从静态网格体（Static Mesh）快速转换/原型化**：你有一个角色的高模静态网格体，想快速为其创建一个单根骨骼的简易骨骼网格体，用于物理碰撞或简单的布料模拟测试。
- **精细调整形态目标（Morph Target）**：你需要管理大量的面部表情 morph target，包括批量重命名、镜像、翻转、合并，或者从一个参考网格体模板批量添加缺失的 morph target。
- **可视化编辑骨架结构**：在模型已经绑定到骨架后，需要微调某根骨骼的位置或旋转，而无需回到 DCC 软件。
- **直接绘制或调整蒙皮权重**：在视口中使用笔刷直接绘制顶点的骨骼权重，或对特定顶点进行精确的权重值编辑。
- **交互式几何体选择与隔离**：需要选择模型的特定部分（如多边形组、边、顶点），并对其进行独立编辑或隐藏，以聚焦工作区域。

## 蓝图用法

该插件主要通过编辑器模式和工具面板（Toolkit）与用户交互，其核心功能并非通过 `BlueprintCallable` 函数直接暴露给蓝图系统。大多数核心 API 是 C++ 端的编辑器扩展和工具逻辑。

### 核心节点

由于该插件的主要用户界面是编辑器模式（Editor Mode）和其工具面板，因此没有常规意义上的“蓝图节点”。所有功能都通过以下方式访问：
1.  打开 **Skeletal Mesh Editor**。
2.  在工具栏中找到并启用 **“Editing Tools”** 模式。
3.  在右侧出现的 **Toolkit** 面板中选择具体工具（如 Morph Target 管理、骨架编辑等）。

如果你需要在编辑器脚本或插件中与这些工具进行 C++ 层面的交互，需要通过获取 `USkeletalMeshModelingToolsEditorMode` 实例及其关联的接口（如 `IMorphTargetManagerDataSource`）。

## C++ 用法

### 头文件引入

```cpp
#include "SkeletalMeshModelingToolsModule.h"
#include "SkeletalMeshEditingCache.h"
#include "SkeletalMeshBackedDynaMeshComponent.h"
```

### 基本用法：通过编辑器模式管理形态目标

以下代码片段展示了如何通过 `IMorphTargetManagerDataSource` 接口与形态目标管理器交互。这通常发生在你的工具或模式已经获得了对该接口的引用之后。

（来源：`Source/SkeletalMeshModelingTools/Private/MorphTargetManagerDataSource.h` 及 `USkeletalMeshModelingToolsEditorMode` 实现）

```cpp
// 假设你已经获取到了一个有效的 IMorphTargetManagerDataSource 指针 (DataSource)
// 它通常由 USkeletalMeshModelingToolsEditorMode 提供

// 1. 获取当前所有形态目标名称
TArray<FName> MorphTargetNames = DataSource->GetMorphTargets();

// 2. 设置某个形态目标的权重（用于预览）
FName MyMorphTarget = TEXT("Mouth_Smile");
DataSource->SetMorphTargetWeight(MyMorphTarget, 0.75f);

// 3. 重命名一个形态目标
FName OldName = TEXT("old_shape");
FName NewName = DataSource->RenameMorphTarget(OldName, TEXT("new_shape"));

// 4. 创建一个新的空形态目标
FName CreatedName = DataSource->AddMorphTarget(FName("CustomMorph_01"));

// 5. 从参考网格体批量添加缺失的形态目标
TArray<FName> NamesToAdd = {TEXT("Brow_Up"), TEXT("Brow_Down")};
TArray<FName> ActuallyAdded = DataSource->AddMorphTargetsIfMissing(NamesToAdd);
```

### 进阶用法：操作底层动态网格体组件

对于更底层的控制，可以直接访问 `USkeletalMeshBackedDynamicMeshComponent`，这是存储和管理编辑状态的核心组件。

（来源：`Source/SkeletalMeshModelingTools/Private/Components/SKMBackedDynaMeshComponent.h`）

```cpp
// 假设你通过编辑模式或上下文对象获取到了组件指针：
// USkeletalMeshBackedDynamicMeshComponent* DynaMeshComponent = ...;

// 1. 初始化组件以编辑特定骨骼网格体的 LOD0
EMeshLODIdentifier EditedLOD = DynaMeshComponent->Init(MySkeletalMesh, EMeshLODIdentifier::LOD0);

// 2. 在组件上执行一系列几何编辑操作（例如，由一个工具完成）
{
    // 使用 FChangeScope 自动管理撤销/重做事务
    USkeletalMeshBackedDynamicMeshComponent::FChangeScope ChangeScope(DynaMeshComponent);

    // 添加一个新的形态目标
    FName NewMorphName = DynaMeshComponent->AddMorphTarget(FName("Sculpt_Morph"));

    // 对几何体进行修改（这里仅为示意，实际修改通过 FDynamicMesh3 进行）
    // ... 编辑网格体顶点 ...

    // 标记组件状态为脏，准备提交
    DynaMeshComponent->MarkDirty();
}

// 3. 将所有编辑的修改（几何、骨架、形态目标变更）提交回原始资产
bool bSuccess = DynaMeshComponent->CommitToSkeletalMesh();

// 4. 如果需要放弃修改
DynaMeshComponent->DiscardChanges();
```

## Demo 示例

下面是一个最小化的示例，演示如何创建一个简单的 C++ 类，该类可以利用此插件的编辑缓存系统来获取并打印当前正在编辑的形态目标信息。此代码假设在一个自定义的编辑器工具或上下文中运行。

### MySkeletalMeshTool.h
```cpp
#pragma once
#include "CoreMinimal.h"

class USkeletalMeshEditingCache;
class UWorld;

class FMySkeletalMeshTool
{
public:
    void Initialize(UWorld* InWorld, USkeletalMeshComponent* InSkeletalMeshComponent);
    void PrintCurrentMorphTargetInfo();

private:
    TWeakObjectPtr<USkeletalMeshEditingCache> EditingCache;
};
```

### MySkeletalMeshTool.cpp
```cpp
#include "MySkeletalMeshTool.h"
#include "SkeletalMeshEditingCache.h"
#include "SkeletalMeshComponent.h"

void FMySkeletalMeshTool::Initialize(UWorld* InWorld, USkeletalMeshComponent* InSkeletalMeshComponent)
{
    if (!InWorld || !InSkeletalMeshComponent)
    {
        return;
    }

    // 创建并 spawn 一个编辑缓存实例（生命周期管理需自行负责）
    EditingCache = NewObject<USkeletalMeshEditingCache>();
    USkeletalMeshEditingCache::FDelegates Delegates; // 可绑定所需代理
    // IToolsContextTransactionsAPI* TransAPI = ...; // 获取事务 API
    EditingCache->Spawn(InWorld, InSkeletalMeshComponent, EMeshLODIdentifier::LOD0, Delegates, nullptr);
}

void FMySkeletalMeshTool::PrintCurrentMorphTargetInfo()
{
    if (!EditingCache.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Editing cache is not valid."));
        return;
    }

    // 获取所有形态目标名称
    TArray<FName> MorphNames = EditingCache->GetMorphTargets();
    UE_LOG(LogTemp, Log, TEXT("Current Morph Targets: %d"), MorphNames.Num());

    for (const FName& Name : MorphNames)
    {
        // 获取其当前权重
        float Weight = EditingCache->GetMorphTargetWeight(Name);
        UE_LOG(LogTemp, Log, TEXT("  - %s : %.2f"), *Name.ToString(), Weight);
    }

    // 检查是否有未应用的更改
    if (EditingCache->HasUnappliedChanges())
    {
        UE_LOG(LogTemp, Log, TEXT("There are unapplied changes."));
        // 可以选择应用: EditingCache->ApplyChanges();
        // 或放弃: EditingCache->DiscardChanges();
    }
}
```

## 模块依赖

使用此插件，你的模块可能需要依赖以下特有模块（除通用的 Core, Engine, Slate 等之外）：

| 模块 | 用途 |
|---|---|
| `Model` | 提供建模模式工具的基础框架（IInteractiveTool, UInteractiveToolBuilder 等） |
| `GeometryFramework` | 提供 `UDynamicMesh`, `UDynamicMeshComponent` 等核心几何数据结构与组件 |
| `GeometryProcessing` | 提供几何处理算法，如网格体细分、简化、布尔操作等，被各种具体工具使用 |
| `EditorFramework` | 编辑器模式（`UBaseLegacyWidgetEdMode`）和工具面板（`FModeToolkit`）的基础 |
| `AnimationBlueprintLibrary` | 可能用于更高级的动画蓝图和骨骼操作 |
| `SkeletalMeshModelingTools` | **本插件模块**。若你的 C++ 代码需要直接使用其内部的 `USkeletalMeshEditingCache`, `USkeletalMeshBackedDynamicMeshComponent` 等类型，则必须依赖此模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 为顶点属性绘制和蒙皮权重绘制工具添加了跨模式同步笔刷半径的功能。 |
| 2026-05-25 | `3a26b322` | [SkeletalMeshModelingTools] Drop redundant FastNotifyPositionsUpdated in DeformPreviewMesh | 移除了在变形预览网格体中冗余的“快速通知位置更新”调用，可能提升性能。 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 优化了当仅编辑顶点时，跳过重建分组拓扑的逻辑，提升编辑响应速度。 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack valid tangents | 当预览或雕刻网格体缺乏有效切线时，自动设置切线计算模式。 |
| 2026-05-20 | `bc0080bb` | [SkeletalMeshModelingTools] Keep active tool alive across unrelated world saves | 优化了工具状态保持逻辑，在进行无关的世界保存时，活动工具不会被意外关闭。 |

### 维护评价

- **创建时间**：2025年3月，是一个相对较新的插件。
- **活跃度**：根据提交记录，该插件在 2026 年 5 月仍有密集的功能性更新和优化，属于 **活跃维护** 状态。更新内容涉及性能优化、功能增强和用户体验改进。
- **稳定性与兼容性**：作为 Epic Games 官方维护的插件，且从 Experimental 分支移至稳定分支，其质量有保障，与引擎版本（当前为 5.8）保持同步。
- **已知限制**：主要围绕 `USkeletalMeshEditingCache` 的临时（Transient）特性，编辑状态依赖于编辑器会话。此外，复杂操作（如大量形态目标管理）可能对性能有影响，需在大型资产上谨慎使用。
- **推荐使用**：**强烈推荐**。该插件极大地提升了在 UE 内部进行角色模型后期处理和迭代的效率，是处理骨骼网格体资产（尤其是面部动画 Morph Target）的利器。对于需要深度编辑骨骼网格体的项目，应将其视为标准工作流的一部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/SkeletalMeshModelingTools)
- 官方文档：暂无独立文档页面。功能使用方法主要集成在 Skeletal Mesh Editor 的界面和工具提示中。
- 测试用例：插件自身的测试用例可能位于 `Engine/Plugins/Animation/SkeletalMeshModelingTools/Tests` 路径下，但在提供的源码摘要中未包含。