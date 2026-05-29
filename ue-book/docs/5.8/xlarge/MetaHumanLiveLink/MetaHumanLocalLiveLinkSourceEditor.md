# MetaHuman Live Link

> Live Link sources and associated utilities for streaming real time MetaHuman animation data.

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman实时链接 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（待确认） |
| 模块 | `LiveLinkFaceDiscovery` (Runtime), `LiveLinkFaceSource` (Runtime), `LiveLinkFaceSourceEditor` (Runtime), `MetaHumanLiveLinkSource` (Runtime), `MetaHumanLiveLinkSourceEditor` (Runtime), `MetaHumanLocalLiveLinkSource` (Runtime), `MetaHumanLocalLiveLinkSourceEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink) | |

## 用途

此插件并非用于实现MetaHuman角色的基础渲染或控制，而是专门解决**实时动画数据流**的获取与集成问题。它提供了一整套 Live Link 框架的 Source（源）和 Subject（主体）实现，使得用户能够从特定的捕获设备或数据流（如 iPhone 上的 Live Link Face 应用、其他面捕/体捕设备）中接收实时的面部、身体动画数据，并将其直接应用于场景中的 MetaHuman 角色。核心价值在于打通了外部实时表演数据与 Unreal Engine 内 MetaHuman 角色之间的桥梁。

## 使用场景

- 你正在使用 iPhone 或专业面捕头盔进行实时面部表演捕捉，希望将数据无缝、低延迟地传输到 UE 中的 MetaHuman 角色上。
- 你需要在一个复杂的多人表演捕捉设置中，为多个 MetaHuman 角色建立独立的、可管理的 Live Link 数据流。
- 你正在开发虚拟制片（Virtual Production）流程，需要实时驱动虚拟 MetaHuman 角色与真人演员互动。
- 你需要编辑器工具来发现和配置本地网络中的面捕设备（Live Link Face 应用）。

## 蓝图用法

此插件主要提供 Live Link 框架的底层数据源和编辑器集成。其蓝图功能主要体现在通过 Live Link 面板选择和配置由该插件提供的“源（Source）”。例如，在 Live Link 窗口中，你可以选择 `MetaHuman Local Live Link Source` 来连接本地设备，或选择其他由该插件提供的源来接收流数据。具体的骨骼映射和动画应用通常通过标准的 Live Link 蓝图节点（如 `Get Live Link Subject Data`）结合角色蓝图中的 `Live Link Component` 来完成。

## C++ 用法

### 头文件引入

```cpp
// 包含LiveLink核心接口
#include "ILiveLinkClient.h"

// 包含特定源或Subject的接口（根据具体使用场景）
#include "MetaHumanLiveLinkSource/Public/IMetaHumanLiveLinkSourceModule.h"
```

### 基本用法

该插件的使用主要通过 Live Link 面板（编辑器UI）进行配置。在 C++ 中，你可能会涉及到创建自定义的动画蓝图逻辑来处理从 Live Link Subject 收到的数据。以下是处理 Live Link 数据的典型代码逻辑（非此插件特有，但为其数据提供消费端）。

```cpp
// 在 AnimInstance 或相关类中获取 Live Link 数据
// 假设我们已经有了一个 Live Link Subject 名称（FName）
void UMyAnimInstance::UpdateFromLiveLink(const FName& SubjectName)
{
    // 获取 Live Link 客户端
    ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get();
    if (!LiveLinkClient)
    {
        return;
    }

    // 获取指定 Subject 的最新数据（面部形态）
    FLiveLinkSubjectFrameData SubjectData;
    if (LiveLinkClient->EvaluateFrame_AnyThread(SubjectName, ULiveLinkBasicRole::StaticClass(), SubjectData))
    {
        // 将数据应用到 MetaHuman 的控制曲线或 Morph Target
        // ... 具体逻辑依赖于数据类型和 MetaHuman 的驱动设置
    }
}
```

**来源**: 这是使用 Live Link 数据的通用模式，具体 Subject 名称由 MetaHumanLiveLink 插件提供的源创建。

### 进阶用法

对于需要从 `MetaHumanLocalLiveLinkSource` 或其他自定义源接收数据的场景，开发者可能需要实现一个自定义的 Live Link Source。这通常涉及继承 `ILiveLinkSource` 接口，并实现 `ReceiveClient`、`IsSourceStillValid` 等方法。此插件中的模块（如 `LiveLinkFaceSource`）就是此类实现的范例。

## Demo 示例

由于该插件主要提供编辑器集成和底层框架，其核心使用场景通过编辑器UI配置，而非编写特定的 Actor 或 Component。一个最小集成示例通常包含：
1.  在 `Project Settings -> Plugins -> Live Link` 中启用相关源。
2.  打开 `Live Link` 面板 (`Window -> Virtual Production -> Live Link`)。
3.  点击 `Source` 按钮，选择由该插件提供的源类型（例如 `MetaHuman Local Live Link Source`）。
4.  按照向导配置设备连接或数据流。
5.  在角色蓝图中添加 `Live Link Component`，并指定接收该源创建的 Subject 数据。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架 |
| `LiveLinkInterface` | Live Link 接口定义 |
| `MetaHumanLocalLiveLinkSource` | 依赖了 `EditorWidgets`, `UnrealEd`, `PropertyEditor`（见下文） |

**注意**: `MetaHumanLocalLiveLinkSource` 模块的依赖列表显示其依赖于 `EditorWidgets`, `UnrealEd`, `PropertyEditor`。这表明该模块包含编辑器特定的功能（如设备发现和UI定制），尽管其模块类型被标记为 `Runtime`。在打包项目时，可能需要特别注意处理这些编辑器依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `9bee2cb0` | [MHA] Expose detection thresholds for body | 为身体检测暴露更多可调参数 |
| 2026-05-14 | `988b3911` | [MHA] Face animation sequence export changes for combined solve | 改进面部动画序列导出以支持组合解算 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-12 | `8bf9ba92` | [MetaHumanLiveLink] Use AvfMedia for FileMediaSource bundles on Apple platforms | 在苹果平台上使用 AvfMedia 处理文件媒体源 |
| 2026-05-12 | `fa06fada` | New ADA model | 更新ADA（可能是一种动画或驱动）模型 |

### 维护评价

该插件处于**积极维护**状态。创建于2025年初，属于较新的插件。从近期（2026年5月）的提交记录看，开发团队持续进行功能增强（如暴露身体检测阈值）、平台兼容性优化（苹果平台媒体支持）和模型更新。这表明 MetaHuman 的实时动捕/驱动管线是 Epic Games 当前重点发展的方向之一。插件功能稳定且在不断进化，**推荐在需要实时驱动 MetaHuman 角色的项目中使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanLiveLink)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现公开路径）