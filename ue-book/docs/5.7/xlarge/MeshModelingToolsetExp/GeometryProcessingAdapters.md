# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、网格操作工具、编辑器模式等） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-29 |
| 年龄标签 | 🆕（约 <1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途

该插件是 UE5 交互式建模框架（Interactive Tools Framework）的实验性扩展集，提供了一系列高度可定制的网格创建、编辑、转换和优化工具。与核心的 `MeshModelingToolset` 相比，此插件中的模块处于早期开发阶段，包含尚未稳定的新功能（如近似 Actor、自动 UV、CubeGrid 增强等），旨在为用户和开发者提供尖端建模能力，并收集反馈以推动最终进入主插件。

**核心解决的问题：**

- 为关卡设计师和美术师提供无需离开编辑器即可快速生成和编辑 3D 网格的工具。
- 通过可脚本化的 C++ 接口，允许程序化调用高级网格处理算法（如网格自动 UV、Actor 网格近似导出）。
- 提供一个统一且可扩展的编辑器 UI 体系 (`ModelingEditorUI` / `ModelingUI`)，使自定义工具能被快速集成到建模模式中。

## 使用场景

- **关卡原型**：在构建游戏关卡时，使用 CubeGrid、MergeActor 等工具快速搭建大块几何体或合并复杂静态网格体。
- **资产优化**：使用“近似 Actor”功能将多个 Actor 自动合并并简化网格，以减少渲染 draw call。
- **程序化内容生成**：通过 C++ 调用 `IGeometryProcessing_MeshAutoUV` 接口为程序生成的网格自动计算 UV。
- **编辑器扩展开发**：基于 `ModelingUI` 模块创建自定义的建模工具 UI 面板，并挂接到已有的建模模式工作流中。
- **试验新功能**：利用实验性标记，安全地尝试不稳定的网格操作算法，并随时回退。

## 子模块概述

由于该插件包含 5 个模块，且文件数超过 150，文档分为以下子模块描述：

| 子模块 | 类型 | 功能简介 |
|---|---|---|
| `GeometryProcessingAdapters` | Runtime | 提供 `IGeometryProcessing_ApproximateActors` 和 `IGeometryProcessing_MeshAutoUV` 等接口的默认实现，将抽象网格处理操作映射到具体的 Geometry 引擎调用。 |
| `MeshModelingToolsExp` | Runtime | 包含实验性的交互工具，如 CubeGrid、MergeActor、MeshSimplify 等。核心功能类以 `UInteractiveTool` 子类形式实现。 |
| `MeshModelingToolsEditorOnlyExp` | Runtime | 仅编辑器使用的工具扩展，如 EditorOnly 的烘焙或转换辅助工具。 |
| `ModelingEditorUI` | Runtime | 建模模式的主 UI 框架，提供工具条、属性面板、模式切换等编辑器 UI 元素。 |
| `ModelingUI` | Runtime | 独立的 UI 组件库，供工具在场景中显示浮窗、按钮、滑块等，不依赖 Editor 模块。 |

## 蓝图用法

