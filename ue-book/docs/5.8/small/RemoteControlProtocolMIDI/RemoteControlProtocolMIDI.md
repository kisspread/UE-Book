# Remote Control Protocol MIDI

> Allows interactions between MIDI and RemoteControl API.

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

本插件是 **Remote Control** 生态系统中的一个协议实现，其核心用途是将物理 MIDI 设备（如音乐键盘、DJ 控制器、灯光控制台）的输入信号映射到 Unreal Engine 中通过 Remote Control API 管理的任何属性上。

它解决的问题是：在虚拟制片（Virtual Production）、现场演出或主题公园等场景中，艺术家和操作员需要快速、直观地通过硬件控制器调整引擎中的各种参数（如灯光强度、材质颜色、动画速率），而不必在软件界面上进行繁琐的鼠标操作。该插件充当了 MIDI 硬件与 Unreal 引擎内部属性系统之间的桥梁。

## 使用场景

- **虚拟制片现场**：灯光师使用 MIDI 推子实时调整 LED 墙上一个材质实例的“粗糙度”或“金属度”参数。
- **音乐可视化**：音乐家通过 MIDI 键盘控制场景中粒子系统的行为或颜色。
- **主题公园游乐设施**：利用 MIDI 时间码同步游乐设施的运动与场景中的动画。
- **自定义控制面板**：使用任何发送标准 MIDI 消息的设备（如 Launchpad、OSC 转 MIDI 工具）来触发引擎内的事件或修改对象属性。

## 蓝图用法

本插件主要通过编辑器中的 **Remote Control 面板** 进行配置和绑定，而非直接在蓝图中创建节点。其核心数据结构体 `FRemoteControlMIDIDevice` 和 `FRemoteControlMIDIProtocolEntity` 主要用于编辑器的 UI 和数据序列化。

### 核心数据结构

| 结构体/枚举 | 说明 |
|---|---|
| `ERemoteControlMIDIDeviceSelector` | 枚举，用于选择如何指定 MIDI 设备：使用项目默认设置、按设备名或按设备 ID。 |
| `FRemoteControlMIDIDevice` | 结构体，封装了 MIDI 设备的选择逻辑和识别信息（ID、名称、是否可用）。 |
| `FRemoteControlMIDIProtocolEntity` | 结构体，继承自 `FRemoteControlProtocolEntity`，定义了一次具体的 MIDI 绑定所需的所有参数（设备、事件类型、通道、消息数据）。 |

### 编辑器配置流程（等同于蓝图“使用”）

1.  在 **Window > Virtual Production > Remote Control** 面板中，为一个 Actor 或 Component 添加一个可暴露的属性。
2.  在该属性的 **Protocols** 列表下，点击 **Add** 并选择 **MIDI**。
3.  在出现的 MIDI 绑定配置中：
    *   **Device**：选择 MIDI 输入设备。可以选择“使用项目设置”（在项目设置中定义默认设备），或直接按名称/ID 指定。
    *   **Event Type**：选择监听的 MIDI 事件类型（如 `Control Change`， `Note On`， `Channel AfterTouch`）。
    *   **Channel**：指定 MIDI 通道（通常 1-16）。
    *   **Message Data 1**：对于 `Control Change` 事件，这是控制器编号（CC Number）；对于 `Note On`，这是音符号。
4.  此时，发送匹配条件的 MIDI 消息即可控制对应的引擎属性。

## C++ 用法

开发者可以通过 C++ 扩展或集成此协议模块。

### 头文件引入

```cpp
#include “RemoteControlProtocolMIDI/Public/RemoteControlProtocolMIDI.h”
```

### 基本用法：理解协议实体

`FRemoteControlMIDIProtocolEntity` 是存储绑定信息的核心。你可以检查或创建它。
（来源：`Public/RemoteControlProtocolMIDI.h`）

```cpp
// 假设你已经有一个 FRemoteControlProtocolEntity 指针 InEntityPtr
FRemoteControlProtocolEntity* InEntityPtr = /* ... */;

if (FRemoteControlMIDIProtocolEntity* MIDIEntity = static_cast<FRemoteControlMIDIProtocolEntity*>(InEntityPtr))
{
    // 获取当前绑定的 MIDI 事件类型
    EMIDIEventType BoundEventType = MIDIEntity->EventType;
    
    // 获取绑定的控制器编号 (CC#) 或音符号
    int32 BoundMessageData = MIDIEntity->MessageData1;
    
    // 获取绑定的 MIDI 通道
    int32 BoundChannel = MIDIEntity->Channel;
    
    // 获取设备信息
    const FRemoteControlMIDIDevice& BoundDevice = MIDIEntity->Device;
    
    UE_LOG(LogTemp, Log, TEXT(“绑定到 MIDI 通道 %d, 事件 %d, 数据1 %d.”), 
           BoundChannel, (int32)BoundEventType, BoundMessageData);
}
```

### 进阶用法：模块接口与设备查询

你可以通过模块接口异步获取可用的 MIDI 设备列表，并监听设备更新。
（来源：`Public/IRemoteControlProtocolMIDIModule.h`, `Private/RemoteControlProtocolMIDIModule.h`）

