# Live Link Hub Unreal Device

> Live Link Hub device providing Take Recorder automation. Must be enabled in both Live Link Hub and Unreal Editor.

| 属性 | 值 |
|---|---|
| 中文名 | 虚幻编辑器设备 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++ 模块） |
| 模块 | `LiveLinkUnrealDevice` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkUnrealDevice) | |

## 用途

本插件的核心作用是充当 **Live Link Hub** 与 **运行中的 Unreal Editor 实例**之间的设备连接桥梁。它解决了在虚拟制作等工作流中，需要从中心控制端（Live Link Hub）远程协调和自动化 Unreal Editor 录制过程的问题。

具体而言，它为 Live Link Hub 添加了一个名为 “Unreal” 的设备类型。通过该设备，用户可以在 Live Link Hub 中：
1.  **远程连接**到一个运行中的 Unreal Editor 实例。
2.  **远程控制**该编辑器的 **Take Recorder**，包括开始/停止录制、设置场记板名称（Slate Name）和拍摄编号（Take Number）。
3.  **同步事件**，确保两个程序间的录制状态和元数据保持一致，并通过内置机制防止事件循环。

它基于 UE 的 **MessageBus** 进行通信，是 Live Link 设备框架 (`LiveLinkDevice`) 的一个具体实现。

## 使用场景

-   **虚拟制作片场**：你需要在 Live Link Hub（可能是现场控制室）集中管理多个设备（如摄像机跟踪、动作捕捉）的录制，同时需要自动触发或同步 Unreal Engine 渲染管线的录制。
-   **自动化测试/CI**：你希望通过脚本或外部工具触发 Unreal Editor 内的场景录制。
-   **多编辑器会话协调**：你有多个 Unreal Editor 实例运行，并希望从一个中心点（Hub）协调它们的录制状态。

## 蓝图用法

经源码分析，本插件主要通过 **设备配置** 和 **设备接口** 在后台工作，不直接向蓝图暴露专用的 `BlueprintCallable` 函数。其交互主要通过 Live Link Hub 的设备 UI 和 C++ 接口进行。

### 核心行为

| 行为 | 说明 | 控制方式 |
|---|---|---|
| 连接编辑器 | 通过 `ClientId` 连接到指定的 Unreal Editor 实例 | Live Link Hub 设备 UI |
| 开始/停止录制 | 发送命令控制远程编辑器的 Take Recorder | Live Link Hub 设备 UI / 消息总线 |
| 同步场记板信息 | 设置或接收来自编辑器的 Slate 和 Take 号 | 设备设置中的权限控制 |
| 监控连接状态 | 获取设备健康状况和连接状态 | `ULiveLinkUnrealDevice` 接口 |

## C++ 用法

此插件是一个 **Editor** 类型的插件，主要用于扩展 Live Link Hub 和 Unreal Editor 之间的通信链路。其主要用法体现在配置和作为设备框架的一部分被系统调用。

### 头文件引入

```cpp
// 引入设备基类和能力接口
#include "Devices/LiveLinkUnrealDevice.h"
```

### 基本用法

本插件的主要功能通过在 Live Link Hub 和 Unreal Editor 中**启用插件**并配置设备实例来使用，C++ 层面更多是内部实现。若要以编程方式与设备交互，需要通过 Live Link 设备框架的接口。

```cpp
// 从 Live Link Device 系统获取已创建的 Unreal 设备实例（示例逻辑）
// 假设你已有 ULiveLinkDeviceSubsystem* DeviceSubsystem;
ULiveLinkDevice* Device = DeviceSubsystem->FindDevice(/* 某种标识 */);
if (ULiveLinkUnrealDevice* UnrealDevice = Cast<ULiveLinkUnrealDevice>(Device))
{
    // 检查连接状态
    ELiveLinkDeviceConnectionStatus Status = UnrealDevice->GetConnectionStatus_Implementation();

    // 获取其特定设置
    const ULiveLinkUnrealDeviceSettings* Settings = UnrealDevice->GetSettings();
    if (Settings)
    {
        // 读取目标编辑器 ClientId 或录制权限等设置
        FLiveLinkHubClientId TargetClientId = Settings->ClientId;
        bool bRemoteEditorCanStartRecord = Settings->bHasRecordStartAuthority;
    }
}
```
*逻辑推断自 `ULiveLinkUnrealDevice` 类声明。*

### 进阶用法

插件内部通过 `ILiveLinkDeviceCapability_Recording` 接口实现录制命令的收发，并通过 `FLiveLinkHubUnrealDeviceAuxManager` 管理消息通道，避免反馈循环。作为插件使用者，通常无需直接调用这些内部类。

## Demo 示例

本插件没有独立的运行时组件，其 “Demo” 体现在**在项目中启用和配置**：

1.  **在 Unreal Editor 中启用插件**：编辑 -> 插件 -> 搜索 “Live Link Unreal Device” -> 启用。
2.  **在 Live Link Hub 中启用插件**：在 Hub 应用的插件管理中启用 “Live Link Unreal Device”。
3.  **添加设备实例**：
    -   在 Live Link Hub 中，转到 “Devices” 面板。
    -   点击 “+” 添加新设备，选择 “Unreal” 类型。
    -   在设备设置中，填入要连接的 **Unreal Editor 实例的 ClientId**（通常在编辑器状态栏或 Live Link 面板可见）。
    -   根据需要调整 “Authority” 设置，决定 Hub 和 Editor 哪一方拥有控制权。
4.  **连接与录制**：
    -   点击 “Connect”。
    -   连接成功后，在 Hub 中使用 “Start Recording” 等按钮即可控制远程编辑器的 Take Recorder。

## 模块依赖

从插件元数据推断，使用者（你的项目或插件）若要依赖 `LiveLinkUnrealDevice` 模块，需要在 `.Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `LiveLinkDevice` | 提供 `ULiveLinkDevice` 基类和设备能力接口 |
| `LiveLinkHub` | 提供与 Live Link Hub 应用程序交互的核心框架和消息类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `e2637557` | LiveLinkHub Unreal Device - fix for doubling of increment take bug when stopping recording. | 修复了停止录制时拍摄编号错误递增两次的 bug。 |
| 2026-04-14 | `f6a8065d` | Matching device name with media source name | 设备名称与媒体源名称匹配。 |
| 2026-04-13 | `6b598084` | Live Link Hub: Enable slate/take number changes to be received from Unreal Editor devices. | 启用了从 Unreal Editor 设备接收场记板/拍摄编号变更的功能。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了变更列表 CL51314860。 |

### 维护评价

该插件是一个**较新的实验性插件**，创建于 2025 年 9 月。从 2026 年 2 月至 4 月，有持续的功能增强和错误修复记录，表明其处于**活跃开发与维护**阶段。最近的更新主要集中在功能完善（如接收编辑器端状态变更）和稳定性修复上。

作为 `IsExperimentalVersion: true` 的插件，其 API 和行为未来可能发生变更。由于其解决的是特定工作流（Hub-Editor 远程录制自动化）的需求，推荐在相关项目中尝试使用，但需留意其实验性标签和后续更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkUnrealDevice)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/LiveLinkUnrealDevice) (路径推测，待确认)