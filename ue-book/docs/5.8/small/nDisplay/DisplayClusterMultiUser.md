# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterDetails` (Runtime), `SharedMemoryMedia` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `SharedMemoryMediaEditor` (Runtime), `DisplayClusterTests` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

> ⚠️ **此插件默认未启用**。需在 `Edit → Plugins` 中手动启用，或在 `.uproject` 文件中添加 `"Enabled": true`。

---

## 用途

nDisplay 是 Unreal Engine 的**集群渲染系统**，用于将一个 UE 项目同步输出到多台 PC 和多个显示器上，构成大规模沉浸式显示环境。

它解决的核心问题是：**如何让一个 UE 场景跨越多台物理机器和多个投影面，实现像素精确的同步渲染？**

典型应用包括：
- **LED 虚拟摄影棚（Virtual Production）**：多块 LED 墙组成的拍摄棚，每块墙由独立 GPU 驱动，所有画面必须帧同步
- **穹顶/CAVE 沉浸式空间**：多台投影仪投射到球幕或多面体墙壁上，需要几何校正（Warp）和边缘融合（Blend）
- **多显示器驾驶模拟器**：多个屏幕环绕驾驶员，视野无缝拼接
- **大型LED舞台演出**：Live Events 中多屏内容同步播放

该插件之所以存在，是因为单台 PC 无法同时驱动如此多的高分辨率显示输出，必须通过多机集群实现分布式渲染，同时保证帧同步和视角一致性。

---

## 系统架构概览

nDisplay 的 29 个模块可按功能划分为以下子系统：

| 子系统 | 关键模块 | 职责 |
|---|---|---|
| **核心运行时** | `DisplayCluster`, `DisplayClusterConfiguration` | 集群通信、节点同步、配置管理 |
| **投影与变形** | `DisplayClusterProjection`, `DisplayClusterWarp`, `ScalableMPCDI` | 多种投影模型（平面/穹顶/MPCDI）、几何校正与边缘融合 |
| **渲染管线** | `DisplayClusterShaders`, `DisplayClusterColorGrading`, `DisplayClusterFillDerivedDataCache` | 专用着色器、色彩分级、DDC 预填充 |
| **媒体与纹理** | `DisplayClusterMedia`, `SharedMemoryMedia`, `DisplayClusterMessageInterception` | 视频输入/输出、共享内存帧传输 |
| **虚拟制片** | `DisplayClusterLightCardEditor`, `DisplayClusterOperator`, `DisplayClusterStageMonitoring` | LED 面板管理、操作面板、现场监控 |
| **多用户协作** | `DisplayClusterMultiUser`, `DisplayClusterReplication` | Concert 多用户同步、资产复制 |
| **远程控制** | `DisplayClusterRemoteControlInterceptor` | Remote Control 插件集成 |
| **影片渲染** | `DisplayClusterMoviePipeline`, `DisplayClusterMoviePipelineEditor` | Movie Render Queue 集成 |
| **编辑器工具** | `DisplayClusterConfigurator`, `DisplayClusterEditor`, `DisplayClusterDetails`, `DisplayClusterMonitor*` | 可视化配置编辑器、节点监控 |
| **测试** | `DisplayClusterTests` | 自动化测试 |

---

## 使用场景

- 你在搭建 LED 虚拟摄影棚（如 Unreal Stage） → 使用 nDisplay + ICVFX 工作流
- 你需要将场景投射到穹顶或 CAVE 多面体 → 使用 nDisplay + MPCDI/自定义投影
- 你有多台 PC 需要帧同步渲染同一场景 → 使用 nDisplay 的集群同步机制
- 你想在 Movie Render Queue 中从多个视角同时渲染 → 使用 nDisplay Movie Pipeline 集成
- 你需要将视频输入（SDI/HDMI）作为 LED 面板纹理 → 使用 nDisplay Media 模块

---

## 蓝图用法

> ⚠️ 由于当前分析模块 `DisplayClusterMultiUser` 仅包含私有头文件，以下蓝图 API 基于 nDisplay 核心运行时的公开接口整理。

nDisplay 的主要蓝图交互通过 **nDisplay 节点（Display Cluster Node）** 和 **配置资产** 进行，大部分高级操作通过编辑器工具完成。运行时可通过蓝图访问以下功能：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node ID` | 获取当前集群节点的唯一标识符 | `UDisplayClusterBlueprintAPI` |
| `Is Primary Node` | 判断当前节点是否为主节点（Primary） | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Viewport Info` | 获取指定视口的尺寸和投影信息 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1. 在任意蓝图中添加 **"Get Cluster Node ID"** 节点，根据返回的字符串判断当前运行的集群节点，执行节点特定逻辑（如不同屏幕显示不同 UI）
2. 通过 **"Is Primary Node"** 判断是否为主节点，主节点通常负责全局控制（如触发场景切换），从节点仅执行渲染