本插件主要面向 C++ 和编辑器交互层，蓝图直接暴露的功能较少。但以下节点可在蓝图调用（来自 `MeshModelingToolsExp` 模块）：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin Cube Grid Tool` | 激活立方体网格工具（实验性） | `UCubeGridToolBuilder` |
| `Begin Merge Actors Tool` | 启动合并选定 Actor 工具 | `UMergeActorsToolBuilder` |
| `Begin Approximate Actors Tool` | 启动近似 Actor 工具 | `UApproximateActorsToolBuilder` |

**注意**：这些节点通常需要配合编辑器工具上下文使用，不能在游戏运行时直接调用。

### 使用示例（蓝图描述）

1. **启动 CubeGrid 工具**  
   - 获取 `Editor Actor Subsystem`  
   - 调用 `Begin Cube Grid Tool`（输入目标 Actor）  
   - 工具激活后，可在视口拖拽生成网格。

2. **快速合并静态网格体**  
   - 选择多个静态网格 Actor  
   - 调用 `Begin Merge Actors Tool`  
   - 在弹出的对话框中配置合并参数（如纹理大小、材质简化等）。

## C++ 用法

以下用法基于 `GeometryProcessingAdapters` 模块，其余模块的 API 可参考各头文件。

### 头文件引入

```cpp
#include "GeometryProcessingAdaptersModule.h"
#include "GeometryProcessing/ApproximateActorsImpl.h"
#include "GeometryProcessing/MeshAutoUVImpl.h"
```

### 基本用法：自动 UV 生成

```cpp
// 获取模块实例
FGeometryProcessingAdaptersModule& Module = FModuleManager::LoadModuleChecked<FGeometryProcessingAdaptersModule>("GeometryProcessingAdapters");
TSharedPtr<UE::Geometry::FMeshAutoUVImpl> AutoUV = Module.GetMeshAutoUV(); // 假设此类方法存在，实际需用内部实例

// 构造默认选项
UE::Geometry::FMeshAutoUVImpl::FOptions Options = AutoUV->ConstructDefaultOptions();

// 准备 FMeshDescription（略）
FMeshDescription MeshDesc;
// ... 填充网格数据

// 执行 UV 生成
UE::Geometry::FMeshAutoUVImpl::FResults Results;
AutoUV->GenerateUVs(MeshDesc, Options, Results);

// 检查 Results.Outcome
if (Results.Outcome == EGeometryProcessingOutcome::Success)
{
    // 处理带 UV 的 MeshDesc
}
```

**来源文件**：`Source/GeometryProcessingAdapters/Public/GeometryProcessing/MeshAutoUVImpl.h`

### 进阶用法：Actor 近似

```cpp
#include "Engine/World.h"
#include "GeometryProcessing/ApproximateActorsImpl.h"

void ApproximateSelectedActors(UWorld* World, TArray<AActor*> Actors)
{
    auto& Module = FModuleManager::LoadModuleChecked<FGeometryProcessingAdaptersModule>("GeometryProcessingAdapters");
    TSharedPtr<UE::Geometry::FApproximateActorsImpl> Approx = Module.GetApproximateActors(); // 假设方法存在

    // 输入
    UE::Geometry::FApproximateActorsImpl::FInput Input;
    Input.World = World;
    Input.Actors = Actors;

    // 选项（从 FMeshApproximationSettings 构建）
    FMeshApproximationSettings Settings;
    // 自定义 Settings.MaterialMergeSettings 等
    auto Options = Approx->ConstructOptions(Settings);

    // 输出
    UE::Geometry::FApproximateActorsImpl::FResults Results;
    Approx->ApproximateActors(Input, Options, Results);

    if (Results.Outcome == EGeometryProcessingOutcome::Success && Results.GeneratedStaticMeshes.Num() > 0)
    {
        // 结果中的 StaticMesh 将被生成到内容浏览器或直接返回
    }
}
```

**注意**：`FGeometryProcessingAdaptersModule` 的 public 访问器尚未在提供头文件中暴露，实际使用时需从模块内部获取私有实例或直接构造具体实现类。更稳健的方式是直接使用 `IGeometryProcessing_ApproximateActors` 接口通过 `IModuleInterface` 查询。

## Demo 示例

以下是一个完整的插件模块示例，演示如何通过 C++ 在编辑器模式下启动 Actor 近似工具并获取结果。

### ApproxActorToolDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FApproxActorToolDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    void RunActorApproximation(UWorld* World, const TArray<AActor*>& SelectedActors);
};
```

### ApproxActorToolDemo.cpp

