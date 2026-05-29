# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的多机集群渲染框架，解决的核心问题是：**如何让多台 PC 同步渲染同一个场景，并输出到多个物理显示设备上**。

典型应用场景：
- **LED 虚拟影棚（Virtual Production）**：多个 LED 面板拼接成一面墙，每块面板由独立 PC 渲染
- **CAVE 系统**：多面投影环境，每面墙由独立 PC 驱动
- **多屏展示**：大型展会、主题公园的环绕式屏幕

该插件包含 29 个子模块，覆盖从配置、投影、校准、媒体输出、电影渲染管线到多用户同步的完整工作流。本文档聚焦于 **DisplayClusterMonitorEditor** 模块——集群监控编辑器。

**DisplayClusterMonitorEditor** 的职责是提供一个编辑器内的监控面板，让你能：
- 发现并浏览集群中所有节点和可观察对象（Viewports、Backbuffer、ICVFX Camera 等）
- 实时查看各节点的渲染画面（通过 NDI 媒体流）
- 管理观察会话（开始/暂停/停止）
- 监控节点连接状态和健康状况

## 使用场景

- 你在搭建 LED 虚拟影棚 → 用 nDisplay 配置集群拓扑和投影
- 你需要在编辑器中远程查看各集群节点的渲染输出 → 用 DisplayClusterMonitorEditor 的集群监控面板
- 你需要调试某个节点的画面是否有问题 → 用监控面板的观察会话功能
- 你需要通过 Movie Pipeline 录制 nDisplay 输出 → 用 DisplayClusterMoviePipeline

## 蓝图用法

DisplayClusterMonitorEditor 是一个纯编辑器 UI 模块，不暴露蓝图 API。它的功能通过编辑器菜单栏的 **Cluster Monitor** 面板访问。

## C++ 用法

### 头文件引入

```cpp
#include "Core/IClusterMonitorController.h"
#include "Core/IClusterObservable.h"
#include "Core/IClusterResidence.h"
```

### 基本用法：创建集群监控控制器

```cpp
// 来源: Private/Core/ClusterMonitorController.h
#include "Core/IClusterMonitorController.h"
#include "Core/ClusterMonitorController.h"

// 创建监控控制器实例
TSharedRef<FClusterMonitorController> Controller = MakeShared<FClusterMonitorController>();

// 启动通信（开始集群发现和消息传递）
bool bStarted = Controller->StartCommunication();

// 获取当前发现的可观察对象数量
int32 ObservableCount = Controller->GetObservablesNum();
int32 ActiveSessions = Controller->GetActiveSessionsNum();
int32 UnresponsiveNodes = Controller->GetUnresponsiveNodesNum();
```

### 基本用法：监听集群事件

```cpp
// 来源: Private/Core/IClusterMonitorController.h

// 监听新的可观察对象被发现
Controller->OnObservableJoined().AddLambda(
    [](const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogClusterMonitorEditor, Log, TEXT("Observable joined: %s [%s]"),
            *Observable->GetName(),
            *Observable->GetId().ToString());
    });

// 监听可观察对象状态更新
Controller->OnObservableUpdated().AddLambda(
    [](const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogClusterMonitorEditor, Log, TEXT("Observable updated: %s"),
            *Observable->GetName());
    });

// 监听可观察对象离线
Controller->OnObservableLeft().AddLambda(
    [](const TSharedRef<IClusterObservable>& Observable, const FString& Reason)
    {
        UE_LOG(LogClusterMonitorEditor, Warning, TEXT("Observable left: %s, Reason: %s"),
            *Observable->GetName(), *Reason);
    });

// 监听节点超时（无响应）
Controller->OnObservableTimeout().AddLambda(
    [](const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogClusterMonitorEditor, Warning, TEXT("Observable timeout: %s"),
            *Observable->GetName());
    });
```

### 进阶用法：管理观察会话

```cpp
// 来源: Private/Core/IClusterMonitorController.h, Private/Core/IClusterObservable.h

// 监听会话状态变化
Controller->OnSessionStarted().AddLambda(
    [](const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogClusterMonitorEditor, Log, TEXT("Session started for: %s"),
            *Observable->GetName());
    });

Controller->OnSessionStopped().AddLambda(
    [](const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogClusterMonitorEditor, Log, TEXT("Session stopped for: %s"),
            *Observable->GetName());
    });

// 请求启动某个可观察对象的观察会话
FGuid TargetObservableId = /* ... */;
Controller->RequestSessionStart(TargetObservableId);

// 请求停止特定会话
Controller->RequestSessionStop(TargetObservableId);

// 请求停止所有活跃会话
Controller->RequestAllSessionsStop();

// 重新扫描集群
Controller->Rescan();

// 清除所有无响应节点
Controller->ClearUnresponsiveEndpoints();
```

### 进阶用法：查询可观察对象详情

