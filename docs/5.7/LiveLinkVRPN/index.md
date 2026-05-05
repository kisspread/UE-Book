# LiveLinkVRPN

> Live Link plugin for the VRPN protocol

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ false |
| 包含内容 | ✅ true |
| 模块 | LiveLinkVRPN (Runtime) |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkVRPN) | |

## 用途

LiveLinkVRPN 将 [VRPN](https://vrpn.cs.unc.edu/)（Virtual-Reality Peripheral Network）协议接入 UE 的 Live Link 框架。VRPN 是学术界和虚拟现实领域广泛使用的开源网络协议，用于将各种输入设备（追踪器、模拟量传感器、按钮、旋钮）的数据通过 UDP/TCP 实时传输到客户端。

这个 plugin 解决的核心问题：**让你在 UE 的 Live Link 体系中直接使用 VRPN 兼容的硬件设备**（如 OptiTrack 追踪器、SpaceMouse、自定义 Arduino 传感器等），而无需编写自定义数据桥接代码。

数据流：`VRPN 设备 → VRPN Server → (网络) → LiveLinkVRPN plugin → Live Link → Actor/Blueprint`

### 支持的 VRPN 设备类型

| 设备类型 | 说明 | Live Link 数据格式 |
|---|---|---|
| **Analog** | 模拟量通道（如鼠标轴、摇杆） | `FLiveLinkBaseFrameData`，属性名 `Channel0`、`Channel1`… |
| **Dial** | 旋钮/编码器 | `FLiveLinkBaseFrameData`，属性名 `Dial`、`Change` |
| **Button** | 按钮/开关 | `FLiveLinkBaseFrameData`，属性名 `Button`、`State` |
| **Tracker** | 位置+旋转追踪器 | `FLiveLinkTransformFrameData`，包含完整 Transform |

> **注意**：Tracker 类型会自动将 VRPN 的米单位转换为 UE 的厘米单位（×100）。

## 使用场景

- 你在使用 OptiTrack / Vicon 等动捕系统，需要通过 VRPN 将追踪数据送入 UE → 配置 Tracker 类型
- 你有 VRPN 兼容的物理输入设备（旋钮、按钮面板），想在 UE 蓝图中读取 → 配置 Analog/Dial/Button 类型
- 你在搭建 nDisplay 多屏投影环境，需要用外部追踪器驱动相机 → 通过 Live Link 将 VRPN Tracker 数据驱动 nDisplay ViewPoint
- 你的学校/实验室已有 VRPN 基础设施，想直接接入 UE 而不写额外适配层

## 蓝图用法

本 plugin 没有暴露 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。它完全通过 **Live Link 面板** 进行配置，数据通过 Live Link 的标准 Subject/Role 系统在蓝图中消费。

### 编辑器配置步骤

1. **启用 Plugin**：Edit → Plugins → 搜索 "LiveLinkVRPN" → 启用（需要重启）
2. **打开 Live Link 面板**：Window → Live Link
3. **添加 Source**：在 Live Link 面板左上角点 "+" → 选择 "LiveLinkVRPN Source"
4. **配置连接参数**：
   - **IP Address**：VRPN Server 的 IP 地址（默认 `127.0.0.1`）
   - **Local Update Rate In Hz**：轮询频率（默认 120，范围 1-1000）
   - **Device Name**：VRPN 设备名称（如 `Mouse0`、`Tracker0@192.168.1.100`）
   - **Subject Name**：Live Link Subject 名称（如 `MouseAxes`）
   - **Type**：设备类型（Analog / Dial / Button / Tracker）
5. 点击 **Add** 按钮

### 在蓝图中消费数据

配置完成后，Live Link Subject 会出现在蓝图的 Live Link 节点中：

- **Analog**：使用 `Evaluate Live Link Frame` 节点，选择 Basic Role，读取 `PropertyValues` 数组
- **Tracker**：使用 `Evaluate Live Link Transform` 节点，直接获取 `Transform`（位置+旋转）
- **Dial / Button**：使用 `Evaluate Live Link Frame` 节点，选择 Basic Role，读取 `Dial`/`Change` 或 `Button`/`State` 属性

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkVRPNSource.h"
#include "LiveLinkVRPNConnectionSettings.h"
```

### 基本用法：编程创建 VRPN Source

```cpp
#include "LiveLinkVRPNSource.h"
#include "LiveLinkVRPNConnectionSettings.h"
#include "ILiveLinkClient.h"

// 配置连接参数
FLiveLinkVRPNConnectionSettings Settings;
Settings.IPAddress = TEXT("192.168.1.100");
Settings.DeviceName = TEXT("Tracker0");
Settings.SubjectName = TEXT("HeadTracker");
Settings.Type = EVRPNDeviceType::Tracker;
Settings.LocalUpdateRateInHz = 120;

// 创建 source（会自动连接 VRPN server 并注册回调）
TSharedPtr<FLiveLinkVRPNSource> Source = MakeShared<FLiveLinkVRPNSource>(Settings);
```

来源：`LiveLinkVRPNSource.cpp` 第 14-100 行的构造函数逻辑。

### 进阶用法：通过 SourceFactory 创建

```cpp
#include "LiveLinkVRPNSourceFactory.h"

// 也可以通过 ConnectionString 创建
ULiveLinkVRPNSourceFactory* Factory = NewObject<ULiveLinkVRPNSourceFactory>();
TSharedPtr<ILiveLinkSource> Source = Factory->CreateSource(
    TEXT("IPAddress=\"127.0.0.1\" DeviceName=\"Mouse0\" SubjectName=\"MouseAxes\" Type=Analog")
);
```

来源：`LiveLinkVRPNSourceFactory.cpp` 第 29-37 行。

## 模块依赖

从 `LiveLinkVRPN.Build.cs` 提取。如果你要在自己的模块中编程引用此 plugin，需要：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Networking` | 网络通信 |
| `Sockets` | Socket 编程 |
| `LiveLinkInterface` | Live Link 框架接口（`ILiveLinkSource`、`ILiveLinkClient`） |
| `Messaging` | UE 消息系统（`FMessageEndpoint`） |

### 第三方依赖

Plugin 自带 VRPN 库（版本 07.34），位于 `ThirdParty/VRPN/`：

| 库文件 | 说明 |
|---|---|
| `vrpn.lib` | VRPN 客户端库 |
| `quat.lib` | 四元数运算库 |

> **平台限制**：仅支持 **Win64**（x64 + arm64）。其他平台无法使用此 plugin。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-06-09 | `f8ff703c` | 添加 Windows arm64 预编译 VRPN 库，x64 库移至子目录，附带 VRPN 07.34 构建脚本 |
| 2024-10-08 | `54fa3a60` | 修复不可移植路径问题（与 ClangWarnings.cs 相关的构建修复） |
| 2023-09-15 | `b8279d86` | 修复 nDisplay 场景下 LiveLinkVRPN 的崩溃（添加临界区保护） |

### 维护评价

- **创建时间**：2021 年 4 月，约 5 年前
- **最近更新**：2025 年 6 月，最近一次更新是添加 arm64 支持，属平台适配性更新
- **更新频率**：低（约每年 1 次），均为修复/适配，无新功能开发
- **Beta 状态**：`.uplugin` 标记 `IsBetaVersion: true`、`EnabledByDefault: false`
- **平台限制**：仅 Win64

**综合评价**：这是一个功能完整的 "set and forget" 型 plugin，代码量小、功能明确。自 2021 年引入后从未有过功能扩展，但也没有被标记为 deprecated。适合 VRPN 生态的用户使用，但 Epic 对其投入的精力有限。如果你的项目深度依赖 VRPN，建议关注替代方案（如直接用 UDP/nDisplay 的原生追踪集成）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkVRPN)
- [VRPN 官方网站](https://vrpn.cs.unc.edu/)
- [UE Live Link 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/live-link-in-unreal-engine)
