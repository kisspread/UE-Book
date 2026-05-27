# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产， 测试资源） |
| 模块 | `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDSchemas` (Runtime), `USDTests` (Runtime), `GeometryCacheUSD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为 Unreal Engine 提供了全面的 USD (Universal Scene Description) 工作流支持。它远不止一个简单的“导入器”，而是一个完整的 USD 场景管理工具集。其核心功能包括：
*   **USD 场景加载与管理**：通过 `AUsdStageActor` 在场景中加载和管理 USD 文件，并支持蓝图派生。
*   **资产转换与导入**：将 USD 中的几何体、材质、动画等资产转换为 Unreal Engine 原生资产（如 StaticMesh、SkeletalMesh、Material）。
*   **场景层级同步**：维护 USD 代（prim）与 Unreal 引擎 Actor 之间的双向同步关系。
*   **USD 原生数据操作**：提供低层级的 API 用于查询和修改 USD 文件中的层（layer）、代（prim）、属性（attribute）。
*   **几何缓存支持**：提供 `GeometryCacheUSD` 模块，用于处理 USD 中的几何体动画。

简而言之，它解决了在游戏引擎中直接使用和交互 USD 生态资产的复杂问题，是影视动画管线与游戏开发流程之间的桥梁。

## 使用场景

*   你正在参与一个需要与 Maya、Houdini 等 DCC 工具紧密协作的影视或动画项目 → 使用本插件直接在 Unreal 编辑器中查看、编辑和同步 USD 场景。
*   你需要导入包含复杂材质图和动画序列的 USD 资产 → 使用 `USDStageImporter` 进行自动化或交互式导入。
*   你需要在运行时动态加载和显示 USD 数据（例如用于建筑可视化或 VR 应用） → 使用 `USDStage` 模块的运行时功能。
*   你需要将 Unreal 场景或资产导出为 USD 格式以供其他软件使用 → 使用 `USDExporter` 模块。

## 蓝图用法

**重要提示**：当前 `USDTests` 模块中暴露的所有蓝图函数均已标记为 `UE_DEPRECATED`，并明确说明仅供内部测试使用。它们**不应用于产品开发**，且将在未来版本中移除。

核心蓝图功能通常通过 `AUsdStageActor` 及其派生类（蓝图或C++）来访问。以下是常见的蓝图交互点：

### 核心节点（基于模块功能推测）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateUSDStageActor` | 在场景中创建并返回一个 USD Stage Actor。 | `USDStageBlueprintLibrary` (推测) |
| `ImportUSDStage` | 触发将当前 Stage Actor 管理的 USD 数据导入为 UE 资产。 | `AUsdStageActor` (推测) |
| `SetRootLayer` | 更改 Stage Actor 加载的 USD 根层文件。 | `AUsdStageActor` (推测) |
| `SetPrimVisibility` | 控制特定 USD Prim 在场景中的可见性。 | `AUsdStageActor` (推测) |
| `GetPrimProperty` | 获取指定 USD Prim 的属性值。 | `UsdPrim` (推测) |

### 使用示例（蓝图描述）

1.  **创建并加载 USD 文件**：
    *   从 `Place Actors` 面板拖入一个 `Usd Stage Actor` 到场景。
    *   在 Actor 的 `Details` 面板中，设置 `Root Layer` 属性为你的 `.usd` 或 `.usda` 文件路径。
    *   或者，通过蓝图调用 `CreateUSDStageActor` 节点，然后使用 `SetRootLayer` 节点动态指定文件。

2.  **触发资产导入**：
    *   获取到 `Usd Stage Actor` 的引用后，调用其 `ImportStage` 或类似功能的蓝图节点，这将启动一个导入任务，将 USD 数据转换为 UE 资产。

## C++ 用法

虽然 `USDTests` 模块的函数已被废弃，但其测试代码仍能展示核心 `USDSchemas` 和 `USDStage` 模块的 C++ 用法模式。

### 头文件引入

```cpp
#include "USDStageActor.h"
#include "USDStage.h"
#include "UsdPrim.h"
```

### 基本用法

以下示例展示了如何以编程方式与 `AUsdStageActor` 和 USD 交互。
*(示例模式源自 `USDTests` 模块中的废弃测试函数)*

