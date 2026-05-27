# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产导入逻辑、蓝图节点、材质转换等） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件提供了一整套工具，用于将 Pixar USD（Universal Scene Description）文件格式集成到 Unreal Engine 工作流中。它不仅仅是简单的网格导入，更是一个完整的 USD 资产管线桥接器。其核心解决的问题是：如何在 DCC 工具（如 Maya、Houdini）与 Unreal Engine 之间，利用 USD 格式高效、无损地交换复杂的场景数据，包括几何体、动画、材质、灯光等，并支持非破坏性的“舞台”（Stage）概念进行动态更新。插件还包含了 `USDExporter` 模块，实现了双向工作流。

## 使用场景

- 你的团队使用 Maya 或 Houdini 进行复杂的场景和动画制作，并需要将资产以 USD 格式导入到 Unreal Engine 中进行实时渲染或游戏开发。
- 你需要导入包含复杂动画序列（如骨骼动画、变换动画）的 USD 文件，并希望将其作为几何体缓存（Geometry Cache）在引擎中高效播放。
- 你需要一个可动态更新的“舞台”来管理 USD 资产，而不是一次性静态导入，并能与原始 USD 文件保持链接。
- 你希望利用 USD 的强大材质网络，并将其转换为 Unreal Engine 的材质系统。

## 蓝图用法

基于 `GeometryCacheUSD` 模块的源码分析，该模块主要为 USD 动画数据提供了一个几何体缓存实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize` | 使用 USD 舞台、Prim 路径和帧范围初始化几何体缓存轨道。 | `UGeometryCacheTrackUsd` |
| `GetMeshDataAtTime` | 在指定时间点获取网格数据。 | `UGeometryCacheTrackUsd` |
| `GetMeshDataAtSampleIndex` | 在指定采样索引获取网格数据。 | `UGeometryCacheTrackUsd` |
| `LoadUsdStage` | 加载或重新连接到 USD 舞台文件。 | `UGeometryCacheTrackUsd` |
| `UnloadUsdStage` | 卸载当前引用的 USD 舞台以释放资源。 | `UGeometryCacheTrackUsd` |

### 使用示例（蓝图描述）

1.  在你的 Actor 蓝图中添加一个 `USD Geometry Cache` 组件（对应 `UGeometryCacheUsdComponent`）。
2.  通过 `USDStageImporter` 模块的蓝图节点，可以打开一个 USD 文件并获取其舞台（Stage）。
3.  找到包含动画网格数据的 Prim 路径（例如 `/Root/AnimatedMesh`）。
4.  调用 `UGeometryCacheTrackUsd` 的 `Initialize` 节点，将舞台、Prim 路径和期望的动画帧范围（StartFrameIndex， EndFrameIndex）传入，完成轨道初始化。
5.  组件随后会根据时间轴自动调用 `GetMeshDataAtTime` 等函数，驱动几何体缓存的播放。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCacheUSD/Public/GeometryCacheTrackUSD.h"
```

### 基本用法

创建并初始化一个 USD 几何体缓存轨道，用于播放 USD 文件中的动画网格。

```cpp
// 假设你已经通过某个方式（如 USDStageImporter 模块）获得了 UsdStage 的弱引用
UE::FUsdStageWeak StageWeak = ...;
FString PrimPath = TEXT("/World/AnimatedCube");
int32 StartFrame = 0;
int32 EndFrame = 100;

// 创建一个轨道实例
UGeometryCacheTrackUsd* UsdTrack = NewObject<UGeometryCacheTrackUsd>();

// 定义一个读取网格数据的 Lambda 函数 (FReadUsdMeshFunction)
// 这是实际从 USD 读取数据的核心逻辑，通常由插件内部实现
FReadUsdMeshFunction ReadFunc = [](const TWeakObjectPtr<UGeometryCacheTrackUsd>& InTrack, float Time, FGeometryCacheMeshData& OutMeshData) -> bool
{
    // ... 使用 USD SDK 根据 Time 和 PrimPath 读取网格数据并填充到 OutMeshData
    return true;
};

// 初始化轨道
UsdTrack->Initialize(StageWeak, PrimPath, StartFrame, EndFrame, ReadFunc);
```
*（代码逻辑基于对 `UGeometryCacheTrackUsd::Initialize` 公开接口的分析）*

### 进阶用法

管理 USD 舞台的加载与卸载，以控制内存使用。

