# AJA Media Player

> Implements input and output using AJA Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | AJA 媒体采集 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、媒体配置） |
| 模块 | `AjaCore` (Runtime), `AjaMedia` (Runtime), `AjaMediaEditor` (Runtime), `AjaMediaFactory` (Runtime), `AjaMediaOutput` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-08-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia) | |

## 总体用途

AJA Media Player 插件提供了对 **AJA 视频采集卡** 的输入输出支持，使虚幻引擎能够直接接收来自专业广播级设备的视频、音频信号，并可将引擎输出发送到外部硬件。它作为媒体框架（Media Framework）的后端，解决了以下问题：

- 实时视频采集（SDI / HDMI 输入）与播放
- 硬件同步（Genlock / Reference）
- 低延迟录制与回放
- 与广播电视流水线无缝集成

该插件广泛应用于直播、虚拟制片、演播室自动化等专业场景。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| **AjaCore** | Runtime | 封装 AJA SDK 核心 API、设备枚举、数据结构与同步操作 | [AjaCore.md](AjaCore.md) |
| **AjaMedia** | Runtime | 实现 UE 媒体框架接口（媒体播放器、媒体源、纹理等） | [AjaMedia.md](AjaMedia.md) |
| **AjaMediaEditor** | Runtime | 提供编辑器配置 UI、自定义细节面板与资产工厂 | [AjaMediaEditor.md](AjaMediaEditor.md) |
| **AjaMediaFactory** | Runtime | 工厂模块，负责创建媒体播放器和媒体源实例 | [AjaMediaFactory.md](AjaMediaFactory.md) |
| **AjaMediaOutput** | Runtime | 实现媒体输出（录制到文件或输出到硬件端口） | [AjaMediaOutput.md](AjaMediaOutput.md) |

## 使用场景

- **电视演播室制作**：将实时摄像机信号通过 AJA 卡输入虚幻引擎，在虚拟布景中合成并输出到播出系统。
- **现场直播节目**：使用 AJA 卡获取外部信号源（如摄像机、回放服务器）进行实时混合推流。
- **后期制作预审**：利用 AJA 输出卡将时间线预览发送到广播级监视器，确保色彩与帧率准确。
- **虚拟制片**：通过 Genlock 同步多台引擎实例或与 LED 墙同步，实现摄像机追踪与实时渲染的无缝融合。
- **科学可视化/模拟**：需要高帧率、低延迟视频输入输出时，借助 AJA 硬件获得确定性实时能力。

## 相关链接

- [源码仓库 (5.7)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AjaMedia)
- [官方文档](https://docs.unrealengine.com/5.7/WorkingWithMedia/AjaMedia/)（需外网访问）
- [模块文档汇总 – AjaCore](AjaCore.md) | [AjaMedia](AjaMedia.md) | [AjaMediaEditor](AjaMediaEditor.md) | [AjaMediaFactory](AjaMediaFactory.md) | [AjaMediaOutput](AjaMediaOutput.md)

---

> **维护状态**：该插件自 2025 年 8 月创建以来保持活跃更新（最近 2025-10-17），包含 SDK 升级、新输出模式与可靠性改进，适合新项目采用。