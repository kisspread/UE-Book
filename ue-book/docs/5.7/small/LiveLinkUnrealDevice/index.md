# Live Link Hub Unreal Device

> Live Link Hub device providing Take Recorder automation. Must be enabled in both Live Link Hub and Unreal Editor.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | LiveLinkUnrealDevice (Editor) |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkUnrealDevice) | |

## 用途

这个 plugin 是 **Live Link Hub** 与 **Unreal Editor** 之间的一个"设备"（Device）插件。它的核心功能是让 Live Link Hub 能够远程控制 Unreal Editor 的 **Take Recorder**（拍摄录制器），实现跨应用的录制自动化。

具体来说，它做了两件事：
1. **在 Live Link Hub 端**（`ULiveLinkUnrealDevice`）：作为设备连接到 Unreal Editor，通过 Message Bus 发送/接收 Take Recorder 命令（开始录制、停止录制、设置 Slate 名称和 Take 编号）
2. **在 Unreal Editor 端**（`FLiveLinkHubUnrealDeviceAuxManager`）：注册辅助消息通道，接收来自 Live Link Hub 的 Take Recorder 命令并执行，同时将本地录制事件广播给所有连接的设备

通信基于 UE 的 **Message Bus** 消息系统，通过 `FMessageEndpoint` 实现异步、可靠的消息传递。

## 使用场景

- 你在使用 **Live Link Hub** 统一管理多个动画数据源，同时需要远程控制 Unreal Editor 的 Take Recorder → 启用此插件
- 你需要在 Live Link Hub 中一键启动/停止 Unreal Editor 端的录制，而不需要手动切换窗口 → 此插件提供自动化支持
- 你希望 Live Link Hub 和 Unreal Editor 的录制状态保持同步（双向同步）→ 通过 `bHasRecordStartAuthority` / `bHasRecordStopAuthority` 控制

## 蓝图用法

此插件没有暴露 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有功能通过 Live Link Hub 的设备管理 UI 和内部 Message Bus 通信实现，不直接面向蓝图用户。

### 设备设置（编辑器属性）

在 Live Link Hub 的设备面板中，你可以配置以下属性：

| 属性 | 说明 | 类型 |
|---|---|---|
| `DisplayName` | 设备显示名称，默认 "Unreal Editor" | `FString` |
| `ClientId` | 要连接的 Unreal Editor 客户端 ID | `FLiveLinkHubClientId` |
| `bHasRecordStartAuthority` | 远程开始录制时，是否也触发本地录制 | `bool`（默认 true） |
| `bHasRecordStopAuthority` | 远程停止录制时，是否也触发本地停止 | `bool`（默认 true） |

## C++ 用法

### 头文件引入

```cpp
#include "Devices/LiveLinkUnrealDevice.h"
#include "LiveLinkUnrealDeviceMessages.h"
#include "LiveLinkHubUnrealDeviceAux.h"
```

### 基本用法

此插件的设计是自包含的——模块加载时自动注册辅助通道处理器，设备实例通过 Live Link Hub 的设备系统管理。通常不需要直接调用 C++ API。

如果你需要理解或扩展消息协议，核心消息类型定义在 `LiveLinkUnrealDeviceMessages.h`：

```cpp
// 命令消息（Hub → Editor）
FLiveLinkTakeRecorderCmd_SetSlateName     // 设置 Slate 名称
FLiveLinkTakeRecorderCmd_SetTakeNumber    // 设置 Take 编号
FLiveLinkTakeRecorderCmd_StartRecording   // 开始录制（携带 SlateInfo）
FLiveLinkTakeRecorderCmd_StopRecording    // 停止录制

// 事件消息（Editor → Hub）
FLiveLinkTakeRecorderEvent_RecordingStarting  // 录制即将开始（带倒计时）
FLiveLinkTakeRecorderEvent_RecordingStarted   // 录制已开始（带起始 Timecode）
FLiveLinkTakeRecorderEvent_RecordingStopped   // 录制已停止（带结束 Timecode + 是否取消）
```

### 进阶用法

