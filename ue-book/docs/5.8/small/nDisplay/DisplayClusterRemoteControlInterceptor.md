# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、编辑器工具、示例场景） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-08 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的专业集群渲染解决方案，主要用于**大规模沉浸式视觉体验**。它解决了在多个物理显示器、投影仪或 LED 墙上同步渲染单个虚拟场景的核心问题。

**核心功能**：
- **多机同步**：协调多台 PC 同时渲染同一场景，保持帧同步
- **投影映射**：支持复杂几何表面（曲面、球面、穹顶）的投影校正
- **立体渲染**：支持被动/主动立体 3D 渲染
- **媒体输入输出**：集成视频输入/输出和共享内存传输
- **远程控制**：通过 Remote Control API 控制渲染参数

**存在原因**：传统单机渲染无法满足大型 LED 墙、穹顶影院、CAVE 系统等沉浸式显示环境的需求，需要专门的技术来处理几何校正、同步和分布式渲染。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED 墙前拍摄时，同步渲染虚拟背景
- **主题公园**：穹顶影院、飞行模拟器、沉浸式游乐设施
- **大型会展**：超宽曲面 LED 显示墙
- **科研可视化**：多屏幕 CAVE 系统、飞行模拟
- **演唱会/舞台**：实时生成背景视觉效果
- **汽车设计评审**：在高分辨率屏幕上同步显示设计模型

## 蓝图用法

nDisplay 主要通过配置资产（DisplayCluster Configuration）进行设置，运行时通过 Remote Control API 进行控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Cluster Nodes` | 获取集群中所有节点信息 | `UDisplayClusterSubsystem` |
| `Get Cluster Node` | 获取指定节点信息 | `UDisplayClusterSubsystem` |
| `Set Node View Offset` | 设置节点视图偏移 | `UDisplayClusterSubsystem` |
| `Get Config Data` | 获取当前配置数据 | `UDisplayClusterSubsystem` |

### 使用示例（蓝图描述）

1. **初始化集群**：
   - 在 GameMode 中创建 `UDisplayClusterSubsystem` 实例
   - 调用 `StartCluster` 启动集群连接
   - 设置同步模式和渲染参数

2. **运行时控制**：
   - 通过 Remote Control API 动态调整渲染参数
   - 监听集群事件进行响应式操作

3. **媒体集成**：
   - 使用 `SharedMemoryMedia` 节点进行视频输入/输出
   - 配置 `DisplayClusterMedia` 处理外部视频信号

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterSubsystem.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterRemoteControlTypes.h"
```

### 基本用法

```cpp
// 初始化 nDisplay 集群
void AMyGameMode::StartnDisplayCluster()
{
    // 获取 nDisplay 子系统
    UDisplayClusterSubsystem* nDisplaySubsystem = GetWorld()->GetSubsystem<UDisplayClusterSubsystem>();
    
    if (nDisplaySubsystem)
    {
        // 配置集群参数
        FDisplayClusterConfigurationCluster ClusterConfig;
        ClusterConfig.SyncPolicy = EDisplayClusterConfigurationClusterSyncPolicy::None;
        
        // 启动集群
        nDisplaySubsystem->StartCluster(ClusterConfig);
        
        // 设置渲染参数
        nDisplaySubsystem->SetRenderMode(EDisplayClusterConfigurationRenderMode::Mono);
    }
}
```

**来源**：DisplayCluster 模块基础 API

### 进阶用法

```cpp
// 通过 Remote Control API 控制渲染
void AMyActor::ControlDisplayCluster()
{
    UDisplayClusterSubsystem* nDisplaySubsystem = GetWorld()->GetSubsystem<UDisplayClusterSubsystem>();
    
    if (nDisplaySubsystem && nDisplaySubsystem->IsPrimary())
    {
        // 创建远程控制对象
        FDisplayClusterRemoteControlController RCController;
        
        // 设置对象属性
        FRCIPropertiesMetadata Properties;
        Properties.ObjectPath = TEXT("/Game/MyActor.MyActor");
        Properties.Properties.Add(FRCIPropertyMetadata{
            TEXT("Visibility"), 
            FRCIValueMetadata{true}
        });
        
        // 发送到集群节点
        RCController.SetObjectProperties(Properties);
        
        // 调用函数
        FRCIFunctionMetadata Function;
        Function.ObjectPath = TEXT("/Game/MyActor.MyActor");
        Function.FunctionName = TEXT("UpdateVisuals");
        
        RCController.InvokeCall(Function);
    }
}
```

