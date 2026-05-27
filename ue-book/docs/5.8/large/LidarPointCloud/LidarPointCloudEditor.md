# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产， 编辑器工具） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

该插件为虚幻引擎提供了一套完整的激光雷达（LiDAR）点云数据工作流支持。它不仅仅是一个数据导入器，更是一个集编辑、优化、转换于一体的综合工具链。其核心解决的问题是：如何将庞大的、无序的点云数据（通常来自激光扫描仪或摄影测量）高效地转化为虚幻引擎中可实时渲染、可交互的资产，并提供必要的后处理工具（如清理、对齐、法线计算、网格化）以优化数据，使其适合用于场景构建、仿真或可视化。

## 使用场景

-   **建筑与建造（AEC）**：您有一个包含数十亿点的现场激光扫描数据（如 .e57, .las 格式），需要将其导入 UE5 中进行施工进度监控、BIM 模型比对或虚拟漫游。
-   **自动驾驶仿真**：您需要将真实世界录制的道路环境点云数据作为背景环境，放入仿真场景中测试感知算法。
-   **遗产保护与考古**：您有古建筑的精细化三维扫描点云，希望在引擎中进行实时展示和虚拟修复研究。
-   **工业资产数字化**：您扫描了一个大型工厂或设备，需要将点云作为参考，在 UE 中重建或叠加数字孪生模型。

## 蓝图用法

该插件的主要蓝图功能通过编辑器工具模式实现，允许在编辑器内对点云资产进行交互式操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MergeActors` | 将多个点云Actor合并到一个新的点云资产中，可选择替换源Actor | `ULidarToolActionsMerge` |
| `MergeData` | 将多个点云资产的数据合并到一个新的点云资产中 | `ULidarToolActionsMerge` |
| `AlignAroundWorldOrigin` | 将选中的点云Actor对齐到世界原点 | `ULidarToolActionsAlign` |
| `AlignAroundOriginalCoordinates` | 将点云对其原始扫描坐标进行对齐 | `ULidarToolActionsAlign` |
| `ResetAlignment` | 重置点云的对齐变换 | `ULidarToolActionsAlign` |
| `BuildCollision` | 为选中的点云重新构建碰撞体 | `ULidarToolActionsCollision` |
| `RemoveCollision` | 移除选中点云的碰撞体 | `ULidarToolActionsCollision` |
| `BuildStaticMesh` | 将点云数据转换为静态网格体 | `ULidarToolActionsMeshing` |
| `CalculateNormals` | 为选中的点云计算法线信息 | `ULidarEditorToolNormals` |

### 使用示例（蓝图描述）

1.  **场景中放置点云**：将 `LidarPointCloudAsset` 拖入场景，或通过 `UActorFactoryLidarPointCloud` 自动创建 `ALidarPointCloudActor`。
2.  **进入编辑模式**：选中一个点云Actor，然后在细节面板或通过快捷键（需注册）进入“LiDAR 编辑模式”。
3.  **选择与操作**：在编辑模式工具栏中，选择不同的工具（如框选、多边形选择、套索选择、笔刷选择）来选中一部分点。
4.  **调用操作**：选中点后，在“工具操作”面板中（例如在“清理”分类下），点击 `DeleteSelected` 节点来删除这些点。或点击 `Extract` 将选中的点提取为一个新的独立资产。
5.  **网格化**：要生成可碰撞和标准光照的网格，在“工具操作”面板的“网格化”分类中，设置 `MaxMeshingError` 后点击 `BuildStaticMesh`。

## C++ 用法

### 头文件引入

```cpp
// 运行时模块
#include "LidarPointCloudRuntime.h"
// 编辑器模块（仅在编辑器代码中）
#include "LidarPointCloudEditor.h"
```

### 基本用法

以下示例展示如何通过 C++ 代码操作点云资产。代码来源于插件内部的编辑器工具逻辑。

```cpp
// 来源：Private/LidarPointCloudEditorHelper.h
#include "LidarPointCloudEditorHelper.h"

