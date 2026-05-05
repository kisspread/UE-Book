# LiveLinkPrestonMDR

> Live Link support for the Preston MDR-3 Motor Driver

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | false (IsBetaVersion=true, Installed=false) |
| 包含内容 | true |
| 模块 | LiveLinkPrestonMDR (Runtime), LiveLinkPrestonMDREditor (Editor) |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR) | |

## 用途

Preston MDR-3 (Motor Driver Remote) 是电影摄影行业广泛使用的镜头马达驱动系统，用于控制镜头的 Focus（对焦）、Iris（光圈）、Zoom（变焦）三个轴。该 plugin 通过 TCP/IP 网络连接到 Preston MDR-3 硬件设备，实时读取 FIZ (Focus-Iris-Zoom) 数据，并通过 UE5 的 Live Link 框架将这些镜头参数传递到引擎内。

核心价值：在虚拟制片 (Virtual Production) 场景中，将真实摄影机镜头的物理操作（跟焦、变焦、光圈调节）实时同步到 Unreal Engine 中的虚拟摄影机，实现真实镜头控制与虚拟画面的精确联动。

## 使用场景

- **虚拟制片 (Virtual Production)**：摄影师在片场操作真实镜头，引擎内虚拟摄影机实时跟随镜头参数变化
- **LED Volume 拍摄**：在 LED 墙场景中，真实镜头的焦距变化需要驱动虚拟背景的透视变化
- **镜头数据录制**：通过 Live Link 录制每帧的 FIZ 数据，用于后期合成（如深度通道的焦距信息）
- **镜头校准与测试**：使用 MDR 的编码器数据验证镜头行程和校准状态

## 蓝图用法

### 核心数据结构

| 结构体 | 说明 | 所在类 |
|---|---|---|
| `FLiveLinkPrestonMDRStaticData` | 静态数据：镜头能力（是否支持变焦/光圈/对焦马达） | 继承自 `FLiveLinkCameraStaticData` |
| `FLiveLinkPrestonMDRFrameData` | 逐帧数据：FocusDistance、Aperture、FocalLength + 原始编码器值 | 继承自 `FLiveLinkCameraFrameData` |
| `FLiveLinkPrestonMDRBlueprintData` | 蓝图数据封装：组合 StaticData + FrameData | 继承自 `FLiveLinkBaseBlueprintData` |

### 帧数据字段

`FLiveLinkPrestonMDRFrameData` 在标准 Camera 帧数据基础上增加了三个原始编码器值：

| 字段 | 类型 | 说明 |
|---|---|---|
| `RawFocusEncoderValue` | `uint16` | 对焦马达原始编码器值 (0–65535) |
| `RawIrisEncoderValue` | `uint16` | 光圈马达原始编码器值 (0–65535) |
| `RawZoomEncoderValue` | `uint16` | 变焦马达原始编码器值 (0–65535) |

### Source 设置面板

在编辑器中通过 Live Link 面板添加 "PrestonMDR" Source 后，可配置以下参数：

**连接设置** (`FLiveLinkPrestonMDRConnectionSettings`)：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `IPAddress` | `FString` | `"0.0.0.0"` | MDR 设备的 IP 地址 |
| `PortNumber` | `uint16` | `0` | TCP 端口号 |
| `SubjectName` | `FName` | `"Preston MDR"` | Live Link Subject 名称 |

**Source 设置** (`ULiveLinkPrestonMDRSourceSettings`)：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `IncomingDataMode` | `EFIZDataMode` | `EncoderData` | 数据模式：原始编码器值 或 校准后的实际物理值 |
| `FocusEncoderRange` | `FEncoderRange` | Min=0, Max=65535 | 对焦编码器映射范围 |
| `IrisEncoderRange` | `FEncoderRange` | Min=0, Max=65535 | 光圈编码器映射范围 |
| `ZoomEncoderRange` | `FEncoderRange` | Min=0, Max=65535 | 变焦编码器映射范围 |

### 蓝图中的使用

在蓝图中，通过 **Live Link** 节点（如 `Get Live Link Subject Data`）获取 Preston MDR Subject 的数据，数据类型为 `FLiveLinkPrestonMDRBlueprintData`。从中读取 `FrameData.FocusDistance`、`FrameData.Aperture`、`FrameData.FocalLength` 等字段，即可驱动虚拟摄影机或其他 Actor 的属性。

### 使用示例（蓝图描述）

