# Capture Manager Application

> The Capture Manager allows control and monitoring of the capture device, obtains and transcodes the data from the devices and upload the data for import to the UE

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerEditor` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerSettings` (Runtime), `CaptureManagerUnrealEndpoint` (Runtime), `ExampleLiveLinkDevices` (Runtime), `IngestLiveLinkDevice` (Runtime), `LiveLinkCapabilities` (Runtime), `LiveLinkFaceMetadata` (Runtime), `StereoCameraMetadata` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp) | |

## 用途

Capture Manager App 是一个面向虚拟制片（Virtual Production）的**端到端采集管理工具**。它解决的核心问题是：在虚拟制片工作流中，如何统一管理多种采集设备（如 iPhone 上的 Live Link Face、立体相机阵列等），将采集到的面部动画、视频、音频等数据进行格式转换和转码，然后上传到 Unreal Engine 中供后续导入使用。

这个插件存在的意义在于将原本分散的采集流程（设备连接 → 数据获取 → 格式转换 → 上传 → 导入）整合为一个统一的 Pipeline，同时提供 LiveLinkHub 集成界面，让用户可以在一个应用内完成从设备监控到数据上传的全流程操作。

**核心能力概览：**

- **设备管理**：通过 Live Link 协议连接和监控采集设备（iPhone、立体相机等）
- **数据采集**：从设备获取面部动画、视频、音频等原始数据
- **格式转换**：将采集到的原始数据转码为 UE 可导入的格式
- **数据上传**：将处理后的数据上传到 Unreal Engine 项目中
- **Pipeline 编排**：可配置的数据处理流水线，支持自定义处理步骤
- **LiveLinkHub 集成**：作为 LiveLinkHub 的应用模式（Application Mode）运行

## 模块架构

本插件由 11 个模块组成，按职责可分为以下几层：

```
┌─────────────────────────────────────────────────┐
│              CaptureManagerEditor                │  ← UI 层（LiveLinkHub 集成）
├─────────────────────────────────────────────────┤
│  CaptureManagerPipeline                         │  ← Pipeline 编排层
├──────────┬──────────┬───────────────────────────┤
│ Capture  │ Capture  │ CaptureManager            │  ← 数据处理层
│ DataConv │ MediaRW  │ UnrealEndpoint            │
├──────────┴──────────┴───────────────────────────┤
│ IngestLiveLinkDevice │ ExampleLiveLinkDevices   │  ← 设备抽象层
├─────────────────────────────────────────────────┤
│ LiveLinkCapabilities │ LiveLinkFaceMetadata     │  ← 元数据层
│                      │ StereoCameraMetadata     │
├─────────────────────────────────────────────────┤
│              CaptureManagerSettings             │  ← 配置层
└─────────────────────────────────────────────────┘
```

| 模块 | 职责 |
|---|---|
| **CaptureManagerEditor** | LiveLinkHub 应用模式集成，提供编辑器 UI |
| **CaptureManagerPipeline** | 数据处理流水线编排，定义处理步骤和执行顺序 |
| **CaptureDataConverter** | 采集数据格式转换（如 Live Link Face 格式 → UE 格式） |
| **CaptureManagerMediaRW** | 媒体文件读写操作（视频、音频的读取和写入） |
| **CaptureManagerUnrealEndpoint** | Unreal Engine 端点，负责数据上传和项目导入 |
| **IngestLiveLinkDevice** | Live Link 设备数据摄取，处理来自设备的实时/离线数据 |
| **ExampleLiveLinkDevices** | 示例 Live Link 设备实现，供开发者参考 |
| **LiveLinkCapabilities** | Live Link 能力定义，描述设备支持的功能 |
| **LiveLinkFaceMetadata** | Live Link Face 应用的元数据解析 |
| **StereoCameraMetadata** | 立体相机阵列的元数据解析 |
| **CaptureManagerSettings** | 插件全局配置和用户设置 |

## 使用场景

- **你在做虚拟制片项目，需要从 iPhone 的 Live Link Face 应用采集面部动画数据** → 使用 Capture Manager App 连接设备、采集数据、转码后上传到 UE 项目
- **你有一个立体相机阵列用于体积视频采集** → 通过 StereoCameraMetadata 解析相机元数据，用 Pipeline 处理多路视频流
- **你需要自定义数据处理流程** → 通过 CaptureManagerPipeline 定义自定义处理步骤
- **你在开发自定义采集设备** → 参考 ExampleLiveLinkDevices 模块实现自己的设备驱动
- **你需要在 LiveLinkHub 中统一管理采集工作流** → CaptureManagerEditor 提供了 LiveLinkHub Application Mode 集成

## 蓝图用法

> ⚠️ 本插件主要面向 C++ 和编辑器工具开发，大部分核心 API 为 C++ 接口。BlueprintCallable 节点主要集中在设备管理和数据操作层面。

### 核心节点

由于本插件为 xlarge 规模（258 个源文件），以下仅列出各模块的关键蓝图接口。完整 API 请参阅各子模块文档。

| 节点 | 说明 | 所在模块 |
|---|---|---|
| 设备连接/断开 | 管理与采集设备的连接生命周期 | `IngestLiveLinkDevice` |
| 数据采集控制 | 开始/停止/暂停采集会话 | `CaptureManagerPipeline` |
| 数据格式转换 | 将原始采集数据转码为目标格式 | `CaptureDataConverter` |
| 数据上传 | 将处理后的数据上传到 UE 项目 | `CaptureManagerUnrealEndpoint` |
| 设置读写 | 读取和修改插件配置 | `CaptureManagerSettings` |

### 使用示例（蓝图描述）

典型的采集工作流蓝图连接方式：

1. **初始化阶段**：创建设备管理器 → 连接到目标采集设备（如 iPhone）
2. **配置阶段**：设置采集参数（分辨率、帧率、输出路径）→ 配置 Pipeline 处理步骤
3. **采集阶段**：调用"开始采集"节点 → 监听采集进度事件 → 调用"停止采集"
4. **处理阶段**：Pipeline 自动执行数据转换 → 监听转换完成事件
5. **上传阶段**：调用"上传到 UE"节点 → 指定目标项目路径 → 等待上传完成

## C++ 用法

### 头文件引入

```cpp
// 编辑器集成
#include "CaptureManagerEditorModule.h"

// 数据转换
#include "CaptureDataConverterModule.h"

// 媒体读写
#include "CaptureManagerMediaRWModule.h"

// Pipeline
#include "CaptureManagerPipelineModule.h"

// 设备管理
#include "IngestLiveLinkDeviceModule.h"

// Unreal 端点
#include "CaptureManagerUnrealEndpointModule.h"

// 设置
#include "CaptureManagerSettingsModule.h"
```

### 基本用法 — LiveLinkHub 应用模式集成

`CaptureManagerEditor` 模块实现了 `ILiveLinkHubApplicationModeFactory` 接口，用于在 LiveLinkHub 中注册自定义应用模式：

```cpp
// 来源: CaptureManagerEditor/Public/CaptureManagerEditorModule.h

// 模块启动时自动注册为 LiveLinkHub 应用模式工厂
class FCaptureManagerEditorModule : public IModuleInterface, 
                                     public ILiveLinkHubApplicationModeFactory
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // 创建 Capture Manager 的 LiveLinkHub 应用模式
    virtual TSharedRef<FLiveLinkHubApplicationMode> CreateLiveLinkHubAppMode(
        TSharedPtr<FLiveLinkHubApplicationBase> InApp) override;
};
```

在你的 LiveLinkHub 宿主应用中，模块加载后会自动注册，无需手动调用。LiveLinkHub 启动时会通过工厂接口创建 Capture Manager 的 UI 模式。

### 进阶用法 — 自定义 Pipeline 处理步骤

`CaptureManagerPipeline` 模块提供了可扩展的数据处理流水线。典型的使用模式：

```cpp
// 1. 获取 Pipeline 模块
FCaptureManagerPipelineModule& PipelineModule = 
    FModuleManager::GetModuleChecked<FCaptureManagerPipelineModule>(
        TEXT("CaptureManagerPipeline"));

// 2. 配置处理步骤（具体 API 取决于模块内部实现）
// Pipeline 通常包含: 数据读取 → 格式转换 → 编码 → 输出

// 3. 执行 Pipeline
// Pipeline 会按配置的步骤顺序处理采集数据
```

### 进阶用法 — 自定义 Live Link 设备

参考 `ExampleLiveLinkDevices` 模块实现自定义设备：

```cpp
// 1. 继承设备基类（定义在 IngestLiveLinkDevice 或 LiveLinkCapabilities 中）
// 2. 实现设备发现、连接、数据获取等接口
// 3. 注册设备到设备管理器

// ExampleLiveLinkDevices 模块提供了完整的示例实现
// 可作为开发自定义设备驱动的模板
```

## Demo 示例

### 最小 LiveLinkHub 集成示例

```cpp
// MyCaptureApp.h
#pragma once

#include "CoreMinimal.h"
#include "LiveLinkHubApplicationBase.h"

class FMyCaptureApp : public FLiveLinkHubApplicationBase
{
public:
    virtual void Initialize() override;
    virtual void Shutdown() override;
    
    // CaptureManagerEditor 模块会通过工厂接口自动注册应用模式
    // 无需手动创建 Capture Manager UI
};
```

