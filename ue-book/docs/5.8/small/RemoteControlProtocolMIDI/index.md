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

本插件是一个**协议桥接器**，它将 MIDI 设备协议与 Unreal Engine 的 RemoteControl API 连接起来。其核心功能是允许开发者和艺术家通过标准的物理 MIDI 控制器（键盘、打击垫、推子、旋钮等）来**实时远程控制引擎中的任何属性或函数**。它解决了在虚拟制片、音乐可视化或现场演出等场景中，需要快速、直观地手动操控引擎参数而无需频繁使用编辑器或编程的问题。

## 使用场景

- **虚拟制片现场**：你正在使用虚拟制片的 LED 墙，并希望现场的灯光师能够用他们熟悉的 MIDI 推子实时调整场景中的灯光参数、材质颜色或摄像机位置。
- **音乐可视化**：你正在开发一个音乐可视化项目，希望用 MIDI 键盘的键位、力度或调制轮来实时驱动粒子系统、动画或后期处理效果。
- **快速原型与调试**：在开发交互式体验时，你想快速地用 MIDI 旋钮来测试某个变量（如移动速度、旋转角度）在不同值下的效果。
- **直播与演出**：你需要一个可靠的物理界面来在直播中或演出时控制引擎中的媒体播放器、虚拟形象表情等。

## 蓝图用法

核心功能封装在 `URemoteControlProtocolMIDI` 类中，通过 RemoteControl 的协议框架工作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect` | 连接到指定的 MIDI 设备输入源。 | `URemoteControlProtocolMIDI` |
| `Disconnect` | 断开当前的 MIDI 设备连接。 | `URemoteControlProtocolMIDI` |
| `Send Controller Value` | 向指定的 MIDI 通道和控制器编号发送一个控制值。 | `URemoteControlProtocolMIDI` |
| `Get MIDI Device List` | 获取当前系统中所有可用的 MIDI 输入设备列表。 | `URemoteControlProtocolMIDI` |
| `Is Connected` | 检查是否已连接到 MIDI 设备。 | `URemoteControlProtocolMIDI` |

### 使用示例（蓝图描述）

1.  **建立连接**：在开始游戏时，调用 `Get MIDI Device List` 节点获取设备名，然后使用 `Connect` 节点连接到你选择的 MIDI 控制器。
2.  **绑定参数**：在 Remote Control Panel 中，右键点击你想要控制的参数（例如灯光强度），选择“创建遥控”。在弹出的协议列表中选择 MIDI，然后设置对应的 MIDI 通道和 CC（控制器）编号。这会自动创建一个映射，无需额外蓝图节点。
3.  **手动发送（高级）**：如果你需要主动发送 MIDI 消息（例如模拟一个按键按下），可以调用 `Send Controller Value` 节点，指定通道、控制号和值（0-127）。

## C++ 用法

主要通过 RemoteControl 的 API 进行交互，本插件提供了协议的实现。

### 头文件引入

```cpp
#include "IRemoteControlProtocol.h"
#include "RemoteControlProtocolMIDI.h" // 如果需要直接访问模块类
```

### 基本用法

协议的使用通常是通过 RemoteControl 的“映射”界面完成的，但在 C++ 中，你可以以编程方式查询协议状态或进行底层操作。以下代码片段演示了如何检查 MIDI 协议是否已注册并可用。

```cpp
// 来源：基于 RemoteControl 框架的典型用法
#include "IRemoteControlModule.h"

// 在某个初始化函数中
if (IRemoteControlModule* RCModule = FModuleManager::GetModulePtr<IRemoteControlModule>(TEXT("RemoteControl")))
{
    // 获取已注册的协议映射
    const TMap<FName, TSharedRef<IRemoteControlProtocol>>& Protocols = RCModule->GetRegisteredProtocols();
    
    // 检查 MIDI 协议是否已注册
    const FName ProtocolName = TEXT("MIDI");
    if (Protocols.Contains(ProtocolName))
    {
        TSharedRef<IRemoteControlProtocol> MIDIProtocol = Protocols[ProtocolName];
        // 此时 MIDIProtocol 可用，但通常直接操作由 RemoteControl 面板管理。
        UE_LOG(LogTemp, Log, TEXT("MIDI Remote Control Protocol is available."));
    }
}
```

## Demo 示例

一个最小完整示例需要结合两个模块。
1.  **Runtime 模块 (`RemoteControlProtocolMIDI`)**：负责核心的 MIDI 消息处理和与 RemoteControl API 的绑定。
2.  **Editor 模块 (`RemoteControlProtocolMIDIEditor`)**：提供编辑器内操作界面，用于设置 MIDI 设备连接和将引擎属性映射到 MIDI CC 编号。

典型的使用流程是：在编辑器中，通过 Remote Control Panel（来自 RemoteControl 插件）为你的属性创建“遥控”，然后在协议下拉菜单中选择 MIDI，并配置通道和控制号。运行时，Runtime 模块负责将物理 MIDI 控制器的输入转换为对引擎属性的控制。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RemoteControl` | 核心的远程控制框架，提供属性控制和协议扩展点。 |
| `MIDIDevice` | 提供跨平台的 MIDI 设备输入/输出访问能力。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式，纯代码风格更新。 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除 Motion Design 相关插件的测试版标签，本插件状态可能随之调整。 |
| 2024-02-23 | `15bede99` | Entire engine compiling with -DisableUnity -IncludeHeaders | 引擎级编译配置调整，旨在确保所有插件在非 Unity 模式下能正确编译。 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were | 为路径过长的模块添加短名称，工程维护性修复。 |
| 2022-10-26 | `ed85af77` | Non unity/pch compile fixes | 修复在非 Unity 或预编译头模式下的编译错误。 |

### 维护评价

- **年龄**：约5年历史，属于“老古董”级别插件。
- **更新频率**：最近一次实质性更新（移除 beta 标签）在2025年9月，最近的2026年4月更新仅为日志宏迁移。更新间隔较长，且多为引擎级兼容性或编译修复。
- **维护状态**：**维护不活跃**。没有发现针对该插件本身的功能性增强或错误修复的近期提交。它主要作为 RemoteControl 和 MIDIDevice 这两个更核心插件的“胶水”层存在，功能已趋于稳定。
- **推荐使用**：如果你需要在 UE 项目中通过 MIDI 控制引擎参数，并且你的目标平台是 Win64 或 Mac，这个插件仍然是官方推荐且功能完整的解决方案。但由于其非活跃的维护状态，遇到特定边界问题时可能需要自行排查。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControlProtocolMIDI)
- [Remote Control 插件文档](https://docs.unrealengine.com/5.8/en-US/remote-control-in-unreal-engine/) （本插件所依赖的核心插件文档）
- [MIDI Device 插件文档](https://docs.unrealengine.com/5.8/en-US/MIDI-over-Bluetooth-in-Unreal-Engine/) （本插件所依赖的核心插件文档）