```cpp
// 在某个时刻需要访问 USD 数据前
bool bStageLoaded = UsdTrack->LoadUsdStage();
if (bStageLoaded)
{
    // 可以安全地调用 GetMeshDataAtTime 等函数
    FGeometryCacheMeshData MeshData;
    UsdTrack->GetMeshDataAtTime(5.0f, MeshData);
    // ... 处理 MeshData
}

// 当不再需要高频访问时，释放对 USD 舞台的引用
UsdTrack->UnloadUsdStage();
```
*（代码逻辑基于对 `LoadUsdStage` 和 `UnloadUsdStage` 公开接口的分析）*

## Demo 示例

一个最小的 C++ 类，演示如何组合使用 `UGeometryCacheUsdComponent` 和 `UGeometryCacheTrackUsd`。

```cpp
// MyUsdGeometryCacheActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "MyUsdGeometryCacheActor.generated.h"

class UGeometryCacheUsdComponent;
class UGeometryCacheTrackUsd;

UCLASS()
class AMyUsdGeometryCacheActor : public AActor
{
	GENERATED_BODY()

public:
	AMyUsdGeometryCacheActor();

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UGeometryCacheUsdComponent> UsdGeometryCacheComponent;

	UPROPERTY()
	TObjectPtr<UGeometryCacheTrackUsd> UsdTrack;
};
```

```cpp
// MyUsdGeometryCacheActor.cpp
#include "MyUsdGeometryCacheActor.h"
#include "GeometryCacheUSD/GeometryCacheUSDComponent.h"
#include "GeometryCacheUSD/GeometryCacheTrackUSD.h"

AMyUsdGeometryCacheActor::AMyUsdGeometryCacheActor()
{
	UsdGeometryCacheComponent = CreateDefaultSubobject<UGeometryCacheUsdComponent>(TEXT("USDGeometryCache"));
	RootComponent = UsdGeometryCacheComponent;
}

void AMyUsdGeometryCacheActor::BeginPlay()
{
	Super::BeginPlay();

	// 注意：此处仅为示例结构。实际的 Stage 获取和 ReadFunc 实现复杂，需使用 USDImporter 插件的其他模块。
	// 假设已获得有效的 Stage 弱引用和定义了 ReadFunc。
	UE::FUsdStageWeak StageWeak = ...; // 需要具体实现
	FString PrimPath = TEXT("/Some/Prim");
	FReadUsdMeshFunction ReadFunc = ...; // 需要具体实现

	UsdTrack = NewObject<UGeometryCacheTrackUsd>(this);
	UsdTrack->Initialize(StageWeak, PrimPath, 0, 120, ReadFunc);

	// 将自定义的轨道关联到组件（可能需要通过更多内部接口，此为简化示意）
	// UsdGeometryCacheComponent->SetTrack(UsdTrack);
}
```

## 模块依赖

`USDImporter` 插件内部模块众多且相互依赖。对于最终使用者（例如，在你的游戏模块中使用 USD 导入功能），最直接的依赖通常来自 `USDStageImporter` 或 `USDStage` 模块，用于加载和管理 USD 舞台。`GeometryCacheUSD` 模块则依赖 USD SDK 和几何体缓存系统。

| 模块 | 用途 |
|---|---|
| `USDStage` | 管理 USD 舞台（Stage）的核心运行时模块。 |
| `USDSchemas` | 提供 USD 类型到 Unreal 类型的映射和转换规则。 |
| `USDStageImporter` | 负责将 USD 资产导入到引擎内容浏览器的逻辑。 |
| `GeometryCacheUSD` | 将 USD 动画数据实现为 Unreal 几何体缓存。 |
| `USDExporter` | 负责将 Unreal 场景/资产导出为 USD 格式。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转浮点产生的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 新增对独立于蓝图控制绑定的分配支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD: 解决更新到 26.03 版本导致 LOD 变化时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符与参数位宽不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 支持烘焙曝光动画轨道的所有帧。 |

### 维护评价

- **状态**：**实验性（Beta）且活跃维护**。尽管插件年龄已有6年，但从提交记录看，截至2026年5月仍有持续的、针对性的功能增加和Bug修复。
- **推荐度**：**推荐用于项目原型或可控环境**。作为 Epic 官方维护的 Beta 插件，其基础功能稳定且持续更新。但由于 `IsBetaVersion=true` 且 `EnabledByDefault=false`，API 可能发生变化，不建议在追求长期稳定性的最终发布版本中毫无准备地依赖。建议密切关注更新日志，并做好适配新版本的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- 官方文档：此插件无独立官方文档链接，功能通常在 Unreal Engine 官方文档的 USD 相关章节中描述。
- 测试用例：路径可能为 `Engine/Plugins/Importers/USDImporter/Source/USDTests/`，具体文件需查看源码仓库。