```cpp
// MyCaptureApp.cpp
#include "MyCaptureApp.h"
#include "CaptureManagerEditorModule.h"

void FMyCaptureApp::Initialize()
{
    FLiveLinkHubApplicationBase::Initialize();
    
    // CaptureManagerEditor 模块在 StartupModule 中已注册为
    // ILiveLinkHubApplicationModeFactory，LiveLinkHub 会自动
    // 调用 CreateLiveLinkHubAppMode() 创建 Capture Manager 面板
    
    UE_LOG(LogTemp, Log, TEXT("Capture Manager App Mode 已自动注册"));
}

void FMyCaptureApp::Shutdown()
{
    FLiveLinkHubApplicationBase::Shutdown();
}
```

## 模块依赖

> 由于本插件包含 11 个模块，以下仅列出各模块的**独特依赖**。所有模块均省略了标准的 Core/CoreUObject/Engine/Slate 等常见依赖。

| 模块 | 用途 |
|---|---|
| `LiveLinkHubApplication` | LiveLinkHub 应用框架，CaptureManagerEditor 依赖它注册应用模式 |
| `LiveLink` | Live Link 协议核心，设备通信基础 |
| `LiveLinkInterface` | Live Link 接口定义 |
| `MediaUtils` | 媒体工具库，CaptureManagerMediaRW 用于音视频读写 |
| `ImageWriteQueue` | 图像写入队列，用于采集帧的异步写入 |
| `RHI` | 渲染硬件接口，用于 GPU 加速的格式转换 |
| `RenderCore` | 渲染核心，配合 RHI 进行数据处理 |
| `PropertyEditor` | 属性编辑器，CaptureManagerSettings 用于自定义设置 UI |

## 维护状态

### 近期更新

```
- fdaf85b60939 [Capture Manager] Fixed several crashes while aborting take upload.
  → 修复了中止 take 上传时的多个崩溃问题，说明上传流程的稳定性在持续改进
- 9b414a8dd0d0 LiveLinkHub - Fix using wrong PropertyEditorModule method to unregister struct customizations
  → 修复了 LiveLinkHub 中结构体自定义注销使用了错误方法的问题
- 8f3b6b801a63 [Capture Manager] Use weak ptrs on endpoint manager interface.
  → 端点管理器接口改用弱指针，防止悬空引用导致的崩溃
```

### 维护评价

- **创建时间**：2025 年 2 月，非常新的插件
- **更新频率**：近期有活跃的 bug 修复和稳定性改进
- **维护状态**：🟢 **活跃维护中** — 由 Epic Games 官方团队维护，属于 Virtual Production 工具链的核心组件
- **已知关注点**：
  - 插件仍在快速迭代中，API 可能会有变动
  - 上传流程（take upload）的稳定性正在持续改进中
  - 端点管理器的内存管理正在优化（弱指针改造）
- **推荐程度**：⭐⭐⭐⭐ — 如果你在做虚拟制片项目需要设备采集管理，这是官方推荐的解决方案。但由于插件较新，建议关注更新日志以跟进 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)
- 官方文档（暂无）
- [Live Link 官方文档](https://docs.unrealengine.com/5.7/en-US/live-link-in-unreal-engine/)

---

## 子模块文档索引

> 本插件为 xlarge 规模（258 个源文件，11 个模块），以下为各子模块的独立文档入口：

| 子模块 | 文档 | 说明 |
|---|---|---|
| CaptureManagerEditor | [CaptureManagerEditor.md](CaptureManagerEditor.md) | LiveLinkHub 应用模式集成 |
| CaptureManagerPipeline | [CaptureManagerPipeline.md](CaptureManagerPipeline.md) | 数据处理流水线 |
| CaptureDataConverter | [CaptureDataConverter.md](CaptureDataConverter.md) | 数据格式转换 |
| CaptureManagerMediaRW | [CaptureManagerMediaRW.md](CaptureManagerMediaRW.md) | 媒体文件读写 |
| CaptureManagerUnrealEndpoint | [CaptureManagerUnrealEndpoint.md](CaptureManagerUnrealEndpoint.md) | UE 端点上传 |
| IngestLiveLinkDevice | [IngestLiveLinkDevice.md](IngestLiveLinkDevice.md) | Live Link 设备数据摄取 |
| ExampleLiveLinkDevices | [ExampleLiveLinkDevices.md](ExampleLiveLinkDevices.md) | 示例设备实现 |
| LiveLinkCapabilities | [LiveLinkCapabilities.md](LiveLinkCapabilities.md) | Live Link 能力定义 |
| LiveLinkFaceMetadata | [LiveLinkFaceMetadata.md](LiveLinkFaceMetadata.md) | Live Link Face 元数据 |
| StereoCameraMetadata | [StereoCameraMetadata.md](StereoCameraMetadata.md) | 立体相机元数据 |
| CaptureManagerSettings | [CaptureManagerSettings.md](CaptureManagerSettings.md) | 插件配置 |