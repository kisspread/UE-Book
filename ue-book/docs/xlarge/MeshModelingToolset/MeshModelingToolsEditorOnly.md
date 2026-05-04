# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

MeshModelingToolset 是 UE5 内置的**综合性网格建模与编辑工具集**，基于 Interactive Tools Framework 构建。它提供了一整套在编辑器内直接创建和编辑 3D 网格的工具，无需依赖外部 DCC 软件。

该插件解决的核心问题：
- **网格拓扑编辑**：简化（Simplify）、重新网格化（Remesh）、布尔运算（Boolean）、多边形切割（Polygon on Mesh）
- **UV 展开与参数化**：自动 UV 展开（UV Atlas、XAtlas、Patch Builder）、UV 编辑
- **骨骼网格编辑**：骨骼创建/删除/重命名/镜像、蒙皮权重绑定、权重绘制
- **网格属性编辑**：法线、切线、UV 通道、自定义属性的查看与编辑
- **组件选择系统**：顶点/边/面的交互式选择，支持扩展/收缩/泛洪选择

插件采用模块化架构，将工具逻辑（Tools）、操作算子（Operators）、基础组件（Components）分离，EditorOnly 后缀的模块包含仅在编辑器中使用的功能。

## 使用场景

- 你需要在 UE 编辑器内快速简化高面数网格以优化性能 → 用 **Simplify Mesh Tool**
- 你需要为静态网格自动生成 UV 坐标 → 用 **Parameterize Mesh Tool**（支持 UV Atlas / XAtlas / Patch Builder 三种算法）
- 你需要在网格上进行布尔切割操作 → 用 **Polygon on Mesh Tool**
- 你需要编辑骨骼网格的参考骨架（添加/删除/重命名骨骼）→ 用 **Skeleton Editing Tool**
- 你需要绑定蒙皮权重（自动计算骨骼影响）→ 用 **Skin Weights Binding Tool**
- 你需要手动绘制蒙皮权重 → 用 **Skin Weights Paint Tool**
- 你需要查看和编辑网格的自定义属性（法线、UV、顶点颜色等）→ 用 **Attribute Editor Tool**

## 蓝图用法

