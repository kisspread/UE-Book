# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay) | |

---

## 用途

nDisplay 是 Unreal Engine 的**多机集群渲染（Clustered Rendering）**系统，用于将一个 UE 场景的渲染输出**同步分发到多台 PC**，驱动多块屏幕或投影仪，组成一个大型沉浸式显示环境。

核心解决的问题：

- **视锥分割**：将一个摄像机的视锥按物理屏幕布局拆分为多个子视锥，每台渲染节点负责其中一块
- **帧同步**：通过网络协议确保所有渲染节点在同一帧渲染相同的内容，避免撕裂和延迟
- **投影变形**：支持平面、圆柱、球面、MPCDI 等多种投影映射方式，适配 CAVE、LED Volume、穹顶等非平面显示设备
- **立体渲染**：支持单目（Mono）和立体（Stereo）渲染模式，用于 VR/AR 虚拟制作场景
- **虚拟制作（Virtual Production）**：与 LED Volume、摄像机追踪系统配合，实现实时合成拍摄

nDisplay 不是一个简单的多屏扩展——它是一个完整的**分布式渲染集群管理框架**，包含配置系统、网络同步、投影校准、色彩管理、媒体输入输出、远程控制等全套基础设施。

## 使用场景

- **LED Volume 虚拟制作**：你在搭建一个 LED 墙体摄影棚，需要多台渲染 PC 驱动 LED 屏幕，且与摄像机追踪系统实时同步 → 用 nDisplay
- **CAVE 沉浸式环境**：你在构建一个多面投影的 CAVE 系统（如 4 面或 6 面投影），需要精确的投影几何校正 → 用 nDisplay + MPCDI
- **穹顶投影**：你需要将渲染内容投影到半球形穹顶上，涉及复杂的鱼眼或等距柱状投影 → 用 nDisplay
- **多屏模拟器**：你在开发驾驶/飞行模拟器，需要多台 PC 分别渲染不同视角的窗外场景 → 用 nDisplay
- **大型活动/展览**：你需要在不规则形状的显示装置上渲染内容（如建筑投影映射）→ 用 nDisplay
- **电影级离线渲染**：你需要用 Movie Render Queue 从 nDisplay 集群输出高分辨率序列帧 → 用 nDisplay + DisplayClusterMoviePipeline

## 模块架构概览

nDisplay 由 27 个模块组成，按功能域划分：

### 核心运行时
| 模块 | 职责 |
|---|---|
| `DisplayCluster` | 主模块，集群同步引擎、渲染逻辑、网络通信 |
| `DisplayClusterConfiguration` | 配置数据模型（.ndisplay 配置文件解析） |
| `DisplayClusterProjection` | 投影策略（平面、MPCDI、UV 等） |
| `DisplayClusterWarp` | 网格变形（Warp）和几何校正 |
| `DisplayClusterShaders` | nDisplay 专用着色器 |
| `DisplayClusterReplication` | 集群节点间状态同步 |
| `DisplayClusterMessageInterception` | 网络消息拦截和路由 |

### 媒体与色彩
| 模块 | 职责 |
|---|---|
| `DisplayClusterMedia` | 媒体输入输出（视频采集卡、SDI 等） |
| `DisplayClusterColorGrading` | 色彩分级和 LUT 管理 |
| `SharedMemoryMedia` | 共享内存媒体传输（低延迟帧传输） |

### 编辑器工具
| 模块 | 职责 |
|---|---|
| `DisplayClusterEditor` | 编辑器引擎扩展（PIE 集成） |
| `DisplayClusterConfigurator` | 可视化配置编辑器 |
| `DisplayClusterOperator` | 运行时操作面板 |
| `DisplayClusterLightCardEditor` | Light Card 编辑器 |
| `DisplayClusterDetails` | 详细信息面板 |
| `DisplayClusterScenePreview` | 场景预览窗口 |

### 集成功能
| 模块 | 职责 |
|---|---|
| `DisplayClusterMoviePipeline` | Movie Render Queue 集成 |
| `DisplayClusterMultiUser` | Multi-User Editing 集成 |
| `DisplayClusterRemoteControlInterceptor` | Remote Control API 集成 |
| `DisplayClusterStageMonitoring` | 舞台监控和诊断 |

### 第三方
| 模块 | 职责 |
|---|---|
| `ScalableMPCDI` | MPCDI 标准的外部实现库 |

---

## 子模块文档

> ⚠️ 本插件包含 1611 个源文件，属于 **xlarge** 规模。以下按子模块拆分文档。

- [DisplayClusterEditor](#displayclustereditor) — 编辑器引擎扩展

---

# DisplayClusterEditor

## 用途

DisplayClusterEditor 是 nDisplay 的**编辑器集成模块**，通过扩展 `UUnrealEdEngine` 来管理 nDisplay 在编辑器 Play-In-Editor（PIE）会话中的生命周期。

该模块解决的核心问题：当用户在编辑器中点击"Play"时，nDisplay 需要判断当前场景是否包含 nDisplay Root Actor，如果包含则启动集群渲染模式（而非普通 PIE），并在会话结束时正确清理集群资源。

## 蓝图用法

本模块不暴露蓝图 API。它是一个纯 C++ 编辑器引擎扩展模块，所有功能在引擎层面自动运行。

## C++ 用法

### 头文件引入

```cpp
#include "IDisplayClusterEditor.h"
#include "DisplayClusterEditorEngine.h"
```

### 模块接口

`IDisplayClusterEditor` 是一个极简的模块接口，仅提供标准的 `IModuleInterface` 生命周期：

```cpp
// 获取模块实例
IDisplayClusterEditor& EditorModule = FModuleManager::GetModuleChecked<IDisplayClusterEditor>("DisplayClusterEditor");
```

### 编辑器引擎扩展

`UDisplayClusterEditorEngine` 继承自 `UUnrealEdEngine`，重写了以下关键方法：

| 方法 | 说明 |
|---|---|
| `Init()` | 引擎初始化时注册 nDisplay 模块引用 |
| `PreExit()` | 引擎退出前清理 nDisplay 资源 |
| `StartPlayInEditorSession()` | PIE 启动时检测 nDisplay Root Actor，决定是否启用集群模式 |
| `LoadMap()` | 地图加载时的 nDisplay 初始化逻辑 |
| `Tick()` | 每帧更新，维护 nDisplay PIE 会话状态 |

### PIE 生命周期管理

该模块通过委托监听 PIE 的开始和结束事件：

```cpp
// PIE 开始回调
void UDisplayClusterEditorEngine::OnBeginPIE(const bool bSimulate)
{
    // 检测当前世界中是否存在 ADisplayClusterRootActor
    // 如果存在，设置 bIsNDisplayPIE = true，启动集群渲染
}

// PIE 结束回调
void UDisplayClusterEditorEngine::OnEndPIE(const bool bSimulate)
{
    // 清理 nDisplay 集群会话
    // 重置 bIsNDisplayPIE 和 bIsActivePIE 标志
}
```

### Root Actor 检测

```cpp
// 在当前世界中查找 nDisplay Root Actor
ADisplayClusterRootActor* UDisplayClusterEditorEngine::FindDisplayClusterRootActor(UWorld* InWorld)
{
    // 遍历世界中的 Actor，查找 ADisplayClusterRootActor 类型
    // 返回找到的第一个实例（nDisplay 配置中每个关卡只有一个 Root Actor）
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器引擎基类 `UUnrealEdEngine` |
| `EditorWidgets` | 编辑器 UI 组件 |
| `LevelEditor` | 关卡编辑器集成 |
| `DisplayCluster` | nDisplay 核心模块（`IPDisplayCluster` 接口） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 近期 | `e352cd7` | 将 `UDisplayClusterEditorEngine` 类移至公共 API，允许外部模块访问 |
| 近期 | `e5cf515` | 重构私有头文件为公共/内部头文件，更新 UE 前缀命名空间，拆分 ClusterUtils |
| 近期 | `d9a0d03` | Actor Replication System 集成（JIRA: UE-155643） |

### 维护评价

**活跃维护**。nDisplay 是 Epic Games 虚拟制作（Virtual Production）战略的核心组件，持续获得功能更新和 bug 修复。近期的改动包括 API 公开化、命名空间规范化、Actor 复制系统集成等，表明该模块仍在积极演进。

注意事项：
- 该模块标记为 `EnabledByDefault: false`，需要在项目设置中手动启用
- 仅支持 Win64 和 Linux 平台
- 作为编辑器扩展模块，它替换了默认的 `UUnrealEdEngine`，可能与其他同样替换编辑器引擎的插件冲突

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/Overview/)