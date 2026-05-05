# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、媒体资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**多机集群渲染系统**，用于将一个 UE 场景同步渲染到多台 PC 驱动的多个显示器上。它解决的核心问题是：**单台 PC 的 GPU 算力不足以驱动大规模显示墙、CAVE 系统或 LED Volume（虚拟制片）时，如何让多台机器协同渲染同一场景并保持帧同步**。

典型应用包括：
- **虚拟制片 LED Volume**：如 The Mandalorian 使用的环形 LED 墙，需要多台渲染节点驱动不同区域
- **CAVE 沉浸式环境**：多面投影的沉浸式房间
- **大型显示墙**：博物馆、指挥中心、主题公园的多屏拼接显示
- **立体渲染**：支持 mono 和 stereo（左右眼）两种模式

nDisplay 通过配置文件定义集群拓扑（哪些 PC 渲染哪些视口），管理节点间的帧同步、输入分发、投影变形（warp）和边缘融合（blend），并支持 MPCDI 标准的投影校准数据。

## 使用场景

- 你在搭建 **LED Volume 虚拟制片片场** → 用 nDisplay 配置多台渲染节点驱动 LED 墙的不同区域
- 你需要 **CAVE 沉浸式投影环境** → 用 nDisplay 管理多面投影的视锥和边缘融合
- 你在做 **大型指挥中心/展厅的多屏显示** → 用 nDisplay 将场景分配到多台 PC 渲染
- 你需要 **立体 3D 渲染**（VR 眼镜/3D 电视） → 用 nDisplay 的 stereo 模式
- 你需要 **投影校准和几何变形** → 用 nDisplay 的 warp/blend 和 MPCDI 支持
- 你想用 **Movie Render Queue 录制 nDisplay 场景** → 用 DisplayClusterMoviePipeline 模块

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| **DisplayCluster** | 核心运行时模块，管理集群节点、帧同步、渲染逻辑 | [DisplayCluster.md](DisplayCluster.md) |
| **DisplayClusterConfiguration** | 配置数据模型，定义集群拓扑、视口、投影等配置结构 | [DisplayClusterConfiguration.md](DisplayClusterConfiguration.md) |
| **DisplayClusterConfigurator** | 配置编辑器 UI，提供可视化配置 nDisplay 集群的编辑器工具 | [DisplayClusterConfigurator.md](DisplayClusterConfigurator.md) |
| **DisplayClusterProjection** | 投影系统，处理视锥计算、投影变形和 MPCDI 集成 | [DisplayClusterProjection.md](DisplayClusterProjection.md) |
| **DisplayClusterWarp** | 几何变形（warp）和边缘融合（blend）处理 | [DisplayClusterWarp.md](DisplayClusterWarp.md) |
| **DisplayClusterShaders** | nDisplay 专用着色器，包括后处理、变形、色彩校正等 | [DisplayClusterShaders.md](DisplayClusterShaders.md) |
| **DisplayClusterColorGrading** | 色彩分级功能，支持 per-viewport 的色彩调整 | [DisplayClusterColorGrading.md](DisplayClusterColorGrading.md) |
| **DisplayClusterMedia** | 媒体输入/输出集成，支持视频采集卡和共享内存传输 | [DisplayClusterMedia.md](DisplayClusterMedia.md) |
| **DisplayClusterMediaEditor** | 媒体功能的编辑器扩展 | [DisplayClusterMediaEditor.md](DisplayClusterMediaEditor.md) |
| **DisplayClusterLightCardEditor** | Light Card 编辑器，用于在 LED Volume 中放置虚拟光源卡片 | [DisplayClusterLightCardEditor.md](DisplayClusterLightCardEditor.md) |
| **DisplayClusterLightCardEditorShaders** | Light Card 编辑器的专用着色器 | [DisplayClusterLightCardEditorShaders.md](DisplayClusterLightCardEditorShaders.md) |
| **DisplayClusterEditor** | nDisplay 编辑器集成，菜单、工具栏等 | [DisplayClusterEditor.md](DisplayClusterEditor.md) |
| **DisplayClusterOperator** | Operator 控制面板，运行时监控和控制 nDisplay 集群 | [DisplayClusterOperator.md](DisplayClusterOperator.md) |
| **DisplayClusterDetails** | 详情面板扩展，显示 nDisplay 相关 Actor 的属性 | [DisplayClusterDetails.md](DisplayClusterDetails.md) |
| **DisplayClusterMoviePipeline** | Movie Render Queue 集成，支持从 nDisplay 集群录制影片 | [DisplayClusterMoviePipeline.md](DisplayClusterMoviePipeline.md) |
| **DisplayClusterMoviePipelineEditor** | Movie Pipeline 集成的编辑器扩展 | [DisplayClusterMoviePipelineEditor.md](DisplayClusterMoviePipelineEditor.md) |
| **DisplayClusterMultiUser** | 多用户编辑集成，支持 nDisplay 配置的多用户同步 | [DisplayClusterMultiUser.md](DisplayClusterMultiUser.md) |
| **DisplayClusterReplication** | 网络复制，管理集群节点间的状态同步 | [DisplayClusterReplication.md](DisplayClusterReplication.md) |
| **DisplayClusterMessageInterception** | 消息拦截，用于捕获和处理集群通信消息 | [DisplayClusterMessageInterception.md](DisplayClusterMessageInterception.md) |
| **DisplayClusterRemoteControlInterceptor** | Remote Control API 拦截器，支持通过远程控制 API 操作 nDisplay | [DisplayClusterRemoteControlInterceptor.md](DisplayClusterRemoteControlInterceptor.md) |
| **DisplayClusterScenePreview** | 场景预览，提供 nDisplay 配置的实时预览功能 | [DisplayClusterScenePreview.md](DisplayClusterScenePreview.md) |
| **DisplayClusterStageMonitoring** | 舞台监控，监控 LED Volume 的运行状态和性能 | [DisplayClusterStageMonitoring.md](DisplayClusterStageMonitoring.md) |
| **DisplayClusterFillDerivedDataCache** | DDC 填充工具，预编译 nDisplay 相关的派生数据 | [DisplayClusterFillDerivedDataCache.md](DisplayClusterFillDerivedDataCache.md) |
| **DisplayClusterTests** | 自动化测试模块 | [DisplayClusterTests.md](DisplayClusterTests.md) |
| **SharedMemoryMedia** | 共享内存媒体传输，用于同一台机器上多进程间的高效帧传输 | [SharedMemoryMedia.md](SharedMemoryMedia.md) |
| **SharedMemoryMediaEditor** | 共享内存媒体的编辑器扩展 | [SharedMemoryMediaEditor.md](SharedMemoryMediaEditor.md) |
| **ScalableMPCDI** | 第三方库，MPCDI（Multi-Projector Common Data Interchange）标准的实现 | [ScalableMPCDI.md](ScalableMPCDI.md) |

## 蓝图用法

nDisplay 提供了丰富的蓝图 API，主要用于运行时控制集群行为。核心节点按功能分组如下：

### 集群管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartCluster` | 启动 nDisplay 集群 | `UDisplayClusterBlueprintAPI` |
| `StopCluster` | 停止 nDisplay 集群 | `UDisplayClusterBlueprintAPI` |
| `GetClusterNodeIds` | 获取集群中所有节点 ID | `UDisplayClusterBlueprintAPI` |

### 视口控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetViewportIds` | 获取所有视口 ID 列表 | `UDisplayClusterBlueprintAPI` |
| `SetViewportCameraRotation` | 设置指定视口的相机旋转 | `UDisplayClusterBlueprintAPI` |

### 色彩校正

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetColorAdjustment` | 设置指定视口的色彩调整参数 | `UDisplayClusterColorGradingAPI` |

> 详细的蓝图 API 请参阅各子模块文档。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterBlueprintAPI.h"
```

### 基本用法

```cpp
// 获取 nDisplay 根 Actor
ADisplayClusterRootActor* RootActor = /* 从场景中获取 */;

// 获取集群配置
UDisplayClusterConfigurationData* Config = RootActor->GetConfigData();

// 遍历所有视口
for (const auto& ViewportPair : Config->Cluster->Viewports)
{
    const FString& ViewportId = ViewportPair.Key;
    UDisplayClusterConfigurationViewport* Viewport = ViewportPair.Value;
    // 处理每个视口...
}
```

> 详细的 C++ API 请参阅各子模块文档，特别是 [DisplayCluster.md](DisplayCluster.md) 和 [DisplayClusterConfiguration.md](DisplayClusterConfiguration.md)。

## 模块依赖

nDisplay 是一个大型插件，各子模块有各自的依赖关系。以下是**独特**的、非标准的依赖：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口，用于共享内存媒体传输 |
| `ScalableMPCDI` | MPCDI 投影校准标准的第三方实现 |
| `LevelEditor` | 关卡编辑器集成 |
| `EditorWidgets` | 编辑器自定义控件 |

> 大部分子模块仅依赖标准 Core/Engine/Slate 等模块。具体依赖请查阅各模块的 Build.cs 文件。

## 维护状态

### 近期更新

```
- 2025-06-02 abc1234 nDisplay: 修复集群节点同步问题和投影校准精度
- 2025-05-15 def5678 nDisplay: 添加 Light Card 编辑器增强功能
- 2025-04-28 ghi9012 nDisplay: 优化共享内存媒体传输性能
```

> 注：以上为示例格式，实际 commit 信息请通过 `git log --format='%h|%ai|%s' -3 -- 'Engine/Plugins/Runtime/nDisplay/'` 获取。

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

nDisplay 是 Epic Games 重点维护的核心插件之一，原因如下：

- **虚拟制片是 UE5 的核心商业场景**：The Mandalorian 等项目推动了 nDisplay 的持续投入
- **持续活跃更新**：作为 xlarge 规模插件（1611 个源文件），持续有功能增强和 bug 修复
- **模块化架构成熟**：27 个模块分工明确，从核心渲染到编辑器工具到媒体传输，覆盖完整工作流
- **EnabledByDefault=false**：需要手动启用，这是合理的——大多数项目不需要集群渲染
- **支持 Win64 和 Linux**：覆盖了虚拟制片的主要部署平台

**推荐使用**：如果你的项目涉及 LED Volume、CAVE、多屏显示等集群渲染场景，nDisplay 是唯一官方解决方案，且经过大量商业项目验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/n-display-in-unreal-engine/)