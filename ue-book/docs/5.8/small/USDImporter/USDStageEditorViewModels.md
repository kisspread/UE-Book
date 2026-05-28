# USD Importer

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD Stage、蓝图资产、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为 Unreal Engine 提供了完整的 USD (Universal Scene Description) 工作流支持，用于导入、编辑和导出 USD 文件格式。它解决了游戏和影视制作中不同数字内容创建工具（DCC，如 Maya、Houdini）之间的资产交换问题，允许用户直接在 Unreal Engine 中使用 USD 资产，而无需进行格式转换或重新构建。

## 使用场景

- **影视与虚拟制片**：从 Maya 或 Houdini 导入复杂的 USD 角色和场景，在 UE 中进行实时渲染和编辑。
- **跨部门协作**：美术团队在 DCC 工具中创建 USD 资产，技术团队在 UE 中利用 USDStage 进行动态加载和变体管理。
- **程序化生成**：通过 UE 的蓝图或 C++ 脚本动态加载和操作 USD 阶段，实现运行时场景构建。
- **资产管线自动化**：作为资产导入管线的一部分，批量导入 USD 文件并自动设置材质、LOD 等。

## 蓝图用法

USDStageEditorViewModels 模块主要提供编辑器 UI 的数据模型，本身不暴露蓝图节点。核心的蓝图 API 集中在 `USDStage` 和 `USDStageImporter` 模块中。以下是其他模块中常见的蓝图节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenStage` | 从文件路径打开一个 USD 阶段 | `AUsdStageActor` |
| `SaveStage` | 保存当前 USD 阶段 | `AUsdStageActor` |
| `ImportStage` | 将当前 USD 阶段作为资产导入到 UE 项目 | `AUsdStageActor` |
| `SetLoadAllRule` / `SetLoadNoneRule` | 设置 USD 负载的加载规则 | `AUsdStageActor` |
| `GetPrimInfo` | 获取指定 USD Prim 的信息（类型、属性等） | `UUsdPrimInfoFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **打开并显示一个 USD 文件**：
    *   在关卡中放置一个 `AUsdStageActor`。
    *   使用 `OpenStage` 节点，将文件路径连接到该 Actor。
    *   USD 阶段中的几何体会自动转换为 UE 的 StaticMesh 或 SkeletalMesh 并在关卡中渲染。
2.  **使用变体集**：
    *   获取一个 USD Prim 的 `VariantSets`。
    *   使用 `SetVariantSelection` 节点选择一个变体，场景会根据所选变体动态更新。

## C++ 用法

### 头文件引入

```cpp
#include "USDStage.h"
#include "UsdWrappers/UsdStage.h"
#include "UsdWrappers/UsdPrim.h"
```

### 基本用法

以下示例演示了如何在 C++ 中打开一个 USD 阶段并遍历其根 Prim 的子级。

```cpp
// 来源：Engine/Plugins/Importers/USDImporter/Source/USDTests/Private/USDImporterTests.cpp
void OpenAndTraverseUSDStage()
{
    // 获取一个 USD 阶段（通常从 AUsdStageActor 获取）
    UE::FUsdStage UsdStage = UE::FUsdStage::Open(TEXT("/Game/USD/MyScene.usd"));
    if (!UsdStage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD stage"));
        return;
    }

    // 获取根 Prim
    UE::FUsdPrim RootPrim = UsdStage.GetPseudoRoot();
    if (RootPrim)
    {
        // 遍历所有直接子 Prim
        for (const UE::FUsdPrim& ChildPrim : RootPrim.GetChildren())
        {
            UE_LOG(LogTemp, Log, TEXT("Child Prim: %s, Type: %s"),
                *ChildPrim.GetName(),
                *ChildPrim.GetTypeName().ToString());
        }
    }
}
```

### 进阶用法

以下示例展示了如何使用 `FUsdStageViewModel` 来管理 USD 阶段的导入流程。

```cpp
// 来源：Engine/Plugins/Importers/USDImporter/Source/USDStageEditorViewModels/Public/USDStageViewModel.h
#include "USDStageViewModel.h"
#include "UsdStageActor.h"

void ImportUSDStageViaViewModel(AUsdStageActor* StageActor)
{
    FUsdStageViewModel ViewModel;
    ViewModel.UsdStageActor = StageActor;

    // 1. 打开一个外部 USD 文件
    ViewModel.OpenStage(TEXT("C:/Assets/Character.usd"));

    // 2. 设置加载规则（例如：全部加载）
    ViewModel.SetLoadAllRule();

    // 3. 将当前阶段导入到 UE 的 /Game/USD_Imports/ 目录
    ViewModel.ImportStage(TEXT("/Game/USD_Imports/"), nullptr);
}
```

## Demo 示例

一个使用 `FUsdPrimViewModel` 在编辑器中查询 Prim 信息的最小示例。

```cpp
// MyUSDPrimQuery.h
#pragma once

#include "CoreMinimal.h"
#include "USDPrimViewModel.h"

class FMyUSDPrimQuery
{
public:
    static void LogPrimHierarchy(const UE::FUsdStageWeak& UsdStage, const UE::FUsdPrim& RootPrim, int32 Depth = 0);
};
```

```cpp
// MyUSDPrimQuery.cpp
#include "MyUSDPrimQuery.h"

void FMyUSDPrimQuery::LogPrimHierarchy(const UE::FUsdStageWeak& UsdStage, const UE::FUsdPrim& RootPrim, int32 Depth)
{
    if (!RootPrim)
    {
        return;
    }

    // 创建一个 ViewModel 来查询 Prim 信息
    FUsdPrimViewModel PrimViewModel(nullptr, UsdStage, RootPrim);

    // 获取数据模型
    const TSharedRef<FUsdPrimModel>& PrimModel = PrimViewModel.RowData;

    // 打印信息
    FString Indent = FString::ChrN(Depth * 4, TEXT(' '));
    UE_LOG(LogTemp, Log, TEXT("%sPrim: %s, Type: %s, Visible: %s, Loaded: %s"),
        *Indent,
        *PrimModel->GetName().ToString(),
        *PrimModel->GetType().ToString(),
        PrimModel->IsVisible() ? TEXT("Yes") : TEXT("No"),
        PrimModel->IsLoaded() ? TEXT("Yes") : TEXT("No"));

    // 递归遍历子 Prim
    TArray<FUsdPrimViewModelRef>& Children = PrimViewModel.UpdateChildren();
    for (const FUsdPrimViewModelRef& Child : Children)
    {
        LogPrimHierarchy(UsdStage, Child->UsdPrim, Depth + 1);
    }
}
```

## 模块依赖

该插件模块（`USDStageEditorViewModels`）依赖于 USD 核心库和 Unreal 自身的 USD 封装层。使用者需要确保 USD 库可用。

| 模块 | 用途 |
|---|---|
| `USDSchemas` | 提供 USD Schema 的定义和操作 |
| `USDStage` | 提供 USD 阶段（Stage）的核心操作和数据结构 |
| `USDClasses` | 提供 USD 相关的 UObject 类定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数时的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 添加支持，允许分配独立于蓝图的控制绑定（Control Rig）。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD: 针对 26.03 更新导致动画查询（AnimQuery）在 LOD 切换时内部引用失效的问题提供变通方案。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串说明符：当参数为64位时使用64位说明符，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光动画轨道的所有帧。 |

### 维护评价

该插件**仍在活跃维护中**。尽管创建于约 6 年前，但其 GitHub 提交记录显示，在最近几个月（2026年4月至今）仍有持续的、实质性的功能更新和 bug 修复。最新的提交集中在动画、控制绑定和编译器警告修复上，表明 Epic 仍在积极开发和改进此插件。

然而，需要注意以下几点：
1.  **实验性状态**：插件的 `.uplugin` 文件中 `IsBetaVersion: true`，并且默认未启用（`EnabledByDefault: false`）。这意味着它可能尚未经过全面的生产环境验证，API 可能在未来版本中发生变化。
2.  **复杂性**：该插件包含多个模块和大量源文件，对于初学者来说学习曲线较陡峭。
3.  **USD 库依赖**：其正常运行依赖于特定版本的 OpenUSD 库。

**推荐**：对于需要 USD 工作流的专业项目（如影视、虚拟制片），推荐在生产环境中谨慎试用此插件，并密切关注引擎更新日志。对于简单的资产导入，可以等待其正式转为稳定版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)