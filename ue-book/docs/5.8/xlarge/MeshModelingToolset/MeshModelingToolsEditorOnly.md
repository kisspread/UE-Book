# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

MeshModelingToolset 是 UE5 中最核心的**运行时网格编辑工具框架**，基于 Interactive Tools Framework 构建，提供从简单到复杂的一整套 3D 网格创建和编辑能力。

该插件解决的核心问题是：**在编辑器中（甚至运行时）提供非破坏性的、交互式的网格几何体编辑能力**。它将网格编辑操作拆分为独立的可组合工具（Tool），每个工具都有独立的属性面板、实时预览和撤销/重做支持。

具体能力包括：

- **静态网格编辑**：网格简化、UV 参数化、多边形切割、属性编辑、顶点属性绘制
- **骨骼网格编辑**：骨骼编辑（创建/删除/重命名/镜像/父子关系）、蒙皮权重绘制、蒙皮权重绑定、Morph Target 编辑
- **底层基础设施**：动态网格（DynamicMesh）操作、选择机制、预览渲染、几何隔离

该插件被标记为 `IsBetaVersion=true` 且 `Hidden=true`，说明它是编辑器建模模式（Modeling Tools Editor Mode）的底层依赖，通常不会直接由用户手动启用。

## 使用场景

- 你正在使用 UE5 编辑器的 **Modeling Mode**（建模模式）→ 背后就是这个插件在提供所有工具
- 你需要在编辑器中**简化网格**以优化性能 → 用 Simplify Mesh Tool
- 你需要为静态网格**自动展开 UV** → 用 Parameterize Mesh Tool
- 你需要在骨骼网格上**绘制蒙皮权重** → 用 Skin Weights Paint Tool
- 你需要**编辑骨骼层级结构**（添加/删除/重命名骨骼）→ 用 Skeleton Editing Tool
- 你需要在网格上**嵌入多边形**进行布尔切割 → 用 Polygon On Mesh Tool
- 你需要管理网格的**顶点属性**（UV、法线、切线、自定义属性）→ 用 Attribute Editor Tool

## 蓝图用法

本插件的工具主要面向编辑器交互，大部分操作通过 Details 面板和视口交互完成，蓝图可调用的公开 API 相对有限。以下是从源码中提取的可蓝图访问的节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRefSkeleton` | 设置参考骨骼 | `URefSkeletonPoser` |
| `GetRefSkeleton` | 获取参考骨骼 | `URefSkeletonPoser` |
| `ModifyBoneAdditiveTransform` | 修改骨骼的附加变换 | `URefSkeletonPoser` |
| `ClearBoneAdditiveTransform` | 清除单个骨骼的附加变换 | `URefSkeletonPoser` |
| `ClearAllBoneAdditiveTransforms` | 清除所有骨骼附加变换 | `URefSkeletonPoser` |
| `GetComponentSpaceTransforms` | 获取组件空间骨骼变换数组 | `URefSkeletonPoser` |
| `GetComponentSpaceTransform` | 获取单个骨骼的组件空间变换 | `URefSkeletonPoser` |
| `BeginPoseChange` | 开始姿态变化记录（用于撤销） | `URefSkeletonPoser` |
| `EndPoseChange` | 结束姿态变化记录 | `URefSkeletonPoser` |
| `GetSelectedBoneNames` | 获取当前选中的骨骼名称列表 | `SReferenceSkeletonTree` |
| `SelectItemFromNames` | 按名称选择骨骼项 | `SReferenceSkeletonTree` |
| `SetLocalRotationAxisLength` | 设置局部旋转轴显示长度 | `USkeletalMeshModelingToolsEditorSettings` |
| `SetShowAllLocalRotationAxes` | 设置是否显示所有局部旋转轴 | `USkeletalMeshModelingToolsEditorSettings` |

### 使用示例（蓝图描述）

由于本插件的工具主要通过编辑器 Mode 面板激活，蓝图层面主要通过 `URefSkeletonPoser` 操控骨骼姿态：

1. 创建一个 `URefSkeletonPoser` 对象
2. 调用 `SetRefSkeleton` 传入骨骼网格的参考骨骼
3. 调用 `BeginPoseChange` 开始记录
4. 使用 `ModifyBoneAdditiveTransform` 修改目标骨骼的变换
5. 调用 `EndPoseChange` 完成修改并生成撤销记录
6. 调用 `GetComponentSpaceTransforms` 获取所有骨骼的最终变换

## C++ 用法

### 头文件引入

```cpp
// 骨骼编辑工具
#include "SkeletalMesh/SkeletonEditingTool.h"

