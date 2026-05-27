# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 肉体模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、测试资源） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 插件旨在为 Unreal Engine 提供基于 Chaos 物理系统的**可变形体（Deformable Body）模拟**，特别是针对**软组织、肌肉、布料等生物或有机材料**的实时模拟。它不是一个传统的刚体物理插件，而是专注于**体积变形**和**非线性材料行为**。

其核心在于使用**四面体（Tetrahedral）网格**来表示物体的体积结构，并通过 **Dataflow（数据流图）** 来驱动模拟的初始化、材料定义和求解过程。这使得艺术家和技术美术能够在编辑器中以可视化、非破坏性的方式构建复杂的物理模拟管线。

插件存在是为了填补 UE 原生物理系统在高级变形模拟方面的空白，常用于电影预览、角色特殊效果（如肌肉膨胀、皮肤撕裂）、物理玩具或需要高度动态物体的游戏场景。

## 使用场景

- 你在制作一个需要表现角色肌肉收缩、膨胀或撕裂效果的过场动画或实时游戏 → 使用 ChaosFlesh 驱动骨骼网格体的变形。
- 你正在为一个软体物理玩具（如可挤压的橡胶玩具）创建原型 → 使用 ChaosFlesh 的四面体网格和材料属性模拟其弹性。
- 你需要在电影或动画项目中，为数字角色（如怪物、外星生物）添加基于物理的皮肤褶皱和脂肪抖动效果 → 结合 ChaosFlesh 和缓存系统。
- 你正在研究生物力学或需要可视化应力分析（如骨骼受力） → 使用其调试渲染功能查看内部四面体结构和向量场。

## 蓝图用法

由于此插件的核心功能（`ChaosFlesh` 模块）主要通过 Dataflow 和 C++ API 暴露，纯粹的 `BlueprintCallable` 函数相对有限。主要交互点集中在资产操作和模拟控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FleshComponent` (属性访问) | 作为 Actor 的组件，持有对 `FleshAsset` 的引用和模拟参数。 | `UFleshComponent` |
| `ChaosDeformableSolver` (资产) | 定义求解器的参数（重力、迭代次数等）。这是一个可蓝图实例化的资产。 | `UChaosDeformableSolver` |

### 使用示例（蓝图描述）

1.  **创建模拟物体**:
    *   从内容浏览器创建一个 `FleshAsset`（肉体资产），导入你的四面体网格或通过 Dataflow 节点生成。
    *   将 `FleshComponent` 添加到场景中的一个 Actor 上。
    *   在该 `FleshComponent` 的细节面板中，设置其 `FleshAsset` 属性为你创建的资产。
    *   （可选）创建一个 `ChaosDeformableSolver` 资产并将其分配给 `FleshComponent`，以自定义求解参数。

2.  **触发模拟**:
    *   模拟通常在编辑器内通过“模拟”按钮或游戏运行时自动开始。`FleshComponent` 会根据其资产中的 Dataflow 图进行初始化和求解。

## C++ 用法

注意：以下示例基于对公共头文件的分析，展示了访问和扩展 ChaosFlesh 功能的典型模式。

### 头文件引入

```cpp
#include "ChaosFlesh/ChaosFleshEditorPlugin.h"
#include "ChaosFlesh/Cmd/ChaosFleshCommands.h"
#include "ChaosFlesh/Asset/AssetDefinition_FleshAsset.h"
```

### 基本用法

作为编辑器插件，`ChaosFleshEditor` 提供了命令行工具和资产自定义。

```cpp
// 在编辑器控制台或通过代码调用命令
void SomeEditorFunction(UWorld* World)
{
    // 1. 调用内置命令，例如查找长宽比异常的四面体
    TArray<FString> Args;
    Args.Add(TEXT("MaxAR"));
    Args.Add(TEXT("100.0"));
    FChaosFleshCommands::FindQualifyingTetrahedra(Args, World);

    // 2. 创建几何缓存（需要正确的组件设置）
    TArray<FString> CacheArgs;
    CacheArgs.Add(TEXT("FrameRate"));
    CacheArgs.Add(TEXT("30"));
    FChaosFleshCommands::CreateGeometryCache(CacheArgs, World);
}
```
*（示例来源于 `Public/ChaosFlesh/Cmd/ChaosFleshCommands.h`）*

### 进阶用法

扩展 `ChaosFleshEditor` 的功能，例如注册自定义的 Dataflow 可渲染类型。

```cpp
#include "ChaosFleshRendering/FleshFiberFieldRenderableType.h"

// 在模块启动时注册自定义的纤维场渲染设置
void RegisterMyFleshRenderers()
{
    UE::Flesh::Private::RegisterFleshFiberFieldRenderableTypes();
    // 其他自定义渲染器注册...
}
```
*（示例来源于 `Private/ChaosFleshRendering/FleshFiberFieldRenderableType.h`）*

## Demo 示例

一个最小化的 C++ 类，用于演示如何在编辑器中访问 `ChaosFleshEditor` 模块并查询其可用性。

```cpp
// MyFleshHelper.h
#pragma once
#include "CoreMinimal.h"

class FMyFleshHelper
{
public:
    static void CheckChaosFleshEditorAvailability();
};
```

```cpp
// MyFleshHelper.cpp
#include "MyFleshHelper.h"
#include "ChaosFlesh/ChaosFleshEditorPlugin.h"

void FMyFleshHelper::CheckChaosFleshEditorAvailability()
{
    if (IChaosFleshEditorPlugin::IsAvailable())
    {
        UE_LOG(LogTemp, Log, TEXT("ChaosFleshEditor 插件已加载，样式集可用。"));
        // 可以获取编辑器样式用于自定义UI
        // const ISlateStyle* Style = IChaosFleshEditorPlugin::GetEditorStyle();
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("ChaosFleshEditor 插件未加载。"));
    }
}
```

## 模块依赖

从 `ChaosFleshEditor` 模块的 `Build.cs` 分析，要使用此编辑器插件，你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `GeometryCollectionEditor` | 提供几何体集合资产的编辑器支持和细节自定义，与 ChaosFlesh 的资产编辑功能紧密相关。 |
| `DataflowEditor` | 提供 Dataflow（数据流图）编辑器的核心框架和节点 UI，ChaosFlesh 依赖它来实现其模拟管线的可视化编辑。 |
| `ChaosFlesh` | ChaosFlesh 的核心运行时模块，包含 `FleshCollection` 等数据结构。 |
| `ChaosFleshEngine` | ChaosFlesh 的引擎集成和模拟求解核心。 |
| `Chaos` | Chaos 物理系统的核心库。 |
| `ChaosSolverEngine` | Chaos 求解器引擎，管理物理模拟的执行。 |
| `Dataflow` | Dataflow 节点图运行时库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `981bc9da` | Dataflow: | 数据流相关更新（具体信息不完整）。 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理肉体纤维场生成节点代码。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复掩码缓冲区赋值错误。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 废弃肉体资产中的 StaticMesh 属性。 |

### 维护评价

**实验性且活跃维护中**。

该插件创建于 2022 年 3 月，作为一项实验性功能，其代码仍在持续更新。从最近的提交记录（2026年5月）来看，维护集中在**代码质量提升、Bug 修复和功能清理**上，例如修复编译警告、废弃冗余属性、优化节点等。这表明 Epic Games 的团队仍在关注和打磨此插件，尽管没有进行大规模的新功能开发。

**主要限制与风险**：
1.  **实验性**：`IsExperimentalVersion=true`，API 和功能可能会发生破坏性更改，不建议用于关键的生产环境项目。
2.  **复杂度**：依赖 Dataflow 系统和多个物理模块，入门门槛和调试难度较高。
3.  **默认禁用**：`EnabledByDefault=false`，需要手动在项目设置中启用。

**推荐使用**：如果你正在从事**电影预演、高级技术原型研究或非核心玩法的特殊效果开发**，并且愿意接受实验性代码的不稳定性，可以尝试使用。对于寻求稳定物理解决方案的主流程游戏项目，应谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)
- 官方文档：无
- 测试用例：用户提供的信息中未包含测试文件路径，可能需要进一步查找 `Engine/Tests/` 或插件内部目录。