# Water

> Full suite of water tools and rendering techniques to easily add oceans, river, lakes or custom water bodies that carve landscape and interacts with gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 水体系统 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质） |
| 模块 | `Water` (Runtime), `WaterEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Water) | |

## 用途

Water 插件为 Unreal Engine 5 提供了一套完整的水体创建、渲染和地形交互解决方案。它解决了在游戏或实时应用中快速、高效地添加逼真水体（如海洋、河流、湖泊）并使其与地形系统自动交互的核心问题。插件通过一系列编辑器工具和运行时组件，允许开发者通过绘制样条线来定义水体形状，系统会自动雕刻地形（如挖出河床）并生成相应的网格、材质和碰撞体。它集成了 Niagara 用于波浪和泡沫效果，并支持与 Landmass 插件的交互，以实现更高级的地形塑造。

## 使用场景

- 你需要在一个开放世界游戏中创建包含河流、湖泊和海洋的复杂地形水系 → 使用 Water 插件的 `AWaterBodyRiver`、`AWaterBodyLake`、`AWaterBodyOcean` Actor。
- 你希望水体能够自动雕刻地形（例如，河流流经时形成河床），而无需手动调整每个地形顶点 → 启用 Water 插件，它会通过 `AWaterBrushManager` 自动处理。
- 你需要一个统一的框架来管理不同水体的渲染、LOD、物理交互和水下后期处理效果 → Water 插件提供了 `AWaterZone` 来管理这些全局设置。
- 你希望快速原型设计或测试不同的水体波浪效果 → 可以创建 `UWaterWavesAsset` 资产，并在专门的波浪编辑器中预览。

## 蓝图用法

WaterEditor 模块主要提供编辑器侧功能和工具，运行时蓝图交互的核心类位于 `Water` 运行时模块中（未在提供资料中）。`WaterEditor` 模块提供的蓝图可调用函数主要用于编辑器调试和缓存管理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ForceUpdate` | 强制水体画刷立即更新（调试用） | `AWaterBrushManager` |
| `SingleBlurStep` | 执行单步边缘模糊（调试用） | `AWaterBrushManager` |
| `FindEdges` | 执行边缘查找算法（调试用） | `AWaterBrushManager` |
| `SingleJumpStep` | 执行单步跳跃泛洪算法（调试用） | `AWaterBrushManager` |
| `SetupDefaultMaterials` | 重置画刷材质为默认值 | `AWaterBrushManager` |
| `GetWaterBodies` | 获取此画刷影响的所有水体 Actor | `AWaterLandscapeBrush` |
| `GetActorsAffectingLandscape` | 获取所有影响此地形的水体笔刷 Actor | `AWaterLandscapeBrush` |
| `SetActorCache` | 为指定 Actor 设置缓存数据 | `AWaterLandscapeBrush` |
| `GetActorCache` | 获取指定 Actor 的缓存数据 | `AWaterLandscapeBrush` |

### 使用示例（蓝图描述）

在关卡编辑器中，当你放置一个 `WaterBodyRiver` Actor 时，它会自动在 `WaterLandscapeBrush` 中注册。你可以通过选中该 `WaterBrushManager` Actor，在其细节面板的 “Debug” 分类下，点击 “Force Update”、“Find Edges” 等按钮来实时调试水体生成过程。要查询当前场景中所有河流，可以调用 `GetWaterBodies` 节点并指定 `WaterBodyRiver` 类。

## C++ 用法

### 头文件引入

```cpp
#include “WaterEditorSubsystem.h”
#include “WaterEditorSettings.h”
```

### 基本用法（配置水体默认值）

通过 `UWaterEditorSettings` 可以在 C++ 中全局配置各类型水体的默认参数。这对于确保项目内所有新创建的水体具有一致的基础设置非常有用。

*来源文件：`WaterEditorSettings.h`*

```cpp
// 获取水体编辑器设置实例
UWaterEditorSettings* Settings = GetMutableDefault<UWaterEditorSettings>();

// 配置河流默认的画刷高度图设置
FWaterBrushActorDefaults& RiverBrushDefaults = Settings->WaterBodyRiverDefaults.BrushDefaults;
RiverBrushDefaults.HeightmapSettings.BlendMode = EWaterBrushBlendMode::AlphaBlend;
RiverBrushDefaults.HeightmapSettings.FalloffSettings.FalloffMode = EWaterBrushFalloffMode::Angle;
RiverBrushDefaults.HeightmapSettings.FalloffSettings.FalloffAngle = 45.0f;

// 为湖泊配置默认的水波资产
UWaterWavesAsset* LakeWavesAsset = LoadObject<UWaterWavesAsset>(nullptr, TEXT(“/Game/Water/DefaultLakeWaves”));
Settings->WaterBodyLakeDefaults.WaterWaves = LakeWavesAsset;
```

### 进阶用法（监听水体画刷状态变化）