// 蒙皮权重绘制
#include "SkeletalMesh/SkinWeightsPaintTool.h"

// 蒙皮权重绑定
#include "SkeletalMesh/SkinWeightsBindingTool.h"

// 网格简化
#include "SimplifyMeshTool.h"

// 属性编辑器
#include "AttributeEditorTool.h"

// 网格上多边形
#include "PolygonOnMeshTool.h"

// UV 参数化
#include "ParameterizeMeshTool.h"

// 骨骼辅助工具
#include "SkeletalMesh/SkeletalMeshToolsHelper.h"

// 骨骼姿态控制
#include "SkeletalMesh/RefSkeletonPoser.h"
```

### 基本用法 — 网格简化

从 `USimplifyMeshTool` 和 `USimplifyMeshToolProperties` 的设计可以提取如下用法模式：

```cpp
// 来源: Public/SimplifyMeshTool.h

// 网格简化工具的核心配置类
// USimplifyMeshToolProperties 继承自 UMeshConstraintProperties

// 在工具内部，通过以下流程执行简化：
// 1. Builder 创建工具实例
// 2. Setup() 初始化，缓存原始网格和空间索引
// 3. 用户修改属性时触发 OnPropertyModified，重新计算简化结果
// 4. 接受时通过 MakeNewOperator() 生成最终几何体

// 简化类型由 ESimplifyType 枚举控制：
// - QEM（二次误差度量）
// - MinimalExistingVertex
// - MinimalPlanar
// - MinimalPolygroup
// - ClusterBased
// - Attribute

// 简化目标由 ESimplifyTargetType 控制：
// - Percentage（百分比）
// - TriangleCount（三角形数）
// - VertexCount（顶点数）
// - EdgeLength（边长度）
// - QuadricError（二次误差）
```

### 基本用法 — 骨骼编辑

```cpp
// 来源: Public/SkeletalMesh/SkeletonEditingTool.h

// USkeletonEditingTool 通过 EEditingOperation 枚举切换操作模式
// 支持的操作：
// - Select: 在视口中选择骨骼
// - Create: 在视口中创建新骨骼
// - Remove: 删除选中的骨骼
// - Transform: 变换骨骼（视口或详情面板）
// - Parent: 设置骨骼父子关系
// - Rename: 重命名骨骼
// - Mirror: 镜像骨骼

// 工具实现了多个接口：
// - IClickDragBehaviorTarget: 支持点击拖拽交互
// - ISkeletalMeshEditingInterface: 接收骨骼网格修改通知
// - ISkeletalMeshGeometryIsolationAwareTool: 几何隔离感知
// - IInteractiveToolManageGeometrySelectionAPI: 几何选择管理
// - IHotkeyHintProvider: 快捷键提示
```

### 进阶用法 — 蒙皮权重绘制系统

```cpp
// 来源: Public/SkeletalMesh/SkinWeightsPaintTool.h

// 蒙皮权重绘制使用双缓冲系统：
// - PreChangeWeights: 笔刷开始时的权重快照
// - CurrentWeights: 绘制过程中的实时权重

// 编辑模式通过 EWeightEditMode 控制：
// - Brush: 笔刷绘制
// - Mesh: 网格选择编辑
// - Bones: 骨骼选择编辑

// 笔刷操作通过 EWeightEditOperation 控制：
// - Add: 增加权重
// - Replace: 替换权重
// - Multiply: 乘以权重
// - Relax: 松弛权重
// - RelativeScale: 相对缩放

// 每次笔刷操作通过 FMultiBoneWeightEdits 记录变更，支持撤销/重做
// 权重修改后通过 FSkinToolDeformer 实时预览蒙皮变形
```

### 进阶用法 — 几何体变换记录（撤销/重做）

```cpp
// 来源: Public/SkeletalMesh/SkeletalMeshToolsHelper.h

// SkeletalMeshToolsHelper 命名空间提供骨骼网格相关的辅助函数：

// 获取未姿态的网格（将编辑空间的网格转换回参考姿态）
SkeletalMeshToolsHelper::GetUnposedMesh(
    [&](FVertInfo Info, const FVector& Position) {
        // 处理未姿态后的顶点位置
    },
    [&](int32 VertID) -> FVector {
        return PosedPositions[VertID];
    },
    SourceMesh,
    BoneMatrices,
    SkinWeightProfile,
    MorphTargetWeights,
    VertexArray  // 可选：只处理指定顶点
);

// 计算骨骼变换矩阵
TArray<FMatrix> BoneMatrices = SkeletalMeshToolsHelper::ComputeBoneMatrices(
    ComponentSpaceTransformsRefPose,
    ComponentSpaceTransforms
);

// 镜像 Morph Target
SkeletalMeshToolsHelper::MirrorMorphTargetOnMesh(
    Mesh,
    MorphTargetName,
    SymmetryData,
    &DeltaChange  // 可选：用于撤销记录
);
```

## Demo 示例

以下是一个完整的骨骼姿态编辑示例，展示如何使用 `URefSkeletonPoser` 在代码中操控骨骼：

```cpp
// MySkeletonPoserComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkeletalMesh/RefSkeletonPoser.h"
#include "MySkeletonPoserComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMySkeletonPoserComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMySkeletonPoserComponent();

    UPROPERTY(EditAnywhere, Category = "Pose")
    FName TargetBoneName;

    UPROPERTY(EditAnywhere, Category = "Pose")
    FRotator AdditionalRotation;

    UFUNCTION(BlueprintCallable, Category = "Pose")
    void ApplyPose();

    UFUNCTION(BlueprintCallable, Category = "Pose")
    void ResetPose();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<URefSkeletonPoser> Poser;

    int32 FindBoneIndex(const FName& BoneName) const;
};
```

```cpp
// MySkeletonPoserComponent.cpp
#include "MySkeletonPoserComponent.h"
#include "Components/SkeletalMeshComponent.h"

UMySkeletonPoserComponent::UMySkeletonPoserComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMySkeletonPoserComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建骨骼姿态控制器
    Poser = NewObject<URefSkeletonPoser>(this);

    // 获取所有者 Actor 上的骨骼网格组件
    AActor* Owner = GetOwner();
    if (!Owner) return;

    USkeletalMeshComponent* SkelMeshComp = Owner->FindComponentByClass<USkeletalMeshComponent>();
    if (!SkelMeshComp || !SkelMeshComp->GetSkeletalMeshAsset()) return;

    // 设置参考骨骼
    const FReferenceSkeleton& RefSkeleton = SkelMeshComp->GetSkeletalMeshAsset()->GetRefSkeleton();
    Poser->SetRefSkeleton(RefSkeleton);
}

int32 UMySkeletonPoserComponent::FindBoneIndex(const FName& BoneName) const
{
    if (!Poser) return INDEX_NONE;
    const FReferenceSkeleton& RefSkel = Poser->GetRefSkeleton();
    return RefSkel.FindBoneIndex(BoneName);
}

