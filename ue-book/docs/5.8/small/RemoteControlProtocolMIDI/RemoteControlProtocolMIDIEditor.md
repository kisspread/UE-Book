# Remote Control Protocol MIDI

> Allows interactions between MIDI and RemoteControl API.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MIDI 远程控制协议 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RemoteControlProtocolMIDI` (Runtime), `RemoteControlProtocolMIDIEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolMIDI) | |

## 用途

这个插件的核心作用是**为 MIDI（Musical Instrument Digital Interface）设备提供了一个标准化的接口，使其能够与 Unreal Engine 的 Remote Control 系统进行通信**。Remote Control 允许用户通过网络或其他协议远程控制引擎内的各种属性（如 Actor 位置、材质参数等）。此插件将 MIDI 信号（如音符、控制变化消息）翻译并映射为 Remote Control API 可理解的格式，从而实现**使用物理 MIDI 控制器（键盘、推子、旋钮等）来操控 Unreal Engine 中的游戏或虚拟制作场景**。

它解决的问题是：在虚拟制作、现场演出或交互式装置中，需要使用 MIDI 硬件进行低延迟、高精度的实时控制，而此插件为此提供了官方的、集成化的解决方案。

## 使用场景

- **现场虚拟制作**：在虚拟摄像机控制、灯光或材质实时调整中，使用 MIDI 推子或旋钮进行流畅的现场操作。
- **音频工作站集成**：将 DAW（数字音频工作站）中的 MIDI 信号发送到 Unreal Engine，用于驱动视觉效果同步于音乐。
- **自定义交互装置**：构建一个 MIDI 控制器，用于操控引擎中复杂的蓝图逻辑或游戏状态。
- **快速原型与调试**：使用廉价的 MIDI 设备快速测试和调整引擎内的数值参数，比用鼠标更直观、高效。

## 蓝图用法

该插件主要通过编辑器中的 **Remote Control** 面板进行配置和使用，其核心映射逻辑在 Runtime 模块中实现。目前提供的头文件主要展示了编辑器侧的设备选择定制，没有直接暴露 `BlueprintCallable` 的节点给蓝图用户。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| **（无直接蓝图节点）** | 功能主要通过编辑器 UI 和 Remote Control 面板配置 | N/A |

### 使用示例（编辑器配置描述）

1.  确保 `RemoteControlProtocolMIDI` 插件在 **编辑器偏好设置 -> 插件** 中已启用。
2.  打开 **Remote Control** 面板（通常在“窗口” -> “虚拟制片”下）。
3.  在 Remote Control 面板中，选择需要控制的 Actor 或组件属性。
4.  在协议列表中，选择 **MIDI** 协议。
5.  此时会出现 MIDI 设备选择的下拉菜单（由 `FRemoteControlMIDIDeviceCustomization` 提供），从中选择你连接的 MIDI 控制器。
6.  在控制器上移动推子或按下按键，面板中对应的属性将自动映射并响应。

## C++ 用法

### 头文件引入

主要的运行时接口包含在 `RemoteControlProtocolMIDI` 模块中。编辑器定制功能则在 `RemoteControlProtocolMIDIEditor` 模块中。
```cpp
// 用于访问 MIDI 设备和映射（Runtime 模块）
#include "RemoteControlProtocolMIDI.h" // 假设存在此主头文件
// 用于编辑器定制（Editor 模块）
#include "DetailCustomizations/RemoteControlMIDIDeviceCustomization.h"
```

### 基本用法

该插件的工作流程通常是被 Remote Control 系统内部调用。开发者更可能通过编辑器 UI 来使用它。如果你需要以编程方式与 MIDI 设备列表交互，可以参考 `FRemoteControlMIDIDeviceCustomization` 中的设备枚举逻辑。

```cpp
// 伪代码：概念性示例，展示设备枚举流程
// 实际实现会涉及 MIDIDevice 插件的 API
TArray<FMIDIDeviceItem> AvailableDevices;
// ... 调用 MIDIDevice 模块获取设备列表并填充 AvailableDevices ...
// 可以参考 OnMIDIDevicesUpdated 回调和 FMIDIDeviceItem 结构体
```

