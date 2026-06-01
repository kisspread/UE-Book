```markdown
# NVIDIA Rivermax Media Streaming

> Adding NVIDIA Rivermax capabilities for Media Captures and Media Players

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 媒体流 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxMedia` (Runtime), `RivermaxMediaEditor` (Runtime), `RivermaxMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia) | |

## 用途

该插件为 UE5 集成 NVIDIA Rivermax SDK，提供基于 IP 的专业级媒体采集和播放能力。Rivermax 是 NVIDIA 提供的硬件加速 RDMA（远程直接内存访问）网络库，专为超低延迟、高吞吐量的视频传输设计。

该插件解决的核心问题是：在虚拟制片（Virtual Production）场景中，通过 IP 网络实现 4K/8K 等高分辨率视频信号的实时采集（Media Capture）和播放（Media Player），取代传统的 SDI 线缆方案。借助 NVIDIA ConnectX 网卡的硬件加速，Rivermax 可以在标准以太网上实现接近零拷贝的视频流传输。

## 使用场景

- 你在做虚拟制片（LED Volume 拍摄），需要将 Unreal 画面通过 IP 输出到 LED 墙 → 使用 Rivermax Media Output 进行视频采集输出
- 你需要从 IP 网络上的专业摄像机（如 SMPTE 2110 兼容设备）接收视频信号 → 使用 Rivermax Media Source 进行视频播放输入
- 你需要基于 ANC（辅助数据）通道传输时间码信息 → 使用 Rivermax 的 ANC Timecode 功能
- 你追求最低延迟的 NDI/ST 2110 替代方案 → Rivermax 通过 RDMA 提供更低延迟

## 模块列表

| 模块 | 说明 | 详细文档 |
|---|---|---|
| `RivermaxMedia` | 核心运行时模块，包含 Rivermax Media Player（IP 视频播放）和 Rivermax Media Capture（IP 视频采集）的实现 | [RivermaxMedia.md](RivermaxMedia.md) |
| `RivermaxMediaEditor` | 编辑器支持模块，提供 Rivermax 媒体资产的编辑器集成和 UI | [RivermaxMediaEditor.md](RivermaxMediaEditor.md) |
| `RivermaxMediaFactory` | 工厂模块，负责 Rivermax MediaSource 和 MediaOutput 的资产创建和实例化 | [RivermaxMediaFactory.md](RivermaxMediaFactory.md) |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RivermaxCore` | Rivermax SDK 的核心封装层（来自同级 Rivermax 插件） |
| `MediaIOCore` | 媒体 I/O 基础设施（Media Source/Media Output 基类和工厂框架） |
| `MediaAssets` | 媒体资产类型定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和采集添加引擎分析数据 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 调整虚拟制片资产的分类目录 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 补充 MediaSource/MediaOutput 子类的资产定义注册 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | 新增 ANC 时间码输入、重构输入流基类、统一像素格式 |

### 维护评价

该插件仍在**活跃维护**中。2026 年有多次功能性更新，包括 ANC 时间码支持、输入流架构重构和像素格式统一等重要改进。作为 Virtual Production 流水线的关键组件，Epic Games 持续投入开发。不过需注意该插件仍标记为 **Beta 版本**（`IsBetaVersion: true`），API 可能发生变化。此外，该插件**默认未启用**，且依赖 NVIDIA ConnectX 网卡硬件和 Rivermax SDK，部署门槛较高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxMedia)
- [NVIDIA Rivermax SDK](https://developer.nvidia.com/rivermax)
```