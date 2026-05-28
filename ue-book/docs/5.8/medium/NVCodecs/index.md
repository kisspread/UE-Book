# NVCodecs

> Adds codecs from the NVIDIA Media Codec SDK to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | NVIDIA编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NVCodecs` (Runtime), `NVCodecsRHI` (Runtime), `NVDEC` (Runtime), `NVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs) | |

## 用途
本插件是 Unreal Engine 5 音视频编解码框架 (`AVCodecs`) 的一个扩展，专门集成了 NVIDIA 的 Media Codec SDK。它的核心目的是为引擎提供对 NVIDIA GPU 硬件编解码器（特别是 NVDEC 解码器和 NVENC 编码器）的直接访问能力。通过此插件，开发者可以在 UE5 项目中利用 NVIDIA 显卡的专用硬件单元进行高性能的视频解码与编码，从而减轻 CPU 负担，适用于需要处理高分辨率、高帧率或大量视频流的场景。

## 使用场景
- **实时视频流处理**：在虚拟制片、远程协作或直播应用中，需要对来自网络或本地设备的高分辨率视频流进行低延迟解码。
- **游戏录制与直播**：使用 NVIDIA 的 NVENC 硬件编码器录制游戏画面或进行直播推流，实现几乎无性能损耗的高质量录制。
- **VR/AR 内容制作**：处理来自多个摄像头的同步高分辨率视频输入，利用 NVDEC 进行解码。
- **媒体应用**：在基于 UE5 的非线性编辑软件或视频播放器中，使用硬件加速解码播放 4K/8K 视频。

## 模块列表
本插件由四个运行时模块组成，协同工作以提供完整的 NVIDIA 编解码支持。

| 模块 | 说明 |
|---|---|
| **NVCodecs** | 提供 NVIDIA 编解码器的基础抽象和公共接口。 |
| **NVCodecsRHI** | 处理与渲染硬件接口 (RHI) 相关的资源管理，特别是用于视频处理的纹理。 |
| **NVDEC** | 集成 NVIDIA 的解码器 (NVDEC) SDK，实现硬件视频解码。 |
| **NVENC** | 集成 NVIDIA 的编码器 (NVENC) SDK，实现硬件视频编码。 |

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (UE5 通用文档，需在特定 AVCodecs 章节查找)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/NVCodecs/Tests)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `408f8cf3` | [NvEnc] Add: Launch arg and config option to revert to legacy D3D12 -> CUDA -> NvEnc code path to wo | 为 NvEnc 编码器添加启动参数和配置选项，允许回退到传统的 D3D12->CUDA->NvEnc 代码路径以解决兼容性问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的“作用域枚举”可能导致输出垃圾字符的错误。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了之前一次错误的“查找并替换”操作后的第二次尝试。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 撤销了 CL 51314860 的更改。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将 `FCoreDelegates::OnPostEngineInit` 迁移为 `FCoreDelegates::GetOnPostEngineInit()` 方法，以修复注册缺失的问题。 |

### 维护评价
本插件是 **活跃维护中** 的实验性插件。从近期提交历史看，维护者仍在积极修复问题（如输出错误、兼容性问题）并添加新功能（如编码器回退路径），表明它处于持续开发和优化阶段。

- **优势**：直接集成 NVIDIA 官方 SDK，能够充分利用特定硬件的性能优势。近期更新显示其仍在解决平台兼容性和稳定性问题。
- **注意事项**：
    1.  **实验性质**：插件标记为 `IsExperimentalVersion: true` 且默认未启用 (`EnabledByDefault: false`)，意味着 API 可能不稳定，未来版本可能有重大更改。
    2.  **平台依赖**：强依赖于 NVIDIA GPU 及其驱动程序，不具备跨平台通用性。
    3.  **集成关系**：它是 `AVCodecs` 生态的一部分，使用时可能需要配合该父插件。
- **推荐使用场景**：如果你的项目 **明确** 需要在 Windows 平台上使用 NVIDIA 硬件进行高性能视频编解码，并且可以接受实验性插件的风险，那么本插件是值得尝试的首选方案。对于通用的跨平台视频播放或处理需求，应优先考虑 `AVCodecs` 提供的软件或更通用的硬件抽象层。