本插件主要面向编辑器工具，大部分功能通过编辑器 UI 交互使用。以下是从源码中提取的可蓝图访问的核心 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRefSkeleton` | 设置参考骨架数据 | `URefSkeletonPoser` |
| `GetRefSkeleton` | 获取参考骨架数据 | `URefSkeletonPoser` |
| `ModifyBoneAdditiveTransform` | 修改骨骼的叠加变换 | `URefSkeletonPoser` |
| `ClearBoneAdditiveTransform` | 清除指定骨骼的叠加变换 | `URefSkeletonPoser` |
| `ClearAllBoneAdditiveTransforms` | 清除所有骨骼的叠加变换 | `URefSkeletonPoser` |
| `GetComponentSpaceTransforms` | 获取组件空间变换数组 | `URefSkeletonPoser` |
| `BeginPoseChange` | 开始记录姿态变更（用于撤销/重做） | `URefSkeletonPoser` |
| `EndPoseChange` | 结束记录姿态变更 | `URefSkeletonPoser` |
| `Initialize` | 初始化骨骼变换代理 | `USkeletonTransformProxy` |
| `GetTransform` | 获取当前变换 | `USkeletonTransformProxy` |
| `SetMesh` | 设置选择器的目标网格 | `UToolMeshSelector` |
| `SetComponentSelectionMode` | 设置组件选择模式（顶点/边/面） | `UToolMeshSelector` |
| `GetSelectedVertices` | 获取当前选中的顶点列表 | `UToolMeshSelector` |
| `GrowSelection` | 扩展当前选择 | `UToolMeshSelector` |
| `ShrinkSelection` | 收缩当前选择 | `UToolMeshSelector` |
| `FloodSelection` | 泛洪选择 | `UToolMeshSelector` |
| `SelectBorder` | 选择边界 | `UToolMeshSelector` |

### 骨架编辑工具属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `BindingType` | `ESkinWeightsBindType` | 绑定类型（直接距离/测地体素） | `USkinWeightsBindingToolProperties` |
| `Stiffness` | `float` | 绑定刚度，值越低远处骨骼影响越大 | `USkinWeightsBindingToolProperties` |
| `MaxInfluences` | `int32` | 每个顶点最大骨骼影响数 | `USkinWeightsBindingToolProperties` |
| `VoxelResolution` | `int32` | 体素绑定的分辨率 | `USkinWeightsBindingToolProperties` |

### 网格简化工具属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `SimplifierType` | `ESimplifyType` | 简化算法类型 | `USimplifyMeshToolProperties` |
| `TargetMode` | `ESimplifyTargetType` | 目标模式（百分比/边长/三角形数/顶点数） | `USimplifyMeshToolProperties` |
| `TargetPercentage` | `int` | 目标三角形百分比 | `USimplifyMeshToolProperties` |
| `TargetEdgeLength` | `float` | 目标边长 | `USimplifyMeshToolProperties` |
| `TargetTriangleCount` | `int` | 目标三角形数量 | `USimplifyMeshToolProperties` |
| `bDiscardAttributes` | `bool` | 丢弃 UV 和法线，允许忽略接缝 | `USimplifyMeshToolProperties` |
| `bGeometricConstraint` | `bool` | 启用几何偏差约束 | `USimplifyMeshToolProperties` |
| `GeometricTolerance` | `float` | 几何偏差容差 | `USimplifyMeshToolProperties` |

### 多边形切割工具属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `Operation` | `EEmbeddedPolygonOpMethod` | 操作类型（穿透切割/外部切割/插入多边形） | `UPolygonOnMeshToolProperties` |
| `Shape` | `EPolygonType` | 多边形形状（圆/方/矩形/圆角矩/自定义） | `UPolygonOnMeshToolProperties` |
| `bCutWithBoolean` | `bool` | 使用体积布尔运算 | `UPolygonOnMeshToolProperties` |
| `PolygonScale` | `float` | 多边形缩放 | `UPolygonOnMeshToolProperties` |
| `Width` | `float` | 多边形宽度 | `UPolygonOnMeshToolProperties` |

### 使用示例（蓝图描述）

**场景：通过蓝图获取骨骼姿态信息**

1. 创建 `URefSkeletonPoser` 对象
2. 调用 `SetRefSkeleton` 传入参考骨架
3. 调用 `GetComponentSpaceTransforms` 获取所有骨骼的组件空间变换
4. 使用 `BeginPoseChange` / `EndPoseChange` 包裹修改操作以支持撤销

**场景：程序化网格选择**

1. 创建 `UToolMeshSelector` 对象
2. 调用 `InitialSetup` 初始化
3. 调用 `SetMesh` 设置目标预览网格
4. 调用 `SetComponentSelectionMode` 设置为 `Vertices` / `Edges` / `Faces`
5. 调用 `GetSelectedVertices` 获取选中结果
6. 使用 `GrowSelection` / `ShrinkSelection` / `FloodSelection` 编辑选择

## C++ 用法

### 头文件引入

```cpp
// 骨架编辑相关
#include "SkeletalMesh/SkeletonEditingTool.h"
#include "SkeletalMesh/SkeletonModifier.h"
#include "SkeletalMesh/RefSkeletonPoser.h"
#include "SkeletalMesh/SkeletalMeshEditingInterface.h"
#include "SkeletalMesh/SkeletalMeshToolsHelper.h"

// 网格工具相关
#include "SimplifyMeshTool.h"
#include "ParameterizeMeshTool.h"
#include "PolygonOnMeshTool.h"
#include "AttributeEditorTool.h"

// 组件选择
#include "ToolMeshSelector.h"

// 蒙皮权重
#include "SkeletalMesh/SkinWeightsBindingTool.h"
#include "SkeletalMesh/SkinWeightsPaintTool.h"
```

### 基本用法：骨架姿态计算

从 `SkeletalMeshToolsHelper` 提取的用法，用于计算骨骼矩阵和姿态变换。

```cpp
// 来源: Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingToolsEditorOnly/Public/SkeletalMesh/SkeletalMeshToolsHelper.h