void UMySkeletonPoserComponent::ApplyPose()
{
    if (!Poser) return;

    int32 BoneIndex = FindBoneIndex(TargetBoneName);
    if (BoneIndex == INDEX_NONE) return;

    // 开始记录姿态变化（用于撤销）
    Poser->BeginPoseChange();

    // 通过附加变换修改骨骼旋转
    FQuat RotationQuat = AdditionalRotation.Quaternion();
    Poser->ModifyBoneAdditiveTransform(BoneIndex, [&](FTransform& Transform)
    {
        Transform.SetRotation(RotationQuat * Transform.GetRotation());
    });

    // 结束姿态变化
    Poser->EndPoseChange();

    // 获取更新后的组件空间变换
    const TArray<FTransform>& ComponentSpaceTransforms = Poser->GetComponentSpaceTransforms();
    UE_LOG(LogTemp, Log, TEXT("Bone %s has %d component space transforms"), 
        *TargetBoneName.ToString(), ComponentSpaceTransforms.Num());
}

void UMySkeletonPoserComponent::ResetPose()
{
    if (!Poser) return;

    int32 BoneIndex = FindBoneIndex(TargetBoneName);
    if (BoneIndex == INDEX_NONE) return;

    Poser->BeginPoseChange();
    Poser->ClearBoneAdditiveTransform(BoneIndex);
    Poser->EndPoseChange();
}
```

## 模块依赖

本插件包含 7 个模块，以下是各模块间的主要依赖关系和外部独特依赖：

| 模块 | 用途 |
|---|---|
| `MeshModelingTools` | 运行时网格建模工具核心实现（简化、布尔、挤出等） |
| `ModelingComponents` | 工具共享组件（预览网格、选择机制、变换 Gizmo 等） |
| `ModelingOperators` | 底层几何运算算子（网格简化、布尔运算、UV 展开算法等） |
| `ModelingComponentsEditorOnly` | 仅编辑器的组件扩展 |
| `MeshModelingToolsEditorOnly` | 仅编辑器的工具（骨骼编辑、蒙皮权重、属性编辑等） |
| `ModelingOperatorsEditorOnly` | 仅编辑器的算子扩展 |
| `SkeletalMeshModifiers` | 骨骼网格修改器（用于骨骼编辑和蒙皮权重） |

无特殊依赖（仅标准 Core/Engine/Slate 等，加上 ModelingComponents/ModelingOperators 等本插件内部模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `2cd4fab7` | SReferenceSkeletonTree: preserve selection across RefreshTreeView so unrelated | 骨骼树视图刷新时保留选择状态 |
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 权重绘制工具添加跨模式同步笔刷半径选项 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 删除骨骼时权重转移到根骨骼而非丢弃 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构笔刷累积器支持松弛笔刷累积 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 仅顶点编辑时跳过拓扑重建以提升性能 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

该插件处于**非常活跃的维护状态**：

- 创建于 2021 年 7 月（UE5 早期开发阶段），是 UE5 Modeling Tools 框架的核心组成部分
- 截至 2026 年 5 月仍有持续的功能更新和 Bug 修复（最近一次更新仅在数日前）
- 从 git 历史看，近期更新涵盖：骨骼权重转移逻辑改进、笔刷行为优化、性能优化、UI 选择保持等
- 虽然标记为 `IsBetaVersion=true`，但这更多表示 API 可能在未来版本中调整，而非功能不稳定
- `Hidden=true` 表明该插件由 Modeling Tools Editor Mode 自动管理，用户无需手动启用

**推荐使用**：如果你需要在 UE5 中进行程序化的网格编辑（特别是骨骼网格相关的编辑操作），这是官方最完善的工具集。注意它依赖 Interactive Tools Framework，使用前需要理解该框架的设计模式。

⚠️ **注意**：该插件当前为 Beta 状态，API 和行为在引擎大版本间可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- [官方文档]()（暂无直接链接）
- [测试用例]()（测试用例位于 Engine/Tests 目录下，需单独查找）