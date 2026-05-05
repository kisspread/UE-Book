# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI 样式资产） |
| 模块 | `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

---

## 用途

Capture Manager Core 是 Epic 虚拟制片（Virtual Production）工作流中 **动作捕捉/数据采集管理** 的核心基础层。它本身不提供完整的应用功能，而是作为 **Capture Manager App**（独立采集应用）和 **Capture Manager Editor**（编辑器内采集工具）之间的共享基础设施。

该插件解决的核心问题是：在虚拟制片场景下，需要一套统一的协议栈、数据摄取管线、Take 元数据管理和 UI 样式系统，供多个上层应用复用。具体包括：

- **CaptureProtocolStack**：实现与外部采集设备（如相机阵列、动作捕捉系统）通信的网络协议栈
- **DataIngestCore**：负责将采集到的原始数据（视频、音频、传感器数据）导入并转换为 UE 可用的资产
- **CaptureManagerTakeMetadata**：管理影视制作中 "Take"（一次拍摄记录）的元数据结构
- **LiveLinkHubCaptureMessaging**：与 Live Link Hub 集成，实现采集过程中的实时数据流传输
- **CaptureUtils**：跨模块共享的通用工具函数
- **CaptureManagerStyle**：统一的 Slate UI 样式定义

## 使用场景

- 你在开发虚拟制片流程中的 **多相机阵列采集系统** → 需要 CaptureProtocolStack 处理设备通信
- 你需要将采集到的视频/音频数据 **自动导入并生成 UE 资产** → 需要 DataIngestCore
- 你在构建 **Take 管理系统**（类似影视制作中的场记板管理）→ 需要 CaptureManagerTakeMetadata
- 你需要在采集过程中通过 **Live Link Hub 实时预览** 数据 → 需要 LiveLinkHubCaptureMessaging
- 你正在开发 Capture Manager App 或 Editor 插件 → 必须依赖此核心插件

> ⚠️ 此插件 `EnabledByDefault=false`，需要在项目设置中手动启用。它是 Capture Manager App 和 Capture Manager Editor 的底层依赖，通常不需要单独使用。

## 模块概览

| 模块 | 类型 | 职责 |
|---|---|---|
| **CaptureManagerStyle** | Runtime | Slate UI 样式集（图标、颜色、字体等） |
| **CaptureManagerTakeMetadata** | Runtime | Take 元数据结构定义与管理 |
| **CaptureProtocolStack** | Runtime | 采集设备通信协议栈实现 |
| **CaptureUtils** | Runtime | 跨模块共享的通用工具函数 |
| **DataIngestCore** | Runtime | 数据摄取管线（原始数据 → UE 资产） |
| **LiveLinkHubCaptureMessaging** | Runtime | Live Link Hub 采集消息集成 |

### CaptureManagerStyle

详见 [CaptureManagerStyle 子模块文档](CaptureManagerStyle.md)。

提供 `FCaptureManagerStyle` 样式集，继承自 `FSlateStyleSet`，为 Capture Manager 系列插件提供统一的 UI 外观（图标、Brush、颜色等）。

### CaptureManagerTakeMetadata

管理影视制作中 "Take" 的元数据。在虚拟制片工作流中，每次采集尝试（一次拍摄）称为一个 Take，此模块定义了 Take 的数据结构（时间码、场景信息、设备配置等）。

### CaptureProtocolStack

实现与外部采集硬件通信的网络协议栈。这是整个采集管线的通信基础，负责设备发现、连接管理、数据传输等底层协议。

### CaptureUtils

跨模块共享的通用工具函数库，被其他所有模块依赖。

### DataIngestCore

数据摄取核心模块，负责将采集设备输出的原始数据（视频帧、音频流、传感器数据等）转换为 Unreal Engine 可用的资产格式。

### LiveLinkHubCaptureMessaging

与 Unreal 的 Live Link Hub 系统集成，实现采集过程中的实时数据流消息传递，允许在采集进行时实时预览和监控数据。

## 蓝图用法

此插件主要面向 C++ 层，作为底层基础设施，大部分 API 为 C++ 接口。UI 样式通过 Slate 框架在 C++ 中使用，不直接暴露蓝图节点。

如需在蓝图中使用采集功能，请使用上层插件：
- **Capture Manager App** — 独立采集应用
- **Capture Manager Editor** — 编辑器内采集工具

## C++ 用法

### CaptureManagerStyle 模块

#### 头文件引入

```cpp
#include "CaptureManagerStyle.h"
```

#### 基本用法

```cpp
// 获取 CaptureManager 样式集单例
const FCaptureManagerStyle& Style = FCaptureManagerStyle::Get();

// 获取样式集名称（用于注册到 FSlateStyleRegistry）
FName StyleSetName = Style.GetStyleSetName();

// 在需要时重新加载纹理资源（例如主题切换后）
FCaptureManagerStyle::ReloadTextures();
```

#### 在自定义 Slate Widget 中使用样式

```cpp
// 在 Slate UI 构建中引用 CaptureManager 的样式 Brush
const FCaptureManagerStyle& Style = FCaptureManagerStyle::Get();

// 使用样式集中的 Image Brush
TSharedRef<SImage> IconImage = SNew(SImage)
    .Image(Style.GetBrush("CaptureManager.LaunchIngestServer"));
```

## Demo 示例

### 自定义 Slate 面板使用 CaptureManager 样式

```cpp
// MyCapturePanel.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class SMyCapturePanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCapturePanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
};
```

```cpp
// MyCapturePanel.cpp
#include "MyCapturePanel.h"
#include "CaptureManagerStyle.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Images/SImage.h"

void SMyCapturePanel::Construct(const FArguments& InArgs)
{
    const FCaptureManagerStyle& Style = FCaptureManagerStyle::Get();

    ChildSlot
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .AutoWidth()
        .Padding(4.0f)
        [
            SNew(SImage)
            .Image(Style.GetBrush("CaptureManager.LaunchIngestServer"))
        ]
        + SHorizontalBox::Slot()
        .FillWidth(1.0f)
        .VAlign(VAlign_Center)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Capture Manager")))
        ]
    ];
}
```

## 模块依赖

此插件的各模块之间存在内部依赖关系，对外部模块的依赖较少：

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLinkHubCaptureMessaging 模块依赖，用于 Live Link 集成 |
| `MediaUtils` | DataIngestCore 可能依赖，用于媒体格式处理 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

> 注：各子模块的具体依赖请参考对应的 `.Build.cs` 文件。

## 维护状态

### 近期更新

```
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- 0a2f65d4a264 [CaptureManager] Updated launch ingest server icon
```

- 第一条为代码规范化维护（DLL 导出符号修正），属于 Epic 全局代码质量改进
- 第二条为 UI 图标更新，说明该插件仍在活跃开发中

### 维护评价

- **创建时间**：2025-02-04，非常新的插件
- **活跃度**：作为 Virtual Production 工作流的核心组件，由 Epic 官方维护，预计会持续更新
- **成熟度**：标记为实验性（IsBetaVersion），API 可能在后续版本中发生变化
- **推荐度**：如果你在开发 Capture Manager 相关功能，这是必须依赖的基础插件。但作为独立使用者，此插件价值有限——它是为上层 Capture Manager App/Editor 服务的底层模块

> ⚠️ 此插件为实验性功能，API 不保证向后兼容。建议在使用时关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- 官方文档：暂无
- 相关插件：Capture Manager App、Capture Manager Editor（同目录下）

---

# CaptureManagerStyle 子模块

> Slate UI 样式集模块，为 Capture Manager 系列插件提供统一的视觉外观。

| 属性 | 值 |
|---|---|
| 模块名 | `CaptureManagerStyle` |
| 类型 | Runtime |
| 源文件数 | ~2（.h + .cpp） |
| 复杂度 | small |

## 模块职责

CaptureManagerStyle 是一个纯 UI 样式模块，提供 `FCaptureManagerStyle` 类——一个继承自 `FSlateStyleSet` 的单例样式集。它集中管理 Capture Manager 系列插件的所有 UI 资源定义：

- **Image Brush**：图标和图片资源
- **Box Brush**：九宫格拉伸图片
- **Color**：主题颜色定义
- **Font**：字体样式

## 核心类

### FCaptureManagerStyle

继承自 `FSlateStyleSet`，采用单例模式。

| 方法 | 说明 |
|---|---|
| `static const FCaptureManagerStyle& Get()` | 获取样式集单例实例 |
| `static void ReloadTextures()` | 重新加载纹理资源 |
| `virtual const FName& GetStyleSetName() const override` | 返回样式集注册名称 |

### 使用模式

```cpp
// 标准使用方式：通过 Get() 获取单例
const FCaptureManagerStyle& Style = FCaptureManagerStyle::Get();

// 引用某个 Brush
const FSlateBrush* MyBrush = Style.GetBrush("BrushName");

// 在 Slate 构建中直接使用
SNew(SImage).Image(Style.GetBrush("CaptureManager.SomeIcon"));
```

## 模块依赖

无特殊依赖（仅标准 Core/Slate）。

## 源码

- [CaptureManagerStyle.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureManagerStyle/Public/CaptureManagerStyle.h)
- [CaptureManagerStyle.Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureManagerStyle/CaptureManagerStyle.Build.cs)