---

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterModule.h"
#include "DisplayClusterConfigurationTypes.h"
```

### 基本用法

获取 nDisplay 模块实例，查询集群状态：

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayCluster/Public/DisplayClusterModule.h
IDisplayClusterModule& DisplayClusterModule = FModuleManager::GetModuleChecked<IDisplayClusterModule>("DisplayCluster");

// 检查 nDisplay 是否已激活（是否通过 nDisplay 启动）
if (DisplayClusterModule.IsModuleInitialized())
{
    // 获取当前节点 ID
    FString NodeId = DisplayClusterModule.GetNodeId();
    
    // 判断是否为主节点
    bool bIsPrimary = DisplayClusterModule.IsPrimary();
    
    UE_LOG(LogTemp, Log, TEXT("Node: %s, Primary: %s"), *NodeId, bIsPrimary ? TEXT("Yes") : TEXT("No"));
}
```

### Multi-User 集成用法

`DisplayClusterMultiUser` 模块通过 Unreal 的 Concert 多用户编辑系统同步 Media Plate 状态：

```cpp
// 来源: Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMultiUser/Private/MediaAssetMultiUserManager.h
// FMediaAssetMultiUserManager 在编辑器中自动注册到 Concert Session

// 当 Media Plate 状态变化时，该管理器会：
// 1. 本地广播变更 → 捕获事件并通过 Concert 发送给所有远程端点
// 2. 远程端点收到事件 → OnStateChangedEvent() 转发给本地 Media Plate

// 状态通过 FConcertMediaStateChangedEvent 结构体传递：
// - ActorsPathNames: 目标 Media Plate Actor 的路径（用于跨机器定位对象）
// - State: 要同步的状态枚举值
```

---

## Demo 示例

> ⚠️ nDisplay 的完整使用需要多台物理机器和投影/显示硬件，无法以单一代码文件演示。以下为最简化的集群节点检测示例。

### MyClusterAwareActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyClusterAwareActor.generated.h"

UCLASS()
class AMyClusterAwareActor : public AActor
{
    GENERATED_BODY()

public:
    AMyClusterAwareActor();

    virtual void BeginPlay() override;

    /** 仅在主节点上执行的操作 */
    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    void DoPrimaryOnlyAction();

protected:
    /** 当前节点是否为主节点 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "nDisplay Demo")
    bool bIsPrimaryNode;

    /** 当前节点 ID */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "nDisplay Demo")
    FString CurrentNodeId;
};
```

### MyClusterAwareActor.cpp

```cpp
#include "MyClusterAwareActor.h"
#include "DisplayClusterModule.h"

AMyClusterAwareActor::AMyClusterAwareActor()
{
    PrimaryActorTick.bCanEverTick = false;
    bIsPrimaryNode = false;
}

void AMyClusterAwareActor::BeginPlay()
{
    Super::BeginPlay();

    IDisplayClusterModule* DCModule = FModuleManager::GetModulePtr<IDisplayClusterModule>("DisplayCluster");
    if (DCModule && DCModule->IsModuleInitialized())
    {
        bIsPrimaryNode = DCModule->IsPrimary();
        CurrentNodeId = DCModule->GetNodeId();
        UE_LOG(LogTemp, Log, TEXT("[nDisplay] Node '%s', Primary: %d"), *CurrentNodeId, bIsPrimaryNode);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("[nDisplay] Module not active, running standalone."));
    }
}

void AMyClusterAwareActor::DoPrimaryOnlyAction()
{
    if (bIsPrimaryNode)
    {
        UE_LOG(LogTemp, Log, TEXT("[nDisplay] Executing primary-only action on node '%s'"), *CurrentNodeId);
        // 主节点专用逻辑：如触发场景切换、控制所有节点等
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("[nDisplay] Action skipped on non-primary node '%s'"), *CurrentNodeId);
    }
}
```

---

## 模块依赖

以下为 nDisplay 各模块的**独特依赖**（已省略 Core/CoreUObject/Engine 等标准依赖）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器工具、配置器、事务处理 |
| `EditorWidgets` | 自定义编辑器控件 |
| `LevelEditor` | 关卡编辑器集成 |
| `D3D12RHI` | DirectX 12 共享内存媒体传输（SharedMemoryMedia） |
| `Concert` / `ConcertSyncClient` | Multi-User 多用户编辑会话（DisplayClusterMultiUser） |
| `MovieRenderPipelineCore` | Movie Render Queue 集成（DisplayClusterMoviePipeline） |
| `RemoteControlAPI` | Remote Control 插件集成（DisplayClusterRemoteControlInterceptor） |

> 使用者需根据具体需求选择依赖的子模块。如果只需要集群渲染核心功能，依赖 `DisplayCluster` 即可。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | Movie Pipeline 支持多层 EXR 输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和 MPCDI 着色器透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码时尊重非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

**🟢 活跃维护中** — 这是 Unreal Engine 中维护最活跃的插件之一。

- **创建时间**：2018 年（UE 4.20 时期），随 Unreal Stage / Virtual Production 工作流一同成长
- **最近更新**：2026 年 5 月仍有密集的功能更新和 Bug 修复（几乎每周都有提交）
- **开发团队**：由 Epic Games 虚拟制片团队直接维护，是 Unreal Stage 的核心组件
- **代码规模**：1351 个源文件、29 个模块，属于超大型插件
- **推荐使用**：✅ 强烈推荐用于任何多屏/集群渲染场景。作为 Epic 官方支持的虚拟制片基础设施，其稳定性、文档和社区支持都属一流

> 该插件默认禁用（`EnabledByDefault: false`）是合理的，因为绝大多数项目不需要集群渲染，启用后会增加编译时间和包体大小。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)（虚幻引擎官方 nDisplay 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)