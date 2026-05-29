# Live Link VRPN

> Live Link plugin for the VRPN protocol

| 属性 | 值 |
|---|---|
| 中文名 | VRPN 链路插件 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkVRPN` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkVRPN) | |

## 用途

本插件将 **VRPN**（Virtual Reality Peripheral Network）协议的数据桥接到 UE5 的 **Live Link** 系统中。

VRPN 是一个广泛使用的开源网络协议，专门用于传输虚拟现实外设数据（跟踪器、按钮、模拟轴、旋钮等）。它在科研实验室、大型 VR 设施和专业虚拟制作环境中非常常见，因为这些场景通常需要将物理硬件设备的数据通过局域网传输到渲染主机上。

本插件存在的意义是：**让你可以直接在 UE5 的 Live Link 面板中连接 VRPN 服务器，无需编写任何中间代码，就能将 VRPN 设备的实时数据用于动画、驱动或蓝图逻辑。**

支持的 VRPN 设备类型：
- **Analog** — 连续模拟值（如摇杆轴、鼠标坐标）
- **Dial** — 旋钮/编码器的增量值
- **Button** — 按钮开关状态（0/1）
- **Tracker** — 六自由度位姿数据（位置 + 旋转四元数）

## 使用场景

- 你在用 OptiTrack、Vicon 等动作捕捉系统，已经配置了 VRPN 服务器 → 用本插件直接将动捕数据引入 Live Link
- 你的实验室环境有 VRPN 基础设施（如 UNC VR 系统），需要将跟踪数据送入 UE5 → 用本插件
- 你有一个运行在另一台机器上的 VRPN 服务器，通过局域网传输 Tracker/Button/Analog 数据 → 用本插件桥接到 UE5
- 你正在做 nDisplay 多机渲染项目，需要从 VRPN 获取同步的外设数据 → 用本插件（参见 git history 中 nDisplay 相关的 crash 修复）

**注意**：本插件默认未启用且标记为 Beta，仅支持 Win64 平台。你需要在项目设置中手动启用。

## 蓝图用法

本插件主要通过 Live Link 面板进行配置，不暴露 BlueprintCallable 节点。

### Live Link 面板配置

在编辑器中通过 **Window → Live Link** 面板添加 VRPN 源：

1. 点击 **Source** 按钮，选择 **VRPN**
2. 在弹出的子面板中配置以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `IPAddress` | String | `"127.0.0.1"` | VRPN 服务器的 IP 地址 |
| `LocalUpdateRateInHz` | uint32 | `120` | 请求服务器更新的最大频率（Hz） |
| `DeviceName` | String | `"Mouse0"` | VRPN 设备名称（与 VRPN 服务器配置对应） |
| `SubjectName` | String | `"MouseAxes"` | Live Link 主题名称 |
| `Type` | EVRPNDeviceType | `Analog` | 设备类型：Analog / Dial / Button / Tracker |

3. 点击创建后，VRPN 数据将以 Live Link Subject 的形式出现在面板中

### Live Link 数据消费

数据接入后，可以通过标准的 Live Link 流程消费：
- **Animation Blueprint** 中通过 Live Link 节点获取 Tracker 的骨骼变换
- **蓝图**中通过 Live Link 节点获取 Analog/Button 的数值变化
- **nDisplay** 场景中用于同步外部追踪数据

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkVRPNConnectionSettings.h"
#include "LiveLinkVRPNSource.h"
```

### 基本用法

手动创建一个 VRPN Live Link 源（程序化方式，不经过 UI 面板）：

```cpp
#include "LiveLinkVRPNConnectionSettings.h"
#include "LiveLinkVRPNSource.h"
#include "ILiveLinkClient.h"

// 配置连接参数
FLiveLinkVRPNConnectionSettings Settings;
Settings.IPAddress = TEXT("192.168.1.100");
Settings.LocalUpdateRateInHz = 60;
Settings.DeviceName = TEXT("Tracker0");
Settings.SubjectName = TEXT("HeadTracker");
Settings.Type = EVRPNDeviceType::Tracker;

// 创建源
TSharedPtr<FLiveLinkVRPNSource> Source = MakeShared<FLiveLinkVRPNSource>(Settings);
```

### 通过 Factory 创建

使用 `ULiveLinkVRPNSourceFactory` 可以通过 Live Link 客户端接口创建源：

