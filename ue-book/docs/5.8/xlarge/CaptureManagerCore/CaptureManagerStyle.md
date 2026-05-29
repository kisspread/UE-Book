# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕捉管理核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（多个运行时模块，包含核心功能、协议、管线、样式等） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

此插件并非独立的功能单元，而是**整个虚幻引擎捕捉管理系统（Capture Manager）的基石和共享工具库**。它被 `Capture Manager App` 和 `Capture Manager Editor` 两个上层插件共同依赖，旨在统一管理捕捉数据流处理中的核心功能，避免代码重复，确保数据流转的一致性和可靠性。

具体来说，它解决了以下核心问题：
- **数据协议与通信**：定义了捕捉设备与虚幻引擎之间的通信协议（CPS - Capture Protocol Stack）和客户端实现。
- **数据转换与处理**：提供将捕捉设备原始数据（视频、音频、元数据）转换为引擎可用格式的管道（Pipeline）和转换器（Converter）。
- **元数据管理**：定义、提取和管理与捕捉会话（Take）相关的元数据（如摄像机参数、场景信息）。
- **数据摄取与存储**：处理从外部设备或文件系统获取（Ingest）原始数据的过程。
- **媒体读写**：封装了底层媒体文件的读写操作。
- **UI与样式**：为捕捉管理相关的编辑器UI提供统一的样式表。
- **LiveLink集成**：提供与LiveLink Hub进行捕捉相关消息通信的模块。

## 使用场景

- **虚拟制片（LED Volume）**：在LED摄影棚中，需要同步捕捉来自摄像机追踪系统、RenderNode、音频设备等的多路数据流。此插件提供了接收、转换、同步和存储这些数据的底层能力。
- **影视制作（动作/面部捕捉）**：使用专业捕捉设备（如OptiTrack, Vicon，移动设备App）采集表演数据时，此插件负责与设备通信、接收数据、解析元数据并将其注入到虚幻引擎的角色或对象上。
- **实时渲染预览**：在拍摄现场，通过CaptureManager App连接设备，实时预览捕捉数据在虚幻引擎场景中的效果，此插件负责驱动数据的实时流转。
- **数据后期处理与导入**：将已录制的捕捉数据（通常包含视频、音频、元数据文件）批量导入引擎，进行校对、编辑和最终应用，此插件提供了数据解析和转换的底层支持。

## 蓝图用法

**注意**：`CaptureManagerCore` 是一个**底层核心插件**，其模块主要以 C++ 形式提供服务。大部分面向美术和技术策划的蓝图操作将通过上层插件（如 `Capture Manager Editor`）提供的蓝图节点来完成。本插件自身提供的蓝图公开接口较少，主要集中在样式和可能的数据结构上。

### 核心节点

基于其作为核心工具库的定位，直接暴露的蓝图节点有限。更高级的蓝图功能（如启动捕捉会话、配置设备）位于上层插件中。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` (静态) | 获取 Capture Manager 的全局样式实例，用于设置UI控件的样式。 | `FCaptureManagerStyle` |
| `ReloadTextures` (静态) | 重新加载样式表引用的纹理资源。 | `FCaptureManagerStyle` |

## C++ 用法

本插件的功能主要通过 C++ 模块被其他插件引用。以下示例展示了如何使用其提供的核心工具。

### 头文件引入

根据你要使用的具体模块引入对应头文件。例如：
```cpp
#include "CaptureManagerStyle.h"
#include "CaptureManagerPipeline/Public/ICaptureManagerPipeline.h"
#include "CaptureProtocolStack/Public/CaptureProtocol.h"
```

### 基本用法 (样式管理)

使用 `CaptureManagerStyle` 模块来应用自定义的捕捉管理UI样式。
```cpp
// 假设在某个 Slate 控件的构造函数中
#include "CaptureManagerStyle.h"

