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
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

MeshModelingToolset 是 UE5 内置的网格体建模工具集插件，基于 Interactive Tools Framework 实现。它提供了完整的 3D 网格创建与编辑能力，包括几何体操作、网格编辑、骨骼修改和蒙皮权重编辑等功能。

**SkeletalMeshModifiers 模块**专注于骨骼网格体（Skeletal Mesh）的骨骼层级结构和蒙皮权重的程序化编辑。它允许通过蓝图或 C++ 以编程方式批量操作骨骼——添加、删除、重命名、镜像、重新定向、修改父子关系，以及编辑顶点蒙皮权重。这个模块解决的核心问题是：在动画制作流程中需要对大量骨骼进行自动化或批量编辑，而手动在编辑器中逐个操作效率低下。

## 使用场景

- 你在制作角色动画时需要批量镜像骨骼（如左臂骨骼生成右臂对应骨骼）→ 用 `USkeletonModifier::MirrorBone`
- 你需要程序化地为角色添加新骨骼（如添加武器挂点）→ 用 `USkeletonModifier::AddBone`
- 你从 DCC 工具导入的模型蒙皮权重需要批量清洗（修剪微小权重、限制最大影响数）→ 用 `USkinWeightModifier::PruneAllWeights` + `EnforceMaxInfluences`
- 你需要通过蓝图脚本批量修改骨骼朝向以修正动画导入问题 → 用 `USkeletonModifier::OrientBone`
- 你在开发工具管线（Pipeline Tools），需要自动化骨骼网格体处理流程

## 蓝图用法

### 核心节点

#### 骨骼修改器（USkeletonModifier）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSkeletalMesh` | 加载目标骨骼网格体用于编辑 | `USkeletonModifier` |
| `CommitSkeletonToSkeletalMesh` | 将所有修改提交回骨骼网格体资产 | `USkeletonModifier` |
| `AddBone` / `AddBones` | 在骨骼层级中添加新骨骼 | `USkeletonModifier` |
| `RemoveBone` / `RemoveBones` | 从骨骼层级中删除骨骼 | `USkeletonModifier` |
| `RenameBone` / `RenameBones` | 重命名骨骼 | `USkeletonModifier` |
| `MirrorBone` / `MirrorBones` | 沿指定轴镜像骨骼 | `USkeletonModifier` |
| `SetBoneTransform` / `SetBonesTransforms` | 设置骨骼的本地变换 | `USkeletonModifier` |
| `OrientBone` / `OrientBones` | 重新定向骨骼朝向 | `USkeletonModifier` |
| `ParentBone` / `ParentBones` | 修改骨骼的父级关系 | `USkeletonModifier` |
| `GetBoneTransform` | 获取骨骼的变换（本地或全局） | `USkeletonModifier` |
| `GetParentName` | 获取骨骼的父级名称 | `USkeletonModifier` |
| `GetChildrenNames` | 获取骨骼的子级列表 | `USkeletonModifier` |
| `GetAllBoneNames` | 获取所有骨骼名称 | `USkeletonModifier` |

#### 蒙皮权重修改器（USkinWeightModifier）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSkeletalMesh` | 加载目标骨骼网格体用于权重编辑 | `USkinWeightModifier` |
| `CommitWeightsToSkeletalMesh` | 将修改后的权重提交回资产 | `USkinWeightModifier` |
| `GetNumVertices` | 获取网格体顶点总数 | `USkinWeightModifier` |
| `GetAllBoneNames` | 获取所有骨骼名称 | `USkinWeightModifier` |
| `GetVertexWeights` | 获取单个顶点的骨骼权重映射 | `USkinWeightModifier` |
| `SetVertexWeights` | 设置单个顶点的骨骼权重 | `USkinWeightModifier` |
| `NormalizeVertexWeights` | 归一化指定顶点的权重 | `USkinWeightModifier` |
| `NormalizeAllWeights` | 归一化所有顶点的权重 | `USkinWeightModifier` |
| `EnforceMaxInfluences` | 限制每个顶点的最大骨骼影响数 | `USkinWeightModifier` |
| `PruneVertexWeights` | 修剪指定顶点的微小权重 | `USkinWeightModifier` |
| `PruneAllWeights` | 修剪所有顶点的微小权重 | `USkinWeightModifier` |

### 使用示例（蓝图描述）

**批量镜像骨骼流程：**

1. 创建 `USkeletonModifier` 实例
2. 调用 `SetSkeletalMesh` 传入目标骨骼网格体
3. 调用 `MirrorBones`，传入要镜像的骨骼名称数组和 `FMirrorOptions`（默认沿 X 轴镜像，自动将 `_l` 替换为 `_r`）
4. 调用 `CommitSkeletonToSkeletalMesh` 提交修改

**清洗蒙皮权重流程：**

1. 创建 `USkinWeightModifier` 实例
2. 调用 `SetSkeletalMesh` 加载网格体
3. 调用 `PruneAllWeights(0.01)` 清除低于 1% 的权重
4. 调用 `EnforceMaxInfluences(8)` 将每个顶点的最大影响数限制为 8
5. 调用 `NormalizeAllWeights` 归一化所有权重
6. 调用 `CommitWeightsToSkeletalMesh` 提交

## C++ 用法

### 头文件引入

