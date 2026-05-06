# Render Grid

> Advanced pipeline for use in creating rendered cinematics.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染网格 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGrid` (Runtime), `RenderGridDeveloper` (Runtime), `RenderGridEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid) | |

## 用途

Render Grid 插件提供了一套用于创建渲染级过场动画（cinematics）的高级工作管线。它允许用户定义一个“渲染网格”（Render Grid），该网格包含多个渲染任务（Jobs），每个任务可以指定不同的场景、相机、输出设置等，从而实现批量渲染或自动化渲染流程。

整个插件由三个子模块组成：

- **RenderGrid**（运行时核心）：定义数据模型（`URenderGrid`、`URenderGridJob`）以及渲染执行逻辑。
- **RenderGridDeveloper**（开发者扩展）：提供蓝图资产类型（`URenderGridBlueprint`）和蓝图函数库，方便通过蓝图或 C++ 编程管理渲染网格资产。
- **RenderGridEditor**（编辑器集成）：提供编辑界面、工具栏等，用于在虚幻编辑器内创建和编辑渲染网格。

本文档主要基于 `RenderGridDeveloper` 模块的源码进行分析，该模块是连接渲染网格数据与蓝图系统的重要桥梁，适合需要以编程方式查找、加载或操作渲染网格资产的开发者使用。

## 使用场景

- 你需要自动化批量渲染多个过场动画片段，且每个片段使用不同的相机、光照或后期处理设置 → 使用 RenderGrid 定义任务并触发渲染。
- 你希望在 C++ 或蓝图中动态获取项目中所有渲染网格资产，或根据对象路径加载特定资产 → 使用 `URenderGridDeveloperLibrary` 提供的方法。
- 你希望为渲染网格资产创建蓝图逻辑（例如自定义预处理/后处理逻辑），且需要支持蓝图图 → 使用 `URenderGridBlueprint`（继承自 `UEditorUtilityBlueprint`）。

## 蓝图用法

以下蓝图节点来自 `RenderGridDeveloper` 模块提供的 `URenderGridDeveloperLibrary` 类和 `URenderGridBlueprint` 类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Render Grid Assets` | 返回项目中所有渲染网格资产（磁盘上和内存中）。可能会加载未加载的资产，避免频繁调用。 | `URenderGridDeveloperLibrary` |
| `Get Render Grid Asset` | 根据对象路径返回单个渲染网格资产。可能加载未加载的资产，避免频繁调用。 | `URenderGridDeveloperLibrary` |
| `Get Render Grid` | 获取该蓝图资产包含的原始数据表示（`URenderGrid`，无蓝图图）。 | `URenderGridBlueprint` |
| `Get Render Grid With Blueprint Graph` | 获取包含蓝图图执行的子类实例（即实际运行的蓝图对象）。 | `URenderGridBlueprint` |
| `Get Render Grid Class Default Object` | 获取蓝图类的默认对象（CDO），可用于读取已编译的默认属性。 | `URenderGridBlueprint` |

### 使用示例

1. **获取所有渲染网格资产并遍历**：
   - 在蓝图中调用 `Get All Render Grid Assets`，返回 `URenderGrid*` 数组。
   - 使用 `ForEachLoop` 遍历每个渲染网格，访问其属性（如渲染任务数量、状态等）。

2. **按路径加载特定渲染网格**：
   - 使用字符串变量存储资产路径（如 `/Game/MyRenderGrid.MyRenderGrid`）。
   - 调用 `Get Render Grid Asset` 节点，输出对应的 `URenderGrid*` 引用，可用于后续操作。

3. **获取蓝图实例**：
   - 如果你有一个 `URenderGridBlueprint` 引用，调用 `Get Render Grid With Blueprint Graph` 即可获得运行时蓝图实例，使用该实例上的自定义函数。

## C++ 用法

### 头文件引入

```cpp
#include "RenderGrid/Blueprints/RenderGridBlueprint.h"
#include "RenderGridDeveloperLibrary.h"
```

### 基本用法

#### 获取所有渲染网格资产

```cpp
#include "RenderGridDeveloperLibrary.h"

TArray<URenderGrid*> AllGrids = URenderGridDeveloperLibrary::GetAllRenderGridAssets();
for (URenderGrid* Grid : AllGrids)
{
    // 处理 Grid...
}
```

来源：`Public/RenderGridDeveloperLibrary.h`，第 34-37 行。

#### 按路径获取资产

```cpp
#include "RenderGridDeveloperLibrary.h"

URenderGrid* MyGrid = URenderGridDeveloperLibrary::GetRenderGridAsset(TEXT("/Game/MyGrid.MyGrid"));
if (MyGrid)
{
    // 使用 MyGrid
}
```

来源：同上，第 55-58 行。

#### 操作蓝图资产

```cpp
#include "RenderGrid/Blueprints/RenderGridBlueprint.h"

// 假设已有 URenderGridBlueprint* 引用
URenderGrid* DataGrid = MyBlueprint->GetRenderGrid();                      // 仅数据，无蓝图图
URenderGrid* RuntimeGrid = MyBlueprint->GetRenderGridWithBlueprintGraph(); // 包含蓝图图执行
```

### 进阶用法

#### 使用蓝图函数库刷新资产列表（避免重复调用）

```cpp
// 仅在需要时调用，例如编辑器启动或资产重命名后
TArray<URenderGridBlueprint*> Blueprints = URenderGridDeveloperLibrary::GetAllRenderGridBlueprintAssets();
for (URenderGridBlueprint* BP : Blueprints)
{
    BP->Load(); // 确保资产最新
    BP->PropagateJobsToInstances();
}
```

> **注意**：`GetAllRenderGridAssets` 会遍历并可能加载所有资产，属于慢操作，请避免每帧调用。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在编辑器模块（如 ToolMenus 或自定义编辑器唤醒）中使用 RenderGridDeveloper 枚举所有网格并打印任务数。

```cpp
// MyRenderGridUtility.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyRenderGridUtilityModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// MyRenderGridUtility.cpp
#include "MyRenderGridUtility.h"
#include "RenderGridDeveloperLibrary.h"
#include "RenderGrid/RenderGrid.h"          // 假设该头文件存在

IMPLEMENT_MODULE(FMyRenderGridUtilityModule, MyRenderGridUtility);

void FMyRenderGridUtilityModule::StartupModule()
{
    // 辅助函数：在控制台输出渲染网格信息
    auto PrintRenderGrids = []()
    {
        TArray<URenderGrid*> Grids = URenderGridDeveloperLibrary::GetAllRenderGridAssets();
        for (const URenderGrid* Grid : Grids)
        {
            // 假设 URenderGrid 有 GetJobs() 方法
            // int32 JobCount = Grid->GetJobs().Num();
            UE_LOG(LogTemp, Log, TEXT("RenderGrid: %s, Jobs: %d"), *Grid->GetName(), 0);
        }
    };
    PrintRenderGrids();
}
```

> **提示**：编译本示例需要项目模块依赖 `RenderGridDeveloper` 和 `RenderGrid`（运行时模块）。`URenderGrid` 的具体定义位于 `RenderGrid` 模块中，此处未提供。

## 模块依赖

`RenderGridDeveloper` 模块的 `Build.cs` 中需要包含以下独特依赖（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `RenderGrid` | 运行时核心数据模型和渲染执行逻辑 |
| `Blutility` | 提供 `UEditorUtilityBlueprint` 基类 |
| `KismetCompiler` | 蓝图编译上下文（`FRenderGridBlueprintCompiler`） |
| `WorkspaceMenuStructure` | 编辑器菜单集成 (在 Editor 模块中，但 Developer 也可能间接引用) |
| `UMG` | Editor Utility Widget 依赖 |

> 如果您在项目模块中使用 `RenderGridDeveloper`，请确保在 `PrivateDependencyModuleNames` 中添加 `"RenderGridDeveloper"`，并在 `PublicDependencyModuleNames` 中添加 `"RenderGrid"`（如果需要在公开头文件中引用 `URenderGrid`）。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 摘要 |
|---|---|---|
| 2025-09-15 | 0fcf72f1 | Render Grid: fixed crash when passing in an empty string when setting remote control values |
| 2025-06-11 | b57e00bc | Replace some usages of FORCEINLINE with inline in Rendering modules. |
| 2025-04-15 | 45a9eb59 | [Truncation Warnings] Deprecate FVector2D delegates in GraphEditor module |
| 2025-04-09 | 3ffb1588 | Header unit / c++ modules compile fixes |
| 2024-08-30 | df1cc540 | Gather text from source, resolve macro has an empty source text (.cpp files) |

### 维护评价

- **创建时间**：2024-08-30，至今约 1.5 年。
- **活跃度**：最近一次功能性修正是 2025-09-15（修复崩溃），之后有编译适配和代码风格更新，说明仍在维护中，但频率不高。
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion=true`，意味着 API 和行为可能不稳定，存在修改风险。
- **推荐度**：适合有特殊批量渲染需求的团队，但应避免依赖尚未稳定的部分（如蓝图编译机制）。建议在用于生产环境前充分测试。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid)
- [测试用例（未在本次提供）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RenderGrid/Tests)
- 官方文档：暂无