# LiveLinkFreeD

> Live Link plugin for the FreeD protocol

| 属性 | 值 |
|---|---|
| 中文名 | 自由D协议 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkFreeD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkFreeD) | |

## 用途

该插件为 Unreal Engine 的 **Live Link** 框架提供了一个数据源，用于接收和解码 **FreeD** 协议数据。FreeD 是一种广泛应用于虚拟制片领域的行业标准协议，主要用于传输外部物理摄像机的位置、旋转、焦距、对焦距离等精确的运动跟踪数据。

**核心功能**：通过 UDP 网络连接，将 FreeD 格式的摄像机追踪数据实时转换为 UE 的 Live Link 帧数据流，从而驱动引擎内的虚拟摄像机（或任何可接收 Live Link 数据的对象）与现实世界中的物理摄像机同步运动。

**存在的意义**：在虚拟制片（VP）和 LED 墙拍摄中，需要将现场实体摄像机的实时运动数据与虚拟场景中的虚拟摄像机同步，以确保前景演员与虚拟背景的视角、运动完全匹配。此插件便是实现这一关键数据链路的桥梁。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 墙或绿幕拍摄中，使用带有追踪系统的实体摄像机控制虚拟摄像机。
-   **实时合成 (Real-time Compositing)**：将实拍镜头与实时渲染的 3D 场景进行匹配。
-   **电视直播/体育转播**：在体育赛事或直播中，将实况摄像机的运动与虚拟图形（如虚拟广告牌、3D 回放）同步。
-   **任何使用 FreeD 协议** 的追踪系统（如 Mo-Sys、NCAM、Stype、Sony、松下等）与 Unreal Engine 的集成。

## 蓝图用法

该插件的核心配置通过编辑器 UI 完成（见 C++ 部分），蓝图中主要涉及对 Live Link 源设置的调整。

### 核心节点

Live Link 源本身在蓝图中通常不直接创建和控制，而是通过 Live Link 面板进行管理。可通过蓝图访问其设置。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get / Set LiveLinkSourceSettings` | 获取或修改此 FreeD 源的特定设置，如编码器参数、默认配置。 | 通过 `ULiveLinkFreeDSourceSettings` 访问 |

### 使用示例（蓝图描述）

1.  **配置源**：在编辑器中，通过 `窗口 -> Live Link` 面板，点击 `+` 号，在 `Virtual Production` 分类下选择 `FreeD` 来创建源。
2.  **调整设置**：在源列表中选中刚创建的 FreeD 源，在下方的 `Details` 面板中可以修改 `ULiveLinkFreeDSourceSettings` 中的属性，如切换默认厂商配置（`Generic`, `Panasonic`, `Sony` 等）或微调焦距、对焦编码器的范围与掩码。
3.  **消费数据**：在场景中的 Actor（如 CineCameraActor）上，使用 `Live Link Controller` 组件，在 `Subject` 属性中选择由 FreeD 源创建的 Live Link 主体（默认为 “Camera” 或自定义名称）。

## C++ 用法

### 头文件引入

```cpp
// 访问连接设置
#include "LiveLinkFreeDConnectionSettings.h"

// 访问源设置（编码器参数等）
#include "LiveLinkFreeDSourceSettings.h"

// 如果需要直接创建源（通常由源工厂完成）
#include "LiveLinkFreeDSource.h"
```

### 基本用法

插件的典型使用是通过编辑器 UI。从代码层面，其核心是 `FLiveLinkFreeDSource` 类，它实现了 `ILiveLinkSource` 和 `FRunnable` 接口。

**核心工作流** (基于 `FLiveLinkFreeDSource`)：
1.  `ReceiveClient`: 将 Live Link 客户端的接口注入源中，用于发送数据。
2.  `Run`: 在独立线程中循环，通过 UDP Socket 接收 FreeD 数据包。
3.  `ProcessEncoderData` 与 `Decode_*` 系列函数: 对数据包进行校验和解码，将原始字节转换为有意义的浮点数（如焦距毫米值、焦距厘米值）。
4.  `Send`: 将处理后的数据打包成 `FLiveLinkFrameDataStruct`，并通过 `ILiveLinkClient` 发送到 Live Link 系统。

**来源文件**：`Source/LiveLinkFreeD/Private/LiveLinkFreeDSource.cpp`

### 进阶用法

高级用户可以通过 `ULiveLinkFreeDSourceSettings` 深度控制数据解码行为。

```cpp
// 获取当前活动的 FreeD 源的设置（假设已知一个源实例）
ULiveLinkFreeDSourceSettings* Settings = Source->GetSettings<ULiveLinkFreeDSourceSettings>();

// 修改默认配置为 Sony
Settings->DefaultConfig = EFreeDDefaultConfigs::Sony;

// 启用用户自定义编码器（通常用于光圈）并设置其范围
Settings->UserDefinedEncoderData.bIsValid = true;
Settings->UserDefinedEncoderData.bUseManualRange = true;
Settings->UserDefinedEncoderData.Min = 0;
Settings->UserDefinedEncoderData.Max = 65535; // 16位最大值

// 禁用发送额外元数据
Settings->bSendExtraMetaData = false;
```

## Demo 示例

以下是一个最小示例，展示如何在 C++ 中手动创建一个 FreeD Live Link 源并配置它。

**MyFreeDLinkActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkFreeDConnectionSettings.h"
#include "MyFreeDLinkActor.generated.h"

class FLiveLinkFreeDSource;

UCLASS()
class AMyFreeDLinkActor : public AActor
{
    GENERATED_BODY()

public:
    AMyFreeDLinkActor();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "LiveLink FreeD")
    FLiveLinkFreeDConnectionSettings ConnectionSettings;

private:
    TSharedPtr<FLiveLinkFreeDSource> FreeDSource;
};
```

**MyFreeDLinkActor.cpp**
```cpp
#include "MyFreeDLinkActor.h"
#include "LiveLinkFreeDSource.h"
#include "ILiveLinkClient.h"
#include "Features/IModularFeatures.h"

AMyFreeDLinkActor::AMyFreeDLinkActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 预置默认连接设置
    ConnectionSettings.IPAddress = TEXT("0.0.0.0");
    ConnectionSettings.UDPPortNumber = 40000;
    ConnectionSettings.SubjectName = TEXT("MyCamera");
}

void AMyFreeDLinkActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建源实例
    FreeDSource = MakeShared<FLiveLinkFreeDSource>(ConnectionSettings);

    // 2. 手动连接到 Live Link 系统（这一步通常由源工厂的UI自动处理）
    // 通过模块化特性找到 Live Link 客户端
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (ModularFeatures.IsModularFeatureAvailable(ILiveLinkClient::ModularFeatureName))
    {
        ILiveLinkClient* LiveLinkClient = &ModularFeatures.GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
        // 生成一个源GUID
        FGuid SourceGuid = FGuid::NewGuid();
        // 将源注册到客户端
        LiveLinkClient->AddSource(FreeDSource, SourceGuid);
        // 通知源已收到客户端（完成连接握手）
        FreeDSource->ReceiveClient(LiveLinkClient, SourceGuid);
    }
}

void AMyFreeDLinkActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 请求源关闭，会停止其内部线程
    if (FreeDSource.IsValid())
    {
        FreeDSource->RequestSourceShutdown();
        FreeDSource.Reset();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

从插件的 `Build.cs` 文件分析，除通用引擎模块外，还需依赖以下模块：

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心运行时框架。 |
| `LiveLinkInterface` | Live Link 公共接口定义。 |
| `Sockets` | 提供跨平台的 Socket 网络通信能力。 |
| `Networking` | 提供更高层的网络功能支持。 |
| `UdpMessaging` | (插件依赖) 启用 UDP 消息总线，是 FreeD 协议基于 UDP 的网络基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 格式。 |
| 2025-08-10 | `f514a032` | LiveLinkFreeD: Fix ip address tooltip. | 修复了 IP 地址设置项的工具提示文本。 |
| 2025-08-10 | `8aebd228` | LiveLinkFreeD: Add subject name override option. | 新增了自定义 Live Link 主体名称的选项。 |
| 2025-08-07 | `11d8ecb8` | LiveLinkFreeD: Clarified tooltip of ip address. | 优化了 IP 地址工具提示的说明文字。 |
| 2023-11-29 | `5edc4334` | LiveLink FreeD: Update default encoder values | 更新了编码器的默认参数值。 |

### 维护评价

-   **活跃状态**：**维护中**。最近的提交记录显示在 2025 年有功能增强（主体名称覆盖）和问题修复（工具提示），2026 年有代码风格迁移。这表明插件仍在持续维护。
-   **年龄**：创建于 2021 年，属于较新的插件。
-   **实验性**：`.uplugin` 中标记为 `IsBetaVersion: true`，且默认不启用（`EnabledByDefault: false`），使用时需手动在插件列表中启用。
-   **已知限制**：作为 Beta 版本，可能在某些边缘情况或特定设备厂商的 FreeD 实现上存在兼容性问题。
-   **推荐使用**：**推荐在虚拟制片项目中使用**。它是连接 UE 与行业标准 FreeD 追踪系统的官方途径之一。尽管是 Beta 版，但已有稳定的功能基础，并且 Epic 仍在更新维护。对于需要此功能的项目，它是必不可少的。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkFreeD)
-   [官方文档]() (暂无)
-   [测试用例]() (插件目录内未发现独立测试文件，可能集成在 LiveLink 整体测试中)