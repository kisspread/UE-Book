# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD（Universal Scene Description）是 Pixar 推出的开放场景格式，广泛应用于电影、动画、游戏等行业的资产交换与管线集成。本插件将 USD 格式的导入能力引入 Unreal Engine，支持将 USD 舞台（Stage）及其内部的几何体、材质、动画、骨骼、摄像机、灯光等元素转换为 UE 的原生资产（Static Mesh、Skeletal Mesh、Animation、Level Sequence、Material 等）。

核心模块 `USDStage` 提供了 USD 舞台在 UE 中的运行时管理能力，包括：
- 以 `AUsdStageActor` 作为舞台容器，动态加载、卸载 USD 文件。
- 自动构建出与舞台层级对应的 `UUsdPrimTwin` 层级树，并生成对应的 Scene Component。
- 将 USD 的时间动画自动映射为 UE 的 Level Sequence，支持子序列、Control Rig 绑定。
- 支持 Undo/Redo、多用户协作（ConcertSync）等编辑器交互。
- 提供信息缓存（`FUsdInfoCache`）和 Prim 链接缓存（`FUsdPrimLinkCache`），优化重复查询性能。

## 使用场景

- 在 VFX 或动画制作管线中，将 Maya/Houdini 等 DCC 工具导出的 USD 文件一键导入到 UE，用于预览或最终渲染。
- 需要将 USD 舞台中的动态物体（如角色动画、粒子变形）实时同步到 UE 的时间线，以便与其他关卡序列混合。
- 在多用户协作编辑环境下，多个美术同时修改 USD 文件，通过 `UUsdTransactor` 自动记录变更到事务缓冲区，实现 Undo/Redo 和场景同步。
- 在运行时或编辑器内动态切换不同的 USD 文件（如同一个场景的不同镜头），通过 `AUsdStageActor` 的 `RootLayer` 属性热加载。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResolveWithStageActor` | 根据舞台演员、Prim 路径等参数，解析 Sequencer 动态绑定应指向的 Actor 或 Component | `UUsdDynamicBindingResolverLibrary` |
| `Set Root Layer` | 设置 USD 主文件路径（`FFilePath`），舞台会自动加载该文件 | `AUsdStageActor` |
| `Set Stage State` | 控制舞台状态：`Closed`、`Opened`、`OpenedAndLoaded` | `AUsdStageActor` |
| `Get Asset Cache` | 获取当前关联的 `UUsdAssetCache3` 对象，用于管理缓存的资产 | `AUsdStageActor` |
| `Get Info Cache`（内部对象） | 获取 `UUsdInfoCache`，可读取舞台中 Prim 的快速缓存数据 | `AUsdStageActor`（通过属性暴露） |

### 使用示例（蓝图描述）

1. **加载 USD 文件并播放动画**  
   - 在关卡中放置一个 `AUsdStageActor`（蓝图生成）。  
   - 在 BeginPlay 时，设置其 `Root Layer` 为 USD 文件路径。  
   - 将 `Stage State` 设为 `OpenedAndLoaded`。  
   - 自动生成的 Level Sequence 将出现在世界大纲中，可以将其嵌入主 Sequence 播放。

2. **动态解析 Sequencer 绑定**  
   - 在 Sequencer 中为某个轨道添加动态绑定，使用 "Evaluator" 绑定库。  
   - 调用 `ResolveWithStageActor`，传入舞台演员的 ID Name（或留空），并指定 Prim 路径，返回绑定的 Actor/Component。

## C++ 用法

### 头文件引入

```cpp
#include "USDStageModule.h"
#include "USDStageActor.h"
#include "USDLevelSequenceHelper.h"
#include "USDPrimTwin.h"
```

### 基本用法

**创建舞台演员并加载 USD 文件**（参考测试用例 `Engine/Plugins/Importers/USDImporter/Source/USDTests/Private/USDTests.cpp`）

```cpp
// 在世界中生成舞台演员
AUsdStageActor* StageActor = World->SpawnActor<AUsdStageActor>();
StageActor->SetRootLayer(FFilePath{ TEXT("/Game/MyAssets/myScene.usd") });
StageActor->SetStageState(EUsdStageState::OpenedAndLoaded);
```

**遍历 Prim 层级树**

```cpp
// 通过 PrimTwin 访问舞台中的 Prim
UUsdPrimTwin* RootTwin = StageActor->GetRootUsdTwin(); // 注意实际 API 名可能为 GetRootUsdTwin
RootTwin->Iterate([](UUsdPrimTwin& Twin)
{
    USceneComponent* Comp = Twin.GetSceneComponent();
    UE_LOG(LogTemp, Log, TEXT("Prim: %s -> Component: %s"), *Twin.PrimPath, *GetNameSafe(Comp));
}, true);
```

**使用 LevelSequenceHelper 手动管理动画**

```cpp
FUsdLevelSequenceHelper& Helper = StageActor->GetLevelSequenceHelper(); // 假定存在访问器
ULevelSequence* MainSeq = Helper.Init(StageActor->GetUsdStage()); // 传入 UE::FUsdStage
Helper.AddPrim(*PrimTwinNode, false);
```

### 进阶用法

**使用 FUsdPrimLocatorFragment 实现 UE 通用对象定位器**（参考 `USDLocatorFragments.h`）

```cpp
// 注册定位器片段，可通过 PrimPath 快速从舞台中找到对应对象
FUsdPrimLocatorFragment Fragment;
Fragment.PrimPath = TEXT("/cube");
Fragment.bPreferComponent = true;
// 在 Sequencer 中使用该片段解析绑定
UE::UniversalObjectLocator::FResolveResult Result = Fragment.Resolve(Params);
```

**事务支持与多用户同步**

```cpp
// UUsdTransactor 自动集成到舞台演员
StageActor->GetTransactor()->Initialize(StageActor);

