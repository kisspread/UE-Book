# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试蓝图函数） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为 Unreal Engine 提供了对 Universal Scene Description (USD) 文件格式的完整导入支持。USD 是由皮克斯开发的一种用于高效描述、交换和协作处理3D场景的文件格式，已成为影视、特效和游戏行业的重要标准。本插件的核心作用是打通虚幻引擎与其它数字内容创作工具（如 Maya、Houdini、Blender 等）之间的资产流转通道，允许用户直接导入包含复杂场景结构、材质、动画和几何缓存的 USD 文件。通过将 USD 的强大场景描述能力与虚幻引擎的实时渲染和交互性能相结合，它极大地提升了虚拟制片、实时渲染和大型场景管理的工作流程。

## 使用场景

-   **影视与虚拟制片**：你需要从其他DCC软件（如Maya）将包含分层材质、角色动画和场景布局的USD场景导入到虚幻引擎中，用于实时渲染和虚拟拍摄。
-   **游戏资产管线**：你的美术团队使用Houdini等工具生成程序化资产（如地形、建筑群），并希望通过USD格式将它们批量、无损地导入到虚幻引擎项目中。
-   **协同工作与版本控制**：你需要使用USD的“图层”功能来管理不同团队（如灯光、特效、动画）对同一个复杂场景的修改，并将这些修改实时同步到虚幻引擎中。
-   **几何缓存播放**：你制作了高精度的角色动画或流体模拟缓存（存储为USD几何缓存格式），并需要在引擎中以高性能播放。

## 蓝图用法

> **重要提示**：提供的当前模块 `USDTests` 主要包含内部测试函数，且均标记为已弃用（Deprecated）。插件更核心的蓝图API（如用于控制 USD Stage、导入设置的节点）很可能位于 `USDStage`, `USDStageImporter` 等其他模块中，当前分析未提供这些模块的详细头文件。以下信息仅基于已提供的测试模块代码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RecompileBlueprintStageActor` | （测试用）重新编译蓝图化的 Stage Actor。 | `UUSDTestsBlueprintLibrary` |
| `GetSubtreeVertexCount` | （测试用）获取指定 Prim 子树的顶点总数。 | `UUSDTestsBlueprintLibrary` |
| `GetSubtreeMaterialSlotCount` | （测试用）获取指定 Prim 子树的材质槽总数。 | `UUSDTestsBlueprintLibrary` |
| `SetUsdStageCpp` | （测试用）设置 Stage Actor 的 USD 根图层路径。 | `UUSDTestsBlueprintLibrary` |
| `ClearTransactionHistory` | （测试用）清除编辑器事务历史记录。 | `UUSDTestsBlueprintLibrary` |

### 使用示例（蓝图描述）

由于提供的节点均为已弃用的测试函数，**不建议在正式项目中使用**。预期的典型工作流程蓝图节点（例如 `ImportUSDFile`, `CreateUsdStageActor` 等）应位于 `USDStage` 或 `USDStageImporter` 模块中，需要参考插件其他模块的文档或源码。通常，使用流程是：
1.  使用 “Open Stage” 或 “Import” 类节点加载一个 `.usd` / `.usda` 文件。
2.  获取或创建一个 `AUsdStageActor`，它代表了整个USD舞台。
3.  通过 `AUsdStageActor` 的蓝图接口（如 `SetRootLayer`, `TraverseStage`, `GetPrimInfo`）来检查和操作导入的USD场景结构。

## C++ 用法

### 头文件引入

```cpp
#include “USDTestsBlueprintLibrary.h” // 仅用于演示已弃用的测试API
// 实际项目应引入对应功能模块的头文件，如 “UsdStage.h”, “UsdStageImporter.h” 等
```

### 基本用法

以下示例来自 `USDTestsBlueprintLibrary`，展示了几个测试函数的调用方式。**请注意：这些API已标记为弃用，仅作原理演示。**

```cpp
// 案例：获取Stage Actor某个Prim子树的顶点数量（用于性能测试）
// 来源：Engine/Plugins/Importers/USDImporter/Source/USDTests/Public/USDTestsBlueprintLibrary.h
AUsdStageActor* MyStageActor = /* 获取或创建一个USD Stage Actor */;
FString PrimPath = TEXT(“/World/MyMesh”);

// 注意：此函数已弃用，内部可能使用UUsdStage接口获取信息
int64 VertexCount = UUSDTestsBlueprintLibrary::GetSubtreeVertexCount(MyStageActor, PrimPath);
UE_LOG(LogTemp, Log, TEXT(“Prim %s 子树的顶点总数为: %lld”), *PrimPath, VertexCount);
```

### 进阶用法

虽然没有提供完整示例，但基于模块结构可以推断，更高级的用法涉及 `USDStage` 模块。以下是一个概念性的代码片段，展示如何通过C++与USD Stage交互（**非真实代码，为逻辑示意**）：

```cpp
// 概念性示例：通过USDStage模块遍历场景
#include “UsdStage.h” // 假设的头文件

// 获取或创建一个UsdStage对象
TSharedRef<FUsdStage> UsdStage = MakeShared<FUsdStage>();
if (UsdStage->Open(“D:/MyScene.usd”))
{
    // 使用UsdStage API遍历所有Prim
    UsdStage->Traverse([&](const FUsdPrim& Prim)
    {
        UE_LOG(LogTemp, Log, TEXT(“找到Prim: %s, 类型: %s”), *Prim.GetPath(), *Prim.GetTypeName());

        // 检查是否为网格体
        if (Prim.IsA(TEXT(“Mesh”)))
        {
            // 获取几何数据等（此处需要 UsdGeom 模块支持）
            // ...
        }
        return true; // 继续遍历
    });
}
```

## Demo 示例

以下是一个最小化的、展示如何获取测试模块中已弃用API的代码示例。**请注意，此示例仅用于结构演示，不推荐在生产环境使用。**

```cpp
// USDImporterTest.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “USDImporterTest.generated.h”

UCLASS()
class MYPROJECT_API AUSDImporterTest : public AActor
{
    GENERATED_BODY()

public:
    AUSDImporterTest();

    UFUNCTION(BlueprintCallable, Category = “USD Test (Deprecated)”)
    void RunDeprecatedTest(AUsdStageActor* StageActor);

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// USDImporterTest.cpp
#include “USDImporterTest.h”
#include “USDTestsBlueprintLibrary.h” // 包含已弃用测试函数的库

AUSDImporterTest::AUSDImporterTest()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AUSDImporterTest::BeginPlay()
{
    Super::BeginPlay();
    UE_LOG(LogTemp, Warning, TEXT(“AUSDImporterTest BeginPlay: USD Tests are deprecated.”));
}

void AUSDImporterTest::RunDeprecatedTest(AUsdStageActor* StageActor)
{
    if (StageActor)
    {
        // 调用已弃用的测试函数
        FString TestPrimPath = TEXT(“/World”);
        int64 VertCount = UUSDTestsBlueprintLibrary::GetSubtreeVertexCount(StageActor, TestPrimPath);
        UE_LOG(LogTemp, Warning, TEXT(“%s 顶点数 (Test): %lld (Note: Function is deprecated)”),
               *TestPrimPath, VertCount);

        // 另一个弃用函数
        UUSDTestsBlueprintLibrary::ClearTransactionHistory();
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“RunDeprecatedTest: StageActor is null!”));
    }
}
```

## 模块依赖

根据插件的模块结构（USDStage, USDSchemas, USDStageImporter等），要使用此插件的核心功能（如USD Stage管理、场景遍历），你的项目模块需要依赖以下独特模块。常见模块如 Core, Engine 等已省略。

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 AUsdStageActor 和核心的 USD Stage 管理功能，是操作导入场景的主要接口。 |
| `USDStageImporter` | 包含实际的 USD 文件导入逻辑和工厂类，负责将 USD 数据转换为虚幻资产。 |
| `USDSchemas` | 定义 USD Prim 类型（如 Mesh, Light, Camera）到虚幻引擎类型（如 UStaticMesh, ULightComponent）的映射规则。 |
| `GeometryCacheUSD` | 实现 USD 几何缓存（如 Alembic 替代品）的导入和播放支持。 |
| `USDExporter` | 提供将虚幻场景或资产导出为 USD 文件的功能（反向流程）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：添加对分配独立于蓝图的控制骨骼的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD var… | USD：解决更新到26.03版本后，当使用LOD变体时导致AnimQuery内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了当参数为64位时32位格式说明符，反之亦然的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

USD Importer 插件创建于 2018 年，历史较长，是一个“老古董”级别的工具。从最近的 Git 提交记录来看，该插件**仍在积极维护中**。最近的更新（截至 2026 年）主要集中在：
1.  **功能增强**：如添加控制骨骼支持、完整烘焙曝光动画。
2.  **兼容性与稳定性修复**：解决新版 USD（26.03）集成带来的问题、修复编译警告和格式说明符错误。
3.  **底层优化**：修复浮点精度警告。

尽管插件标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明 Epic 可能认为其稳定性和 API 完整性尚在打磨中，但持续的维护表明它是一个重要且受支持的模块。**推荐在需要 USD 工作流的项目中使用**，但需注意其 Beta 状态，部分 API（如测试函数）可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/usd-in-unreal-engine/) （假设的通用 USD 文档链接，.uplugin 未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) （基于提供的模块路径）