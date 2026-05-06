# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置模板） |
| 模块 | `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageImporter` (Runtime), `USDExporter` (Runtime), `USDClassesEditor` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDTests` (Runtime), `GeometryCacheUSD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 是一个完整的、基于 Pixar USD（通用场景描述） 的导入/导出框架。它允许用户：

- 将 `.usd`、`.usda`、`.usdc`、`.usdz` 等文件导入到 Unreal Engine，并转换为静态网格体、Skeletal Mesh、动画、材质、光照等。
- 将 Unreal 内容导出为 USD 格式，以便与其他 DCC 工具（如 Maya、Houdini、Katana）互操作。
- 在编辑器内通过 **USD Stage Editor** 面板实时查看和操作 USD 舞台。
- 使用 **Geometry Cache USD** 模块将 USD 中的动画网格缓存数据作为 Geometry Cache 播放。

本插件是实验性功能，需要手动启用（`EnabledByDefault = false`），并且仍处于 Beta 阶段（`IsBetaVersion = true`）。

## 使用场景

- **跨 DCC 工具管线**：在 Maya 中制作动画，导出为 USD，在 Unreal 中直接导入并烘焙材质，无需 FBX 中间格式。
- **大型场景引用**：将复杂的外景或建筑模型以 USD 引用方式组织，通过分层加载实现按需流送。
- **离线模拟数据播放**：将物理模拟或流体模拟输出的顶点动画缓存为 USD，在 Unreal 中用 Geometry Cache 回放。
- **多语言协作**：通过 USD 的变体（Variants）和图层（Layers）实现多版本对比与快速迭代。

## 蓝图用法

`GeometryCacheUSD` 模块为蓝图提供了 **UGeometryCacheTrackUsd** 类，它继承自 `UGeometryCacheTrack`，并标记为 `BlueprintType`。因此，你可以在蓝图中创建或引用该类的实例，但**没有公开的 BlueprintCallable 函数**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| *（无公开蓝图函数）* | 本模块所有 API 均为 C++ 接口，蓝图端仅能通过 Geometry Cache 组件间接使用。 | - |

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheTrackUSD.h"
#include "GeometryCacheUSDComponent.h"
#include "GeometryCacheUSDStream.h"
```

### 基本用法

创建一个 `UGeometryCacheTrackUsd` 并关联到 USD 舞台中的某个 Prim（几何体），然后将其添加到 `UGeometryCache` 中。

```cpp
// 来源：Engine/Plugins/Importers/USDImporter/Source/GeometryCacheUSD/Private/GeometryCacheTrackUSD.cpp
// 简化示例

UE::FUsdStage Stage = UnrealUSDWrapper::OpenStage(TEXT("C:/MyScene.usda"));
if (!Stage)
{
    return;
}

// 找到目标 Prim（如 /Root/Mesh）
FString PrimPath = TEXT("/Root/Mesh");

// 创建 Track
UGeometryCacheTrackUsd* Track = NewObject<UGeometryCacheTrackUsd>();
Track->Initialize(
    Stage,
    PrimPath,
    0,       // StartFrameIndex
    100,     // EndFrameIndex
    FReadUsdMeshFunction::CreateLambda([](const TWeakObjectPtr<UGeometryCacheTrackUsd>, float Time, FGeometryCacheMeshData& OutMeshData) -> bool
    {
        // 自定义读取逻辑（通常由 USDImporter 内部提供）
        return true;
    })
);

// 将 Track 添加到 GeometryCache
UGeometryCache* Cache = NewObject<UGeometryCache>();
Cache->AddTrack(Track);
```

### 进阶用法

使用 `UGeometryCacheUsdComponent` 直接在场景中播放上述 Geometry Cache：

```cpp
// 创建 Component 并附加到 Actor
UGeometryCacheUsdComponent* CacheComp = NewObject<UGeometryCacheUsdComponent>(MyActor);
CacheComp->RegisterComponent();
CacheComp->SetGeometryCache(Cache);
CacheComp->SetPlaybackSpeed(24.0f);
CacheComp->Play();
```

## Demo 示例

以下是一个最小化 C++ 示例，在游戏世界启动时自动从 USD 文件加载并播放 Geometry Cache。

**AMyUSDGeometryActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GeometryCacheUSDComponent.h"
#include "GeometryCacheTrackUSD.h"
#include "MyUSDGeometryActor.generated.h"

UCLASS()
class AMyUSDGeometryActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UGeometryCacheUsdComponent* CacheComponent;
};
```

**AMyUSDGeometryActor.cpp**
```cpp
#include "MyUSDGeometryActor.h"
#include "GeometryCache.h"
#include "UsdWrappers/UsdStage.h"
#include "Modules/ModuleManager.h"

void AMyUSDGeometryActor::BeginPlay()
{
    Super::BeginPlay();

    // 打开 USD 舞台
    UE::FUsdStage Stage = UnrealUSDWrapper::OpenStage(TEXT("D:/Content/AnimCube.usda"));
    if (!Stage)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open USD stage"));
        return;
    }

    // 创建 Track（简化读取，使用默认读取函数）
    UGeometryCacheTrackUsd* Track = NewObject<UGeometryCacheTrackUsd>(this);
    Track->Initialize(
        Stage,
        TEXT("/CubeMesh"),
        0,
        48,
        FReadUsdMeshFunction::CreateLambda([](const TWeakObjectPtr<UGeometryCacheTrackUsd>, float Time, FGeometryCacheMeshData& OutMeshData) -> bool
        {
            // 实际项目中应调用 USD 的网格读取 API
            return false; // 仅供参考
        })
    );

    // 创建 GeometryCache 并添加 Track
    UGeometryCache* Cache = NewObject<UGeometryCache>(this);
    Cache->AddTrack(Track);

    // 创建并挂载组件
    CacheComponent = NewObject<UGeometryCacheUsdComponent>(this);
    CacheComponent->RegisterComponent();
    CacheComponent->SetGeometryCache(Cache);
    CacheComponent->Play();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 `UE::FUsdStage` 等核心 USD 舞台封装 |
| `GeometryCache` | 引擎内置 Geometry Cache 系统（`UGeometryCacheTrack`, `FGeometryCacheMeshData`） |
| `USDClasses` | 提供网格转换选项 `UsdToUnreal::FUsdMeshConversionOptions` 和 USD 材质转换工具 |
| `USDGeomMeshConversion` | 处理 USD 几何体到 Unreal 网格数据的转换 |
| `UnrealUSDWrapper` | 封装 USD C++ API 的 C++ 包装器 |

## 维护状态

### 近期更新

- 2025-10-22 a1039b2 USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 be609b7 [Backout] - CL47041219
- 2025-10-17 7ab7923 USD: Disabled UE allocator in USD for Windows.
- 2025-10-03 d887bd6 USD: Use the default collision profile for generated static meshes.
- 2025-10-01 b4449c5 Anim In Engine: Fix broken linked anim sequences.

### 维护评价

- **创建时间**：2025年10月（不到1年）。
- **更新频率**：近期有实质性更新（修复 Windows allocator、碰撞配置），表明仍在活跃维护。
- **实验性状态**：标记为 Beta，API 可能不向后兼容。
- **文档欠缺**：DocsURL 为空，官方文档不足。
- **推荐使用**：适合需要 USD 管线的高级用户，但应注意实验性阶段可能带来的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [官方 USD 文档（Pixar）](https://graphics.pixar.com/usd/release/index.html)
- [测试用例（GeometryCache）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests)