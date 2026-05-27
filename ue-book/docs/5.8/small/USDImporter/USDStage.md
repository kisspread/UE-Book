# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为 Unreal Engine 提供了对 Pixar Universal Scene Description (USD) 文件格式的全面支持。其核心功能远超简单的“导入”，它允许你在 UE 编辑器中直接打开一个 `.usd`、`.usda` 或 `.usdc` 文件，并将其作为“舞台 (Stage)”进行实时查看和交互。插件会将 USD 层级结构（Prims）转换为 UE 中对应的 Actor 和组件（如 StaticMeshComponent, SkeletalMeshComponent 等），并管理它们的生命周期、动画、材质以及与 USD 世界的双向同步。它解决了在数字内容创作（DCC）工具和游戏引擎之间进行资产交换和场景管理的核心痛点，特别是为影视、动画和虚拟制片工作流提供了强大的支持。

## 使用场景

- **影视/动画资产审阅**：你正在制作一部使用 USD 流水线的动画电影，需要将整个场景（包括资产、灯光、动画）直接拖入 UE 中进行实时预览、光照测试或虚拟摄像机操作。
- **虚拟制片**：在虚拟制片现场，美术总监或导演希望实时调整由 DCC 工具（如 Houdini, Maya）生成的 USD 场景布局（例如移动一棵树），并立即在 UE 的最终渲染视图中看到效果。
- **程序化内容生成**：你的技术美术使用 Houdini 等工具通过 USD 描述了复杂的程序化场景（如建筑群、地形植被），你需要将这个“描述”作为 UE 中的一个动态生成和管理的对象。
- **资产管线集成**：你的资产管线以 USD 作为主要交换格式，你需要将经过部门审核通过的 USD 资产（包含复杂的材质和动画）“导入”或“链接”到 UE 项目中，而不是进行破坏性的 FBX 转换。

## 蓝图用法

插件的核心蓝图交互对象是 `AUsdStageActor`。它提供了一套完整的蓝图节点来控制 USD 舞台的加载、查询和状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRootLayer` | 设置要加载的 USD 文件路径。 | `AUsdStageActor` |
| `SetStageState` | 控制舞台的打开、加载和关闭状态。 | `AUsdStageActor` |
| `SetTime` | 设置舞台当前的动画时间，以驱动 TimeCode 动画。 | `AUsdStageActor` |
| `GetGeneratedComponent` | 根据 USD Prim 路径（如 `"/root/my_mesh"`）获取其生成的 UE 组件。 | `AUsdStageActor` |
| `GetGeneratedAssets` | 根据 USD Prim 路径获取其生成的 UE 资产（如 UStaticMesh）。 | `AUsdStageActor` |
| `GetSourcePrimPath` | 根据一个 UE 组件或资产，反向查询其源 USD Prim 路径。 | `AUsdStageActor` |
| `SetRenderContext` | 设置用于解析 USD 材质的渲染上下文（如 `“unreal”`, `“glslfx”`）。 | `AUsdStageActor` |
| `SetMaterialPurpose` | 设置解析 USD 材质绑定时使用的目的（如 `“allPurpose”`）。 | `AUsdStageActor` |
| `SetKindsToCollapse` | 设置根据哪些 Prim 类型（如模型组）来自动合并子 Prim。 | `AUsdStageActor` |
| `GetLevelSequence` | 获取由 USD 动画自动生成的主 LevelSequence 资产。 | `AUsdStageActor` |

### 使用示例（蓝图描述）

1.  **打开一个 USD 文件**：
    - 在关卡中拖入一个 `AUsdStageActor`。
    - 使用 `Set Root Layer` 节点，将其 `RootFilePath` 参数连接到你的 `.usd` 文件路径。
    - 使用 `Set Stage State` 节点，将其设置为 `EUsdStageState::OpenedAndLoaded`。此时舞台将被加载，USD 场景将出现在世界大纲视图中。

2.  **控制动画播放**：
    - 使用 `Get Level Sequence` 节点获取生成的动画序列。
    - 使用 `Set Sequence` 节点将此序列连接到一个 `Level Sequence Player` 或通过 Sequencer 面板打开。
    - 使用 `Set Time` 节点，结合一个 `Timeline` 节点，即可在蓝图中实时驱动 USD 动画的播放。

3.  **交互式查询**：
    - 在鼠标点击事件中，获取被点击的 Actor。
    - 将其输入到 `Get Source Prim Path` 节点，即可在屏幕上显示或调试该 UE 对象对应的 USD 原始路径。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageActor.h" // 核心舞台Actor
#include "USDLevelSequenceHelper.h" // 动画序列管理
#include "USDPrimTwin.h" // USD Prim 与 UE 对象的映射关系
```

### 基本用法

在 C++ 中，你可以程序化地创建和控制 `AUsdStageActor`，这在制作工具或自动化管线时非常有用。
（*来源: Public/USDStageActor.h*）

```cpp
// 假设在某个 Actor 或 GameMode 中
#include "USDStageActor.h"
#include "Kismet/GameplayStatics.h"

void AMyToolActor::LoadUsdScene(const FString& UsdFilePath)
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 在指定位置生成一个 USD Stage Actor
    FActorSpawnParameters SpawnParams;
    AUsdStageActor* StageActor = World->SpawnActor<AUsdStageActor>(FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);

    if (StageActor)
    {
        // 设置 USD 文件路径并打开舞台
        StageActor->SetRootLayer(UsdFilePath);
        StageActor->SetStageState(EUsdStageState::OpenedAndLoaded);

        // 监听舞台加载完成的事件
        StageActor->OnStageLoaded.AddLambda([this, StageActor]()
        {
            // 舞台加载完成后，可以获取其 LevelSequence
            ULevelSequence* Sequence = StageActor->GetLevelSequence();
            if (Sequence)
            {
                UE_LOG(LogTemp, Log, TEXT("USD Animation Sequence loaded: %s"), *Sequence->GetName());
            }
        });
    }
}
```