void AMergeAndAlignPointClouds()
{
    // 1. 创建一个新的空白点云资产
    ULidarPointCloud* NewCloud = FLidarPointCloudEditorHelper::CreateNewAsset();

    // 2. 假设我们有一些源点云资产
    TArray<ULidarPointCloud*> SourceClouds;
    // ... 填充 SourceClouds ...

    // 3. 合并数据
    FLidarPointCloudEditorHelper::MergeLidar(NewCloud, SourceClouds);

    // 4. 获取当前编辑器中选中的点云Actor并进行对齐
    // 注意：这些静态函数通常操作编辑器选中的Actor
    FLidarPointCloudEditorHelper::SetOriginalCoordinateForSelection(); // 先设置原始坐标
    FLidarPointCloudEditorHelper::AlignSelectionAroundWorldOrigin();   // 然后对齐到世界原点
}
```

### 进阶用法

自定义点云导入工厂或扩展编辑器模式。

```cpp
// 来源：Private/LidarPointCloudFactory.h 和 Private/LidarPointCloudEdMode.h
// 示例：了解插件如何通过工厂和模式工作
// 1. 导入工厂 (UCLASS)
// 插件注册了 ULidarPointCloudFactory，它处理文件导入和重新导入逻辑。
// 您可以研究它来了解支持的文件格式和导入设置 (FLidarPointCloudImportSettings)。

// 2. 编辑器模式 (UCLASS)
// 插件注册了 ULidarEditorMode，它管理工具的激活、切换和特定的交互逻辑。
// 要扩展，您可以继承相关的工具类（如 ULidarEditorToolBase）并在模式中注册新的工具调色板。
```

## Demo 示例

一个最小化的示例，展示如何在运行时通过 C++ 代码创建一个点云组件并将其添加到 Actor。

```cpp
// MyLidarActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyLidarActor.generated.h"

class ULidarPointCloudComponent;

UCLASS()
class AMyLidarActor : public AActor
{
    GENERATED_BODY()
public:
    AMyLidarActor();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<ULidarPointCloudComponent> PointCloudComponent;
};

// MyLidarActor.cpp
#include "MyLidarActor.h"
#include "LidarPointCloudComponent.h" // 来自 LidarPointCloudRuntime 模块

AMylidarActor::AMyLidarActor()
{
    PrimaryActorTick.bCanEverTick = false;

    PointCloudComponent = CreateDefaultSubobject<ULidarPointCloudComponent>(TEXT("PointCloud"));
    RootComponent = PointCloudComponent;
}

void AMyLidarActor::BeginPlay()
{
    Super::BeginPlay();

    // 在BeginPlay中，您可以通过代码加载或设置点云资产
    // ULidarPointCloud* LoadedCloud = LoadObject<ULidarPointCloud>(nullptr, TEXT("/Path/To/YourAsset"));
    // if (LoadedCloud)
    // {
    //     PointCloudComponent->SetPointCloud(LoadedCloud);
    // }
}
```

## 模块依赖

要使用此插件的功能，您的 `.Build.cs` 文件需要添加以下依赖。已省略常见的 Core/Engine/Slate 依赖。

| 模块 | 用途 |
|---|---|
| `LidarPointCloudRuntime` | 访问点云资产类、组件和基础运行时功能 |
| `LidarPointCloudEditor` | （仅编辑器项目）访问导入工厂、编辑器模式、工具和资产定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/取消关联逻辑，提取公共代码 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了一个提交（CL53913857） |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联逻辑（可能为另一个尝试） |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 与硬件光线追踪相关，添加了网格批次视图并统一了所有权（底层引擎改动） |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中 32 位与 64 位不匹配的问题 |

### 维护评价

**成熟且活跃的企业级插件。**

-   **创建时间**：2020 年初，已有约 6 年历史，属于较成熟的工具。
-   **更新频率**：从最近的提交记录（2026 年 5 月）看，**仍处于活跃维护状态**。更新内容主要集中在引擎底层兼容性（如光线追踪、视口框架重构）和稳定性修复上，表明其与 UE5 引擎的持续集成工作良好。
-   **功能完整性**：从源码分析，其功能集（导入、编辑、优化、网格化）非常完整，满足了企业级应用的基本需求。
-   **使用建议**：**推荐使用**。它是一个官方维护的、功能完备的点云解决方案。虽然 `EnabledByDefault` 为 `false`（需要手动启用），但这可能是出于避免影响其他项目启动时间的考虑。对于需要处理点云的项目，这是一个可靠且专业的选择。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)
-   官方文档：无（`DocsURL` 为空）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud/Tests)（推测路径，基于常规结构）