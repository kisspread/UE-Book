# USD Importer

> Adds support for importing the USD file format into Unreal Engine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

本插件为 Unreal Engine 提供了对 Pixar USD (Universal Scene Description) 文件格式的完整支持。它不仅仅是一个简单的文件导入器，更是一个完整的 USD 场景编辑、交互和同步框架。其核心功能是允许用户将 USD 文件作为“舞台（Stage）”在 UE 内部直接打开、查看和修改，并能将修改实时或批量写回 USD 文件。这解决了影视、虚拟制片和工业可视化领域中，艺术家需要在 DCC 工具（如 Maya、Houdini）与 UE 之间高效交换复杂、分层、动画化的 3D 场景资产的核心痛点。

## 使用场景

-   你正在使用 **虚拟制片** 流程，需要将 DCC 软件中建立的复杂场景（包含灯光、摄像机、材质和动画）实时同步到 UE 中的 LED 墙后。
-   你是一个 **动画师**，需要在 Sequencer 中直接编辑 USD 资产内的关键帧动画，并将这些编辑保存回 USD 文件。
-   你需要处理由多个部门或软件生成的、分层引用的 USD 资产，并希望在 UE 中作为一个整体进行管理和预览。
-   你的工作流要求资产在 UE 中保持与源 USD 文件的 **动态链接**，当 USD 文件更新时，UE 内的资产可以同步更新。

## 蓝图用法

搜索 `UFUNCTION(BlueprintCallable)` 和 `UPROPERTY(BlueprintReadWrite)`，核心功能集中在 `AUsdStageActor` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRootLayer` | 设置要打开的 USD 根文件路径。 | `AUsdStageActor` |
| `SetStageState` | 控制 USD 舞台的状态（打开、加载等）。 | `AUsdStageActor` |
| `SetUsdAssetCache` | 指定用于存储生成资产的缓存对象。 | `AUsdStageActor` |
| `SetInitialLoadSet` | 设置舞台初始加载哪些类型的 Prim。 | `AUsdStageActor` |
| `SetRenderContext` | 指定解析材质时使用的渲染上下文。 | `AUsdStageActor` |
| `GetGeneratedComponent` | 根据 Prim 路径获取其生成的对应 UE 组件。 | `AUsdStageActor` |
| `GetGeneratedAssets` | 根据 Prim 路径获取其生成的对应 UE 资产。 | `AUsdStageActor` |
| `GetSourcePrimPath` | 根据一个 UE 对象，反向查询其来源的 USD Prim 路径。 | `AUsdStageActor` |
| `SetIsolatedRootLayer` | 进入或退出子图层隔离模式，只显示和编辑指定的子图层。 | `AUsdStageActor` |
| `SetTime` | 设置 USD 舞台当前的评估时间码，用于查看动画。 | `AUsdStageActor` |
| `GetLevelSequence` | 获取由 USD 动画生成的主 LevelSequence 资产。 | `AUsdStageActor` |
| `SetPurposesToLoad` | 通过位掩码指定只加载具有特定 Purpose 的 Prim。 | `AUsdStageActor` |
| `SetSubdivisionLevel` | 设置细分曲面的细分级别。 | `AUsdStageActor` |

### 使用示例（蓝图描述）

1.  **基础导入与查看**：在关卡中放置一个 `AUsdStageActor`。在“细节”面板或通过蓝图，调用 `SetRootLayer` 节点，输入你的 USD 文件路径（如 `“/path/to/scene.usd”`）。然后调用 `SetStageState` 并设置为 `OpenedAndLoaded`。场景将被解析，对应的 UE 组件（StaticMeshComponent、SkeletalMeshComponent 等）会自动在 Stage Actor 下生成。
2.  **动画回放**：在 `AUsdStageActor` 的“细节”面板中，找到 `Time` 属性并拖动滑块，或使用蓝图 `SetTime` 节点传入不同的时间值，即可预览 USD 文件中的动画。其内部会自动生成并关联一个 `ULevelSequence`。
3.  **查询与交互**：使用 `GetGeneratedComponent` 节点，传入一个 Prim 路径（如 `“/root/character”`），即可获得代表该 Prim 的 `USceneComponent`，然后可以对该组件进行移动、旋转等操作。反之，使用 `GetSourcePrimPath` 可以知道某个被操作的组件来源于哪个 USD Prim。
4.  **高级配置**：通过 `SetPurposesToLoad` 可以仅加载 `proxy` 或 `guide` 类型的 Prim，用于快速预览。通过 `SetRenderContext` 可以指定使用 `“unreal”` 或 `“mdl”` 等特定上下文的着色器来解析材质。

## C++ 用法

重点从提供的头文件中提取，贴近官方用法。

### 头文件引入

```cpp
#include "USDStageActor.h"
#include "USDStageModule.h"
#include "USDLevelSequenceHelper.h"
```

### 基本用法

最基本的操作是通过模块接口获取或查找 `AUsdStageActor`，然后调用其方法。
*(来源: `Public/USDStageModule.h`)*

```cpp
// 获取或查找当前世界中的 USD Stage Actor
IUsdStageModule& StageModule = FModuleManager::Get().LoadModuleChecked<IUsdStageModule>(TEXT("USDStage"));
AUsdStageActor* StageActor = StageModule.FindUsdStageActor(MyWorld);
if (StageActor)
{
    // 打开一个新的 USD 文件
    StageActor->SetRootLayer(TEXT("/Content/MyScene.usd"));
    StageActor->SetStageState(EUsdStageState::OpenedAndLoaded);
}
```

### 进阶用法

可以直接操作 `AUsdStageActor` 提供的 USD 舞台句柄和内部助手类，进行更精细的控制。
*(来源: `Public/USDStageActor.h`)*

```cpp
// 获取底层的 USD Stage 对象进行直接操作
UE::FUsdStage& UsdStage = StageActor->GetOrOpenUsdStage();
// 获取动画序列助手，管理 LevelSequence 生成
const FUsdLevelSequenceHelper& SeqHelper = StageActor->GetLevelSequenceHelper(); // 假设有此访问器
// 获取 Prim 链接缓存，查询生成的资产
UUsdPrimLinkCache* LinkCache = StageActor->PrimLinkCache;
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个自定义的 Actor，内部包含一个 USD Stage Actor 并管理其生命周期。

### MyUsdControllerActor.h
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyUsdControllerActor.generated.h"

class AUsdStageActor;

UCLASS()
class AMyUsdControllerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyUsdControllerActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable)
    void LoadUSDScene(const FString& InUsdFilePath);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "USD")
    TObjectPtr<AUsdStageActor> ControlledStageActor;

    UPROPERTY(Transient)
    TObjectPtr<UUsdAssetCache3> AssetCache;
};
```

### MyUsdControllerActor.cpp
```cpp
#include "MyUsdControllerActor.h"
#include "USDStageActor.h"
#include "USDAssetCache3.h"
#include "Engine/World.h"

AMyUsdControllerActor::AMyUsdControllerActor()
{
    PrimaryActorTick.bCanEverTick = false;
    AssetCache = CreateDefaultSubobject<UUsdAssetCache3>(TEXT("USDAssetCache"));
}

void AMyUsdControllerActor::BeginPlay()
{
    Super::BeginPlay();
    // 在运行时动态生成一个 USD Stage Actor
    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = this;
    ControlledStageActor = GetWorld()->SpawnActor<AUsdStageActor>(SpawnParams);
    if (ControlledStageActor)
    {
        // 将我们预先创建的资产缓存赋给它
        ControlledStageActor->SetUsdAssetCache(AssetCache);
    }
}

void AMyUsdControllerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (ControlledStageActor)
    {
        ControlledStageActor->Destroy();
        ControlledStageActor = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

void AMyUsdControllerActor::LoadUSDScene(const FString& InUsdFilePath)
{
    if (ControlledStageActor && !InUsdFilePath.IsEmpty())
    {
        ControlledStageActor->SetRootLayer(InUsdFilePath);
        ControlledStageActor->SetStageState(EUsdStageState::OpenedAndLoaded);
    }
}
```

## 模块依赖

从 `USDStage.Build.cs` 和其关联模块推断，要使用此插件的完整功能，你的模块需要依赖以下核心模块。

| 模块 | 用途 |
|---|---|
| `USDSchemas` | 包含用于解析各种 USD Schema（如 Mesh、SkelAnimation）的翻译器，是导入逻辑的核心。 |
| `USDClasses` | 定义 USD 相关的通用数据结构、枚举和工具类。 |
| `UnrealUSDWrapper` | 封装了底层 USD C++ SDK 的 UE 接口层。 |
| `USDStage` | 包含 `AUsdStageActor` 及其相关的核心逻辑，是使用 USD 舞台功能的主要入口模块。 |
| `USDStageImporter` | 处理将 USD Stage 导入为 UE Level 或 LevelSequence 资产的逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：支持分配与蓝图无关的 Control Rig。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD values are updated. | USD：解决更新到 26.03 后，在 LOD 值更新时导致 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了 32 位格式说明符与 64 位参数不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

**活跃维护**。该插件自 2018 年创建，历史悠久，但近期（2026 年）仍有持续且实质性的功能更新（如支持 Control Rig、动画烘焙改进）和问题修复。虽然 `.uplugin` 中标记为 `IsBetaVersion: true`，表明其 API 和功能可能还不稳定，但其持续的更新频率证明 Epic 在积极开发和维护它。

**推荐使用**：对于有 USD 格式交互需求的专业流程（如影视虚拟制片），此插件是 UE 官方提供的、功能最全面的解决方案，推荐在明确其“实验性”状态的前提下使用。对于简单的资产一次性导入，也可以使用更轻量的 FBX/glTF 方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]() (待补充，可参考 Epic 官方文档站点或相关技术博客)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)