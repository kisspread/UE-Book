# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、示例项目） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途
nDisplay 是 Unreal Engine 中用于驱动**多台计算机（集群）进行同步渲染**的核心框架。它解决了一个主机无法驱动超高分辨率或多视角渲染的问题，通过网络将渲染任务分发到多个“渲染节点”（Render Nodes），并将它们的输出精确同步后组合到物理显示设备上（如 LED 墙、穹顶、CAVE 系统）。这是**虚拟制片（LED Volume）、沉浸式投影环境（Immersive Projection）和多通道渲染测试**等专业场景的基石。

## 使用场景
- **虚拟制片（LED 墙拍摄）**：在摄影棚内使用大型 LED 墙实时渲染并显示背景环境，nDisplay 负责确保 LED 墙上每块屏幕的画面由对应的渲染节点生成且完全同步。
- **沉浸式投影环境（CAVE, 穹顶）**：在多面投影或穹顶投影系统中，由多台投影仪和对应的渲染节点共同生成一个无缝的、包围观众的 360° 画面。
- **超宽幅/超高分辨率显示**：驱动由多个物理显示器拼接而成的超大屏，每个显示器由一台 PC 驱动。
- **专业 A/V 集成**：与现实世界的硬件同步器、媒体服务器和几何校正软件（如 ScalableMPCDI）集成，用于复杂的固定安装项目。
- **电影制作与预演**：在虚拟摄影和后期制作中，用于精确渲染多视角画面。

## 蓝图用法
nDisplay 提供了丰富的蓝图接口用于运行时管理、控制和监控集群。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartCluster` / `StopCluster` | 启动或停止 nDisplay 集群 | `UDisplayClusterManager` |
| `GetClusterNodes` | 获取当前集群中所有节点的列表 | `UDisplayClusterManager` |
| `GetRenderNode` | 获取指定 ID 的渲染节点对象 | `UDisplayClusterManager` |
| `SetViewPoint` | 设置用于渲染的视点位置和旋转 | `UDisplayClusterViewport` |
| `SetViewportTexture` | 为视口设置特定的渲染目标纹理 | `UDisplayClusterViewport` |
| `SetProjectionPolicy` | 设置视口的投影策略（如平面、穹顶） | `UDisplayClusterProjectionPolicy` |
| `SetWarpBlendMode` | 设置视口的几何校正与融合模式 | `UDisplayClusterWarpBlend` |
| `GetColorGradingSettings` | 获取并修改视口的颜色分级设置 | `UDisplayClusterColorGrading` |

### 使用示例（蓝图描述）
在 `BeginPlay` 中，使用 `StartCluster` 节点，传入配置资产（`UDisplayClusterConfigurationData`）来初始化并启动集群。随后，可通过 `GetClusterNodes` 循环获取每个 `UDisplayClusterRenderNode`，并对其上的 `UDisplayClusterViewport` 调用 `SetViewPoint`，将相机的位置和旋转数据传入，以实现多视角渲染。对于投影变换，可实例化一个 `UDisplayClusterProjectionPolicy` 并调用 `SetProjectionPolicy` 将其应用到指定视口。

## C++ 用法

### 头文件引入
```cpp
#include "DisplayCluster.h"
#include "DisplayClusterManager.h"
#include "DisplayClusterViewport.h"
#include "DisplayClusterProjectionPolicy.h"
#include "DisplayClusterWarpBlend.h"
```

### 基本用法
从测试用例中提取的典型操作流程。
```cpp
// 来源：DisplayClusterTests 模块
// 1. 获取全局的 nDisplay 管理器
UDisplayClusterManager* DisplayManager = UDisplayClusterManager::Get();
if (DisplayManager)
{
    // 2. 加载 nDisplay 配置资产
    UDisplayClusterConfigurationData* ConfigData = LoadObject<UDisplayClusterConfigurationData>(nullptr, TEXT("/Game/Config/MyDisplayConfig"));

    // 3. 启动集群
    DisplayManager->StartCluster(ConfigData);

    // 4. 获取主渲染节点
    UDisplayClusterRenderNode* MainNode = DisplayManager->GetRenderNode(TEXT("Node1"));
    if (MainNode)
    {
        // 5. 获取其上的视口并进行操作
        UDisplayClusterViewport* Viewport = MainNode->GetViewport(TEXT("Viewport1"));
        if (Viewport)
        {
            // 更新视口的视图变换（通常从相机获取）
            FDisplayClusterViewProjectionMatrix ViewProjection;
            // ... 填充 ViewProjection 矩阵 ...
            Viewport->SetViewProjectionMatrix(ViewProjection);
        }
    }
}
```

### 进阶用法
结合投影、几何校正和颜色分级进行高级设置。
```cpp
// 来源：综合 DisplayClusterProjection 和 DisplayClusterColorGrading 模块
// 1. 为视口应用自定义的投影策略
UDisplayClusterProjectionPolicy* DomePolicy = NewObject<UDisplayClusterProjectionPolicy>(GetTransientPackage(), UDisplayClusterProjectionPolicyDome::StaticClass());
Viewport->SetProjectionPolicy(DomePolicy);

