# Live Link Hub OBS Device

> Live Link Hub device for controlling OBS Studio recording and ingesting recorded video as mono takes via the OBS WebSocket v5 protocol.

| 属性 | 值 |
|---|---|
| 中文名 | OBS 直播设备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOBSDevice` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkOBSDevice) | |

## 用途

本插件将 **OBS Studio** 作为虚拟制片工作流中的录制设备集成到 **Live Link Hub** 中。它通过 OBS WebSocket v5 协议与运行中的 OBS 实例建立 WebSocket 连接，从而实现：

1. **远程控制录制**：在 Live Link Hub 发起录制会话时，自动启动/停止 OBS 的录制功能
2. **智能文件命名**：根据 Live Link Hub 的 Slate 名称、Take 编号等会话信息，通过 NamingTokens 模板动态生成 OBS 录制文件名
3. **素材摄入（Ingest）**：将 OBS 录制完成的视频文件作为单目（mono）Take 导入 Capture Manager，纳入资产管线管理

简单来说，它解决了"如何将 OBS 录制无缝嵌入虚拟制片的 Capture Manager 流程"的问题，让视频录制与动作捕捉数据保持同步管理。

## 使用场景

- 你在使用 Live Link Hub 管理虚拟制片的多设备录制 → 需要将 OBS 作为视频录制设备同步控制
- 你需要将 OBS 录制的参考视频自动纳入 Capture Manager 的 Take 管理体系 → 使用本插件自动摄入
- 你的工作流要求录制文件名包含 Slate、Take 等制片元数据 → 通过 FilenameFormat 模板实现

## 蓝图用法

本插件主要作为 Live Link Hub 的设备运行，蓝图暴露的 API 集中在设备设置和状态查询上。

### 核心设置（ULiveLinkOBSDeviceSettings）

所有设置通过编辑器 Detail 面板配置：

| 属性 | 类型 | 说明 | 默认值 |
|---|---|---|---|
| `Host` | `FString` | OBS WebSocket 服务器地址 | `127.0.0.1` |
| `Port` | `int32` | OBS WebSocket 端口（OBS 设置中的端口） | `4455` |
| `Password` | `FString` | OBS WebSocket 认证密码（留空则无密码） | 空 |
| `FilenameFormat` | `FString` | 录制文件名命名模板，支持 NamingTokens 语法 | `{session}/{slate}_tk{take}` |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect_Implementation` | 连接到 OBS WebSocket 服务器 | `ULiveLinkOBSDevice` |
| `Disconnect_Implementation` | 断开 OBS WebSocket 连接 | `ULiveLinkOBSDevice` |
| `StartRecording_Implementation` | 开始 OBS 录制 | `ULiveLinkOBSDevice` |
| `StopRecording_Implementation` | 停止 OBS 录制 | `ULiveLinkOBSDevice` |
| `IsRecording_Implementation` | 查询 OBS 当前是否正在录制 | `ULiveLinkOBSDevice` |
| `GetDeviceHealth` | 获取设备健康状态 | `ULiveLinkOBSDevice` |
| `GetSettings` | 获取设备设置对象 | `ULiveLinkOBSDevice` |

### FilenameFormat 命名模板

FilenameFormat 使用 **NamingTokens** 语法，支持以下 token：

| Token 命名空间 | Token 名 | 说明 |
|---|---|---|
| `llh` | `{slate}` | Live Link Hub Slate 名称 |
| `llh` | `{take}` | Take 编号 |
| `llh` | `{session}` | 会话名称 |
| `llh` | `{config}` | 配置名称 |
| 全局 | `{project}` | 项目名称 |
| 全局 | `{user}` | 用户名 |
| 全局 | `{yyyy}` | 年份 |
| 全局 | `{mm}` | 月份 |
| 全局 | `{Ddd}` | 星期 |

此模板同时用于**反向解析**已录制文件，从中提取 Slate/Take 信息。

### 使用示例

设备连接与录制的典型流程（通过 Live Link Hub UI 操作）：

1. 在 Live Link Hub 中添加 OBS Studio 设备
2. 配置 Host/Port/Password 连接到 OBS
3. 配置 FilenameFormat（如 `{session}/{slate}_tk{take}`）
4. 发起 Live Link Hub 录制会话 → 设备自动启动 OBS 录制并设置文件名
5. 录制结束后 → OBS 视频文件自动作为 Take 出现在 Capture Manager 中
6. 在 Capture Manager 中选择 Take 进行 Ingest

## C++ 用法

### 头文件引入

```cpp
#include "Devices/LiveLinkOBSDevice.h"
```

### 基本用法 — 获取设备并查询状态

```cpp
// 获取 Live Link Hub 中的 OBS 设备实例
// 设备通过 Live Link Hub 设备管理器自动创建，通常不需要手动实例化
ULiveLinkOBSDevice* OBSDevice = /* 从设备管理器获取 */;

// 查询连接状态
ELiveLinkDeviceConnectionStatus Status = OBSDevice->GetConnectionStatus_Implementation();

// 查询健康状态
EDeviceHealth Health = OBSDevice->GetDeviceHealth();
FText HealthText = OBSDevice->GetHealthText();

// 查询录制状态
bool bRecording = OBSDevice->IsRecording_Implementation();
```

### 进阶用法 — 自定义设备设置

```cpp
// 获取设置对象并修改
ULiveLinkOBSDeviceSettings* Settings = OBSDevice->GetSettings();
Settings->Host = TEXT("192.168.1.100");
Settings->Port = 4455;
Settings->Password = TEXT("my_password");
Settings->FilenameFormat = TEXT("{session}/{slate}_tk{take}_{yyyy}{mm}");
```

### 进阶用法 — OBS WebSocket v5 协议交互

插件内部实现了完整的 OBS WebSocket v5 协议栈，包括：

```cpp
// 认证流程（内部自动处理）
// 1. OBS 发送 Hello (op 0)：包含版本信息和认证 challenge/salt
// 2. 客户端发送 Identify (op 1)：计算并发送 auth response
// 3. OBS 发送 Identified (op 2)：认证成功

// 向 OBS 发送请求
FString RequestId = OBSDevice->SendRequest(
    TEXT("GetRecordDirectory"),
    nullptr,
    [](const TSharedRef<FJsonObject>& ResponseData, bool bSuccess)
    {
        if (bSuccess)
        {
            FString RecordDirectory;
            ResponseData->TryGetStringField(TEXT("recordDirectory"), RecordDirectory);
        }
    }
);
```

## Demo 示例

一个最小的自定义 OBS 设备设置类：

```cpp
// MyOBSDeviceConfig.h
#pragma once

#include "Devices/LiveLinkOBSDevice.h"
#include "MyOBSDeviceConfig.generated.h"

// 自定义设置覆盖示例：修改默认文件名格式
UCLASS()
class UMyOBSDeviceSettings : public ULiveLinkOBSDeviceSettings
{
    GENERATED_BODY()

public:
    UMyOBSDeviceSettings()
    {
        // 自定义默认值
        Host = TEXT("192.168.1.50");
        FilenameFormat = TEXT("{project}/{session}/{slate}_take{take}");
    }
};
```

```cpp
// MyOBSDeviceConfig.cpp
#include "MyOBSDeviceConfig.h"
```

## 模块依赖

从 .uplugin 的 Plugins 依赖和代码推断，使用本插件需要以下独特依赖：

| 模块 | 用途 |
|---|---|
| `LiveLinkDevice` | Live Link 设备基类和接口（连接/录制能力接口） |
| `LiveLinkHub` | Live Link Hub 核心功能（会话管理、Slate/Take 机制） |
| `CaptureManagerApp` | Capture Manager 应用程序集成 |
| `CaptureManagerDevices` | Capture Manager 设备层（Ingest 能力基类 `UBaseIngestLiveLinkDevice`） |
| `WebSockets` | WebSocket 客户端实现（`IWebSocket` 接口） |
| `Json` | OBS WebSocket v5 协议的 JSON 解析 |
| `NamingTokens` | 文件名模板的命名 Token 解析 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `62dc6acc` | [Live Link Hub OBS device] Update to use {session}/{slate}_tk{take} notation on generated filenames | 更新默认文件名格式为 `{session}/{slate}_tk{take}` 语法 |
| 2026-04-22 | `0644cc28` | Unshelved from pending changelist '52696293' | 从待提交变更列表中恢复搁置的代码 |
| 2026-04-14 | `f6a8065d` | Matching device name with media source name | 使设备名称与媒体源名称保持一致 |
| 2026-04-14 | `214f687b` | Added Live Link OBS Studio Device | 初始提交，添加 OBS Studio 设备插件 |

### 维护评价

本插件创建于 2026 年 4 月，是一个**非常新的实验性插件**。从创建至今约一个月内有 4 次提交，频率适中，主要集中在初始功能实现和命名格式调整。

**需要注意的风险**：
- **实验性标记**：`IsExperimentalVersion=true`，且 `Installed=false`（默认未启用），说明 Epic 尚未将其视为稳定功能
- **API 可能变化**：作为实验性功能，设备接口和设置项可能在后续版本中发生变化
- **依赖链较深**：依赖 LiveLinkHub + CaptureManager 一整套虚拟制片管线

**建议**：适合在虚拟制片项目中试用，但不建议在生产环境的关键路径上依赖此插件。密切关注后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkOBSDevice)