# ICVFX

> Conveniently collects plugins for In-Camera VFX

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | false (Installed=false) |
| 包含内容 | false |
| 模块 | 无（纯聚合 plugin） |
| 创建时间 | 2021-04-29 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ICVFX) | |

## 用途

ICVFX（In-Camera VFX）本身**不包含任何源代码或资产**，它是一个纯粹的 **plugin 聚合器**。它的作用是一键启用影视虚拟制作（Virtual Production）所需的所有相关 plugin，避免用户逐个手动开启。

这在 LED Volume 拍摄场景中尤其重要——一个典型的 ICVFX 摄影棚工作流涉及实时渲染、摄像机追踪、色彩管理、媒体 I/O、多机同步等多个子系统，每个子系统对应一个或多个 plugin。ICVFX 将它们打包在一起，通过 `IsBetaVersion: true` 和 `Installed: false` 标记为可选的 Beta 功能集合。

## 使用场景

- 你正在搭建一个 **LED Volume 虚拟摄影棚**（如 nDisplay + LED 墙），需要一次启用所有相关 plugin → 启用 ICVFX
- 你在做 **影视级别 In-Camera VFX** 项目，需要 Live Link、摄像机校准、色彩管理、媒体采集等功能 → 启用 ICVFX
- 你需要使用 **Takes Recorder** 进行拍摄记录和回放 → ICVFX 会拉取 Takes 和 MultiUserTakes
- 你想用 **Switchboard** 管理多台渲染节点 → ICVFX 包含 Switchboard

如果你只需要其中部分功能（比如只需要 Composure 做合成），不必启用 ICVFX，直接启用对应 plugin 即可。

## 蓝图用法

ICVFX 本身没有模块，因此**没有蓝图节点**。它的价值体现在它拉取的子 plugin 提供的功能。启用 ICVFX 后，以下子 plugin 的蓝图功能自动可用：

### 子 plugin 功能一览

| 子 plugin | 功能 |
|---|---|
| **nDisplay** | 多屏幕/LED 墙渲染，ICVFX 的核心 |
| **Composure** | 实时合成框架，图层混合 |
| **CameraCalibration** | 摄像机参数校准（焦距、畸变等） |
| **LiveLink / LiveLinkCamera / LiveLinkLens / LiveLinkOverNDisplay** | 实时数据流传输（摄像机追踪、镜头数据） |
| **ColorCorrectRegions** | 区域色彩校正 |
| **OpenColorIO** | 色彩空间管理（ACES 等） |
| **Takes / MultiUserTakes** | 拍摄记录、回放、多用户协作 |
| **LevelSnapshots** | 关卡快照，快速回退 |
| **Switchboard** | 多节点管理与启动 |
| **MultiUserClient** | 多用户编辑协作 |
| **RemoteControl / RemoteControlWebInterface** | 远程控制与 Web 界面 |
| **AjaMedia / BlackmagicMedia / RivermaxMedia** | 专业视频 I/O 硬件支持 |
| **MediaFrameworkUtilities** | 媒体框架工具 |
| **GPULightmass** | GPU 光照烘焙 |
| **OSC** | OSC 协议通信 |
| **TimedDataMonitor** | 时间数据监控 |
| **SequencerScripting** | Sequencer 脚本化 |
| **ConsoleVariables** | 控制台变量管理 |
| **VirtualProductionUtilities** | 虚拟制作工具集 |
| **EpicStageApp** | Epic Stage App 移动端控制 |
| **StageMonitoring** | 舞台状态监控 |
| **ICVFXTesting** | ICVFX 自动化测试工具 |

## C++ 用法

ICVFX 没有自身模块，不需要在 C++ 中引用。它是纯粹的 plugin 依赖聚合器。

如果你需要在 C++ 中使用 ICVFX 拉取的子 plugin 功能，直接引用对应模块：

```cpp
// 例如使用 nDisplay
#include "IDisplayCluster.h"

// 例如使用 Composure
#include "ICompositingModule.h"

// 例如使用 CameraCalibration
#include "CameraCalibrationSubsystem.h"
```

## Demo 示例

不适用。ICVFX 没有自身代码或资产，它只是声明了一组 plugin 依赖。启用后，所有子 plugin 的功能即可使用。

一个典型的虚拟摄影棚项目设置：
1. 启用 ICVFX plugin
2. 在项目设置中配置 nDisplay cluster（LED 墙拓扑）
3. 配置 CameraCalibration（摄像机标定数据）
4. 配置 OpenColorIO（色彩空间管线）
5. 设置 Live Link 数据源（追踪系统）
6. 使用 Switchboard 启动集群

## 模块依赖

无。ICVFX 不包含模块。它通过 `.uplugin` 的 `Plugins` 数组声明对以下 29 个 plugin 的依赖：

| 分类 | Plugin |
|---|---|
| 核心渲染 | nDisplay, GPULightmass |
| 合成 | Composure |
| 摄像机 | CameraCalibration, LiveLink, LiveLinkCamera, LiveLinkLens, LiveLinkOverNDisplay |
| 色彩 | ColorCorrectRegions, OpenColorIO |
| 媒体 I/O | AjaMedia (Win64), BlackmagicMedia (Win64/Linux), RivermaxMedia (Win64), MediaFrameworkUtilities |
| 拍摄记录 | Takes, MultiUserTakes |
| 多用户 | MultiUserClient |
| 远程控制 | RemoteControl, RemoteControlWebInterface, Switchboard, EpicStageApp, OSC |
| 监控工具 | StageMonitoring, TimedDataMonitor |
| 编辑器 | LevelSnapshots, SequencerScripting, ConsoleVariables, VirtualProductionUtilities |
| 测试 | ICVFXTesting |

**平台限制**：部分 plugin 限定 Win64 或 Win64+Linux（如 AjaMedia 仅 Win64，nDisplay 和 BlackmagicMedia 支持 Win64+Linux）。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-06-09 | `3311e62` | Updating supported platforms, now matching QAVirtualProduction | 更新平台支持列表，与 QA 虚拟制作测试配置保持一致 |
| 2023-01-31 | `b58de93` | Create ICVFXTesting plugin with the intention of porting SaloonPerf to use it | 新增 ICVFXTesting 子 plugin，用于自动化性能测试 |
| 2022-10-21 | `610c467` | Update vendor links for built-in plugins to use secure protocol | URL 安全协议更新（http→https），无功能变更 |

### 维护评价

- **年龄**：创建于 2021 年 4 月，已超过 5 年
- **最近更新**：最后一次实质更新在 2023 年 6 月，距今近 3 年
- **更新频率**：自 2022 年以来仅有 2 次更新，且都非功能性改动（平台列表调整、URL 更新）
- **状态**：`IsBetaVersion: true` + `Installed: false`，仍标记为实验性 Beta
- **评估**：⚠️ **维护不活跃**。作为聚合 plugin，其价值在于声明依赖关系，本身不需要频繁更新。但如果 ICVFX 生态有新增重要 plugin（如新的媒体格式支持），此聚合 plugin 可能未及时跟进。使用前建议确认各子 plugin 是否满足你的需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ICVFX)
- 官方文档：无（.uplugin 的 DocsURL 为空）
- [ICVFXTesting](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/ICVFXTesting) — 配套测试 plugin
