# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染同步 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMultiUser` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于驱动大规模、高分辨率沉浸式显示系统的核心框架。其核心目标是实现跨多个物理PC的**集群渲染**，确保所有节点上渲染的视口（Viewport）在时间和空间上精确同步。

它解决的关键问题包括：
1.  **同步**：保证多个PC渲染的每一帧都完全对齐，用于立体投影、多通道投影或大型拼接墙。
2.  **投影与变形**：支持复杂的投影几何体（如穹顶、弧形屏幕），并通过Warper和MPCDI进行像素级的几何校正。
3.  **集群管理**：提供编辑器和运行时工具来配置、部署和监控整个渲染集群。
4.  **媒体集成**：通过共享内存（SharedMemoryMedia）等方式，实现集群与外部视频设备或采集卡的高效数据传输。
5.  **后期集成**：与Movie Render Queue、Sequencer等编辑器功能深度集成，支持离线渲染高质量的集群内容。

它主要用于**虚拟制片（Virtual Production）**、**主题公园大型游乐设施**、**沉浸式展览**、**驾驶模拟器**和**科研可视化**等需要多PC协同渲染单一或立体场景的领域。

## 使用场景

-   **虚拟制片 LED墙**：使用多台PC驱动一块巨大的LED墙，每一台PC负责渲染墙的一个或多个面板，需要像素级完美的拼接和同步。
-   **穹顶投影系统**：为天文馆或飞行模拟器驱动一个穹顶投影，需要通过几何校正将3D场景正确投射到球面上。
-   **立体3D投影**：为每只眼睛独立渲染视图（左眼/右眼），并通过同步确保立体效果无撕裂。
-   **多GPU渲染**：在一台拥有多个高端GPU的PC上，将渲染任务分配给不同GPU，以提升单机多屏渲染的性能。
-   **数据大屏可视化**：需要将实时渲染的数据可视化内容，以超高清分辨率输出到大型监控墙或指挥中心。

## 蓝图用法

nDisplay 提供了丰富的蓝图节点用于控制集群。以下为核心功能节点分组：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start Cluster` | 启动本地和远程节点上的nDisplay集群。 | `UDisplayClusterBlueprintAPI` |
| `Stop Cluster` | 停止正在运行的nDisplay集群。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Nodes Ids` | 获取当前集群中所有节点的ID列表。 | `UDisplayClusterBlueprintAPI` |
| `Set Viewport Buffer Ratio` | 动态设置指定视口的渲染分辨率比例。 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport Buffer Ratio` | 获取指定视口的当前渲染分辨率比例。 | `UDisplayClusterBlueprintAPI` |
| `Set Cluster Render Mode` | 设置集群的渲染模式（如单眼、立体等）。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Render Mode` | 获取当前集群的渲染模式。 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport Context` | 获取指定视口的渲染上下文信息。 | `UDisplayClusterBlueprintAPI` |
| `Render Texture to Viewport` | 将一张纹理直接渲染到指定的视口上（覆盖场景）。 | `UDisplayClusterBlueprintAPI` |
| `Reset Viewport` | 重置视口，清除之前渲染的纹理覆盖。 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **启动集群**：在 `BeginPlay` 事件中，调用 `Start Cluster` 节点，并将 `bAutoConnect` 参数设为 `true`，即可让当前PC（主节点）尝试连接并启动配置文件中定义的所有从节点。
2.  **动态调整画质**：当检测到性能不足时，可以通过 `Get Cluster Nodes Ids` 获取节点，然后对每个节点调用 `Set Viewport Buffer Ratio` 将其渲染分辨率从 1.0 降至 0.75，以提高帧率。
3.  **显示调试信息**：创建一个简单的UI，使用 `Get Viewport Context` 节点获取某个视口的当前帧号、时间等信息，并显示在屏幕上。

## C++ 用法

nDisplay 主要通过其模块接口和蓝图API进行控制。以下为C++中的基本操作示例。

### 头文件引入

```cpp
// 核心API头文件
#include "DisplayClusterBlueprintAPI.h"
// 如果需要直接操作配置
#include "DisplayClusterConfigurationTypes.h"
```

### 基本用法

以下是通过C++代码控制nDisplay集群的基础示例。

**来源文件**: 基于 `DisplayClusterBlueprintAPI` 公共接口推断的典型用法。

```cpp
#include "DisplayClusterBlueprintAPI.h"

void AMyClusterController::StartMyCluster()
{
    // 获取nDisplay蓝图API单例
    UDisplayClusterBlueprintAPI* API = UDisplayClusterBlueprintAPI::Get();
    if (API)
    {
        // 在编辑器或独立进程中启动集群
        // 第一个参数是配置文件路径（可选，通常使用默认或当前加载的）
        // 第二个参数指定是否自动连接所有节点
        API->StartCluster(TEXT(""), true);
        
        UE_LOG(LogTemp, Log, TEXT("nDisplay Cluster Started."));
    }
}

void AMyClusterController::SetDynamicResolution()
{
    UDisplayClusterBlueprintAPI* API = UDisplayClusterBlueprintAPI::Get();
    if (API)
    {
        // 获取所有节点的ID
        TArray<FString> NodeIds;
        API->GetClusterNodesIds(NodeIds);
        
        // 为每个视口设置80%的渲染分辨率以提升性能
        for (const FString& NodeId : NodeIds)
        {
            // 这里假设每个节点都有一个名为 “Viewport_1” 的视口
            // 实际视口ID需根据.nDisplay配置文件确定
            const FString ViewportId = FString::Printf(TEXT("%s_Viewport_1"), *NodeId);
            API->SetViewportBufferRatio(ViewportId, 0.8f);
        }
    }
}
```

### 进阶用法：手动触发DDC预填充

`DisplayClusterFillDerivedDataCache` 模块用于在编辑器启动时异步填充nDisplay相关的派生数据缓存（如材质、着色器），以避免运行时卡顿。以下是其内部工作机制的简化说明。

**来源文件**: `DisplayClusterFillDerivedDataCacheWorker.h`

```cpp
#include "DisplayClusterFillDerivedDataCacheWorker.h"
#include "Async/AsyncWork.h"

// 理论上，模块启动时会自动创建并运行此Worker
// 如需手动触发或控制，可参考其模式
class FMyDDCFillTask : public FRunnable
{
public:
    virtual uint32 Run() override
    {
        // 此Worker的核心是启动一个外部命令行进程（Commandlet），
        // 该进程负责扫描nDisplay资产并预编译/填充DDC。
        // Worker通过管道读取该进程的输出，并解析进度信息（编译总数、已完成数）。
        // 同时，它会更新编辑器的通知区域，显示“正在预热nDisplay缓存...”。
        
        FString CommandletParams = TEXT("-run=FillDerivedDataCache -platform=Win64");
        // 启动子进程并监控其输出...
        
        return 0;
    }
};
```

## Demo 示例

一个最小化的C++类，演示如何从代码中启动和查询nDisplay状态。

**MyDisplayClusterManager.h**
```cpp
// MyDisplayClusterManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDisplayClusterManager.generated.h"

class UDisplayClusterBlueprintAPI;

UCLASS()
class MYPROJECT_API AMyDisplayClusterManager : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDisplayClusterManager();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

public:
    /** 从蓝图调用，启动集群 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay")
    void StartDisplayCluster();

    /** 从蓝图调用，查询并打印集群状态 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay")
    void PrintClusterStatus();

private:
    /** 保存的API指针 */
    UPROPERTY()
    UDisplayClusterBlueprintAPI* DisplayClusterAPI = nullptr;
};
```

**MyDisplayClusterManager.cpp**
```cpp
// MyDisplayClusterManager.cpp
#include "MyDisplayClusterManager.h"
#include "DisplayClusterBlueprintAPI.h"
#include "Kismet/GameplayStatics.h"

AMyDisplayClusterManager::AMyDisplayClusterManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDisplayClusterManager::BeginPlay()
{
    Super::BeginPlay();
    // 获取API实例
    DisplayClusterAPI = UDisplayClusterBlueprintAPI::Get();
}

void AMyDisplayClusterManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 考虑在结束时停止集群
    if (DisplayClusterAPI)
    {
        DisplayClusterAPI->StopCluster();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyDisplayClusterManager::StartDisplayCluster()
{
    if (DisplayClusterAPI)
    {
        DisplayClusterAPI->StartCluster(TEXT(""), true);
        UE_LOG(LogTemp, Warning, TEXT("Display Cluster Start Command Issued."));
    }
}

void AMyDisplayClusterManager::PrintClusterStatus()
{
    if (!DisplayClusterAPI) return;

    TArray<FString> NodeIds;
    DisplayClusterAPI->GetClusterNodesIds(NodeIds);
    
    UE_LOG(LogTemp, Log, TEXT("--- nDisplay Cluster Status ---"));
    UE_LOG(LogTemp, Log, TEXT("Connected Nodes: %d"), NodeIds.Num());
    
    for (const FString& NodeId : NodeIds)
    {
        // 获取该节点上的一些基础信息，例如渲染模式
        EDisplayClusterRenderMode RenderMode = EDisplayClusterRenderMode::Mono;
        // 假设我们有一个函数可以获取模式，此处为示例
        UE_LOG(LogTemp, Log, TEXT("Node: %s"), *NodeId);
    }
}
```

## 模块依赖

nDisplay插件包含多个模块，不同模块有不同的依赖。以下是**非标准**的依赖列表：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 用于DisplayClusterMedia和SharedMemoryMedia模块，支持基于DirectX 12的GPU间共享内存通信。 |
| `ScalableMPCDI` | (External) 第三方库，用于读取和应用MPCDI格式的投影校正配置文件。 |
| `UnrealEd` | 多个编辑器相关模块（如DisplayClusterConfigurator, DisplayClusterWarp）的依赖，用于提供编辑器工具、资产编辑和UI。 |

*其他如Core, CoreUObject, Engine, Slate等常见模块的依赖已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | nDisplay与Movie Graph结合，新增EXR多图层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 简化了Movie Pipeline中的WarpBlend模式，合并了Alpha通道处理。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了Movie Render Queue中的相机命名问题，并解决了MPCDI/ICVFX着色器中的透明度错误。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码时未能正确遵循自定义Gamma值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当UI纹理尺寸小于视口尺寸时可能出现的渲染闪烁问题。 |

### 维护评价

nDisplay 是 Unreal Engine 中用于**高端商业和虚拟制片领域**的**核心组件**，而非实验性功能。
*   **创建时间**：2018年，已是一个成熟的插件。
*   **更新频率**：**极其活跃**。从提交记录看，几乎每周甚至每天都有更新，内容涉及新功能（EXR多图层）、Bug修复（闪烁、透明度、Gamma）以及与Movie Render Graph等新系统的集成。
*   **维护状态**：**积极维护中**。Epic Games持续投入资源，确保其与最新的UE引擎功能（如Movie Graph）兼容并修复问题。
*   **已知限制**：作为默认禁用的插件，需要用户主动启用并具备相应的硬件（多PC、专业GPU、投影设备）和网络环境。配置过程相对复杂，对新手不友好。
*   **推荐**：**强烈推荐**给所有从事**虚拟制片、大型沉浸式体验、飞行/驾驶模拟器、专业可视化**等项目的开发者。它是实现像素级精确的多机同步渲染的**唯一官方解决方案**。对于普通游戏开发或小型项目则无需关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-in-unreal-engine/) (通常为DocsURL为空时，引擎有通用文档页)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) (DisplayClusterTests模块)