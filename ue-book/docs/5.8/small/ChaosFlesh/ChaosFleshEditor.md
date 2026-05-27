# Chaos Flesh

> Chaos Flesh Simulation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 布料模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、渲染资源） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Editor), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是一个基于 Chaos Physics 引擎的可变形体（Flesh）模拟插件，使用四面体网格（Tetrahedron Mesh）对肉质/软体物体进行物理模拟。该插件解决的核心问题是：**如何在 Unreal Engine 中对肉质、有机体等软体对象进行基于物理的真实变形模拟**。

该插件提供完整的资产管线：
1. **FleshAsset** — 存储四面体网格数据的资产类型
2. **ChaosDeformableSolver** — 可变形体求解器资产
3. **Dataflow 图表** — 通过节点图定义纤维场（Fiber Field）、向量场（Vector Field）等物理属性
4. **几何缓存导出** — 将模拟结果烘焙为 GeometryCache 资产
5. **调试可视化** — 在编辑器中查看四面体结构、纤维场、向量场

## 使用场景

- 你在制作电影级特效或生物模拟 → 用 ChaosFlesh 模拟肌肉、内脏等有机体的变形
- 你需要对骨骼网格体附加物理驱动的软体变形 → 用 FleshAsset + SkeletalMesh 联动
- 你需要将模拟结果导出为 GeometryCache 供 Sequencer 使用 → 用 CreateGeometryCache 命令
- 你需要调试四面体网格质量（如检查高长宽比的四面体） → 用 FindQualifyingTetrahedra 命令

## 蓝图用法

ChaosFleshEditor 模块主要面向编辑器扩展，核心功能通过控制台命令和编辑器 UI 暴露，而非蓝图节点。可配置的属性通过 Dataflow 渲染设置类暴露。

### 渲染设置属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bVisible` (FiberField) | 控制纤维场的可见性 | `UDataflowFleshFiberFieldRenderSettings` |
| `Color` | 纤维场的显示颜色 | `UDataflowFleshFiberFieldRenderSettings` |
| `LineThickness` | 纤维场线宽 | `UDataflowFleshFiberFieldRenderSettings` |
| `LengthScalar` | 纤维场向量长度缩放 | `UDataflowFleshFiberFieldRenderSettings` |
| `bVisible` (VectorField) | 控制向量场的可见性 | `UDataflowFleshVectorFieldRenderSettings` |
| `LineThickness` | 向量场线宽 | `UDataflowFleshVectorFieldRenderSettings` |
| `LengthScalar` | 向量场向量长度缩放 | `UDataflowFleshVectorFieldRenderSettings` |
| `bVisible` (Tetrahedrons) | 控制四面体网格的可见性 | `UDataflowFleshTetrahedronRenderSettings` |
| `LineThickness` | 四面体线宽 | `UDataflowFleshTetrahedronRenderSettings` |
| `LineColor` | 四面体线颜色 | `UDataflowFleshTetrahedronRenderSettings` |

### 控制台命令

| 命令 | 说明 | 参数 |
|---|---|---|
| `ImportFile` | 导入文件 | 文件路径参数 |
| `FindQualifyingTetrahedra` | 查找符合条件的四面体并输出索引到日志 | `MaxAR`, `MinVol`, `XCoordGT/LT`, `YCoordGT/LT`, `ZCoordGT/LT`, `HideTets` |
| `CreateGeometryCache` | 将缓存的 Flesh 模拟结果烘焙为 GeometryCache 资产 | `UsdFile`, `FrameRate`, `MaxNumFrames` |

### 使用示例（控制台命令）

```
# 查找长宽比大于 5.0 的四面体
FChaosDeformableCommands.FindQualifyingTetrahedra MaxAR 5.0

# 查找体积小于 0.001 的四面体并隐藏
FChaosDeformableCommands.FindQualifyingTetrahedra MinVol 0.001 HideTets

# 从缓存模拟创建 GeometryCache，帧率 30fps，最多 120 帧
FChaosDeformableCommands.CreateGeometryCache FrameRate 30 MaxNumFrames 120
```

## C++ 用法

### 头文件引入

```cpp
// 控制台命令
#include "ChaosFlesh/Cmd/ChaosFleshCommands.h"

// 资产转换
#include "ChaosFlesh/Cmd/FleshAssetConversion.h"

// 渲染设置
#include "ChaosFleshRendering/FleshFiberFieldRenderableType.h"
#include "ChaosFleshRendering/FleshVectorFieldRenderableType.h"
#include "ChaosFleshRendering/FleshTetrahedronRenderableType.h"

// 编辑器插件接口
#include "ChaosFlesh/ChaosFleshEditorPlugin.h"
```

### 基本用法

从 `.tet` 或 `.geo` 文件导入四面体网格数据创建 FleshCollection：

```cpp
// 来源: Public/ChaosFlesh/Cmd/FleshAssetConversion.h
#include "ChaosFlesh/Cmd/FleshAssetConversion.h"

// 从文件导入四面体网格（支持 .tet 和 .geo 格式，兼容 version 19）
TUniquePtr<FFleshCollection> FleshCollection = FFleshAssetConversion::ImportTetFromFile(TEXT("/path/to/mesh.tet"));
if (FleshCollection.IsValid())
{
    // 使用 FleshCollection 创建或更新 FleshAsset
    UE_LOG(LogTemp, Log, TEXT("成功导入四面体网格"));
}
```