#include "SkeletalMesh/SkeletalMeshToolsHelper.h"

// 计算骨骼矩阵（从参考姿态到当前姿态的变换）
TArray<FMatrix> BoneMatrices = SkeletalMeshToolsHelper::ComputeBoneMatrices(
    ComponentSpaceTransformsRefPose,  // 参考姿态的组件空间变换
    ComponentSpaceTransforms           // 当前姿态的组件空间变换
);

// 获取未姿态化的网格（重置骨架姿态并禁用变形目标）
SkeletalMeshToolsHelper::GetUnposedMesh(
    [](SkeletalMeshToolsHelper::FVertInfo VertInfo, const FVector& Position)
    {
        // 处理每个顶点的位置
    },
    PosedMesh,       // 当前姿态的网格
    SourceMesh,      // 源网格
    BoneMatrices,    // 骨骼矩阵
    SkinWeightProfile,
    MorphTargetWeights,
    VertArray        // 可选：只处理指定顶点子集
);

// 获取姿态化的网格
SkeletalMeshToolsHelper::GetPosedMesh(
    [](int32 VertIndex, const FVector& Position)
    {
        // 处理每个顶点
    },
    SourceMesh,
    BoneMatrices,
    SkinWeightProfile,
    MorphTargetWeights
);
```

### 基本用法：姿态变更检测

```cpp
// 来源: Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingToolsEditorOnly/Public/SkeletalMesh/SkeletalMeshToolsHelper.h

SkeletalMeshToolsHelper::FPoseChangeDetector PoseDetector;

// 注册变更通知回调
PoseDetector.GetNotifier().AddLambda(
    [](SkeletalMeshToolsHelper::FPoseChangeDetector::FPayload Payload)
    {
        switch (Payload.CurrentState)
        {
        case SkeletalMeshToolsHelper::FPoseChangeDetector::PoseJustChanged:
            // 姿态刚刚发生变化
            break;
        case SkeletalMeshToolsHelper::FPoseChangeDetector::PoseChanged:
            // 姿态持续变化中
            break;
        case SkeletalMeshToolsHelper::FPoseChangeDetector::PoseStoppedChanging:
            // 姿态变化停止
            break;
        }
    }
);

// 每帧检查姿态是否变化
PoseDetector.CheckPose(ComponentSpaceTransforms, MorphTargetWeights);
```

### 进阶用法：参考骨架姿态编辑

```cpp
// 来源: Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingToolsEditorOnly/Public/SkeletalMesh/RefSkeletonPoser.h

#include "SkeletalMesh/RefSkeletonPoser.h"

URefSkeletonPoser* Poser = NewObject<URefSkeletonPoser>();
Poser->SetRefSkeleton(InRefSkeleton);

// 开始记录姿态变更（支持撤销/重做）
Poser->BeginPoseChange();

// 修改指定骨骼的叠加变换
Poser->ModifyBoneAdditiveTransform(BoneIndex, [](FTransform& Transform)
{
    // 自定义修改逻辑
    Transform.SetLocation(Transform.GetLocation() + FVector(0, 0, 10));
});

// 结束记录
Poser->EndPoseChange();

// 获取组件空间变换
const TArray<FTransform>& CompSpaceTransforms = Poser->GetComponentSpaceTransforms();
const FTransform& SingleTransform = Poser->GetComponentSpaceTransform(BoneIndex);

// 清除叠加变换
Poser->ClearBoneAdditiveTransform(BoneIndex);
Poser->ClearAllBoneAdditiveTransforms();
```

### 进阶用法：网格组件选择系统

```cpp
// 来源: Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingToolsEditorOnly/Public/ToolMeshSelector.h

#include "ToolMeshSelector.h"

UToolMeshSelector* MeshSelector = NewObject<UToolMeshSelector>();

// 初始化选择器
MeshSelector->InitialSetup(World, ParentTool, [this]()
{
    // 选择变更回调
    OnSelectionChanged();
});

// 设置目标网格
MeshSelector->SetMesh(PreviewMesh, MeshTransform);

// 设置选择模式
MeshSelector->SetComponentSelectionMode(EComponentSelectionMode::Vertices);