`WaterEditorSubsystem` 提供了一些服务接口，虽然主要用于编辑器内部，但了解其模式有助于理解插件架构。

*来源文件：`WaterEditorSubsystem.h`*

```cpp
// 获取编辑器子系统（在编辑器模块中）
UWaterEditorSubsystem* WaterSubsystem = GEditor->GetEditorSubsystem<UWaterEditorSubsystem>();

// 检查是否有水体包被修改但未标记为脏（开发工具）
if (WaterSubsystem->HasAnyModifiedPackages())
{
    UE_LOG(LogWaterEditor, Warning, TEXT(“有水体资产已被修改但尚未保存。”));
    // 可以遍历这些包
    WaterSubsystem->ForEachModifiedPackage([](UPackage* Package) -> bool {
        UE_LOG(LogWaterEditor, Log, TEXT(“Modified Package: %s”), *Package->GetName());
        return true; // 继续遍历
    });
}
```

## Demo 示例

一个最小的编辑器子系统注册示例，展示如何使用 `WaterEditorSubsystem` 提供的服务。

```cpp
// MyWaterEditorExtensions.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "MyWaterEditorExtensions.generated.h"

UCLASS()
class UMyWaterEditorExtensions : public UEditorSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    void OnWaterBodySpawned(AActor* NewActor);
};
```

```cpp
// MyWaterEditorExtensions.cpp
#include "MyWaterEditorExtensions.h"
#include "WaterEditorSubsystem.h"
#include "Engine/World.h"
#include "Editor.h"

void UMyWaterEditorExtensions::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 监听编辑器中 Actor 的生成
    FEditorDelegates::OnMapOpened.AddUObject(this, &UMyWaterEditorExtensions::OnMapOpened);
    UE_LOG(LogTemp, Log, TEXT(“MyWaterEditorExtensions 初始化”));
}

void UMyWaterEditorExtensions::Deinitialize()
{
    FEditorDelegates::OnMapOpened.RemoveAll(this);
    Super::Deinitialize();
}

void UMyWaterEditorExtensions::OnMapOpened(const FString& Filename, bool bAsTemplate)
{
    // 在这里可以执行一些地图打开后的初始化
    UE_LOG(LogTemp, Log, TEXT(“地图已打开: %s”), *Filename);
}

void UMyWaterEditorExtensions::OnWaterBodySpawned(AActor* NewActor)
{
    // 这是一个示例回调，实际中需要连接到相应的委托
    UWaterEditorSubsystem* WaterSubsystem = GEditor->GetEditorSubsystem<UWaterEditorSubsystem>();
    if (WaterSubsystem)
    {
        // 使用子系统服务，例如尝试标记包为已修改
        UPackage* Package = NewActor->GetPackage();
        if (WaterSubsystem->TryMarkPackageAsModified(Package))
        {
            UE_LOG(LogTemp, Log, TEXT(“新水体的包已被静默标记为修改状态。”));
        }
    }
}
```

## 模块依赖

`WaterEditor` 模块依赖于 `Water` 运行时模块以及一些标准引擎模块。使用者需要在自己的模块 `Build.cs` 中添加对 `WaterEditor` 的依赖。

| 模块 | 用途 |
|---|---|
| `Water` | 运行时水体系统核心逻辑和类 |
| `Landmass` | （插件依赖）用于高级地形塑造交互 |
| `Niagara` | （插件依赖）用于水体波浪和粒子效果 |
| `GeometryProcessing` | （插件依赖）用于网格生成和处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `5fd19ba7` | [Water] Trash the old ocean collision components to free up their path names so new components will | 清理旧的海洋碰撞组件以释放路径名，便于新组件使用。 |
| 2026-05-14 | `1e201bfa` | Fix UWaterSplineMetadata parallel-curve desync when Depth, WaterVelocityScalar, or AudioIntensity ar | 修复水体样条元数据中，深度、流速标量或音频强度参数变化时，平行曲线不同步的问题。 |
| 2026-05-12 | `dc876c8f` | [Water] Restored the behavior where if a water body has an unset material and “always generate water | 恢复了当水体材质未设置且勾选“始终生成水体网格”时的行为。 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 为光线追踪添加网格批次视图，并统一网格批次所有权。 |
| 2026-05-12 | `40da2015` | Only perform the water body static mesh conservative rasterization check if the static mesh is valid | 仅在静态网格有效时，才执行水体静态网格的保守光栅化检查。 |

### 维护评价

该插件自 2020 年创建以来仍在**活跃维护**中。从近期 git 历史看，更新频繁（最近一周内有多次提交），且内容集中在功能优化、Bug 修复和一致性改进上，表明 Epic 仍在积极投入开发。虽然插件标记为“实验性”，但其功能已相当完整和稳定，是创建高质量地形水体的首选方案。**推荐在新项目中使用**，但需注意其“实验性”状态可能意味着未来 API 仍有变动的可能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Water)
- [官方文档]() （.uplugin 中未提供）