```cpp
#include "ApproxActorToolDemo.h"
#include "GeometryProcessingAdaptersModule.h"
#include "GeometryProcessing/ApproximateActorsImpl.h"
#include "Engine/World.h"
#include "Engine/StaticMeshActor.h"

IMPLEMENT_MODULE(FApproxActorToolDemoModule, ApproxActorToolDemo);

void FApproxActorToolDemoModule::StartupModule()
{
    // 注册编辑器命令等（略）
}

void FApproxActorToolDemoModule::ShutdownModule()
{
}

void FApproxActorToolDemoModule::RunActorApproximation(UWorld* World, const TArray<AActor*>& SelectedActors)
{
    if (!World || SelectedActors.Num() == 0) return;

    // 加载模块并获取实现（策略：通过 IGeometryProcessing_ApproximateActors）
    FGeometryProcessingAdaptersModule& GPModule = FModuleManager::LoadModuleChecked<FGeometryProcessingAdaptersModule>("GeometryProcessingAdapters");
    // 注意：GPModule 的公共接口未暴露，此处应通过 IModuleInterface 的 GetImplementation 方式，但为演示直接创建
    UE::Geometry::FApproximateActorsImpl ApproxImpl;

    // 构建输入
    UE::Geometry::FApproximateActorsImpl::FInput Input;
    Input.World = World;
    Input.Actors = SelectedActors;

    // 使用默认设置构造选项
    FMeshApproximationSettings DefaultSettings;
    auto Options = ApproxImpl.ConstructOptions(DefaultSettings);

    // 执行
    UE::Geometry::FApproximateActorsImpl::FResults Results;
    ApproxImpl.ApproximateActors(Input, Options, Results);

    // 输出结果
    if (Results.Outcome == EGeometryProcessingOutcome::Success)
    {
        UE_LOG(LogTemp, Log, TEXT("Approximation succeeded. Generated %d static meshes."), Results.GeneratedStaticMeshes.Num());
        // 可将生成的网格添加到场景或保存到包
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Approximation failed."));
    }
}
```

**说明**：此示例为概念性演示，实际使用需根据模块 API 版本调整。生产环境中建议通过 `Tool` 对象或 `UInteractiveToolManager` 启动内置工具。

## 模块依赖

以下为 `MeshModelingToolsetExp` 各模块的显著依赖（省略基础 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `GeometryFramework` | 提供基础几何体数据类型（`FDynamicMesh3`、`FMeshDescription` 等） |
| `GeometryProcessingInterfaces` | 定义抽象接口（如 `IGeometryProcessing_ApproximateActors`） |
| `MeshModelingToolset` | 依赖基础建模工具集的核心类和框架（`UInteractiveTool`） |
| `ModelingComponents` | 提供共享建模工具组件（如 `UPolygroupLayersProperties`） |
| `InteractiveToolsFramework` | 交互工具框架的基础运行时支持 |

## 维护状态

### 近期更新

- 2025-12-18 `79bdb336` — #jira UE-356302（修复问题）
- 2025-11-18 `e352ab23` — 修复将多个动态网格源转换为静态网格体时的崩溃（建模模式转换）
- 2025-10-03 `fea318f1` — PR #13360: 向立方体网格工具添加“分配并开始新”键盘命令
- 2025-10-03 `53d4840d` — ModelingTools: 修复 CubeGrid “接受并开始新”操作在编辑已存在 Actor 时不工作
- 2025-09-29 `300d2503` — Merge Actor - Approximate: 使用正确的合并材质以避免显示默认引擎纹理

### 维护评价

- **活跃度**：最近 3 个月内（截至 2025-12-18）有多次功能性修复和增强，项目处于**活跃开发**状态。
- **稳定性**：由于是实验性插件（`IsExperimentalVersion = true`），API 可能随时变化，部分功能存在已知 bug（如材质合并问题）。
- **推荐度**：对于需要前沿建模功能的开发者/工作室，可以谨慎使用并准备好出现不兼容更新。对于生产项目，建议等待功能迁移至核心 `MeshModelingToolset` 后再使用。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/modeling-mode-in-unreal-engine/)（建模模式通用文档，本插件为扩展部分）
- [测试用例（部分）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp/Tests)