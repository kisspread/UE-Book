# Audio Definition Model (ADM)

> Currently only supports output spatialized using WASAPI aggregate output channels and spatial ADM information transmitted using Open Sound Control (OSC).

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `ADMSpatialization` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-11-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ADM) | |

## 用途

该插件为 Unreal Engine 提供了基于 **Audio Definition Model (ADM)** 标准的空间音频输出能力。它并非一个通用的空间化解决方案，而是专注于将引擎内的音频源位置信息，按照 ADM-OSC 规范，通过网络协议（OSC）实时发送给外部的音频处理系统（如专业音频工作站、沉浸式音频渲染器等）。同时，它支持通过 Windows 的 WASAPI 驱动，将音频直接输出到指定的聚合音频设备通道，实现精确的物理声道映射。

**核心解决的问题**：在需要与外部专业音频硬件或软件进行集成，以实现符合行业标准（ADM）的沉浸式音频制作、广播或现场演出时，提供引擎内的数据接口和音频路由能力。

## 使用场景

- 你正在为音乐演出、广播或虚拟现实体验开发一个需要精确控制声音在三维空间中位置的应用程序，并希望将空间化数据发送到外部的 Dolby Atmos 渲染器或专业音频接口。
- 你的音频工作流基于 ADM 标准，需要将 Unreal Engine 作为内容生成端，与基于 ADM 的音频制作工具链（如 Reaper 的 ADM 插件、SPAT Revolution 等）进行实时数据同步。
- 你需要将游戏引擎中的多个音频对象，通过网络协议（OSC）控制外部音频矩阵或空间音频处理器。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Send IP Address` | 设置用于发送 ADM-OSC 数据的远程 IP 地址和端口。 | `UADMEngineSubsystem` |
| `Connect ADM OSC Client` | （仅编辑器）根据项目设置中的 IP 和端口，初始化或重新初始化 ADM OSC 客户端连接。 | `UADMSpatializationSettings` |

### 使用示例（蓝图描述）

1.  **配置连接**：
    - 在项目设置中找到 “ADM Spatialization Settings”。
    - 填写 “OSC IP Address” 和 “OSC IP Port”（默认 4001）。
    - 点击 “Connect ADM OSC Client” 按钮进行测试连接。
2.  **运行时动态设置**：
    - 在蓝图中，使用 `Get Audio Engine Subsystem` 节点获取 `UADMEngineSubsystem` 实例。
    - 调用 `Set Send IP Address` 节点，传入新的 IP 和端口字符串，以在运行时更改数据发送目标。

## C++ 用法

### 头文件引入

```cpp
#include "ADMSpatialization.h"
#include "ADMSpatializationSettings.h"
```

### 基本用法

主要涉及通过工厂类创建空间化插件实例，以及通过设置类配置网络参数。

```cpp
// 获取 ADM 空间化工厂（通常由音频设备内部管理）
UE::ADM::Spatialization::FADMSpatializationFactory* ADMFactory = ...; // 通过模块获取

// 设置 OSC 发送端点
FIPv4Endpoint Endpoint;
Endpoint.Address = FIPv4Address(192, 168, 1, 100);
Endpoint.Port = 4001;
ADMFactory->SetSendIPEndpoint(Endpoint);

// 创建空间化插件实例（通常由音频设备自动调用）
TAudioSpatializationPtr SpatializationPlugin = ADMFactory->CreateNewSpatializationPlugin(OwningAudioDevice);
```

### 进阶用法

直接操作 `FSourceDirectOut` 类来管理音频源到物理输出通道的映射。

```cpp
// 假设已获得一个 FSourceDirectOut 实例
UE::ADM::Spatialization::FSourceDirectOut* DirectOutChannel = ...;

// 激活该通道并绑定音频源
DirectOutChannel->SetIsActive(true);
DirectOutChannel->SetSourceId(AudioSourceId);

// 在音频渲染线程中处理音频数据
DirectOutChannel->ProcessDirectOut(InputAudioData);
```

## Demo 示例

以下是一个最小化的示例，展示如何在 C++ 中初始化 ADM 空间化插件并配置其网络设置。

**MyADMGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyADMGameMode.generated.h"

UCLASS()
class MYPROJECT_API AMyADMGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void StartPlay() override;

private:
    void InitializeADMPlugin();
};
```

**MyADMGameMode.cpp**
```cpp
#include "MyADMGameMode.h"
#include "ADMSpatialization.h"
#include "ADMSpatializationModule.h"
#include "AudioDevice.h"

void AMyADMGameMode::StartPlay()
{
    Super::StartPlay();
    InitializeADMPlugin();
}

void AMyADMGameMode::InitializeADMPlugin()
{
    // 获取音频设备
    FAudioDeviceHandle AudioDevice = GEngine->GetMainAudioDevice();
    if (!AudioDevice.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("No valid audio device found."));
        return;
    }

    // 获取 ADM 模块和工厂
    UE::ADM::Spatialization::FModule& ADMModule = FModuleManager::GetModuleChecked<UE::ADM::Spatialization::FModule>(TEXT("ADMSpatialization"));
    UE::ADM::Spatialization::FADMSpatializationFactory& ADMFactory = ADMModule.GetFactory();

    // 配置 OSC 发送地址 (例如，发送到本机的另一个音频处理程序)
    FIPv4Endpoint Endpoint;
    Endpoint.Address = FIPv4Address(127, 0, 0, 1);
    Endpoint.Port = 4001;
    ADMFactory.SetSendIPEndpoint(Endpoint);

    UE_LOG(LogTemp, Log, TEXT("ADM Spatialization Plugin initialized. Sending OSC to 127.0.0.1:4001"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OSC` | 用于通过 Open Sound Control 协议发送 ADM 空间化数据。 |
| `AudioMixer` | 提供底层音频混合器平台接口，用于直接输出到音频设备通道。 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` 将 UE_LOG 迁移至 UE_LOGF 宏。
- 2025-04-22 `017ec0fc` 添加聚合设备枚举和用于音频设备选择的编辑器 UI。
- 2025-01-28 `b71c100e` 修复了 UE 到 ADM-OSC 坐标转换不正确的问题。

### 维护评价

该插件创建于 2024 年底，属于较新的功能。从提交历史看，它在 2025 年初进行了重要的功能增强（设备选择、坐标修复）和维护性更新（日志宏迁移），表明它处于**活跃维护**状态。作为实验性插件，其 API 和功能在未来版本中可能会有变动。目前它专注于 Win64 平台和特定的 WASAPI/OSC 输出路径，适用场景明确但相对专业。对于需要与外部 ADM 兼容音频系统集成的项目，这是一个值得尝试的实验性功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ADM)
- [官方文档]() (暂无)