// 2. 配置几何校正与融合
UDisplayClusterWarpBlend* WarpBlend = Viewport->GetWarpBlend();
if (WarpBlend)
{
    // 加载 MPCDI 或 Mesh 用于几何校正
    WarpBlend->LoadWarpData(WarpDataPath);
    WarpBlend->SetBlendMode(EDisplayClusterWarpBlendMode::WarpBlendAlpha);
}

// 3. 调整颜色分级
FDisplayClusterColorGradingSettings ColorSettings;
ColorSettings.WhiteBalance.Temperature = 6500.f;
Viewport->GetColorGradingComponent()->SetSettings(ColorSettings);
```

## Demo 示例
一个最小的 nDisplay 集群管理器类示例。
```cpp
// NDdisplayDemoManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NDdisplayDemoManager.generated.h"

class UDisplayClusterManager;
class UDisplayClusterConfigurationData;

UCLASS()
class UNDdisplayDemoManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    void StartDemoCluster(const FString& ConfigAssetPath);

    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    void StopDemoCluster();

private:
    UPROPERTY()
    TObjectPtr<UDisplayClusterManager> DisplayManager;

    UPROPERTY()
    TObjectPtr<UDisplayClusterConfigurationData> CurrentConfig;
};
```

```cpp
// NDdisplayDemoManager.cpp
#include "NDdisplayDemoManager.h"
#include "DisplayCluster.h"
#include "DisplayClusterManager.h"
#include "DisplayClusterConfiguration.h"

void UNDdisplayDemoManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    DisplayManager = UDisplayClusterManager::Get();
}

void UNDdisplayDemoManager::Deinitialize()
{
    if (DisplayManager)
    {
        DisplayManager->StopCluster();
    }
    Super::Deinitialize();
}

void UNDdisplayDemoManager::StartDemoCluster(const FString& ConfigAssetPath)
{
    if (!DisplayManager) return;

    CurrentConfig = LoadObject<UDisplayClusterConfigurationData>(nullptr, *ConfigAssetPath);
    if (CurrentConfig)
    {
        DisplayManager->StartCluster(CurrentConfig);
    }
}

void UNDdisplayDemoManager::StopDemoCluster()
{
    if (DisplayManager)
    {
        DisplayManager->StopCluster();
        CurrentConfig = nullptr;
    }
}
```

## 模块依赖
nDisplay 插件的模块依赖非常广泛，以下是区别于常见 Core/Engine 依赖的特殊项：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 被 `DisplayClusterMedia` 和 `SharedMemoryMedia` 用于基于 DirectX 12 的高效 GPU 间共享内存传输。 |
| `MPCDI` (ScalableMPCDI) | 被 `DisplayClusterWarp` 依赖，用于加载和解析 MPCDI 格式的几何校正与融合数据。 |
| `LevelEditor`, `UnrealEd`, `EditorWidgets` | 多个编辑器模块（如 `DisplayClusterEditor`, `DisplayClusterOperator`）依赖，用于构建 nDisplay 的专用编辑器 UI 和操作面板。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影渲染图增加了多层 EXR 格式输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将“仅Alpha融合”模式合并到主融合模式中，简化了电影管线中的设置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了电影渲染图中相机命名的问题，以及MPCDI/ICVFX着色器中不透明度Alpha通道的错误。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在备用帧编码路径下未正确处理非默认显示伽马值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时导致的渲染闪烁问题。 |

### 维护评价
nDisplay 是 Unreal Engine **长期维护且功能不断演进**的核心专业渲染插件。自2018年创建以来，尽管已有8年历史，但近期的 git 记录显示其仍在**非常活跃地更新**，修复集中在电影渲染管线（MoviePipeline）、几何校正（Warp/Blend）和着色器等关键功能上。作为虚拟制片和沉浸式投影领域的**事实标准**，其稳定性和功能完善度极高。**强烈推荐**用于所有涉及多机同步渲染的专业项目。该插件默认未启用（`EnabledByDefault: false`），因为其配置复杂且面向特定硬件集群，需要用户在项目设置中手动开启。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档（链接待补充）
- 测试用例：`Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/`