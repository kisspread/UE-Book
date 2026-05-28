# Skeletal Mesh Simplifier (Early Access)

> A plugin to generate LOD for deforming meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼网格简化器 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `SkeletalMeshReduction` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-15 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SkeletalReduction) | |

## 用途

本插件实现了一个专门为骨骼网格设计的二次误差度量（Quadric Error Metric）网格简化算法。与普通的静态网格简化工具不同，它能够正确处理骨骼权重、法线、切线、UV等顶点属性，并在简化过程中尝试保持动画变形的质量。其核心功能是为带有骨骼动画的角色或物体自动生成多级细节（LOD），从而在不影响视觉表现的前提下，显著降低渲染时的顶点数量和三角形数量，优化运行时性能。

## 使用场景

- 你正在开发一个拥有大量角色或复杂生物模型的游戏，需要优化同屏渲染性能。
- 你的项目需要为移动端或性能受限的平台部署，需要为高精度骨骼角色创建多个LOD级别。
- 美术师希望在编辑器中直观地控制骨骼网格的简化程度和质量，以平衡性能与视觉效果。

## 蓝图用法

该插件主要通过编辑器界面提供功能，而非暴露大量蓝图节点。其核心功能是集成在 `Skeletal Mesh` 编辑器中的 LOD 生成工具。用户通常在编辑器中通过以下方式使用：

1.  在内容浏览器中打开一个 `Skeletal Mesh` 资产。
2.  在属性面板的 “LOD Settings” 或 “Reduction Settings” 部分，选择使用本插件提供的简化算法来生成新的 LOD 级别。
3.  调整相关参数（如期望的三角形数量百分比、最大误差阈值等），然后执行生成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无公开蓝图节点 | 主要功能通过编辑器UI访问 | `ISkeletalMeshReduction` (模块接口) |

### 使用示例（蓝图描述）

由于主要功能在编辑器中操作，无典型的蓝图连接图示。在C++中，可以通过`ISkeletalMeshReduction`模块接口获取实例，但通常由引擎内部调用。

## C++ 用法

该插件的公共API相对有限，主要提供了一个模块接口。其核心简化算法作为编辑器工具内部使用。

### 头文件引入

```cpp
#include "ISkeletalMeshReduction.h"
```

### 基本用法

获取模块接口的单例实例以检查其可用性。主要功能通常由编辑器和引擎内部调用。

```cpp
// 检查模块是否已加载并可用
if (ISkeletalMeshReduction::IsAvailable())
{
    // 获取模块实例 (通常用于调用其公共方法，但当前接口方法较少)
    ISkeletalMeshReduction& SkeletalMeshReductionModule = ISkeletalMeshReduction::Get();
    FString ModuleName = SkeletalMeshReductionModule.GetName();
    UE_LOG(LogTemp, Log, TEXT("Skeletal Mesh Reduction Module Name: %s"), *ModuleName);
}
```
*来源：`Source/Public/ISkeletalMeshReduction.h`*

### 进阶用法

插件的核心功能由 `SkeletalSimplifier` 命名空间下的内部类实现，这些类并未公开。一个简化的内部使用流程概念如下（非公开API，仅供理解算法）：

1.  **构建简化器网格管理器**：将原始的骨骼网格顶点和索引数据输入 `FSimplifierMeshManager`。
2.  **创建核心简化器**：使用 `FMeshSimplifier`，传入网格管理器及各种权重参数（如属性权重、边界约束权重）。
3.  **设置终止条件**：定义 `FSimplifierTerminator`，指定最小保留的三角形/顶点数量或最大允许的误差。
4.  **执行简化**：调用 `FMeshSimplifier::SimplifyMesh()`，传入终止条件。算法会迭代地合并误差最小的边，直到满足终止条件。
5.  **输出结果**：通过 `OutputMesh()` 获取简化后的顶点和索引缓冲区。

```cpp
// 概念性伪代码，展示内部算法流程 (不可直接编译)
using namespace SkeletalSimplifier;

// 1. 构建网格管理器 (需要原始网格数据)
FSimplifierMeshManager MeshManager(SrcVerts, NumSrcVerts, SrcIndexes, NumSrcIndexes, true);

// 2. 创建核心简化器 (需要设置多项权重和参数)
FMeshSimplifier Simplifier(SrcVerts, NumSrcVerts, SrcIndexes, NumSrcIndexes,
                           CoAlignmentLimit, VolumeImportance, bVolumePreservation,
                           bEnforceBoundaries, bMergeCoincidentVertBones, bUseLegacyAttrGrad);

// 设置属性权重 (法线、切线、颜色、UV等)
FMeshSimplifier::DenseVecDType BasicAttrWeights;
// ... 填充权重值
Simplifier.SetAttributeWeights(BasicAttrWeights);

// 设置骨骼权重 (稀疏属性)
FMeshSimplifier::SparseWeightContainerType BoneWeights;
// ... 填充权重值
Simplifier.SetSparseAttributeWeights(BoneWeights);

// 锁定网格边界，防止被简化
Simplifier.SetBoundaryLocked();

// 3. 定义终止条件：至少保留 1000 个三角形，或最大误差超过 1.0
FSimplifierTerminator Terminator(1000, /* MaxTri */, 1000, /* MaxVert */, 1.0f, /* MaxCost */ 100.0f);

// 4. 执行简化
float FinalError = Simplifier.SimplifyMesh(Terminator);

// 5. 获取结果
int32 ReducedVertCount = Simplifier.GetNumVerts();
int32 ReducedTriCount = Simplifier.GetNumTris();
TArray<MeshVertType> ResultVerts(ReducedVertCount);
TArray<uint32> ResultIndexes(ReducedTriCount * 3);
Simplifier.OutputMesh(ResultVerts.GetData(), ResultIndexes.GetData());
```

## Demo 示例

该插件主要通过编辑器界面使用，且其核心算法为内部实现，没有面向运行时的公开组件或蓝图节点。因此，不需要提供可独立运行的 `.h + .cpp` 代码示例。最佳示例是直接在UE编辑器中打开一个 `Skeletal Mesh`，使用其LOD生成工具。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `030a3957` | Skeletal Mesh Reduction: Only run mesh or bone weight reduction if actually required. | 优化性能：仅在网格或骨骼权重确实需要简化时才执行减少操作。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 代码维护：将旧式UE_LOG日志宏迁移到UE_LOGF。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复编译错误：解决了代码中存在不可达代码段的问题。 |
| 2025-10-30 | `0990a715` | Ran UnrealCodeFixup on Fortnite to change all ~Type() {} to instead be ~Type() = default | 代码标准化：将空的析构函数体 `~Type() {}` 统一替换为 `~Type() = default`。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 编译警告修复：解决了一些琐碎的不可达代码编译警告。 |

### 维护评价

- **年龄**：创建于2018年底，已有约7年历史。
- **维护活跃度**：近期（2026年4月）仍有功能性更新（优化了执行逻辑），表明插件处于**活跃维护**状态。之前的提交多为代码标准化和编译修复，属于正常的维护工作。
- **状态**：尽管插件标记为“Early Access”且位于 `Experimental` 目录下，但其核心算法成熟，且持续有维护更新。推荐在需要为骨骼网格生成LOD的场景中使用。
- **已知限制**：作为实验性插件，其API和行为在未来的UE版本中可能会有变动。主要限制是它专注于骨骼网格，不适用于静态网格的简化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SkeletalReduction)