### 注册自定义渲染设置

```cpp
// 来源: Private/ChaosFleshRendering/FleshFiberFieldRenderableType.h
#include "ChaosFleshRendering/FleshFiberFieldRenderableType.h"

// 在模块启动时注册 Flesh 渲染类型
void MyModule::StartupModule()
{
    UE::Flesh::Private::RegisterFleshFiberFieldRenderableTypes();
    UE::Flesh::Private::RegisterFleshVectorFieldRenderableTypes();
    UE::Flesh::Private::RegisterFleshTetrahedronRenderableTypes();
}
```

### 进阶用法

使用 `FChaosFleshCommands` 调用编辑器命令进行四面体网格分析和 GeometryCache 创建：

```cpp
// 来源: Public/ChaosFlesh/Cmd/ChaosFleshCommands.h
#include "ChaosFlesh/Cmd/ChaosFleshCommands.h"

// 查找高长宽比的四面体
TArray<FString> FindArgs;
FindArgs.Add(TEXT("MaxAR"));
FindArgs.Add(TEXT("10.0"));
FindArgs.Add(TEXT("HideTets")); // 同时隐藏这些四面体
FChaosFleshCommands::FindQualifyingTetrahedra(FindArgs, GetWorld());

// 从模拟缓存创建 GeometryCache
TArray<FString> CacheArgs;
CacheArgs.Add(TEXT("FrameRate"));
CacheArgs.Add(TEXT("30"));
CacheArgs.Add(TEXT("MaxNumFrames"));
CacheArgs.Add(TEXT("240"));
CacheArgs.Add(TEXT("UsdFile"));
CacheArgs.Add(TEXT("/path/to/simulation.usd"));
FChaosFleshCommands::CreateGeometryCache(CacheArgs, GetWorld());
```

### 自定义资产缩略图渲染器

```cpp
// 来源: Public/ChaosFlesh/Asset/FleshAssetThumbnailRenderer.h
#include "ChaosFlesh/Asset/FleshAssetThumbnailRenderer.h"

// FleshAsset 使用专用的 ThumbnailRenderer 在内容浏览器中显示预览
// UFleshAssetThumbnailRenderer 继承自 UDefaultSizedThumbnailRenderer
// 内部使用 FFleshAssetThumbnailScene 创建预览场景

// 来源: Public/ChaosFlesh/Asset/FleshAssetThumbnailScene.h
#include "ChaosFlesh/Asset/FleshAssetThumbnailScene.h"

// FFleshAssetThumbnailScene 管理预览 Actor (AFleshActor)
// 通过 SetFleshAsset() 设置要预览的 FleshAsset
// 自动计算视图矩阵参数用于缩略图渲染
```

## Demo 示例

以下展示如何创建自定义的 Flesh 资产定义类：

```cpp
// MyFleshAssetDefinition.h
#pragma once

#include "CoreMinimal.h"
#include "ChaosFlesh/Asset/AssetDefinition_FleshAsset.h"

class UMyFleshAssetDefinition : public UAssetDefinition_FleshAsset
{
    GENERATED_BODY()

    // 可以覆盖父类方法来自定义资产在编辑器中的行为
    // 例如：修改显示名称、颜色、分类等
};
```

## 模块依赖

从 `ChaosFleshEditor` 模块的代码分析，该插件依赖以下特殊模块：

| 模块 | 用途 |
|---|---|
| `ChaosFlesh` | 运行时核心模块，提供 FleshCollection 数据结构 |
| `ChaosFleshEngine` | 引擎集成模块 |
| `ChaosFleshNodes` | Dataflow 节点定义 |
| `Chaos` | Chaos Physics 物理引擎核心 |
| `Dataflow` | Dataflow 图表框架 |
| `GeometryCache` | GeometryCache 资产用于烘焙模拟结果 |
| `GeometryCollectionEngine` | 几何集合引擎（与可变形体协同工作） |
| `Slate` / `SlateCore` | 编辑器 UI 样式系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-05-12 | `981bc9da` | Dataflow: | Dataflow 框架相关更新 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理纤维场生成节点的代码 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复 MaskBuffer 中 NumMaskBuffer 的赋值错误 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃 FleshAsset 中的 StaticMesh 属性 |

### 维护评价

**活跃维护中**。ChaosFlesh 插件创建于 2022 年 3 月，是 Epic Games 在 UE5 中推进 Chaos Physics 生态系统的重要实验性组件。从近期 git 记录来看：

- **更新频率**：近期有多次连续提交（2026-05-12/13），说明仍在积极开发
- **开发方向**：正在进行代码清理（纤维场节点）、废弃旧接口（StaticMesh 属性）、修复兼容性问题
- **实验性状态**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，说明 API 可能随时变化
- **注意事项**：作为实验性插件，不建议在生产环境中依赖；`FleshAssetConversion::ImportTetFromFile` 的注释中提及相关读取功能"Currently disabled"

**推荐**：适合在实验性/研发项目中使用，用于探索软体物理模拟功能。不建议在生产环境中使用，等待 API 稳定后再考虑。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试文件）