### 进阶用法

结合 `FUsdLevelSequenceHelper` 和 `UUsdPrimTwin`，可以进行更底层的控制。
（*来源: Public/USDLevelSequenceHelper.h, Public/USDPrimTwin.h*）

```cpp
// 获取舞台 Actor 的内部 USD 舞台句柄和动画助手
if (StageActor)
{
    // 获取底层 USD 舞台对象（轻量级句柄）
    const UE::FUsdStage& Stage = StageActor->GetUsdStage();

    // 获取根 PrimTwin（UE 对象树的根）
    UUsdPrimTwin* RootTwin = StageActor->GetRootPrimTwin();
    if (RootTwin)
    {
        // 遍历所有 USD Prim 对应的 UE 对象树
        RootTwin->Iterate([](UUsdPrimTwin& PrimTwin)
        {
            // 打印每个 Prim 的路径和它对应的 UE SceneComponent
            USceneComponent* Comp = PrimTwin.GetSceneComponent();
            UE_LOG(LogTemp, Log, TEXT("USD Prim '%s' mapped to Component: %s"),
                *PrimTwin.PrimPath,
                Comp ? *Comp->GetName() : TEXT("None"));
        }, /*bRecursive=*/ true);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何在 GameMode 中实例化并使用 USD Stage Actor。
（*.h 文件省略，仅展示 .cpp 实现*）

```cpp
// MyGameMode.h
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class AUsdStageActor;
class ULevelSequence;

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    virtual void StartPlay() override;

    UPROPERTY(BlueprintReadOnly, Category="USD")
    TObjectPtr<AUsdStageActor> CurrentStageActor;

    UFUNCTION(BlueprintCallable, Category="USD")
    void OpenUsdFile(const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category="USD")
    void CloseCurrentUsdFile();
};

// MyGameMode.cpp
#include "MyGameMode.h"
#include "USDStageActor.h"
#include "Kismet/GameplayStatics.h"

void AMyGameMode::StartPlay()
{
    Super::StartPlay();
    // 可以在此处自动打开一个测试USD文件
    // OpenUsdFile(TEXT("/Game/MyAssets/Scene.usda"));
}

void AMyGameMode::OpenUsdFile(const FString& FilePath)
{
    CloseCurrentUsdFile(); // 关闭之前的舞台

    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    CurrentStageActor = GetWorld()->SpawnActor<AUsdStageActor>(AUsdStageActor::StaticClass(), SpawnParams);

    if (CurrentStageActor)
    {
        CurrentStageActor->SetRootLayer(FilePath);
        CurrentStageActor->SetStageState(EUsdStageState::OpenedAndLoaded);
        UE_LOG(LogTemp, Display, TEXT("Opened USD Stage: %s"), *FilePath);
    }
}

void AMyGameMode::CloseCurrentUsdFile()
{
    if (CurrentStageActor)
    {
        // 将舞台状态设为关闭，这会卸载所有生成的资产和组件
        CurrentStageActor->SetStageState(EUsdStageState::Closed);
        CurrentStageActor->Destroy();
        CurrentStageActor = nullptr;
    }
}
```

## 模块依赖

要使用此插件（尤其是 USDStage 模块），你的项目模块需要链接其依赖。由于 USDImporter 是一个复杂的集成插件，它依赖于一系列内部和第三方模块。

| 模块 | 用途 |
|---|---|
| `USDClasses` | 提供 USD 与 UE 之间转换的通用类型和工具函数。 |
| `UnrealUSDWrapper` | 对 Pixar USD 库的底层 C++ 封装，是插件与 USD 交互的基石。 |
| `LevelSequence` | 用于处理由 USD 动画生成的 UE 动画序列。 |
| `Sequencer` | 用于在编辑器中展示和编辑上述动画序列。 |
| `GeometryCache` | 用于处理 USD 的点云或网格缓存动画。 |
| `MovieScene` | Sequencer 的核心，用于表示序列数据结构。 |
| `UniversalObjectLocator` | 用于在 Sequencer 中定位 USD 生成的动态对象（参见 `FUsdPrimLocatorFragment`）。 |
| `PropertyEditor`, `DetailsCustomization` | 用于自定义 `AUsdStageActor` 在细节面板中的显示（编辑器依赖）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转浮点数导致的编译器警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD支持：新增为骨骼网格分配非蓝图依赖的Control Rig功能。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD支持：解决更新至26.03版本后，LOD变化时AnimQuery内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位格式说明符与64位参数不匹配的问题，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD支持：烘焙“曝光”动画轨道的所有帧。 |

### 维护评价

**USD Importer 处于积极维护状态。** 作为 Epic Games 为影视和虚拟制片工作流投入的关键插件，它保持着定期更新。从最近的提交记录看（截至2026年4月、5月），更新集中在功能增强（如 Control Rig 集成）和与新引擎版本/API（如 26.03 AnimQuery）的兼容性修复上。尽管其历史较长（约8年），但近期活动表明它并非“僵尸”代码，而是作为官方支持的核心工具在持续演进。插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它虽然功能强大，但可能尚未达到完全稳定的“正式版”状态，用户需要手动启用。**对于需要 USD 集成的影视、虚拟制片项目，强烈推荐使用并关注其更新。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- 官方文档：未在 .uplugin 中提供，通常可在 Unreal Engine 官方文档的“USD”相关章节找到。
- 测试用例：`Source/USDTests/` 目录下可能包含相关测试代码。