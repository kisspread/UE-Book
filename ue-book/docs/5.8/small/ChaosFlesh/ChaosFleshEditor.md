# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（图标资源、SVG 素材） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是基于 Chaos 物理系统的**体积肉体/软体模拟插件**。它使用四面体网格（Tetrahedral Mesh）作为体素化表示，实现可变形物体的物理模拟，典型应用是模拟肌肉、肉体等软组织在外力下的形变行为。

核心数据结构是 `FFleshCollection`，存储了四面体化的几何信息（节点、四面体元素、材质绑定等）。插件支持从外部格式（`.tet`、`.geo`）导入四面体网格，通过 Dataflow 节点图驱动模拟流程，并可将模拟结果烘焙为 GeometryCache 供动画回放。

**解决的问题**：在 Chaos 物理框架下提供一套完整的肉体/可变形体模拟管线，包括资产创建、数据导入、模拟求解、结果可视化与缓存导出。

## 使用场景

- 你需要模拟角色肌肉在骨骼动画驱动下的体积形变 → 使用 ChaosFlesh 配合 DeformableSolver
- 你需要从外部 DCC 工具（如 Houdini）导出四面体网格并在 UE 中进行物理模拟 → 使用 `.tet`/`.geo` 导入功能
- 你需要将物理模拟结果烘焙为 GeometryCache 以便在游戏中回放 → 使用 `CreateGeometryCache` 命令
- 你需要调试四面体网格质量（查找高纵横比或退化四面体）→ 使用 `FindQualifyingTetrahedra` 命令

## 蓝图用法

本插件主要面向编辑器工作流和 C++ 扩展，公开的蓝图 API 较少。核心交互通过编辑器命令和 Dataflow 节点完成。

### 可渲染类型设置

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bVisible` (纤维场) | 控制纤维场的可见性 | `UDataflowFleshFiberFieldRenderSettings` |
| `Color` | 纤维场显示颜色 | `UDataflowFleshFiberFieldRenderSettings` |
| `LineThickness` | 纤维场线宽 | `UDataflowFleshFiberFieldRenderSettings` |
| `LengthScalar` | 纤维场矢量长度缩放 | `UDataflowFleshFiberFieldRenderSettings` |
| `bVisible` (矢量场) | 控制矢量场的可见性 | `UDataflowFleshVectorFieldRenderSettings` |
| `LineThickness` | 矢量场线宽 | `UDataflowFleshVectorFieldRenderSettings` |
| `LengthScalar` | 矢量场长度缩放 | `UDataflowFleshVectorFieldRenderSettings` |
| `bVisible` (四面体) | 控制四面体线框的可见性 | `UDataflowFleshTetrahedronRenderSettings` |
| `LineThickness` | 四面体线框线宽 | `UDataflowFleshTetrahedronRenderSettings` |
| `LineColor` | 四面体线框颜色 | `UDataflowFleshTetrahedronRenderSettings` |

这些设置类继承自 `UDataflowRenderableTypeSettings`，用于在 Dataflow 编辑器中控制模拟结果的可视化效果。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosFlesh/ChaosFleshEditorPlugin.h"
#include "ChaosFlesh/Cmd/ChaosFleshCommands.h"
#include "ChaosFlesh/Cmd/FleshAssetConversion.h"
```

### 基本用法 — 四面体网格导入

从 `FFleshAssetConversion` 提取的文件导入功能：

```cpp
// 从文件导入四面体网格为 FleshCollection
// 来源: Public/ChaosFlesh/Cmd/FleshAssetConversion.h
TUniquePtr<FFleshCollection> Collection = FFleshAssetConversion::ImportTetFromFile(TEXT("/path/to/mesh.tet"));
```

> 注意：当前版本中此功能标注为 "Currently disabled"，可能需要在代码中启用。

### 基本用法 — 控制台命令调用

编辑器提供了通过控制台命令驱动的工具集，定义在 `FChaosFleshCommands` 中：

```cpp
// 查找高纵横比四面体（用于网格质量检查）
// 来源: Public/ChaosFlesh/Cmd/ChaosFleshCommands.h
// 控制台命令: FChaosDeformableCommands.FindHighAspectRatioTetrahedra
// 支持参数:
//   MaxAR <float>    - 纵横比阈值
//   MinVol <float>   - 最小体积阈值
//   XCoordGT/LT等    - 坐标范围过滤
//   HideTets         - 将选中四面体加入隐藏列表
FChaosFleshCommands::FindQualifyingTetrahedra(Args, World);
```

### 进阶用法 — 创建 GeometryCache

将缓存的肉体模拟结果烘焙为 GeometryCache 资产：