1. 在 Live Link 面板中添加 "PrestonMDR" Source，填入 MDR 设备的 IP 和端口
2. 蓝图中添加 `Get Live Link Subject Data` 节点，Subject Name 设为 `"Preston MDR"`
3. 拆分 Blueprint Data 中的 FrameData，将 FocusDistance 连接到 CineCamera Actor 的 CurrentFocalLength
4. 将 Aperture 连接到 CineCamera 的 CurrentAperture

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkPrestonMDRTypes.h"
#include "LiveLinkPrestonMDRRole.h"
#include "LiveLinkPrestonMDRConnectionSettings.h"
#include "LiveLinkPrestonMDRSourceSettings.h"
```

### 数据类型

```cpp
// 继承自 FLiveLinkCameraFrameData，额外包含原始编码器值
FLiveLinkPrestonMDRFrameData FrameData;
FrameData.FocusDistance = ...;        // 校准后的对焦距离 (0-1 或实际值)
FrameData.Aperture = ...;            // 校准后的光圈值
FrameData.FocalLength = ...;         // 校准后的焦距值
FrameData.RawFocusEncoderValue = ...; // 原始 16-bit 编码器值
FrameData.RawIrisEncoderValue = ...;
FrameData.RawZoomEncoderValue = ...;
```

### 数据模式说明

MDR 设备支持两种数据发送模式：

- **EncoderData（默认）**：发送原始编码器位置 (uint16)。需要在 Source Settings 中配置编码器范围 (Min/Max)，插件会将其映射到 0–1 的归一化值。
- **CalibratedData**：发送校准后的实际物理值（如真实焦距 mm、T-stop 等）。此时编码器范围设置无效，原始编码器值字段为 0。

### 连接状态

Source 经历以下状态：

```
NotConnected → WaitingToConnect → ConnectedActive
                                     ↕ (空闲超时)
                                  ConnectedIdle
                                    
ConnectionLost → NotConnected → (自动重连)
ConnectionFailed
```

连接超时 5 秒，数据接收超时 2 秒后触发软重置，再次超时触发硬重置。

## Demo 示例

```cpp
// 通过 LiveLink 预设或 connection string 创建 source
// 通常不需要手动创建，通过编辑器 UI 添加即可

// 如果需要通过代码创建 source
#include "LiveLinkPrestonMDRFactory.h"

FLiveLinkPrestonMDRConnectionSettings Settings;
Settings.IPAddress = TEXT("192.168.1.100");
Settings.PortNumber = 65535;
Settings.SubjectName = FName(TEXT("Preston MDR"));

FString ConnectionString = ULiveLinkPrestonMDRSourceFactory::CreateConnectionString(Settings);
// 使用 LiveLink 的 API 创建 source（通过 preset 或面板操作更常见）
```

### Build.cs 依赖

```csharp
// Runtime 模块（如果需要直接引用类型）
PublicDependencyModuleNames.AddRange(new string[] {
    "LiveLinkInterface"
});

PrivateDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "LiveLinkPrestonMDR"  // 如果在 Editor 模块中使用
});
```

## 模块依赖

### LiveLinkPrestonMDR (Runtime)

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 框架接口 (Public) |
| `Core` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `Json` | JSON 序列化 |
| `Networking` | 网络通信 |
| `Sockets` | TCP Socket 操作 |

### LiveLinkPrestonMDREditor (Editor)

| 模块 | 用途 |
|---|---|
| `LiveLinkPrestonMDR` | Runtime 模块（Source 和数据类型） |
| `PropertyEditor` | Details 面板中的属性编辑器 |
| `Slate` / `SlateCore` | 创建 Source 连接面板 UI |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-01-25 | `57ca7547` | Fixed up more bool-taking calls to take EAllowShrinking instead | API 适配：`TArray::RemoveAt` 等函数的参数从 `bool` 改为 `EAllowShrinking` 枚举，属于引擎 API 迁移 |
| 2023-11-20 | `763a6119` | Fix C4072 warnings #rnx | 编译警告修复：C4072 是 MSVC 的非标准调用约定警告 |
| 2023-01-16 | `bbc37aa2` | Another batch iwyu updates to reduce number of includes | IWYU（Include What You Use）清理，减少不必要的头文件包含 |

### 维护评价

- **年龄**：约 5.2 年（创建于 2021-03-05）
- **Beta 状态**：`IsBetaVersion=true`，从未正式转为正式版
- **最近更新频率**：最近一次实质性更新在 2024 年初，且仅为 API 适配而非功能更新
- **最后的功能性更新**：从 git 历史看，近年的提交全部是编译修复和 IWYU 清理，没有新功能
- **维护状态**：⚠️ **维护不活跃** — 自创建以来一直是 Beta 状态，过去 2 年无实质性功能更新
- **已知限制**：
  - 仅支持 Preston MDR-3 设备，不兼容 MDR-4 或其他品牌
  - 需要 MDR 设备在网络上可访问（TCP 连接）
  - 编码器范围映射需要手动校准
- **推荐**：如果您的虚拟制片工作流中使用 Preston MDR-3 镜头马达系统，此 plugin 可以使用但需注意其 Beta 状态。对于其他镜头马达系统（如 Tilta Nucleus、Arri Hi-5），需要使用不同的 Live Link Source。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR)
- [Preston MDR-3 官方手册](https://www.prestonscinema.com/)（设备端协议参考）
- [测试用例]：本 plugin 无独立测试用例
