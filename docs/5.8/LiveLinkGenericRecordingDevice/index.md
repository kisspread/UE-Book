# LiveLinkGenericRecordingDevice

> Provides a generic recording device that can be used by Python scripts for Live Link Hub. It is hidden by default as the classes are abstract.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkGenericRecordingDevice` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkGenericRecordingDevice) | |

## 用途

该插件为 **Live Link Hub** 提供了一个可扩展的、基于 Python 的录制设备框架。它本身不实现具体的录制逻辑，而是定义了一个抽象基类 `ULiveLinkGenericRecordingDevice`，该类实现了 `ILiveLinkDeviceCapability_Recording` 接口。开发者（主要是 Python 脚本）可以继承这个基类，快速创建自定义的 Live Link 录制设备，而无需从头实现所有设备接口和录制能力。其核心价值在于为 Python 脚本提供了一个标准化的“桩”（Stub），用于构建 Live Link 生态中的自定义录制工具。

## 使用场景

-   **Python 脚本开发 Live Link 录制设备**：当你需要使用 Python 为 Live Link Hub 快速原型化或实现一个自定义的录制设备时，继承此插件提供的基类可以省去大量样板代码。
-   **集成特定数据源的录制**：如果你的数据源（如特定的传感器、自定义协议）有 Python SDK 或库，你可以通过继承此设备类，利用 Python 的生态来实现数据的捕获和录制逻辑。
-   **Live Link Hub 扩展开发**：作为 Live Link Device 插件体系的一部分，它为通过 Python 扩展 Live Link Hub 的设备类型提供了官方支持路径。

## 蓝图用法

该插件主要面向 Python 脚本扩展，其核心类 `ULiveLinkGenericRecordingDevice` 被标记为 `Abstract` 和 `Blueprintable`，意味着它不能直接在蓝图中实例化，但可以被蓝图或 Python 子类继承。其暴露给蓝图（及 Python）的接口主要是用于重写的 `BlueprintNativeEvent` 函数和可读写的属性。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDisplayNameHelper` | (BlueprintNativeEvent) 获取设备的显示名称，供 Python 子类重写。 | `ULiveLinkGenericRecordingDevice` |
| `GetDeviceHealthHelper` | (BlueprintNativeEvent) 获取设备的健康状态，供 Python 子类重写。 | `ULiveLinkGenericRecordingDevice` |
| `GetHealthTextHelper` | (BlueprintNativeEvent) 获取设备健康状态的文本描述，供 Python 子类重写。 | `ULiveLinkGenericRecordingDevice` |
| `StartRecording` | (来自 ILiveLinkDeviceCapability_Recording) 开始录制，供 Python 子类实现具体逻辑。 | `ULiveLinkGenericRecordingDevice` |
| `StopRecording` | (来自 ILiveLinkDeviceCapability_Recording) 停止录制，供 Python 子类实现具体逻辑。 | `ULiveLinkGenericRecordingDevice` |
| `IsRecording` | (来自 ILiveLinkDeviceCapability_Recording) 查询是否正在录制，供 Python 子类实现。 | `ULiveLinkGenericRecordingDevice` |

### 使用示例（蓝图/Python 描述）

在 Python 中，你会创建一个继承自 `ULiveLinkGenericRecordingDevice` 的子类，并重写上述 `BlueprintNativeEvent` 函数。例如：
```python
import unreal

@unreal.uclass()
class MyPythonRecorder(unreal.LiveLinkGenericRecordingDevice):
    @unreal.ufunction(override=True)
    def get_display_name_helper(self):
        return unreal.Text("My Python Recorder")

    @unreal.ufunction(override=True)
    def start_recording(self):
        # 实现你的开始录制逻辑
        self.set_editor_property('b_is_recording', True)
        return True

    # ... 重写其他函数
```
在蓝图中，你可以创建一个继承自 `LiveLinkGenericRecordingDevice` 的蓝图类，并在事件图表中重写 `GetDisplayNameHelper`、`StartRecording` 等事件。

## C++ 用法

虽然此插件主要设计给 Python 使用，但 C++ 开发者也可以继承其基类。不过，更推荐使用 Python 进行快速开发。

### 头文件引入

```cpp
#include "LiveLinkGenericRecordingDevice.h"
```

### 基本用法

C++ 中继承该抽象类需要实现所有纯虚函数和接口函数。
```cpp
// MyRecorderDevice.h
#pragma once
#include "LiveLinkGenericRecordingDevice.h"
#include "MyRecorderDevice.generated.h"

UCLASS()
class UMyRecorderDevice : public ULiveLinkGenericRecordingDevice
{
    GENERATED_BODY()

public:
    // 重写 ULiveLinkDevice 接口
    virtual FText GetDisplayName() const override;
    virtual EDeviceHealth GetDeviceHealth() const override;
    virtual FText GetHealthText() const override;

    // 重写 ILiveLinkDeviceCapability_Recording 接口
    virtual bool StartRecording_Implementation() override;
    virtual bool StopRecording_Implementation() override;
    virtual bool IsRecording_Implementation() const override;
};
```