```cpp
#include "SkeletonModifier.h"
#include "SkinWeightModifier.h"
```

### 基本用法

以下示例展示了如何通过 C++ 程序化地镜像骨骼：

```cpp
// 创建骨骼修改器
USkeletonModifier* Modifier = NewObject<USkeletonModifier>();

// 设置目标骨骼网格体
USkeletalMesh* SkeletalMesh = LoadObject<USkeletalMesh>(nullptr, TEXT("/Game/Characters/Mannequin/Meshes/SK_Mannequin"));
Modifier->SetSkeletalMesh(SkeletalMesh);

// 配置镜像选项
FMirrorOptions MirrorOpts;
MirrorOpts.MirrorAxis = EAxis::X;        // 沿 X 轴镜像
MirrorOpts.bMirrorRotation = true;       // 同时镜像旋转
MirrorOpts.LeftString = TEXT("_l");       // 左侧标识
MirrorOpts.RightString = TEXT("_r");      // 右侧标识
MirrorOpts.bMirrorChildren = true;       // 递归镜像子骨骼

// 镜像指定骨骼
Modifier->MirrorBone(FName("upperarm_l"), MirrorOpts);

// 提交修改
Modifier->CommitSkeletonToSkeletalMesh();
```

### 进阶用法

批量编辑蒙皮权重的完整流程：

```cpp
// 创建蒙皮权重修改器
USkinWeightModifier* WeightModifier = NewObject<USkinWeightModifier>();
WeightModifier->SetSkeletalMesh(SkeletalMesh);

// 获取顶点数量并遍历编辑
int32 NumVertices = WeightModifier->GetNumVertices();
for (int32 i = 0; i < NumVertices; ++i)
{
    // 获取当前权重
    TMap<FName, float> Weights = WeightModifier->GetVertexWeights(i);
    
    // 移除某个骨骼的影响
    Weights.Remove(FName("spine_01"));
    
    // 设置修改后的权重
    WeightModifier->SetVertexWeights(i, Weights, true);
}

// 批量修剪微小权重并限制影响数
WeightModifier->PruneAllWeights(0.01f);
WeightModifier->EnforceMaxInfluences(8);

// 提交修改（会自动归一化）
WeightModifier->CommitWeightsToSkeletalMesh();
```

## Demo 示例

### 骨骼批量重定向示例

```cpp
// SkeletonOrientTool.h
#pragma once

#include "CoreMinimal.h"
#include "SkeletonModifier.h"

class FSkeletonOrientTool
{
public:
    static bool OrientAllBonesToChildren(USkeletalMesh* InSkeletalMesh)
    {
        if (!InSkeletalMesh) return false;
        
        USkeletonModifier* Modifier = NewObject<USkeletonModifier>();
        if (!Modifier->SetSkeletalMesh(InSkeletalMesh))
        {
            return false;
        }
        
        // 配置朝向选项：主轴朝向 +X
        FOrientOptions OrientOpts;
        OrientOpts.Primary = EOrientAxis::PositiveX;
        OrientOpts.Secondary = EOrientAxis::PositiveY;
        OrientOpts.bUsePlaneAsSecondary = true;
        OrientOpts.bOrientChildren = false; // 不递归影响子骨骼
        
        // 获取所有骨骼
        TArray<FName> AllBones = Modifier->GetAllBoneNames();
        
        // 对所有骨骼应用朝向调整
        return Modifier->OrientBones(AllBones, OrientOpts);
        // 注意：此处省略了 Commit 调用，实际使用时需要调用 CommitSkeletonToSkeletalMesh()
    }
};
```

```cpp
// SkeletonOrientTool.cpp
// 使用示例：
// FSkeletonOrientTool::OrientAllBonesToChildren(MySkeletalMesh);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MeshModelingTools` | 核心网格建模工具实现 |
| `ModelingComponents` | 建模组件（交互式工具框架基础） |
| `ModelingOperators` | 建模运算符（几何体操作） |
| `GeometryCore` | 几何体核心库 |
| `GeometryFramework` | 几何体框架 |
| `DynamicMesh` | 动态网格体数据结构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `2cd4fab7` | SReferenceSkeletonTree: preserve selection across RefreshTreeView so unrelated | 骨骼树视图刷新时保持选择状态不丢失 |
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 蒙皮权重绘制工具新增跨模式同步画笔半径选项 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 骨骼编辑工具：删除骨骼时将其权重转移到根骨骼而非丢失 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构绘制笔触累加器以支持松弛画笔并修复问题 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 仅编辑顶点时跳过拓扑组重建，提升性能 |

### 维护评价

该插件创建于 2021 年 7 月，至今约 5 年历史。从近期 git 记录来看，**维护非常活跃**——最近的提交集中在 2026 年 5 月，涉及骨骼编辑工具的 bug 修复（删除骨骼时权重转移策略优化）、蒙皮权重绘制工具的功能增强（同步画笔半径）以及性能优化（跳过不必要的拓扑重建）。

需要注意的是，该插件标记为 **Beta** 版本（`IsBetaVersion=true`）且 **Hidden=true**，说明 Epic 仍视其为实验性功能。API 可能在未来版本中发生变化。但由于有 Epic Games 持续维护，功能完整度高，推荐在生产环境中谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- 官方文档（无）