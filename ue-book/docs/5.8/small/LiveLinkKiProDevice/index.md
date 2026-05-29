# Live Link KiPro Device

> AJA Ki Pro recorder support for Live Link Hub with recording and connection capabilities

| 属性 | 值 |
|---|---|
| 中文名 | KiPro 录制设备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkKiProDevice` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkKiProDevice) | |

## 用途

该插件为 **Live Link Hub** 提供了对 **AJA Ki Pro** 录像机的原生支持。它是一个纯 C++ 实现，通过 Ki Pro 设备的 REST API 进行通信，解决了在虚拟制片工作流中需要远程控制和同步外部录制设备的痛点。

**核心功能**：
- **连接**：建立与 Ki Pro 设备的 HTTP 连接，定期轮询和重连。
- **录制控制**：远程启动和停止 Ki Pro 设备的录制，并同步元数据（Slate 名称和 Take 编号）。
- **状态监控**：解码设备固件版本，实时获取传输状态。
- **为测试提供模拟器**：附带 Python 脚本模拟 Ki Pro 设备，无需真实硬件即可开发和测试。

它取代了之前依赖 Switchboard 的解决方案，将控制功能直接集成到 Unreal 的 Live Link 设备框架中，简化了虚拟制片的录制流程。

## 使用场景

- **虚拟制片（Virtual Production）现场**：在拍摄过程中，需要将 Unreal Engine 中的 Take 信息（如 Slate 和 Take Number）同步到实际用于记录画面的 Ki Pro 录像机上。
- **多设备协同录制**：使用 Live Link Hub 统一管理多个录制设备（包括虚拟摄像机信号和物理录像机），确保所有源的元数据一致。
- **自动化录制工作流**：通过蓝图或 C++ 代码，根据场景需求（如开拍、停机）自动触发 Ki Pro 设备的录制和停止。

## 蓝图用法

该插件是一个纯 C++ 的 Live Link 设备实现，**没有暴露任何蓝图节点**（无 `BlueprintCallable` 或 `BlueprintReadWrite` 的 UFUNCTION）。其功能完全通过 Live Link Hub 的设备管理界面或继承其 C++ 基类来使用。

## C++ 用法

主要通过继承 `ULiveLinkKiProDeviceBase` 并实现 `ILiveLinkDeviceCapability_Connection` 和 `ILiveLinkDeviceCapability_Recording` 接口来使用。通常你只需要配置设备设置。

### 头文件引入

```cpp
#include “LiveLinkKiProDeviceBase.h”
#include “LiveLinkKiProDeviceSettings.h”
```

### 基本用法：创建并使用设备

此示例展示了如何在 C++ 中创建一个 Ki Pro 设备实例并配置其设置。
*(来源：插件基类 `LiveLinkKiProDeviceBase.h` 与 `LiveLinkKiProDeviceSettings.h`)*

```cpp
// 假设你已经通过设备管理器获取了一个 ULiveLinkDevice 引用
ULiveLinkDevice* SomeDevice = ...;

// 检查是否为 Ki Pro 设备
if (ULiveLinkKiProDeviceBase* KiProDevice = Cast<ULiveLinkKiProDeviceBase>(SomeDevice))
{
    // 获取或修改设备设置
    ULiveLinkKiProDeviceSettings* Settings = KiProDevice->GetSettings<ULiveLinkKiProDeviceSettings>();
    if (Settings)
    {
        Settings->IpAddress = TEXT(“192.168.1.105”);
        Settings->Port = 8080;
        Settings->bAutoPlayAfterStop = true;
        // 触发设置更新，设备会尝试重新连接
        KiProDevice->OnSettingChanged(FPropertyChangedEvent(nullptr));
    }

    // 尝试连接设备
    bool bConnected = KiProDevice->Connect_Implementation();

    // 开始录制
    if (bConnected && !KiProDevice->IsRecording_Implementation())
    {
        KiProDevice->StartRecording_Implementation();
    }
}
```

### 进阶用法：自定义设备行为

你可以继承 `ULiveLinkKiProDeviceBase` 来扩展或修改其默认行为。例如，在连接成功后执行自定义逻辑。

```cpp
// MyCustomKiProDevice.h
#pragma once
#include “LiveLinkKiProDeviceBase.h”
#include “MyCustomKiProDevice.generated.h”

UCLASS()
class UMyCustomKiProDevice : public ULiveLinkKiProDeviceBase
{
    GENERATED_BODY()

public:
    virtual void OnDeviceAdded() override
    {
        Super::OnDeviceAdded();
        // 设备被添加到 Live Link Hub 后的自定义初始化
        UE_LOG(LogTemp, Log, TEXT(“Custom KiPro device added. IP: %s”), *GetSettings<ULiveLinkKiProDeviceSettings>()->IpAddress);
    }

    virtual bool Connect_Implementation() override
    {
        bool bSuccess = Super::Connect_Implementation();
        if (bSuccess)
        {
            // 连接成功后的自定义逻辑
            UE_LOG(LogTemp, Log, TEXT(“Successfully connected to KiPro device.”));
        }
        return bSuccess;
    }
};
```

## Demo 示例

一个最小化的 Ki Pro 设备实现，继承了所有默认行为。

### MyMinimalKiProDevice.h
```cpp
#pragma once

#include “CoreMinimal.h”
#include “LiveLinkKiProDeviceBase.h”
#include “MyMinimalKiProDevice.generated.h”

UCLASS()
class UMyMinimalKiProDevice : public ULiveLinkKiProDeviceBase
{
	GENERATED_BODY()

public:
    // 使用基类默认设置类
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override
    {
        return ULiveLinkKiProDeviceSettings::StaticClass();
    }
};
```

### MyMinimalKiProDevice.cpp
```cpp
#include “MyMinimalKiProDevice.h”

// 此文件可以为空，所有功能均继承自 ULiveLinkKiProDeviceBase
```

## 模块依赖

该插件的 `Build.cs` 文件声明了对以下模块的依赖。使用者在构建自己的模块时，如果需要与 `LiveLinkKiProDevice` 交互，可能需要添加这些依赖。

| 模块 | 用途 |
|---|---|
| `LiveLinkDevice` | 提供 `ULiveLinkDevice` 基类和设备管理框架 |
| `LiveLinkGenericRecordingDevice` | 提供录制设备通用功能 |
| `PythonScriptPlugin` | 支持插件附带的 Python 模拟器脚本 |
| `HTTP` | 实现与 Ki Pro 设备的 REST API 通信 |
| `Json` | 解析 Ki Pro 设备返回的 JSON (或 JavaScript) 响应 |

## 维护状态

该插件为实验性功能，但创建时间较新，且有活跃的功能性更新和问题修复。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `106d5dfb` | Fix KiPro comms to query device for commands versus using hardcoded command names. | 修复通信逻辑，动态查询设备命令而非使用硬编码命令名。 |
| 2026-04-14 | `f6a8065d` | Matching device name with media source name | 使设备名称与媒体源名称匹配。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-27 | `acd2adc3` | Real KiPro hardware returns JavaScript notation instead of valid JSON. Preprocess strings from KiPro | 修复真实设备返回非标准JSON（JavaScript表示法）的问题，增加了预处理。 |
| 2026-03-10 | `ad0de199` | Live Link KiPro Device Plugin - Pure C++ Implementation | 插件首次提交，纯C++实现。 |

### 维护评价

- **状态**：**实验性 (Experimental)**，但**活跃维护中**。
- **评价**：该插件创建于 2026 年 3 月，年龄极短（约 0 年）。从提交历史看，在创建后的一个月内有多次重要的 bug 修复和功能改进（如处理非标准 JSON、动态查询命令），表明 Epic 团队正在积极开发和完善它。
- **建议**：由于是实验性功能，其 API 和功能未来可能会发生变化。适合在开发或测试环境中尝试使用，并关注后续更新。在生产环境中使用需谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkKiProDevice)
- [测试用例/模拟器](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkKiProDevice/Source/Scripts) （插件附带的 Python Mock 设备脚本）