// 获取选中的顶点
const TArray<int32>& SelectedVerts = MeshSelector->GetSelectedVertices();

// 编辑选择
MeshSelector->GrowSelection();    // 扩展选择
MeshSelector->ShrinkSelection();  // 收缩选择
MeshSelector->FloodSelection();   // 泛洪选择
MeshSelector->SelectBorder();     // 选择边界

// 获取选中的三角形
TArray<int32> Triangles;
MeshSelector->GetSelectedTriangles(Triangles);

// 渲染（在工具的 Render 回调中调用）
MeshSelector->Render(RenderAPI);
MeshSelector->DrawHUD(Canvas, RenderAPI);
```

### 进阶用法：骨骼网格编辑接口

```cpp
// 来源: Engine/Plugins/Runtime/MeshModelingToolset/Source/MeshModelingToolsEditorOnly/Public/SkeletalMesh/SkeletalMeshEditingInterface.h

#include "SkeletalMesh/SkeletalMeshEditingInterface.h"

// 实现骨骼网格编辑接口
class UMySkeletalMeshTool : public UInteractiveTool, public ISkeletalMeshEditingInterface
{
    // ...
protected:
    // 必须实现的通知处理函数
    virtual void HandleSkeletalMeshModified(
        const TArray<FName>& BoneNames,
        const ESkeletalMeshNotifyType InNotifyType) override
    {
        switch (InNotifyType)
        {
        case ESkeletalMeshNotifyType::BoneAdded:
            // 处理骨骼添加
            break;
        case ESkeletalMeshNotifyType::BoneRemoved:
            // 处理骨骼移除
            break;
        case ESkeletalMeshNotifyType::BoneRenamed:
            // 处理骨骼重命名
            break;
        case ESkeletalMeshNotifyType::BoneTransformed:
            // 处理骨骼变换
            break;
        }
    }
};

// 获取通知器
TSharedPtr<ISkeletalMeshNotifier> Notifier = MyTool->GetNotifier();
bool bNeedsNotification = MyTool->NeedsNotification();

// 获取骨骼修改器
TWeakObjectPtr<USkeletonModifier> Modifier = MyTool->GetModifier();
```

## Demo 示例

### 骨架姿态编辑器工具

```cpp
// MySkeletonPoseTool.h
#pragma once

#include "CoreMinimal.h"
#include "BaseTools/SingleSelectionMeshEditingTool.h"
#include "SkeletalMesh/RefSkeletonPoser.h"
#include "SkeletalMesh/SkeletalMeshToolsHelper.h"

#include "MySkeletonPoseTool.generated.h"

UCLASS()
class UMySkeletonPoseTool : public USingleSelectionMeshEditingTool
{
    GENERATED_BODY()

public:
    virtual void Setup() override;
    virtual void OnShutdown(EToolShutdownType ShutdownType) override;
    virtual void OnTick(float DeltaTime) override;

protected:
    UPROPERTY()
    TObjectPtr<URefSkeletonPoser> Poser;

    SkeletalMeshToolsHelper::FPoseChangeDetector PoseDetector;

    void OnPoseChanged(SkeletalMeshToolsHelper::FPoseChangeDetector::FPayload Payload);
};
```

```cpp
// MySkeletonPoseTool.cpp
#include "MySkeletonPoseTool.h"

void UMySkeletonPoseTool::Setup()
{
    USingleSelectionMeshEditingTool::Setup();

    // 创建姿态编辑器
    Poser = NewObject<URefSkeletonPoser>(this);
    // Poser->SetRefSkeleton(TargetSkeletalMesh->GetRefSkeleton());

    // 注册姿态变更检测
    PoseDetector.GetNotifier().AddUObject(this, &UMySkeletonPoseTool::OnPoseChanged);
}

void UMySkeletonPoseTool::OnShutdown(EToolShutdownType ShutdownType)
{
    if (ShutdownType == EToolShutdownType::Accept)
    {
        // 提交修改到骨骼网格
    }
    USingleSelectionMeshEditingTool::OnShutdown(ShutdownType);
}