### 进阶用法

通常，C++ 子类会结合 `ULiveLinkGenericRecordingDeviceSettings` 来提供更具体的配置选项。你可以通过重写 `GetSettingsClass()` 来返回自定义的设置类。

## Demo 示例

以下是一个完整的、可编译的 C++ 子类最小示例，展示了如何实现一个简单的录制设备。

**MyRecorderDevice.h**
```cpp
// Copyright Your Company. All Rights Reserved.
#pragma once
#include "LiveLinkGenericRecordingDevice.h"
#include "MyRecorderDevice.generated.h"

UCLASS(Blueprintable)
class UMyRecorderDevice : public ULiveLinkGenericRecordingDevice
{
    GENERATED_BODY()

public:
    UMyRecorderDevice();

    //~ Begin ULiveLinkDevice interface
    virtual TSubclassOf<ULiveLinkDeviceSettings> GetSettingsClass() const override;
    virtual FText GetDisplayName() const override;
    virtual EDeviceHealth GetDeviceHealth() const override;
    virtual FText GetHealthText() const override;
    //~ End ULiveLinkDevice interface

    //~ Begin ILiveLinkDeviceCapability_Recording interface
    virtual bool StartRecording_Implementation() override;
    virtual bool StopRecording_Implementation() override;
    virtual bool IsRecording_Implementation() const override;
    //~ End ILiveLinkDeviceCapability_Recording interface
};
```

**MyRecorderDevice.cpp**
```cpp
// Copyright Your Company. All Rights Reserved.
#include "MyRecorderDevice.h"

UMyRecorderDevice::UMyRecorderDevice()
{
    // 可以在这里设置默认的 Slate 和 Take
    Slate = TEXT("DefaultSlate");
    Take = TEXT("1");
}

TSubclassOf<ULiveLinkDeviceSettings> UMyRecorderDevice::GetSettingsClass() const
{
    // 使用基类提供的默认设置类，或返回自定义的设置类
    return ULiveLinkGenericRecordingDeviceSettings::StaticClass();
}

FText UMyRecorderDevice::GetDisplayName() const
{
    return FText::FromString(TEXT("My C++ Recorder"));
}

EDeviceHealth UMyRecorderDevice::GetDeviceHealth() const
{
    // 根据你的设备状态返回健康状态
    return EDeviceHealth::Nominal;
}

FText UMyRecorderDevice::GetHealthText() const
{
    return FText::FromString(TEXT("Device is operational."));
}

bool UMyRecorderDevice::StartRecording_Implementation()
{
    if (!bIsRecording)
    {
        UE_LOG(LogTemp, Log, TEXT("Recording started for Slate: %s, Take: %s"), *Slate, *Take);
        bIsRecording = true;
        // 在这里添加实际的录制启动逻辑
        return true;
    }
    return false;
}

bool UMyRecorderDevice::StopRecording_Implementation()
{
    if (bIsRecording)
    {
        UE_LOG(LogTemp, Log, TEXT("Recording stopped."));
        bIsRecording = false;
        // 在这里添加实际的录制停止逻辑
        return true;
    }
    return false;
}

bool UMyRecorderDevice::IsRecording_Implementation() const
{
    return bIsRecording;
}
```

## 模块依赖

该插件依赖于 `LiveLinkDevice` 插件，以获取 `ULiveLinkDevice` 基类和相关接口。

| 模块 | 用途 |
|---|---|
| `LiveLinkDevice` | 提供 Live Link 设备的基础框架、接口（如 `ILiveLinkDeviceCapability_Recording`）和设置类。 |

## 维护状态

### 近期更新

-   2026-04-14 f6a8065d Matching device name with media source name
-   2026-03-06 27378fe7 A generic recording device that is implementable by python plugins. This is the stubbed functionality.

### 维护评价

该插件创建时间非常近（2026年3月），并且在一个月后就有了一次功能性更新（设备名称匹配）。这表明它处于**活跃维护**阶段，是 Epic 为 Live Link 生态引入的新功能。由于它被标记为 `Hidden` 和 `IsExperimentalVersion`，说明它仍处于实验性阶段，API 和功能在未来版本中可能会有变动。目前推荐用于实验和原型开发，不建议在需要长期稳定性的生产环境中直接依赖。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkGenericRecordingDevice)