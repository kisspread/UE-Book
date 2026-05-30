# Motion Design

> Compositing, designer and broadcasting tool.
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（完整的动态图形设计、合成与广播工具链） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheShapes` (Runtime), `AvalancheMedia` (Runtime), ... (共43个模块) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Avalanche 插件（又称 Motion Design）是 Epic 为虚拟制作（Virtual Production）领域提供的一个**功能极其全面的一站式动态图形（Motion Graphics）设计与广播解决方案**。它并非一个单一功能的插件，而是一个庞大的工具集和框架，旨在将 UE 的实时渲染能力与专业广播和动态图形设计的工作流程深度结合。

其核心目标是解决**在虚幻引擎内创建、编辑、排练和播出高质量实时动态图形**的复杂需求。它整合了场景构建（Scenes）、形状与文本生成、材质设计、动画控制（属性动画）、克隆与效果器、远程控制、序列器集成、媒体输出等几乎所有相关功能，并提供了专门的编辑器界面（如大纲、属性面板、视口工具）来支撑这套工作流。

## 使用场景

- **电视节目/演唱会/颁奖典礼的虚拟场景与视觉包装**：设计师可以在 UE 中直接设计复杂的实时动态背景、转场、字幕条和视觉特效。
- **虚拟演播室/新闻广播图形**：构建可实时控制的虚拟演播室，动态更新图表、数据、连线画面等。
- **实时内容制作与预演**：用于预演复杂的灯光、动画和场景切换，节省实体搭建和拍摄成本。
- **交互式数字标牌/展览装置**：创建可远程控制、实时响应的动态视觉内容。

## 蓝图用法

由于模块庞大，这里仅列出最核心、最基础的蓝图功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Motion Design Scene` | 在指定位置创建一个新的 Motion Design 场景根组件。 | `UMotionDesignSubsystem` |
| `Add Text3D` | 向场景中添加一个 3D 文本元素。 | `UAvaSceneSubsystem` |
| `Add Shape` | 向场景中添加一个几何形状（如矩形、圆形）。 | `UAvaSceneSubsystem` |
| `Add Media Input` | 添加一个媒体输入源（如摄像头、视频文件）。 | `UAvaMediaSubsystem` |
| `Set Remote Control Value` | 通过远程控制接口，设置场景中某个对象的属性值（如位置、颜色、文本内容）。 | `UAvaRemoteControlSubsystem` |

### 使用示例（蓝图描述）

1.  **创建场景**：在 BeginPlay 事件中，调用 `Create Motion Design Scene` 节点，为后续元素提供一个挂载的根节点。
2.  **添加元素**：使用 `Add Text3D` 和 `Add Shape` 节点，将文本和形状作为场景的子项添加，并通过 Transform 数据设置它们的位置、旋转和缩放。
3.  **动态更新**：通过一个自定义事件或定时器，调用 `Set Remote Control Value` 节点，将外部数据（如股票信息、比分）实时更新到对应的文本或材质参数上。
4.  **媒体合成**：使用 `Add Media Input` 节点引入实机摄像头信号，并与场景中的图形元素叠加，最终通过 Media Output 节点或 Composure 节点输出合成画面。

## C++ 用法

### 头文件引入

根据你使用的功能模块，引入对应的头文件。最核心的头文件通常包括：
```cpp
#include “AvaSceneSubsystem.h” // 场景管理
#include “AvaMotionDesignSubsystem.h” // 核心子系统
#include “AvaMediaSubsystem.h” // 媒体管理
```

### 基本用法

以下示例展示如何通过代码创建一个简单的 Motion Design 文本对象。

```cpp
// 假设在某个 Actor 或 Blueprint Function Library 中
#include “AvaSceneSubsystem.h”
#include “AvaText3DActor.h”

void CreateSimpleText()
{
    // 1. 获取场景子系统
    UAvaSceneSubsystem* SceneSubsystem = GEngine->GetEngineSubsystem<UAvaSceneSubsystem>();
    if (!SceneSubsystem) return;

    // 2. 创建一个新的 3D 文本 Actor
    AAvaText3DActor* TextActor = SceneSubsystem->SpawnActorInScene<AAvaText3DActor>(FVector::ZeroVector, FRotator::ZeroRotator);
    if (TextActor)
    {
        // 3. 设置文本内容和样式
        TextActor->SetText(TEXT(“Hello Motion Design!”));
        TextActor->SetFontSize(100.0f);
        TextActor->SetColor(FLinearColor::Red);
    }
}
```
*（示例基于通用子系统模式推断，具体类名请参考实际源码）*

### 进阶用法

进阶用法涉及将多个模块组合，例如结合 `PropertyAnimator` 实现动画，并通过 `RemoteControl` 进行外部控制。这通常需要在编辑器中进行复杂的配置，代码层面更多是启动、配置和连接这些系统。

## Demo 示例

由于 Motion Design 是一个复杂的工作流系统，一个最小的可编译示例也需要数十行代码和多个类。核心模式是：

1.  **继承或使用 `UAvaSceneSubsystem`**。
2.  **在场景中 `SpawnActor` 各种 `Ava` 相关的 Actor 类型**。
3.  **通过子系统的接口管理这些元素的生命周期和交互**。
一个完整的示例通常体现在编辑器内的可视化操作中，而非一个独立的代码片段。

## 模块依赖

此插件自身高度依赖其他多个专用插件，以下是其关键且独特的依赖项：

| 模块 | 用途 |
|---|---|
| `ClonerEffector` | 提供克隆体和效果器系统，用于创建粒子状或规律性动画。 |
| `MaterialDesigner` | 提供节点式的材质设计工具。 |
| `GeometryMask` | 提供几何遮罩功能。 |
| `OperatorStack` | 提供节点式操作栈，用于构建复杂效果链。 |
| `PropertyAnimator` | 提供强大的属性动画系统，可对几乎任何属性进行关键帧动画。 |
| `Text3D` | 提供 3D 文本生成与渲染功能。 |
| `ActorModifierCore` | 提供对 Actor 属性进行修改和动画化的核心框架。 |
| `MediaCompositing` | 提供媒体合成框架。 |
| `RemoteControl` | 提供通过外部接口（如网页、移动应用）远程控制引擎属性的能力。 |
| `SVGImporter` | 支持导入 SVG 文件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将运动设计相关的编辑器面板整合到独立分组，优化UI布局 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为使用 Rundown 页面设置时增加了 MRQ 分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added... | 在播控工具栏增加了页面加载选项（全部、下一个、选中），增强播控灵活性 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 增加了项目设置，可强制禁用 Text3D 和形状的碰撞检测 |

### 维护评价

Avalanche（Motion Design）是 Epic 在虚拟制作领域的一个**战略性核心产品**。

- **活跃维护**：从提交记录看，更新非常频繁，持续在增加新功能、优化工作流和修复问题。
- **状态**：插件正处于**积极开发和迭代期**。它于 2025 年中从实验目录迁移至正式产品目录，标志着其已成为 Epic 虚拟制作管线中一个稳定且重要的组件。
- **推荐使用**：如果你是从事**虚拟制作、现场活动图形、实时广播**相关的 UE 开发者或设计师，**强烈建议学习和使用**此插件。它提供了 UE 内目前最完整的 Motion Design 工具链。对于其他场景，除非有明确的动态图形需求，否则可以暂不关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- 官方文档：暂无独立文档，相关信息通常包含在 UE 虚拟制作文档中。
- 测试用例：插件内包含 `AvalancheFunctionalTest` 模块，用于功能测试。