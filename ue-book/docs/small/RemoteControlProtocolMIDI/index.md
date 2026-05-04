# Remote Control Protocol MIDI

> Allows interactions between MIDI and RemoteControl API.

| 属性 | 值 |
|---|---|
| 分类 | VirtualProduction |
| 默认启用 | — |
| 包含内容 | false |
| 模块 | RemoteControlProtocolMIDI (Runtime), RemoteControlProtocolMIDIEditor (Editor) |
| 创建时间 | 2021-04-08 |
| 年龄标签 | 👴 老古董(>5年) |
| 平台 | Win64, Mac |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/RemoteControlProtocolMIDI) | |

## 用途

RemoteControlProtocolMIDI 是 UE5 Remote Control 框架的协议扩展插件，将 MIDI 控制器的物理输入（旋钮、推子、打击垫）桥接到 Remote Control API 的属性绑定系统中。

它解决的核心问题是：在虚拟制片 (Virtual Production) 场景中，灯光师、音效师需要通过 MIDI 硬件控制器实时调整引擎参数（灯光强度、材质参数、Actor 变换等）。该插件通过 Remote Control Preset 的协议绑定机制，让 MIDI 消息自动映射到已暴露的属性上，实现硬件即控制台的工作流。

插件本身不直接暴露 BlueprintCallable 函数——它的工作方式是注册为 Remote Control 协议（协议名 `"MIDI"`），然后在 Remote Control Preset 面板中通过 UI 配置绑定。

## 使用场景

- 你在做虚拟制片，用 MIDI 推子控制 DMX 灯光参数 → 用此插件 + Remote Control Preset
- 你想用 MIDI 打击垫触发 Unreal 中的开关型属性（如开关灯） → 配置 NoteOn 事件绑定
- 你想用 MIDI 旋钮连续调节材质参数（如粗糙度 0-1） → 配置 ControlChange 事件绑定
- 你需要多个 MIDI 设备分别控制不同参数 → 支持按设备名/设备 ID 选择

## 支持的 MIDI 事件类型

| MIDI 事件 | 枚举值 | 行为 | 典型用途 |
|---|---|---|---|
| `ControlChange` | 11 | 传递 MessageData2（0-127）作为连续值 | 旋钮、推子 |
| `NoteOn` | 9 | NoteOn 时传 127，NoteOff 时传 0（自动 toggle） | 打击垫、按键 |
| `ChannelAfterTouch` | 13 | 传递 MessageData1 作为通道压力值 | 触后压力感应 |

## 蓝图用法

此插件不直接暴露 BlueprintCallable 节点。它的功能通过 Remote Control Preset 面板以 UI 方式使用：

### 配置流程（编辑器操作）

1. **启用插件**：Edit → Plugins → 搜索 "Remote Control Protocol MIDI" → 启用（需同时启用 `RemoteControl` 和 `MIDIDevice` 插件）
2. **配置默认设备**：Edit → Project Settings → Plugins → Remote Control MIDI Protocol → 设置默认 MIDI 设备
3. **创建 Remote Control Preset**：在 Content Browser 右键 → Miscellaneous → Remote Control Preset
4. **暴露属性**：在 Preset 面板中点击 "Add" 暴露目标 Actor 的属性
5. **添加 MIDI 绑定**：选中已暴露的属性 → 在 Protocol Bindings 区域选择 "MIDI" → 点击 "Awaiting" 按钮进入监听模式
6. **发送 MIDI 信号**：操作 MIDI 控制器，插件自动捕获事件类型、通道、MessageData1 并完成绑定
7. **微调绑定参数**：绑定完成后可手动调整 Channel、Identifier (MessageData1)、Type

### 设备选择模式

绑定中每个 MIDI 设备配置支持三种选择模式：

| 模式 | 说明 |
|---|---|
| Use Project Settings | 使用 Project Settings 中配置的默认设备 |
| Device Name | 按设备名匹配（大小写不敏感），适合跨机器一致性 |
| Device Id | 按设备 ID 数字匹配，适合固定硬件环境 |

## C++ 用法

此插件主要通过 Remote Control 协议框架以声明式方式工作，C++ 直接交互的场景较少。

### 头文件引入

```cpp
#include "RemoteControlProtocolMIDI.h"
#include "IRemoteControlProtocolMIDIModule.h"
#include "RemoteControlProtocolMIDISettings.h"
```

### 获取 MIDI 设备列表

通过模块接口异步获取系统中的 MIDI 输入设备：

```cpp
// 来源: Source/RemoteControlProtocolMIDI/Public/IRemoteControlProtocolMIDIModule.h
IRemoteControlProtocolMIDIModule& MIDIModule =
    FModuleManager::LoadModuleChecked<IRemoteControlProtocolMIDIModule>("RemoteControlProtocolMIDI");

// bRefresh=true 强制刷新设备列表
MIDIModule.GetMIDIDevices(/*bRefresh=*/ true).Next(
    [](TSharedPtr<TArray<FFoundMIDIDevice>, ESPMode::ThreadSafe> Devices)
    {
        for (const FFoundMIDIDevice& Device : *Devices)
        {
            UE_LOG(LogTemp, Log, TEXT("MIDI Device [%d]: %s (Input: %s)"),
                Device.DeviceID, *Device.DeviceName,
                Device.bCanReceiveFrom ? TEXT("Yes") : TEXT("No"));
        }
    });
```

### 监听设备变更

```cpp
// 来源: Source/RemoteControlProtocolMIDI/Public/IRemoteControlProtocolMIDIModule.h
MIDIModule.GetOnMIDIDevicesUpdated().AddLambda(
    [](FMIDIDeviceCollection& Devices)
    {
        UE_LOG(LogTemp, Log, TEXT("MIDI devices updated, count: %d"), Devices->Num());
    });
```

### 编程式配置协议实体

```cpp
// 来源: Source/RemoteControlProtocolMIDI/Public/RemoteControlProtocolMIDI.h
// 创建 MIDI 协议实体（用于编程式绑定）
FRemoteControlMIDIProtocolEntity MIDIBinding;
MIDIBinding.Device.DeviceId = 1;  // 使用设备 ID 1
MIDIBinding.EventType = EMIDIEventType::ControlChange;  // CC 事件
MIDIBinding.Channel = 1;          // MIDI 通道 1
MIDIBinding.MessageData1 = 74;    // CC#74（通常是滤波器截止频率）
```

## Demo 示例

此插件没有提供独立的 Demo 或测试用例。它的使用完全集成在 Remote Control Preset 的编辑器工作流中。

一个最小的自定义模块使用示例（仅查询设备）：

```cpp
// MyMIDIModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[] {
    "RemoteControlProtocolMIDI"
});
```

```cpp
// MyMIDIHelper.h
#pragma once
#include "IRemoteControlProtocolMIDIModule.h"

class FMyMIDIHelper
{
public:
    static void LogAvailableDevices()
    {
        auto& Module = FModuleManager::LoadModuleChecked<IRemoteControlProtocolMIDIModule>(
            "RemoteControlProtocolMIDI");
        Module.GetMIDIDevices(true).Next([](auto Devices) {
            for (const auto& D : *Devices)
            {
                UE_LOG(LogTemp, Display, TEXT("[%d] %s"), D.DeviceID, *D.DeviceName);
            }
        });
    }
};
```

## 模块依赖

### RemoteControlProtocolMIDI 模块 (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `MIDIDevice` | MIDI 设备输入/输出（底层硬件抽象） |
| `RemoteControl` | Remote Control 框架（Private） |
| `RemoteControlProtocol` | 协议扩展接口（Private） |
| `InputCore` | 输入核心（仅 Editor，Private） |
| `RemoteControlProtocolWidgets` | 协议 UI 组件（仅 Editor，Private） |

### RemoteControlProtocolMIDIEditor 模块 (Editor)

| 模块 | 用途 |
|---|---|
| `PropertyEditor` | 属性面板自定义（Private） |
| `Slate` / `SlateCore` | UI 框架（Private） |
| `EditorStyle` / `EditorWidgets` | 编辑器样式（Private） |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `RemoteControl` | Remote Control API 基础框架 |
| `MIDIDevice` | MIDI 设备驱动与管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `df329aa2` | Motion Design: removed beta tag from motion design plugins | 批量清理 beta 标记，非功能性改动 |
| 2024-02-23 | `15bede99` | Entire engine compiling with -DisableUnity -IncludeHeaders | 全引擎编译配置变更，非插件特定改动 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules with long paths | 模块路径长度修复，添加了 `ShortName = "RCPMidiEd"` |

### 维护评价

- **创建时间**：2021 年 4 月，约 5 年历史
- **最近实质性更新**：最近 3 次提交均为引擎级批量修改，该插件自创建以来**没有功能性更新**
- **维护状态**：**维护不活跃** — 代码结构和功能自初始提交后基本未变
- **稳定性**：作为 Runtime 模块，功能完整且稳定，无已知严重 bug
- **限制**：
  - 仅支持 Win64 和 Mac 平台
  - 仅支持 MIDI 输入（不支持 MIDI 输出）
  - 无自动化测试用例
- **是否推荐使用**：**推荐**，作为 Remote Control 框架的协议扩展，虽然不常更新，但功能成熟。适合虚拟制片场景中需要 MIDI 硬件控制的团队。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/RemoteControlProtocolMIDI)
- [官方文档]()（无）
- 测试用例：无