// 当 USD 舞台发生变更时，变更数据会被序列化到事务缓冲区
// 撤销 / 重做时会自动应用到舞台
```

## Demo 示例

以下是一个最小示例，展示如何在 C++ 中加载 USD 舞台并获取 Prim 的 SceneComponent。

**MyActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "USDStageActor.h"
#include "MyActor.generated.h"

UCLASS()
class AMYPROJECT_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "USD")
    FFilePath UsdFilePath;

private:
    AUsdStageActor* LoadedStageActor = nullptr;
};
```

**MyActor.cpp**

```cpp
#include "MyActor.h"
#include "Engine/World.h"
#include "USDPrimTwin.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    UWorld* World = GetWorld();
    if (!World) return;

    // 生成舞台演员
    LoadedStageActor = World->SpawnActor<AUsdStageActor>();
    LoadedStageActor->SetRootLayer(UsdFilePath);
    LoadedStageActor->SetStageState(EUsdStageState::OpenedAndLoaded);

    // 获取根 PrimTwin 并输出其 SceneComponent
    UUsdPrimTwin* RootTwin = LoadedStageActor->GetRootUsdTwin(); // 实际 API 可能不同
    if (RootTwin)
    {
        USceneComponent* Comp = RootTwin->GetSceneComponent();
        if (Comp)
        {
            UE_LOG(LogTemp, Log, TEXT("Root SceneComponent: %s"), *Comp->GetName());
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | 底层 USD C++ 库的 UE 封装，提供 `UE::FUsdStage`、`UE::FUsdPrim` 等核心类型 |
| `USDClasses` | USD 导入 / 导出的公共数据结构与配置 |
| `USDSchemas` | USD Schema 解析与转换逻辑（几何体、材质、骨骼等） |
| `LevelSequence` | 用于管理从 USD 动画生成的关卡序列 |
| `MovieScene` | Sequencer 核心框架，支持轨道、绑定等 |
| `UniversalObjectLocator` | 通用对象定位器机制，`FUsdPrimLocatorFragment` 在此基础上实现 Prim 解析 |
| `GeometryCache` | 如果启用了几何缓存导入，依赖此模块 |

## 维护状态

### 近期更新

- 2025-10-22 a1039b21 — USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 be609b71 — [Backout] - CL47041219
- 2025-10-17 7ab79237 — USD: Disabled UE allocator in USD for Windows.
- 2025-10-03 d887bd60 — USD: Use the default collision profile for generated static meshes.
- 2025-10-01 b4449c58 — Anim In Engine: Fix broken linked anim sequences.

### 维护评价

该插件创建于 2025-10-01，至今约 1 个月，仍处于非常积极的开发阶段。近期更新包括对 Windows 平台分配器的修复、碰撞 profile 的默认设置优化，以及动画序列修复。整体代码质量较高，模块划分清晰，并提供了事务系统、多用户支持等企业级功能。**推荐使用**，但需要注意其仍标记为 `IsBetaVersion=true`，API 可能在未来版本中调整。如果追求长期稳定，建议持续关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/importing-and-exporting-usd-files-in-unreal-engine/)（USD 导入通用指南）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests)