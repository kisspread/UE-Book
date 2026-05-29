# LiveLinkCamera

> Live Link plugin adding functionalities for camera handling

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接摄像头 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LiveLinkCamera` (Runtime), `LiveLinkCameraEditor` (Runtime), `LiveLinkCameraRecording` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera) | |

## 用途

LiveLinkCamera 是 Unreal Engine **Live Link** 系统的一个专用扩展插件。它解决了在虚拟制作（Virtual Production）流程中，**实时接收、处理和控制摄像头数据**的核心问题。该插件为 Live Link 框架添加了针对摄像头（Camera）主题（Subject）的特殊处理能力，使得来自真实摄像机、虚拟摄像机控制器或其他支持 Live Link 的设备的摄像头数据（如变换、光圈、焦距、Filmback 等）能够被引擎实时消费和驱动。

简而言之，它是连接外部摄像头数据源与引擎内虚拟摄像机的桥梁。

## 使用场景

- **虚拟拍摄（Virtual Production）**：在 LED 体积墙或绿幕拍摄中，需要将摄影机运动实时同步到引擎中的虚拟摄像机，以获得正确的透视关系和背景。
- **实时预览**：使用外部追踪系统（如 OptiTrack, Vicon）控制虚拟摄像机，用于实时预览或排练。
- **远程控制**：通过 Live Link 协议，远程控制引擎中虚拟摄像机的参数（如光圈、焦距、对焦距离）。
- **多机位同步**：在需要同步多个虚拟或真实摄像机数据的复杂场景中使用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `LiveLinkCamera` | Runtime | 核心运行时模块，定义摄像头数据主题、接口及运行时逻辑。 |
| `LiveLinkCameraEditor` | Runtime | 提供编辑器集成工具，例如在 Sequencer 中支持摄像头数据轨道。 |
| `LiveLinkCameraRecording` | Runtime | 提供将摄像头数据录制到资产或回放的功能。 |

## 蓝图用法

该插件主要通过 Live Link 框架工作，蓝图节点通常围绕 `Live Link Camera Controller` 组件和 `Live Link` 通用节点构建。核心是配置 Live Link 节点来接收特定的摄像头主题数据，并将其应用到 `CineCameraActor` 或 `CameraComponent` 上。

### 核心节点

*详细节点列表请参考各子模块文档。*

## C++ 用法

该插件的 C++ 用法主要涉及 Live Link 框架的扩展和自定义。开发者可以通过子类化来创建自定义的摄像头数据处理逻辑。

### 头文件引入

根据需要使用的模块引入对应头文件。

```cpp
#include “LiveLinkCamera.h”
// 或编辑器相关功能
#include “LiveLinkCameraEditor.h”
```

### 基本用法

使用 Live Link 通用接口订阅摄像头主题。

```cpp
// 伪代码示例：通过 Live Link 获取摄像头数据
ILiveLinkClient* LiveLinkClient = /* 获取 Live Link 客户端 */;
FLiveLinkSubjectKey CameraSubjectKey = /* 指定摄像头主题 */;

// 获取最新帧数据
FLiveLinkSubjectFrameData SubjectData;
LiveLinkClient->EvaluateFrame_AnyThread(CameraSubjectKey, SubjectData);

// 从数据中提取摄像头特定属性（如 Filmback）
if (const FLiveLinkCameraStaticData* StaticData = SubjectData.StaticData.Cast<FLiveLinkCameraStaticData>())
{
    // 处理静态数据
}
if (const FLiveLinkCameraFrameData* FrameData = SubjectData.FrameData.Cast<FLiveLinkCameraFrameData>())
{
    // 处理动态帧数据，应用到虚拟摄像机
}
```

*（来源：基于 Live Link 框架的通用用法推断）*

### 进阶用法

结合 `LiveLinkCameraController` 组件，实现自动化的摄像头跟随或参数映射。

## 模块依赖

从各模块的 `Build.cs` 分析，该插件的核心依赖是 Live Link 框架本身。以下是不常见的、该插件特有的依赖：

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心运行时框架，是必需的依赖。 |
| `LiveLinkInterface` | Live Link 的接口定义，用于数据结构和主题。 |
| `LiveLinkComponents` | 提供 Live Link 相关的组件（如 `LiveLinkComponent`）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 规范化插件配置文件命名。 |
| 2025-04-22 | `92ef0a10` | - Update the LiveLinkCameraController to support dynamic filmback resolution from a frame data. | 功能更新：控制器支持从帧数据动态获取胶片背板分辨率。 |
| 2025-01-27 | `ef0d3477` | [Sequencer] Update Tracks Names and Reorganize Tracks Order | Sequencer 集成优化：更新轨道名称并重新组织顺序。 |

### 维护评价

- **创建时间**：2021年3月，随 UE5 早期版本一同出现，相对年轻。
- **更新频率**：近期（2025年）有实质性功能更新（动态 Filmback 分辨率支持）和维护性更新，表明该插件仍处于**活跃维护**状态。
- **状态**：`.uplugin` 标记为 `IsBetaVersion: true`，表明其功能可能尚未完全稳定或 API 可能随版本变化，但在虚拟制作流程中已被广泛使用。
- **推荐**：对于任何需要实时摄像头数据流或虚拟制作管线的项目，**推荐使用**此插件。它是 UE5 虚拟制作工具集的重要组成部分。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkCamera)
- [子模块文档 - LiveLinkCamera](LiveLinkCamera.md)
- [子模块文档 - LiveLinkCameraEditor](LiveLinkCameraEditor.md)
- [子模块文档 - LiveLinkCameraRecording](LiveLinkCameraRecording.md)