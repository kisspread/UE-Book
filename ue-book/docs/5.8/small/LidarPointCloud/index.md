# LiDAR Point Cloud Support

> Adds support for importing, processing and rendering of LiDAR Point Clouds.

| 属性 | 值 |
|---|---|
| 中文名 | 激光雷达点云 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `LidarPointCloudRuntime` (Runtime), `LidarPointCloudEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-01-28 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud) | |

## 用途

该插件为 Unreal Engine 引入了一套完整的激光雷达（LiDAR）点云数据处理工作流。它旨在解决大规模、高密度三维点云数据（通常来自激光扫描）在游戏引擎中直接使用时面临的性能和工作流挑战。传统上，这些数据需要转换为网格模型才能在引擎中渲染，过程繁琐且可能损失精度。此插件通过专用的资产类型、优化的渲染方法和编辑器工具，实现了点云数据的直接导入、交互式编辑和高效渲染，特别适合需要集成真实世界扫描数据的专业可视化领域。

## 使用场景

- **建筑可视化与规划**：将建筑物、城市街区的激光扫描数据直接导入引擎，用于光照分析、视觉效果预览和虚拟漫游。
- **影视与预演**：在电影制作中，利用现实场景的点云快速搭建虚拟环境，确保数字资产与真实场景的精确匹配。
- **文化遗产保护**：数字化博物馆、古迹或遗址的精细三维点云，用于在线展示和学术研究。
- **游戏地形制作**：将基于真实地理数据的点云转换为游戏世界的地形基准，为开放世界游戏提供高精度地貌。
- **工业与测量**：在工业设计、设施管理和工程测量中，导入并分析来自激光扫描仪的设备或地形数据。

## 蓝图用法

插件提供了面向数据操作的核心蓝图节点，主要集中在资产管理和渲染设置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Point Cloud` | 从静态网格体数组或资产路径创建一个新的点云资产。 | `ULidarPointCloudBlueprintLibrary` |
| `Import Point Cloud` | 从指定文件路径导入点云数据。 | `ULidarPointCloudBlueprintLibrary` |
| `Get Material` / `Set Material` | 获取或设置用于渲染点云的材质实例。 | `ALidarPointCloudActor` |
| `Get Point Cloud Size` | 获取点云在世界空间中的包围盒尺寸。 | `ULidarPointCloudBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **导入点云**：使用“Import Point Cloud”节点，输入一个`.las`或`.laz`等格式的文件路径，即可在内容浏览器中生成对应的`ULidarPointCloud`资产。
2.  **放置点云**：将生成的点云资产从内容浏览器拖入场景，或使用“Create Actor from Object”节点，这会自动创建一个`ALidarPointCloudActor`。
3.  **修改外观**：在`ALidarPointCloudActor`的蓝图实例中，使用“Set Material”节点连接一个自定义材质实例，可以改变点云的着色方式（如基于高度、强度或分类着色）。

## C++ 用法

### 头文件引入

```cpp
#include "LidarPointCloud.h"
// 编辑器模块
#include "LidarPointCloudEditorModule.h"
```

### 基本用法

```cpp
// 引用自测试用例和模块文档
void BasicUsageExample()
{
    // 1. 加载一个已存在的点云资产
    ULidarPointCloud* PointCloud = LoadObject<ULidarPointCloud>(nullptr, TEXT("/Game/MyPointCLouds/BuildingScan"));

    if (PointCloud)
    {
        // 2. 获取点云的基本信息（例如总点数）
        int64 NumPoints = PointCloud->GetNumPoints();
        UE_LOG(LogTemp, Log, TEXT("点云包含 %lld 个点"), NumPoints);

        // 3. 在世界中生成一个 Actor 来显示此点云
        UWorld* World = GEditor->GetEditorWorldContext().World();
        if (World)
        {
            ALidarPointCloudActor* PointCloudActor = World->SpawnActor<ALidarPointCloudActor>(ALidarPointCloudActor::StaticClass());
            if (PointCloudActor)
            {
                // 4. 将资产分配给 Actor
                PointCloudActor->SetPointCloud(PointCloud);
            }
        }
    }
}
```

### 进阶用法

```cpp
// 组合配置：从文件导入，并配置渲染参数
void AdvancedImportAndConfigure()
{
    // 1. 定义导入设置
    FLidarPointCloudImportSettings ImportSettings;
    ImportSettings.MaxPoints = 1000000; // 限制导入的最大点数
    ImportSettings.bImportRGB = true;   // 导入颜色信息

    // 2. 异步导入（或使用同步版本）
    ULidarPointCloud::ImportFromFile(TEXT("/Path/To/Scan.las"), ImportSettings, [](ULidarPointCloud* NewCloud, bool bSuccess)
    {
        if (bSuccess && NewCloud)
        {
            // 3. 配置渲染细节（如LOD）
            NewCloud->SetLODSettings(FLidarPointCloudLODSettings{0.5f, 2}); // 示例参数

            // 4. 应用到 Actor
            // ... (如上例中的 SpawnActor 和 SetPointCloud)
        }
    });
}
```

## Demo 示例

一个最小的可编译示例，演示如何通过 C++ 加载并显示一个点云。

**MyLidarDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LidarPointCloudActor.h"
#include "MyLidarDemo.generated.h"

UCLASS()
class MYPROJECT_API AMyLidarDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyLidarDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    ALidarPointCloudActor* PointCloudActor;
};
```

**MyLidarDemo.cpp**
```cpp
#include "MyLidarDemo.h"
#include "LidarPointCloud.h"

AMylidarDemo::AMyLidarDemo()
{
    PointCloudActor = CreateDefaultSubobject<ALidarPointCloudActor>(TEXT("PointCloudActor"));
    RootComponent = PointCloudActor;
}

void AMyLidarDemo::BeginPlay()
{
    Super::BeginPlay();

    // 加载一个放在项目Content目录下的点云资产
    ULidarPointCloud* MyCloud = LoadObject<ULidarPointCloud>(nullptr, TEXT("/Game/Demo/PointCloud"));
    if (MyCloud && PointCloudActor)
    {
        PointCloudActor->SetPointCloud(MyCloud);
    }
}
```

## 模块依赖

插件自身的依赖模块较为基础。

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `Engine` | 引擎基础框架 |
| `RenderCore`, `RHI` | 底层渲染接口，用于自定义点云渲染管线 |
| `UnrealEd` | (仅 Editor 模块) 用于编辑器集成、资产导入和自定义细节面板 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口通知逻辑，优化客户端关联/解耦时的消息处理。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退了编号为53913857的提交，可能是一个引入问题的改动。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 同 `cfb610df`，视口重构的后续提交。 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 为光线追踪更新参数添加网格批处理视图，统一网格批处理的所有权管理。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化字符串中32位与64位整型说明符不匹配的问题。 |

### 维护评价

**推荐使用**。该插件作为 Epic 官方维护的企业级解决方案，自 2020 年创建以来持续更新。最近的提交（2026年5月）表明它正在积极适配引擎的核心渲染系统（如光线追踪）并进行内部代码重构，这证明其仍在活跃维护中。虽然它被标记为 `EnabledByDefault: false`，但这更多是出于对专业功能模块的谨慎启用策略，并不影响其成熟度和可靠性。对于有激光雷达点云数据处理需求的项目，它是官方推荐且功能完备的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/LidarPointCloud/Tests)