# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | Blackmagic媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime), `BlackmagicSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-06-18 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia) | |

## 总体用途

本插件封装了 Blackmagic Design 的采集卡 SDK，为 Unreal Engine 提供高质量的视频输入和输出能力。通过本插件，用户可以直接在引擎中接收来自 Blackmagic 采集卡的实时信号（如 HDMI、SDI），或将渲染画面输出到外接设备。适用于广电级制作、现场直播、虚拟演播室等需要低延迟、高帧率媒体 I/O 的场景。

插件按功能拆分为多个子模块，分别处理底层 SDK 封装、媒体播放、输出、编辑器交互及工厂创建。

## 模块列表

| 子模块 | 类型 | 一句话总结 |
|---|---|---|
| `BlackmagicCore` | Runtime | 提供 Blackmagic SDK 的 C++ 封装，包含设备枚举、帧缓冲、时间码等核心抽象。 |
| `BlackmagicMedia` | Runtime | 实现基于 Blackmagic 输入的媒体播放器（`UMediaPlayer` 接口），负责信号采集与播放逻辑。 |
| `BlackmagicMediaEditor` | Runtime (Editor 依赖) | 提供编辑器界面的自定义设置、媒体源配置面板及播放预览支持。 |
| `BlackmagicMediaFactory` | Runtime | 负责创建 `BlackmagicMedia` 媒体播放器实例，实现工厂模式。 |
| `BlackmagicMediaOutput` | Runtime | 实现渲染画面到 Blackmagic 输出卡的提交逻辑，支持帧同步与格式转换。 |
| `BlackmagicSDK` | External | 包含 Blackmagic 官方 SDK 头文件与库文件，不生成引擎模块，由其他模块引用。 |

各模块详细 API 请参阅对应文档：
- [BlackmagicCore](./BlackmagicCore.md)
- [BlackmagicMedia](./BlackmagicMedia.md)
- [BlackmagicMediaEditor](./BlackmagicMediaEditor.md)
- [BlackmagicMediaFactory](./BlackmagicMediaFactory.md)
- [BlackmagicMediaOutput](./BlackmagicMediaOutput.md)
- [BlackmagicSDK](./BlackmagicSDK.md)

## 使用场景

- **广电级摄像机/信号源接入**：将 SDI/HDMI 摄像机的实时画面导入 UE 作为背景或纹理，用于虚拟制片、混合现实。
- **现场直播推流**：将引擎渲染内容通过 Blackmagic 输出卡发送到切换台或编码器，实现低延迟直播。
- **虚拟演播室**：同时采集多路视频信号（如主持人、背景）并输出合成画面，需要精确帧同步。
- **专业监听与回放**：通过输出卡在专业监视器上预览最终画面，确保颜色与时间码准确。

## 依赖关系

Build.cs 中 `PublicDependencyModuleNames` 包含以下独特依赖（省略常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaSource` 等媒体播放基础设施。 |
| `BlackmagicCore` | （各模块依赖的核心底层库） |
| `MediaIOCore` | 提供媒体 I/O 通用框架（帧同步、时间码等）。 |

其余依赖均为标准引擎模块。

## 维护状态

### 近期更新

- 2025-09-23 `9d85dc0e` — 修复 Blackmagic 源在已有有效配置时仍分配默认配置的问题。
- 2025-08-21 `8143139e` — 补充缺失的 `#include` 头文件。
- 2025-08-20 `2f0476a2` — 添加缺失的头文件包含。
- 2025-07-22 `d0ba5722` — 为 AJA、Blackmagic、NDI 媒体源和输出的 Category 显示顺序添加排序。
- 2025-06-18 `60a45027` — 在 Windows Arm64 上禁用 BlackmagicMedia 插件。

### 维护评价

插件创建于 2025 年 6 月，属于全新功能插件。近期提交包含功能性修复（配置默认值）、编译修复和平台适配，显示团队在持续维护。目前无废弃标记，推荐在已有 Blackmagic 硬件且需要原生集成时使用。注意插件不默认启用，需在项目设置中手动启用，且目前仅支持 Win64 和 Linux（不支持 Windows Arm64）。

## 相关链接

- [源码 (branch 5.7)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/blackmagic-media-player-in-unreal-engine/)（假设存在，请以实际为准）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BlackmagicMedia/Tests)（如存在）