连接流程（源码 `LiveLinkUnrealDevice.cpp`）：

```
1. ULiveLinkUnrealDevice::OnDeviceAdded()
   → 注册 Take Recorder 事件监听
   → 调用 Connect()

2. Connect()
   → 通过 FMessageEndpointBuilder 创建消息端点
   → 向目标 ClientId 发送 FLiveLinkUnrealDeviceAuxChannelRequestMessage
   → 状态变为 Connecting

3. Editor 端 FLiveLinkHubUnrealDeviceAuxManager 收到请求
   → 注册 Channel ↔ Address 映射
   → 回复 FLiveLinkHubAuxChannelAcceptMessage

4. Hub 端收到 Accept → 状态变为 Connected
```

录制同步流程：

```
Hub 发起录制:
  Hub::StartRecording_Implementation()
    → 发送 FLiveLinkTakeRecorderCmd_StartRecording
    → Editor 端 HandleStartRecording() → TakeRecorderSubsystem::StartRecording()
    → Editor 端 OnRecordingStarted() → 广播 FLiveLinkTakeRecorderEvent_RecordingStarted
    → Hub 端收到事件 → bIsRecording = true → 如果有 authority 则本地也开始录制
```

## Demo 示例

此插件无需编写代码即可使用。配置步骤：

1. 在 Unreal Editor 中启用插件：Edit → Plugins → 搜索 "Live Link Unreal Device" → 启用
2. 在 Live Link Hub 中同样启用此插件
3. 在 Live Link Hub 设备面板中添加 "Unreal" 设备
4. 设置 `ClientId` 为你的 Unreal Editor 实例
5. 连接后，Hub 和 Editor 的 Take Recorder 操作会自动同步

如需自定义消息协议，在你的模块 `Build.cs` 中添加依赖：

```csharp
PrivateDependencyModuleNames.AddRange(new string[] {
    "LiveLinkHubMessaging",
    "Messaging",
});
```

## 模块依赖

此插件的所有依赖均为 `PrivateDependencyModuleNames`（不暴露公共 API）：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和工具 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统 |
| `LiveLink` | Live Link 基础框架 |
| `LiveLinkDevice` | Live Link 设备基类和能力接口 |
| `LiveLinkHub` | Live Link Hub 客户端模型 |
| `LiveLinkHubMessaging` | Live Link Hub 消息通道管理 |
| `LiveLinkSequencer` | Live Link 序列器集成 |
| `Messaging` | UE Message Bus 消息系统 |
| `Networking` | 网络通信 |
| `Projects` | 项目和插件信息 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心 |
| `TakeRecorder` | Take Recorder 子系统 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2026-04-23 | `8793759847e5` | LiveLinkHub Unreal Device - fix for doubling of increment take bug when stopping recording | 修复停止录制时 Take 编号重复递增的 bug |
| 2026-04-14 | `f6a8065da707` | Matching device name with media source name | 设备名称与媒体源名称匹配 |
| 2026-04-13 | `6b5980847b91` | Enable slate/take number changes to be received from Unreal Editor devices | 支持从 Unreal Editor 设备接收 Slate/Take 编号变更 |

### 维护评价

- **创建时间**：2025-09-03（约 7 个月前，最初名为 "LiveLinkStandardDevices"，9 天后重命名）
- **实验性插件**：`IsExperimentalVersion: true`，`EnabledByDefault: false`
- **维护状态**：**活跃维护** — 最近一个月有多次功能更新和 bug 修复
- **代码规模**：7 个源文件（5 .cpp + 2 .h），代码精简、结构清晰
- **已知限制**：作为实验性功能，API 可能变动；测试用例目前为空壳（仅验证对象创建）
- **推荐使用**：如果你在使用 Live Link Hub 并需要远程控制 Take Recorder，此插件是官方推荐方案。注意它是实验性的，生产环境需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLinkUnrealDevice)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/LiveLinkUnrealDevice/Source/LiveLinkUnrealDevice/Private/Tests/LiveLinkUnrealDeviceTests.cpp)
