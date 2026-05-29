# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（核心运行时模块与功能库） |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

CaptureManagerCore 是虚幻引擎虚拟制作管线中设备捕获功能的核心基础架构插件。它**不是**一个面向最终用户的独立工具，而是一个提供底层服务、协议、数据格式和工具函数的“工具箱”库。其主要目的是**为 `CaptureManagerApp`（控制设备的客户端应用）和 `CaptureManagerEditor`（引擎内的编辑器插件）提供一套共享的、标准化的底层能力**，确保两者在数据通信、格式解析、状态管理和媒体处理上行为一致。

## 使用场景

- **开发虚幻引擎虚拟制作插件**：当你需要为新的捕获设备或协议编写支持时，可以复用本插件中的 `CaptureProtocolStack` 通信协议、`CaptureManagerTakeMetadata` 数据定义和 `CaptureDataConverter` 工具。
- **构建自定义数据处理流水线**：利用 `CaptureManagerPipeline` 模块提供的可扩展节点，构建从原始捕获数据到可用资产的自动化处理流程。
- **集成第三方编码器**：通过 `CaptureManagerMediaRW` 模块将自定义的编码器/解码器集成到虚幻引擎的媒体框架中。
- **增强Live Link工作流**：`LiveLinkHubCaptureMessaging` 提供了与Live Link Hub等外部工具进行捕获数据交换的消息通道。

## 蓝图用法

本插件主要提供底层C++服务和API，**直接的蓝图可调用节点相对有限**。其功能通常被上层插件（如CaptureManagerEditor）封装后供蓝图使用。开发者主要通过C++接口进行集成和扩展。建议查阅具体的模块文档以了解其提供的接口。

## C++ 用法

### 基本用法

以下示例展示了如何使用 `CaptureDataConverter` 模块进行基础的数据转换。

```cpp
// 头文件引入
#include “CaptureDataConverter/CaptureDataConverter.h”

// 创建转换器并转换一个 TakeMetadata 文件
FCaptureDataConverter::FConvertResult ConvertTake(const FString& InputTakePath, const FString& OutputDir)
{
    // 配置转换选项
    FCaptureDataConverter::FConvertOptions Options;
    Options.OutputDirectory = OutputDir;
    // ... 其他选项设置

    // 执行转换
    return FCaptureDataConverter::ConvertTake(InputTakePath, Options);
}
```
*来源: `Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureDataConverter/Tests/CaptureDataConverterTest.cpp`*

### 进阶用法

结合 `CaptureProtocolStack` 和 `CaptureManagerCPSClient` 实现一个简单的捕获设备发现流程。

```cpp
#include “CaptureProtocolStack/CPSClient.h”
#include “CaptureManagerCPSClient/CaptureManagerCPSClient.h”

// 初始化CPS客户端并搜索设备
void DiscoverDevices()
{
    // 获取 CPS 客户端单例
    FCPSClient* CPSClient = FCPSClient::Get();
    if (CPSClient)
    {
        // 设置设备发现回调
        CPSClient->SetDeviceDiscoveryCallback([](const FCPSDeviceId& DeviceId, const FDeviceInfo& Info)
        {
            UE_LOG(LogTemp, Log, TEXT(“发现设备: %s - %s”), *DeviceId.ToString(), *Info.DeviceName);
        });

        // 开始异步搜索
        CPSClient->StartDiscovery();
    }
}
```
*来源: 结合 `CaptureProtocolStack` 和 `CaptureManagerCPSClient` 模块的典型用法模式*

## Demo 示例

本插件作为核心库，不包含独立的运行示例项目。其功能通过上层插件 `CaptureManagerApp` 和 `CaptureManagerEditor` 进行演示和使用。开发者应参考这些插件的示例，或编写针对特定模块功能的小型测试程序。

## 模块依赖

使用本插件时，你的构建目标需要根据所使用的具体子模块添加依赖。以下是各模块独特的、非常见的依赖项列表：

| 模块 | 用途 |
|---|---|
| `CaptureProtocolStack` | 与捕获设备通信的底层协议实现 |
| `MediaUtils`, `MediaAssets` | `CaptureManagerMediaRW` 模块的媒体框架集成依赖 |
| `LiveLinkInterface` | `LiveLinkHubCaptureMessaging` 模块的 Live Link 接口依赖 |
| `RenderCore`, `RHI` | `CaptureDataConverter` 中涉及纹理和渲染资源处理 |
| `EngineSettings` | `CaptureManagerPipeline` 读取引擎配置 |
| `AutomationController` | `CaptureDataConverter` 等模块的自动化测试依赖 |

**注意**：以上列表仅包含不常见的依赖。所有模块均隐含依赖于 `Core`, `CoreUObject`, `Engine` 等基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 优化第三方编码器，支持取消音视频转换任务 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补回在模块迁移过程中遗漏的代码修复 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复因事务ID数据竞争导致的偶发性下载失败问题 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构JSON对象以同时支持FString和SharedString，提升性能 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增CaptureManagerDeviceBlueprint模块（来自历史记录） |

### 维护评价

**活跃维护中**。该插件创建时间较新（2025年初），近期（2026年）更新非常频繁，显示出核心功能正在积极开发和优化。最近的提交涉及性能优化、bug修复和新功能模块的添加。作为虚拟制作管线的基础设施，其维护质量对整个工作流至关重要。目前没有废弃迹象，**推荐在需要虚拟制作捕获功能时使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Tests)

### 子模块文档导航

- [CaptureDataConverter.md](CaptureDataConverter.md)
- [CaptureManagerCPSClient.md](CaptureManagerCPSClient.md)
- [CaptureManagerMediaRW.md](CaptureManagerMediaRW.md)
- [CaptureManagerPipeline.md](CaptureManagerPipeline.md)
- [CaptureManagerStyle.md](CaptureManagerStyle.md)
- [CaptureManagerTakeMetadata.md](CaptureManagerTakeMetadata.md)
- [CaptureMetadataExtraction.md](CaptureMetadataExtraction.md)
- [CaptureProtocolStack.md](CaptureProtocolStack.md)
- [CaptureUtils.md](CaptureUtils.md)
- [DataIngestCore.md](DataIngestCore.md)
- [LiveLinkHubCaptureMessaging.md](LiveLinkHubCaptureMessaging.md)