```cpp
// 来源: Public/ChaosFlesh/Cmd/ChaosFleshCommands.h
// 控制台命令: FChaosDeformableCommands.CreateGeometryCache
// 前提条件:
//   1. 选中的 Actor 需有 FleshComponent 和 SkeletalMeshComponent
//   2. FleshComponent 的 RestCollection 需包含 deformer bindings
// 可选参数:
//   UsdFile </path/to/file.usd>  - 覆盖 USD 文件路径
//   FrameRate 24                 - 输出帧率（默认 24）
//   MaxNumFrames <int>           - 最大帧数限制
TArray<FString> Args = {TEXT("FrameRate"), TEXT("30"), TEXT("MaxNumFrames"), TEXT("120")};
FChaosFleshCommands::CreateGeometryCache(Args, World);
```

## Demo 示例

以下展示 FleshAsset 的资产定义扩展模式（自定义资产在内容浏览器中的展示）：

```cpp
// FleshAssetDefinition.h
#pragma once

#include "AssetDefinitionDefault.h"
#include "FleshAssetDefinition.generated.h"

UCLASS()
class UFleshAssetDefinition : public UAssetDefinitionDefault
{
    GENERATED_BODY()

public:
    // 资产在内容浏览器中显示的名称
    virtual FText GetAssetDisplayName() const override;
    
    // 关联的资产类
    virtual TSoftClassPtr<UObject> GetAssetClass() const override;
    
    // 内容浏览器中的图标颜色
    virtual FLinearColor GetAssetColor() const override;
    
    // 资产分类（出现在哪个右键菜单分类下）
    virtual TConstArrayView<FAssetCategoryPath> GetAssetCategories() const override;
    
    // 加载缩略图信息
    virtual UThumbnailInfo* LoadThumbnailInfo(const FAssetData& InAssetData) const override;
    
    // 双击资产时的打开行为
    virtual EAssetCommandResult OpenAssets(const FAssetOpenArgs& OpenArgs) const override;
};
```

```cpp
// FleshAssetDefinition.cpp
#include "FleshAssetDefinition.h"
#include "FleshAsset.h"
#include "FleshAssetThumbnailRenderer.h"

FText UFleshAssetDefinition::GetAssetDisplayName() const
{
    return NSLOCTEXT("AssetTypeActions", "FleshAsset", "Flesh Asset");
}

TSoftClassPtr<UObject> UFleshAssetDefinition::GetAssetClass() const
{
    return UFleshAsset::StaticClass();
}

FLinearColor UFleshAssetDefinition::GetAssetColor() const
{
    return FLinearColor(FColor(255, 100, 100)); // 自定义资产颜色
}

TConstArrayView<FAssetCategoryPath> UFleshAssetDefinition::GetAssetCategories() const
{
    static const TArray<FAssetCategoryPath> Categories = {
        FAssetCategoryPath(NSLOCTEXT("ChaosFlesh", "PhysicsCategory", "Physics"))
    };
    return Categories;
}

UThumbnailInfo* UFleshAssetDefinition::LoadThumbnailInfo(const FAssetData& InAssetData) const
{
    // 返回自定义缩略图渲染器信息
    return nullptr; // 实际实现中会返回 UFleshAssetThumbnailInfo
}

EAssetCommandResult UFleshAssetDefinition::OpenAssets(const FAssetOpenArgs& OpenArgs) const
{
    // 打开 FleshAsset 编辑器
    return EAssetCommandResult::Handled;
}
```

## 模块依赖

基于插件的功能分析（四面体物理模拟、Dataflow 集成、GeometryCache 导出、Slate 编辑器 UI），推断的关键依赖：

| 模块 | 用途 |
|---|---|
| `Chaos` | Chaos 物理系统核心 |
| `ChaosSolverEngine` | Chaos 求解器引擎 |
| `Dataflow` | Dataflow 节点图框架 |
| `DataflowEngine` | Dataflow 引擎运行时 |
| `DataflowEditor` | Dataflow 编辑器集成 |
| `GeometryCache` | 模拟结果烘焙为 GeometryCache |
| `GeometryCollectionEngine` | 几何集合引擎（与破碎系统共享基础设施） |
| `ChaosFlesh` | 肉体模拟运行时核心模块 |
| `ChaosFleshEngine` | 肉体模拟引擎模块 |
| `ChaosFleshNodes` | Dataflow 肉体节点 |

> 注：以上依赖基于源码功能推断，实际 Build.cs 可能有差异。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 相关更新 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理纤维场生成节点代码 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复掩码缓冲区赋值错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃 FleshAsset 中的 StaticMesh 属性 |

### 维护评价

- **状态**：🟢 **活跃维护中**
- **年龄**：约 4 年（2022 年创建），仍处于实验阶段
- **更新频率**：非常活跃，最近一次更新在 2026-05-13，近期内有多次密集提交
- **开发方向**：正在清理代码（纤维场节点）、修复 bug（缓冲区赋值）、推进 API 迭代（废弃 StaticMesh 属性）
- **风险提示**：⚠️ 作为实验性插件（`IsExperimentalVersion=true`，`EnabledByDefault=false`），API 随时可能发生破坏性变更（如废弃 StaticMesh 属性所示）。不建议在生产环境中依赖此插件
- **推荐**：适合用于研究和原型开发，如需在产品中使用建议持续跟踪上游变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档]()（暂无）