```cpp
// 来源: Private/Core/IClusterObservable.h, Private/Core/IClusterResidence.h

// 获取特定可观察对象
TSharedPtr<IClusterObservable> Observable = Controller->GetObservable(ObservableId);
if (Observable.IsValid())
{
    // 基本信息
    FString Name = Observable->GetName();
    EDCObservableType Type = Observable->GetType();
    FIntPoint Resolution = Observable->GetResolution();

    // 是否是 Tile（拼接块）
    bool bIsTile = Observable->IsTile();
    if (bIsTile)
    {
        TOptional<FString> ParentName = Observable->GetParentName();
        TOptional<FIntPoint> TilePos = Observable->GetTilePos();
    }

    // 获取所属的集群节点（Residence）
    TSharedRef<IClusterResidence> Residence = Observable->GetResidence();
    FString ClusterName = Residence->GetClusterName();
    FString NodeName = Residence->GetNodeName();
    FString Hostname = Residence->GetHostname();
    bool bIsOffscreen = Residence->IsNodeOffscreen();
    IClusterResidence::EConnectionState ConnState = Residence->GetConnectionState();

    // 会话控制
    IClusterObservable::ESessionState SessionState = Observable->GetSessionState();
    if (Observable->IsSessionRunning())
    {
        Observable->Play();
        // Observable->Pause();
        // Observable->Stop();
    }

    // 获取媒体资源（用于自定义渲染）
    UNDIMediaSource* MediaSource = Observable->GetMediaSource();
    UMediaTexture* MediaTexture = Observable->GetMediaTexture();
    UMediaPlayer* MediaPlayer = Observable->GetMediaPlayer();
}
```

## Demo 示例

### DisplayClusterMonitorEditor 模块入口

```cpp
// DCMonitorEditorModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FDCMonitorEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// DCMonitorEditorModule.cpp
#include "DCMonitorEditorModule.h"
#include "DCMonitorEditorLog.h"
#include "DCMonitorEditorStyle.h"
#include "Widgets/SClusterMonitorPanel.h"

DEFINE_LOG_CATEGORY(LogClusterMonitorEditor);

static const FLazyName NAME_ClusterMonitor_Container("nDisplay");
static const FLazyName NAME_ClusterMonitor_Category("Cluster Monitor");
static const FLazyName NAME_ClusterMonitor_Section("General");

void FDCMonitorEditorModule::StartupModule()
{
    // 注册编辑器样式
    FDCMonitorEditorStyle::Get();

    // 注册设置项和 UI 面板标签页
    RegisterSettings();
    RegisterTabs();
}

void FDCMonitorEditorModule::ShutdownModule()
{
    UnregisterSettings();
    UnregisterTabs();
}
```

### 自定义监控面板集成示例

```cpp
// MyMonitorExtension.h
#pragma once

#include "CoreMinimal.h"
#include "Core/IClusterMonitorController.h"
#include "Core/IClusterObservable.h"

// 演示如何在自定义模块中集成集群监控功能
class FMyMonitorExtension
{
public:
    void Initialize(TSharedRef<IClusterMonitorController> InController)
    {
        Controller = InController;

        // 绑定事件
        Controller->OnObservableJoined().AddSP(
            SharedThis(this), &FMyMonitorExtension::HandleObservableJoined);

        Controller->OnObservableTimeout().AddSP(
            SharedThis(this), &FMyMonitorExtension::HandleObservableTimeout);

        // 启动通信
        Controller->StartCommunication();
    }

    void Shutdown()
    {
        if (Controller.IsValid())
        {
            Controller->StopCommunication();
            Controller.Reset();
        }
    }

    // 列出所有当前活跃的可观察对象
    void ListAllObservables()
    {
        int32 Count = Controller->GetObservablesNum();
        UE_LOG(LogTemp, Log, TEXT("Found %d observables in cluster"), Count);

        // 注意：接口未提供遍历所有 Observable 的方法，
        // 需通过事件回调逐个收集
    }

private:
    void HandleObservableJoined(const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogTemp, Log, TEXT("[Joined] %s (Type: %d) on node: %s"),
            *Observable->GetName(),
            static_cast<int32>(Observable->GetType()),
            *Observable->GetResidence()->GetNodeName());
    }

    void HandleObservableTimeout(const TSharedRef<IClusterObservable>& Observable)
    {
        UE_LOG(LogTemp, Warning, TEXT("[Timeout] %s on host: %s"),
            *Observable->GetName(),
            *Observable->GetResidence()->GetHostname());
    }

    TSharedPtr<IClusterMonitorController> Controller;
};
```

## 模块依赖

DisplayClusterMonitorEditor 模块自身 Build.cs 中的特殊依赖：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器框架集成（设置注册、标签页管理） |

nDisplay 插件整体还有其他独特依赖（跨模块）：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口（DisplayClusterMedia, SharedMemoryMedia） |
| `LevelEditor` | 关卡编辑器集成（DisplayCluster） |
| `EditorWidgets` | 编辑器控件（DisplayCluster） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 添加 EXR 多层渲染支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和 MPCDI/ICVFX 着色器的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** ★★★★★

- **创建于 2018 年**，约 8 年历史，是 UE 虚拟制片（Virtual Production）核心功能之一
- **最近一周内有多次提交**（2026-05-16 至 2026-05-26），更新频率极高
- 更新内容涵盖功能增强（EXR 多层支持、WarpBlend 模式合并）和 Bug 修复（着色器、Gamma、闪烁）
- 作为 Epic Games 官方维护的虚拟制片基础设施，长期获得持续投入
- `EnabledByDefault: false` 表示该插件需要手动启用，适合特定的虚拟制片/多屏渲染场景
- **强烈推荐**用于 LED 虚拟影棚、多机集群渲染等专业场景

> ⚠️ 注意：这是一个超大型插件（29 个模块，1351 个源文件），本文档仅覆盖 DisplayClusterMonitorEditor 模块。完整文档需要按子模块拆分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：（未提供 DocsURL，请参考 [UE 官方 nDisplay 文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)）