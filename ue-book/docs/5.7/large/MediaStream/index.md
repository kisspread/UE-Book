```markdown
# Media Stream

> Content/type agnostic chainable media proxy with media player integration.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体流 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（插件内容，可能包含蓝图、配置及编辑器资源） |
| 模块 | `MediaStream` (Runtime), `MediaStreamEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-21 |
| 年龄标签 | 🆕（约 0.3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream) | |

## 总体用途

Media Stream 提供了一套内容/类型无关的**可链式媒体代理**（chainable media proxy），并深度集成 UE 的媒体播放器（Media Player）与 Sequencer 轨道。它允许开发者将多个媒体处理单元（如解码、过滤、格式转换、缓冲等）串联成一条管道，对媒体源进行透明化的流式处理。核心设计目标是：

- 解耦媒体格式与播放逻辑，通过代理链灵活扩展；
- 与 Media Compositing 和 Sequencer 原生配合，支持在时间线上编辑、混合多个媒体流；
- 提供编辑器工具（图形化节点图）来可视化构建媒体处理管段。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [MediaStream](MediaStream.md) | Runtime | 核心运行时模块，实现媒体代理管道的概念、基类与基本流程控制。 |
| [MediaStreamEditor](MediaStreamEditor.md) | Editor | 编辑器集成模块，提供 Sequencer 轨道支持、代理节点图编辑与可视化调试。 |

## 使用场景

- **多格式媒体源统一管理**：你有一个项目需要同时支持本地 MP4、HLS 直播流、RTMP 推流等不同格式的媒体播放 → 利用 Media Stream 构建适配不同源的代理链，统一输出为 UE 媒体纹理。
- **媒体处理管线编辑**：你需要在编辑器中对视频流进行实时滤镜、字幕叠加、色彩校正等处理 → 在 Sequencer 中结合 Media Stream 的代理节点图，可视化编排处理步骤。
- **动态媒体路由**：你的游戏内直播系统需要根据用户选择切换不同分辨率的视频流 → 通过运行时更换代理链中的中间节点实现无缝切换。
- **媒体合成与时间线编辑**：将多个媒体流（如摄像头画面、录制的视频、实时抠像）在 Sequencer 中混合 → 利用 Media Compositing + Media Stream 实现多层轨道合成。

## 蓝图用法

详细的蓝图可调用节点请参阅各模块文档：

- [MediaStream 蓝图节点](MediaStream.md#蓝图用法)
- [MediaStreamEditor 蓝图节点](MediaStreamEditor.md#蓝图用法)

核心涉及：创建/配置媒体代理链、绑定媒体播放器、控制播放（播放/暂停/跳转）等。所有运行时接口均在 `MediaStream` 模块中公开。

## C++ 用法

请参阅各模块文档中的 C++ 示例与测试用例：

- [MediaStream C++ 用法](MediaStream.md#c-用法)
- [MediaStreamEditor C++ 用法](MediaStreamEditor.md#c-用法)

典型场景：继承 `UMediaStreamProxy` 实现自定义代理节点，或通过 `FMediaStreamChain` 构建运行时管道。

## Demo 示例

插件包含编辑器演示资源（位于 Content/ 目录下），可直接在 Sequencer 中加载并测试媒体流代理链。详细的构建和运行步骤请参见模块文档中的 “Demo 示例” 章节。

## 模块依赖

要使用 Media Stream，你的项目/模块的 `Build.cs` 中需添加以下依赖（常见引擎模块已省略）：

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | 提供 Sequencer 编辑器集成 |
| `MediaCompositing` | 媒体合成与轨道支持 |
| `MediaPlayerEditor` | 媒体播放器编辑与资源管理 |

运行时仅需依赖 `MediaStream` 模块，编辑器功能需额外加载 `MediaStreamEditor`。

## 维护状态

### 近期更新

| 日期 | 提交 | 解读 |
|---|---|---|
| 2025-08-19 | `e555c6cb` | Media Stream: Removed Blueprint nodes. (清理蓝图节点) |
| 2025-07-10 | `9803c443` | 为源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏 (编译优化) |
| 2025-07-01 | `7ef6bcad` | Media Stream: Fixed for packaged games (修复打包游戏问题) |
| 2025-05-28 | `4ab4a67c` | Media Stream: Fixed relevancy issue for Sequencer. (修复 Sequencer 关联性) |
| 2025-05-21 | `fe3f901d` | Media Stream: Fixed sequencer binding issues (修复 Sequencer 绑定) |

### 维护评价

- **创建时间**：2025-05-21，距今约 3 个月，属于早期插件。
- **更新频率**：自创建以来保持每月 1-2 次提交，最近一次在 2025-08-19，修复/优化内容为主，无新增功能。
- **活跃度**：目前处于积极维护状态，但注意其 `IsExperimentalVersion=true`，API 可能随版本变化。
- **限制**：仅支持 UE 5.7+ 的实验性特性，不适合需要长期稳定 API 的生产项目。如果需要稳定的媒体管道方案，建议等待其正式发布。
- **推荐度**：如果项目已采用 UE 5.7 并需要灵活的媒体流代理能力，可以尝试使用，但需做好 API 变动的准备。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream)
- [模块文档 – MediaStream (Runtime)](MediaStream.md)
- [模块文档 – MediaStreamEditor (Editor)](MediaStreamEditor.md)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MediaStream/Tests)（如果存在）
```