### 进阶用法

要创建自定义的 MIDI 控制交互，通常需要理解 `RemoteControlProtocolMIDI` 运行时模块如何将 MIDI 消息（如 `CC` 消息）映射到 `FRemoteControlField` 或 `FRemoteControlActor` 上。这通常涉及修改 `RemoteControlProtocolMIDI` 模块自身的代码，或者监听其定义的委托。

## Demo 示例

以下是一个概念性的 C++ 示例，展示了如何可能集成 MIDI 设备发现功能。请注意，此示例高度简化，实际应用需要遵循引擎的模块依赖和线程安全规则。

```cpp
// MyMIDIController.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
// 假设存在这个头文件，用于设备信息
#include "RemoteControlProtocolMIDI/Types/MIDIDeviceInfo.h"
#include "MyMIDIController.generated.h"

UCLASS()
class AMyMIDIController : public AActor
{
    GENERATED_BODY()

public:
    AMyMIDIController();

    virtual void BeginPlay() override;

    // 用于接收可用 MIDI 设备列表的回调
    void OnMIDIDevicesFound(const TArray<FMIDIDeviceInfo>& Devices);

private:
    // 存储找到的设备
    UPROPERTY()
    TArray<FMIDIDeviceInfo> ConnectedDevices;
};

// MyMIDIController.cpp
#include "MyMIDIController.h"
#include "MIDIDeviceManager.h" // 来自 MIDIDevice 插件

AMyMIDIController::AMyMIDIController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMIDIController::BeginPlay()
{
    Super::BeginPlay();

    // 异步请求获取 MIDI 设备列表
    // 注意：这是一个示意，实际 API 请查阅 MIDIDevice 插件文档
    UMIDIDeviceManager::Get()->FindMIDIDevices_Async(
        FOnMIDIDevicesFound::CreateUObject(this, &AMyMIDIController::OnMIDIDevicesFound)
    );
}

void AMyMIDIController::OnMIDIDevicesFound(const TArray<FMIDIDeviceInfo>& Devices)
{
    ConnectedDevices = Devices;
    for (const auto& Device : Devices)
    {
        UE_LOG(LogTemp, Log, TEXT("Found MIDI Device: %s (ID: %d)"), *Device.Name.ToString(), Device.DeviceId);
    }
}
```

## 模块依赖

根据 `.uplugin` 的 `Plugins` 字段，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `RemoteControlAPI` | 核心的远程控制框架，此插件为其提供 MIDI 协议实现 |
| `MIDIDevice` | 提供底层的 MIDI 设备枚举、消息收发功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除了动态设计插件的 beta 标签，表明其已趋于稳定。 |
| 2024-02-23 | `15bede99` | Entire engine compiling with -DisableUnity -IncludeHeaders | 引擎级编译修复，与插件功能无关。 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were | 为路径过长的模块添加 ShortName，属于引擎内部维护。 |
| 2022-10-26 | `ed85af77` | Non unity/pch compile fixes | 编译修复，解决非统一编译问题。 |

### 维护评价

该插件创建于 2021 年，拥有超过 5 年的历史。从提交记录看，**近期的更新均为引擎级的维护性提交**（如编译修复、日志宏迁移、标签管理），而非插件功能本身的增强或修复。最后一次实质性功能相关更新可能在更早的时间。这表明该插件已进入**稳定维护期，但活跃开发基本停滞**。考虑到虚拟制作领域技术迭代较快，且此插件依赖的 `RemoteControl` 和 `MIDIDevice` 基础可能也在变化，**不推荐在全新的、需要长期维护的核心项目中依赖此插件作为唯一的 MIDI 控制方案**。建议评估是否有更新的社区插件或自行基于 `MIDIDevice` 插件进行开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolMIDI)
- 官方文档链接（`.uplugin` 中为空）
- 测试用例（未在提供的文件列表中明确标识，可能位于 `Engine/Tests/` 或插件内部的 `Tests/` 目录下）