SMyCustomWidget::SMyCustomWidget()
{
    // 获取全局的 Capture Manager 样式
    const FCaptureManagerStyle& Style = FCaptureManagerStyle::Get();
    
    // 使用该样式中的一个按钮样式来创建子控件
    ChildSlot
    [
        SNew(SButton)
        .ButtonStyle(&Style.Get().GetWidgetStyle<FButtonStyle>("CaptureManager.PrimaryButton"))
        .Text(FText::FromString(TEXT("Start Capture")))
    ];
}
```
*（来源：基于 `FCaptureManagerStyle` 类的接口设计推断）*

### 进阶用法 (协议与管线)

以下为概念性代码，展示如何利用核心模块构建数据处理链。
```cpp
// 1. 建立与捕捉设备的连接 (使用 CaptureProtocolStack)
FCaptureProtocol Protocol;
if (Protocol.Connect(DeviceAddress, Port))
{
    // 2. 创建数据处理管线 (使用 CaptureManagerPipeline)
    TSharedPtr<ICaptureManagerPipeline> Pipeline = ICaptureManagerPipeline::Create();
    
    // 3. 向管线添加处理器（例如，视频解码、元数据提取）
    Pipeline->AddProcessor(MakeShared<FVideoDecoderProcessor>());
    Pipeline->AddProcessor(MakeShared<FCaptureMetadataExtractor>());
    
    // 4. 启动管线，将来自协议的数据流送入处理
    Pipeline->Start(Protocol.GetDataStream());
    
    // ... 运行，直到需要停止 ...
    
    Pipeline->Stop();
    Protocol.Disconnect();
}
```
*（来源：基于模块职责和常见管道模式推断）*

## Demo 示例

一个最小化的示例，展示如何在自己的编辑器模块中注册并应用 `CaptureManagerCore` 提供的样式。

**MyEditorModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "CaptureManagerStyle.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 确保 CaptureManagerStyle 模块已加载并初始化
    FModuleManager::Get().LoadModuleChecked<FCaptureManagerStyleModule>("CaptureManagerStyle");
    
    // 通常，样式会自动注册。你可以通过 FCaptureManagerStyle::Get() 访问它。
    UE_LOG(LogTemp, Log, TEXT("Capture Manager Style is available: %s"), 
        *FCaptureManagerStyle::Get().GetStyleSetName().ToString());
}

void FMyEditorModule::ShutdownModule()
{
    // 清理工作（如有）
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

使用 `CaptureManagerCore` 中的特定模块时，你的 `Build.cs` 文件需要添加相应的依赖。下表列出了各核心模块的独特依赖（常见引擎模块已省略）：

| 模块 | 用途 |
|---|---|
| `Media` | 基础媒体框架，用于媒体资产读写 (`CaptureManagerMediaRW`)。 |
| `MediaAssets` | 引擎媒体资产（如 `UMediaSource`），用于媒体集成。 |
| `MediaUtils` | 媒体工具函数。 |
| `LiveLinkHub` | 与 LiveLink Hub 应用程序通信，用于 `LiveLinkHubCaptureMessaging`。 |
| `Json` | JSON 解析与序列化，广泛用于元数据交换。 |
| `DesktopPlatform` | 平台相关的文件对话框等，可能用于文件选择。 |
| `RHI` / `RenderCore` | 与渲染硬件交互，可能用于视频纹理处理。 |
| `Slate` / `SlateCore` | 构建编辑器UI，用于 `CaptureManagerStyle`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 将停止令牌传递给第三方编码器，使音视频转换支持取消操作。 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补充了之前模块迁移时遗漏的修复。 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复因事务ID数据竞争导致的偶发性下载失败。 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以支持FString和UE::FSharedString，提升性能。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 添加了新的设备蓝图模块（注：该模块可能位于其他路径）。 |

### 维护评价

**综合评价：活跃维护，核心组件，推荐使用。**

- **创建时间**：约1年，属于较新的插件，但已稳定用于虚幻引擎的虚拟制片流程。
- **更新频率**：从git历史看，近期（2026年4-5月）有连续的实质性更新，包括性能优化、错误修复和新功能添加，表明开发非常活跃。
- **维护状态**：**活跃维护**。Epic Games的Virtual Production团队正在积极开发和优化此核心库。
- **已知问题**：commit历史显示近期修复了数据竞争等并发问题，说明在实际使用中可能遇到多线程相关的复杂问题，但这些问题正在被解决。
- **使用建议**：**强烈推荐**在开发基于虚拟制片流程的自定义捕捉系统时使用此插件。它提供了经过验证的底层基础架构，可以避免重复造轮子，并能随着引擎更新获得持续优化和兼容性支持。由于是核心模块，建议关注其更新日志以获取最新的改进和API变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- 官方文档：暂无
- 测试用例：请查看 `Engine/Tests/VirtualProduction/CaptureManager/` 或插件源码内可能存在的 `Tests` 目录。