```cpp
// 获取 MIDI 模块接口
IRemoteControlProtocolMIDIModule& MIDIModule = FModuleManager::GetModuleChecked<IRemoteControlProtocolMIDIModule>(“RemoteControlProtocolMIDI”);

// 注册设备更新回调
MIDIModule.GetOnMIDIDevicesUpdated().AddLambda([](FMIDIDeviceCollection& Devices)
{
    UE_LOG(LogTemp, Log, TEXT(“MIDI 设备列表已更新，共 %d 个设备。”), Devices->Num());
    for (const FFoundMIDIDevice& Device : *Devices)
    {
        UE_LOG(LogTemp, Log, TEXT(“  设备 ID: %d, 名称: %s”), Device.ID, *Device.Name.ToString());
    }
});

// 异步刷新并获取设备列表
TFuture<FMIDIDeviceCollection> DevicesFuture = MIDIModule.GetMIDIDevices(true); // true 强制刷新
DevicesFuture.Then([](TFuture<FMIDIDeviceCollection> Future)
{
    if (Future.Get().IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT(“成功异步获取到 MIDI 设备列表。”));
    }
});

// 检查设备列表是否正在更新中
if (MIDIModule.IsUpdatingDevices())
{
    UE_LOG(LogTemp, Log, TEXT(“MIDI 设备正在刷新，请稍候…”));
}
```

## Demo 示例

以下是一个如何在 C++ 中配置一个 `FRemoteControlMIDIProtocolEntity` 的最小示例。通常这由 Remote Control 编辑器 UI 自动完成，但理解其结构有助于调试或动态创建绑定。

```cpp
// MyMIDIBindingExample.h
#pragma once

#include “CoreMinimal.h”
#include “RemoteControlProtocolMIDI/Public/RemoteControlProtocolMIDI.h”

class FMyMIDIBindingExample
{
public:
    static void CreateSampleBinding();
};

// MyMIDIBindingExample.cpp
#include “MyMIDIBindingExample.h”

void FMyMIDIBindingExample::CreateSampleBinding()
{
    // 1. 创建一个协议实体实例
    FRemoteControlMIDIProtocolEntity MIDIEntity;

    // 2. 配置设备：使用项目默认设置
    MIDIEntity.Device.DeviceSelector = ERemoteControlMIDIDeviceSelector::ProjectSettings;

    // 3. 配置绑定：监听 MIDI 通道 1 上的 Control Change 事件，控制器编号为 20 (例如一个旋钮)
    MIDIEntity.EventType = EMIDIEventType::ControlChange;
    MIDIEntity.Channel = 1;
    MIDIEntity.MessageData1 = 20; // CC Number

    // 4. 设置范围属性模板 (0-127 映射)
    MIDIEntity.RangeInputTemplate = 127;

    // 5. 实体现在已配置完成，但实际绑定通常由 Remote Control 系统管理。
    //    你可以将其序列化或用于初始化绑定逻辑。
    UE_LOG(LogTemp, Log, TEXT(“创建示例 MIDI 绑定配置完成：事件=%d, 通道=%d, CC#=%d”),
           (int32)MIDIEntity.EventType, MIDIEntity.Channel, MIDIEntity.MessageData1);

    // 注意：要让它真正工作，需要将其添加到 Remote Control 系统的某个 Property 上。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MIDIDevice` | 提供底层的 MIDI 设备输入输出功能，是 `UMIDIDeviceInputController` 的来源。 |
| `RemoteControl` | 提供远程控制 API 核心框架、协议接口 (`FRemoteControlProtocol`, `FRemoteControlProtocolEntity`) 和绑定管理系统。 |
| `RemoteControlAPI` | （隐含依赖）Remote Control 的运行时 API 模块。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧式 `UE_LOG` 迁移到新的 `UE_LOGF` 格式，属于引擎级维护。 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除了 Motion Design 相关插件的测试版标签，表明该插件随母项目趋于稳定。 |
| 2024-02-23 | `15bede99` | Entire engine compiling with -DisableUnity -IncludeHeaders | 修复了全引擎在特定编译选项（禁用 Unity 构建，包含所有头文件）下的编译错误。 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were | 为路径过长的模块添加短名称，可能是为了兼容性或构建系统优化。 |
| 2022-10-26 | `ed85af77` | Non unity/pch compile fixes | 修复了非 Unity 构建模式下的编译错误，保持代码的健壮性。 |

### 维护评价

该插件创建于 2021 年 4 月，已有约 5 年历史。从 Git 历史看，它并非处于高频活跃开发状态，但自 2024 年起仍有维护性提交（如编译修复）。最近的更新（2025 年 9 月）与 Remote Control 生态的稳定化相关。

- **优点**：作为 Epic 官方 Remote Control 套件的一部分，其设计稳定，API 变化不大。主要功能在创建初期已基本完成。
- **状态**：**维护中，但更新不频繁**。最后一次功能性更新（非编译修复）可追溯到 2024 年或更早。没有迹象表明其已被废弃，它作为虚拟制作工作流的基础组件仍然有效。
- **建议**：**可以安全使用**。其核心逻辑成熟，适合作为项目基础设施的一部分。如果项目需要深度定制 MIDI 解析逻辑，可能需要扩展或替换该协议模块，但基础功能是可靠的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolMIDI)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/remote-control-in-unreal-engine/) （Remote Control 总览文档，包含 MIDI 协议部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolMIDI/Tests)