**来源**：DisplayClusterRemoteControlInterceptor 模块

## Demo 示例

### 集群渲染控制器

```cpp
// DisplayClusterController.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DisplayClusterSubsystem.h"
#include "DisplayClusterController.generated.h"

UCLASS()
class ADisplayClusterController : public AActor
{
    GENERATED_BODY()
    
public:
    ADisplayClusterController();
    
protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    
    // 集群配置
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FDisplayClusterConfigurationCluster ClusterConfig;
    
    // 渲染目标
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    UTextureRenderTarget2D* RenderTarget;
    
private:
    UPROPERTY()
    UDisplayClusterSubsystem* nDisplaySubsystem;
    
    bool bClusterStarted;
};
```

```cpp
// DisplayClusterController.cpp
#include "DisplayClusterController.h"

ADisplayClusterController::ADisplayClusterController()
{
    PrimaryActorTick.bCanEverTick = true;
    
    // 默认集群配置
    ClusterConfig.SyncPolicy = EDisplayClusterConfigurationClusterSyncPolicy::None;
    ClusterConfig.RenderMode = EDisplayClusterConfigurationRenderMode::Mono;
}

void ADisplayClusterController::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取 nDisplay 子系统
    nDisplaySubsystem = GetWorld()->GetSubsystem<UDisplayClusterSubsystem>();
    
    if (nDisplaySubsystem)
    {
        // 配置投影设置
        FDisplayClusterConfigurationProjection ProjectionConfig;
        ProjectionConfig.Type = EDisplayClusterConfigurationProjectionType::MPCDI;
        
        // 应用配置
        ClusterConfig.Projection = ProjectionConfig;
        
        // 启动集群
        bClusterStarted = nDisplaySubsystem->StartCluster(ClusterConfig);
        
        if (bClusterStarted)
        {
            UE_LOG(LogTemp, Log, TEXT("nDisplay cluster started successfully"));
        }
    }
}

void ADisplayClusterController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    if (bClusterStarted && nDisplaySubsystem)
    {
        // 动态调整渲染参数
        if (GEngine->GetActiveStereoRenderingDevice())
        {
            // 立体渲染模式切换
            nDisplaySubsystem->SetRenderMode(
                nDisplaySubsystem->GetRenderMode() == EDisplayClusterConfigurationRenderMode::Mono 
                    ? EDisplayClusterConfigurationRenderMode::Stereo 
                    : EDisplayClusterConfigurationRenderMode::Mono
            );
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaFrameworkUtilities` | 处理视频输入/输出和媒体集成 |
| `MPCDI` | MPCDI 投影映射格式支持 |
| `WarpBlend` | 几何校正和边缘混合处理 |
| `SharedMemoryMedia` | 共享内存视频传输 |
| `DisplayClusterProjection` | 投影映射算法实现 |
| `DisplayClusterWarp` | 变形和校正处理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MoviePipeline 添加 EXR 多层渲染支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend 处理 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和不透明通道处理 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复非默认显示伽马的输出帧编码 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** - nDisplay 是 Epic Games 持续维护的专业解决方案：

- **最新更新**：最近一周内有多次功能性更新
- **功能演进**：持续添加新功能（如 EXR 多层支持、拓扑感知相机）
- **问题修复**：定期修复渲染问题和边缘案例
- **企业支持**：作为企业版功能得到专门支持
- **兼容性**：支持 Win64 和 Linux 平台

**建议**：
- 适用于专业沉浸式显示项目
- 需要专门的硬件设置和配置
- 学习曲线较陡，但提供强大功能
- 建议参考 Epic 官方示例项目和文档

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)
- [Remote Control API](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterRemoteControlInterceptor)
- [MPCDI 格式](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/ThirdParty/ScalableMPCDI)