```cpp
#include "LiveLinkVRPNSourceFactory.h"

// 获取 Factory 实例
ULiveLinkVRPNSourceFactory* Factory = GetMutableDefault<ULiveLinkVRPNSourceFactory>();

// Factory 内部会调用 CreateSourceFromSettings
// 实际使用中推荐通过 Live Link 面板操作
```

### EVRPNDeviceType 枚举

```cpp
UENUM(BlueprintType)
enum class EVRPNDeviceType : uint8
{
    Analog,   // 模拟量（连续值，如摇杆、鼠标坐标）
    Dial,     // 旋钮（增量值）
    Button,   // 按钮（布尔值 0/1）
    Tracker,  // 跟踪器（6DOF 位姿：位置 + 四元数旋转）
};
```

## Demo 示例

以下示例展示如何在运行时程序化创建 VRPN Live Link 源，用于连接一个远程 Tracker 设备：

```cpp
// VRPNDemoComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "LiveLinkVRPNConnectionSettings.h"
#include "VRPNDemoComponent.generated.h"

class FLiveLinkVRPNSource;
class ILiveLinkClient;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UVRPNDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "VRPN")
    FString ServerIP = TEXT("127.0.0.1");

    UPROPERTY(EditAnywhere, Category = "VRPN")
    FString DeviceName = TEXT("Tracker0");

    UPROPERTY(EditAnywhere, Category = "VRPN")
    EVRPNDeviceType DeviceType = EVRPNDeviceType::Tracker;

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    TSharedPtr<FLiveLinkVRPNSource> VRPNSource;
};
```

```cpp
// VRPNDemoComponent.cpp
#include "VRPNDemoComponent.h"
#include "LiveLinkVRPNSource.h"
#include "LiveLinkVRPNConnectionSettings.h"

void UVRPNDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    // 构建连接设置
    FLiveLinkVRPNConnectionSettings Settings;
    Settings.IPAddress = ServerIP;
    Settings.LocalUpdateRateInHz = 120;
    Settings.DeviceName = DeviceName;
    Settings.SubjectName = *FString::Printf(TEXT("%s_%s"), *DeviceName, *UEnum::GetValueAsString(DeviceType));
    Settings.Type = DeviceType;

    // 创建 VRPN Live Link 源
    VRPNSource = MakeShared<FLiveLinkVRPNSource>(Settings);

    UE_LOG(LogTemp, Log, TEXT("VRPN Live Link source created: %s @ %s"), *DeviceName, *ServerIP);
}

void UVRPNDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 释放源，自动断开 VRPN 连接
    VRPNSource.Reset();

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

本插件的 Build.cs 依赖（基于源码分析推断）：

| 模块 | 用途 |
|---|---|
| `LiveLink` | UE5 Live Link 核心框架，提供 ILiveLinkSource、ILiveLinkClient 等接口 |
| `LiveLinkInterface` | Live Link 接口定义 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

**插件依赖**：
- **UdpMessaging** — 网络消息传输（已在 .uplugin 中声明）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复不可达代码编译警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，统一日志格式 |
| 2025-06-09 | `f8ff703c` | Add Windows Arm64 libraries for vrpn | 为 VRPN 添加 Windows Arm64 库支持 |
| 2024-10-08 | `54fa3a60` | Fix nonportable paths for UnrealEditor | 修复编辑器中不可移植的路径问题 |
| 2023-09-15 | `b8279d86` | nDisplay: added critsection to fix LiveLinkVRPN crash | 为 nDisplay 场景添加临界区，修复 VRPN 源的崩溃问题 |

### 维护评价

- **状态**：Beta，维护不活跃
- **最后实质性功能更新**：从未有过功能性增强，所有 commit 都是编译修复、平台适配和崩溃修复
- **平台限制**：仅 Win64
- **风险**：插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明 Epic 将其视为实验性质的功能
- **nDisplay 兼容性**：2023 年修复了 nDisplay 场景中的线程安全崩溃，说明在多视口场景中使用需要额外注意

**总结**：本插件功能稳定但处于 Beta 状态，适合有 VRPN 设备集成需求的专业虚拟制作管线使用。如果你的场景不需要对接 VRPN 协议设备，无需使用本插件。对于新项目，建议评估是否有更现代的替代方案（如直接使用 Live Link 的其他源插件）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkVRPN)
- [VRPN 官网](https://vrpn.org/)
- [VRPN 文档](https://www.cs.unc.edu/Research/vrpn/)