```cpp
// 假设已有对 AUsdStageActor 的引用 StageActor
if (StageActor)
{
    // 1. 更改加载的 USD 根层文件
    // 注意：原测试函数名为 SetUsdStageCpp，但更通用的方法可能是通过 Stage 接口
    if (Usd::IUsdStage* Stage = StageActor->GetStage())
    {
        Stage->SetRootLayerPath(TEXT("/Game/MyAssets/new_asset.usda"));
    }

    // 2. 获取特定 Prim 的子树顶点数（用于资源分析）
    // 注意：以下函数 GetSubtreeVertexCount 已被废弃
    // int64 VertexCount = USDTestsBlueprintLibrary::GetSubtreeVertexCount(StageActor, TEXT("/MyModel/Geometry"));

    // 3. 操作 USD 原始数据（需要 USDSchemas 知识）
    UsdPrim RootPrim = Stage->GetPseudoRoot();
    UsdPrim MyPrim = RootPrim.GetChild(TEXT("SomePrim"));
    if (MyPrim.IsValid())
    {
        UsdAttribute MyAttr = MyPrim.GetAttribute(TEXT("my:custom:attr"));
        if (MyAttr.HasValue())
        {
            // 获取属性值...
        }
    }
}
```

### 进阶用法

结合 `USDExporter` 和 `USDSchemas` 模块，可以实现更复杂的管线操作，例如：

```cpp
// 创建一个自定义的 USD 属性 Schema
// 需要包含 #include "UsdAttribute.h" 和相关 Schema 头文件
// UsdAttribute NewAttr = MyPrim.CreateAttribute(TEXT("MyAttribute"), SdfValueTypeNames->Bool);
// NewAttr.Set(true);
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何创建一个 Stage Actor 并在其蓝图中加载 USD 文件。
*(注：实际创建和管理 Actor 通常在编辑器工具或 GameMode 中完成)*

**USDDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "USDDemoActor.generated.h"

class AUsdStageActor;

UCLASS()
class YOURPROJECT_API AUSDDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AUSDDemoActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "USD")
    AUsdStageActor* USDStage;

    virtual void BeginPlay() override;
};
```

**USDDemoActor.cpp**
```cpp
#include "USDDemoActor.h"
#include "USDStageActor.h" // 需要依赖 USDStage 模块

AUSDDemoActor::AUSDDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AUSDDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        // 在运行时动态生成一个 USD Stage Actor
        FActorSpawnParameters SpawnParams;
        SpawnParams.Owner = this;
        USDStage = World->SpawnActor<AUsdStageActor>(SpawnParams);

        if (USDStage)
        {
            // 假设 USD 文件位于 Content 目录下
            USDStage->SetRootLayerPath(TEXT("/Game/USD/test_scene.usda"));
            // 通常还需要触发 Stage 的初始解析和场景对象生成
        }
    }
}
```

## 模块依赖

要使用此插件的功能，你的项目模块通常需要依赖以下核心 USD 模块（基于模块功能和常见 UE 插件依赖模式）：

| 模块 | 用途 |
|---|---|
| `USDStage` | 核心运行时模块，提供 USD Stage Actor 和 Stage 管理功能。 |
| `USDSchemas` | 提供 C++ API 用于直接操作 USD Prim、Attribute、Relationship 等底层数据。 |
| `USDClasses` | 提供在 Editor 和 Runtime 中通用的 USD 相关类和工具。 |
| `USDExporter` | 提供将 UE 场景和资产导出为 USD 格式的功能。 |

*注意：具体依赖哪些模块取决于你使用插件的哪部分功能。例如，仅做运行时加载可能只需 `USDStage`；而进行深度 USD 数据操作则需要 `USDSchemas`。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 增加对蓝图无关控制骨骼的分配支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD: 针对26.03更新导致动画查询内部引用在LOD变化时失效的问题提供变通方案。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位格式说明符与64位参数不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光动画轨道的所有帧。 |

### 维护评价

*   **活跃维护**：插件仍在积极更新，最近的提交集中在2026年4月至5月，内容涉及新功能（控制骨骼支持）、问题修复（浮点警告、格式说明符）和针对上游USD版本变更的适配。
*   **成熟但仍在演进**：自2018年创建以来已有约8年历史，是一个成熟的大型模块。其架构完整，功能丰富，但仍在随着USD标准和UE需求进行功能增强和优化。
*   **实验性状态**：尽管活跃维护，但插件的 `.uplugin` 文件仍标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`。这意味着它可能尚未达到 Epic Games 的“生产就绪”标准，API 有可能变动，或某些功能需要更全面的稳定性测试。
*   **推荐使用**：对于在生产管线中必须使用USD的项目，它是UE官方提供的、功能最全面的选择。但使用者需要接受其“实验性”标签，并做好应对API调整和可能存在的边缘问题的心理准备。对于仅需基础USD导入的小型项目，可考虑更轻量的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/working-with-universal-scene-description-usd-in-unreal-engine/) (通用指南)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)