void UMySkeletonPoseTool::OnTick(float DeltaTime)
{
    // 获取当前姿态
    const TArray<FTransform>& CompSpaceTransforms = Poser->GetComponentSpaceTransforms();
    TMap<FName, float> MorphWeights; // 从目标获取

    // 检测姿态变化
    PoseDetector.CheckPose(CompSpaceTransforms, MorphWeights);
}

void UMySkeletonPoseTool::OnPoseChanged(
    SkeletalMeshToolsHelper::FPoseChangeDetector::FPayload Payload)
{
    if (Payload.CurrentState == SkeletalMeshToolsHelper::FPoseChangeDetector::PoseStoppedChanging)
    {
        // 姿态稳定后，计算骨骼矩阵并更新预览
        TArray<FMatrix> BoneMatrices = SkeletalMeshToolsHelper::ComputeBoneMatrices(
            Payload.PreviousComponentSpaceTransforms,
            Payload.ComponentSpaceTransforms
        );
        // 使用 BoneMatrices 更新网格预览...
    }
}
```

## 模块依赖

从各模块的 Build.cs 提取的非标准依赖：

| 模块 | 用途 |
|---|---|
| `ModelingComponents` | 建模基础组件（预览网格、变换代理、选择机制等） |
| `ModelingOperators` | 建模操作算子（简化、UV 展开、布尔运算等） |
| `ModelingComponentsEditorOnly` | 编辑器专用建模组件 |
| `ModelingOperatorsEditorOnly` | 编辑器专用建模操作算子 |
| `MeshModelingTools` | 运行时网格建模工具实现 |
| `SkeletalMeshModifiers` | 骨骼网格修改器 |
| `GeometryFramework` | 几何框架（动态网格组件） |
| `InteractiveToolsFramework` | 交互式工具框架 |
| `MeshConversion` | 网格格式转换（MeshDescription ↔ DynamicMesh） |
| `MeshDescription` | 网格描述数据结构 |
| `DynamicMesh` | 动态网格库 |
| `GeometryCore` | 几何核心算法库 |
| `SkeletalMeshEditor` | 骨骼网格编辑器集成 |

## 维护状态

### 近期更新

```
- 8b858c134635 Unshelved from pending changelist '46933319'（从待处理变更列表中恢复）
- 2a082081a451 Dataflow: Update EditSkinWeightTool - Add support for dynamic mesh component target - Add bone manipulator - Check if the tool can start and output errors to the log if it cannot - Also avoid crashing if there's no bones in the target when opening the tool in EditSkinWeightEditor - Only enable the accept button when the weights have actually changed（编辑蒙皮权重工具更新：支持动态网格组件目标、添加骨骼操纵器、增加启动检查和错误日志、防止无骨骼崩溃、仅在权重实际变更时启用接受按钮）
- 77bf994b5d35 [SkinWeightsPaintTool] Fixed removing weights from rigid weighted verts turning them into unweighted verts（修复从刚性加权顶点移除权重后变为未加权顶点的问题）
```

### 维护评价

**活跃维护中** ✅

- **创建时间**：2019 年 10 月，已有约 6 年历史
- **近期更新**：最近的提交集中在蒙皮权重工具的改进和 bug 修复，表明该模块仍在积极开发
- **代码规模**：850+ 源文件，属于超大型插件，功能持续扩展
- **实验性状态**：标记为 Beta 且默认隐藏（`Hidden=true`），说明 Epic 仍在迭代完善
- **架构成熟度**：模块化设计良好，Tools/Operators/Components 分层清晰

**注意事项**：
- 该插件标记为 `IsBetaVersion=true`，API 可能在未来版本中发生变化
- `Hidden=true` 和 `Installed=false` 表明需要手动启用
- 作为 Beta 插件，部分功能可能不够稳定，建议在生产环境中谨慎使用

**推荐使用**：✅ 推荐。这是 UE5 内置的最全面的网格编辑工具集，对于需要在编辑器内进行程序化网格编辑的项目非常有价值。虽然标记为 Beta，但 Epic 持续投入开发，且是 UE5 编辑器建模模式的核心依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mesh-modeling-tools-in-unreal-engine/)（UE5 建模工具文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset/Tests)