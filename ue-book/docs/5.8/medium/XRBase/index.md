# XR Base

> XR Base Feature Implementations. (Generally this plugin will be automatically enabled by another plugin that requires it.)

| 属性 | 值 |
|---|---|
| 中文名 | XR 基础运行时 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `XRBase` (Runtime), `XRBaseEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XRBase) | |

## 用途

XRBase 是 UE5 的 XR（扩展现实）基础设施插件。它源自对引擎核心 `HeadMountedDisplay` 模块的抽取重构——将大量原本嵌入在引擎 Runtime 中的 VR/XR 功能代码迁移到独立插件，目的是**减小最小可执行文件的体积和内存占用**，同时改善代码组织结构。

该插件由其他 XR 插件（如 OpenXR、SteamVR 等）自动依赖启用，普通项目无需手动开启。它提供了 HMD 追踪、Motion Controller、XR 交互系统等核心抽象和基础实现，是 UE5 整个 XR 生态的底层基石。

`SupportedPrograms` 限定为 `LiveLinkHub`，说明此插件目前主要面向 LiveLinkHub 程序编译使用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`XRBase`](XRBase.md) | Runtime | XR 核心运行时：HMD 追踪、Motion Controller、XR 输入、XR 相机等基础功能实现 |
| [`XRBaseEditor`](XRBaseEditor.md) | Editor | XR 编辑器支持：编辑器内 VR 预览、XR 相关资产和设置的编辑器扩展 |

## 使用场景

- **你正在开发 VR/XR 应用** → 无需直接使用此插件，它会被 OpenXR 等上层插件自动拉入
- **你需要自定义 XR 输入或追踪逻辑** → 引用 `XRBase` 模块，基于其提供的 HMD/Controller 抽象类扩展
- **你在开发 LiveLinkHub 相关工具** → 此插件已包含在 LiveLinkHub 的编译依赖中
- **你需要在编辑器中预览 VR 内容** → `XRBaseEditor` 提供编辑器侧的 XR 支持

## 模块依赖

`XRBase` 是从引擎核心抽取出来的，其依赖关系已通过重构尽量精简。以下为与 XR 功能直接相关的特殊依赖：

| 模块 | 用途 |
|---|---|
| `OpenXR` | OpenXR 运行时接口（Shader 迁移相关） |
| `AugmentedReality` | AR 能力抽象，XR 追踪与 AR 功能有交叉依赖 |

> 大部分依赖仍为标准 Core/Engine/Slate 等基础模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 的截断警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式 UE_LOGF |
| 2026-04-08 | `01e78a0b` | Moving open xr shaders to XR base | 将 OpenXR 着色器代码迁移到 XRBase 插件 |
| 2026-04-03 | `22c896f3` | PR #13335: Add OpenXR XR_KHR_COMPOSITION_LAYER_CUBE_EXTENSION layer type | 新增 OpenXR 立方体贴图合成层扩展支持 |
| 2026-04-02 | `85acc4bf` | [Backout] - CL52371899 | 回退此前的一次提交 |

### 维护评价

- **活跃维护中**：最近一个月内有多次实质性更新，包括新功能（OpenXR 立方体层扩展）、代码迁移（着色器、日志宏）和编译修复
- 创建于 2023 年，是 UE5 模块化重构的一部分，属于较新但稳定的基础设施插件
- 持续从引擎核心向插件迁移更多 XR 代码（如 OpenXR 着色器），说明 Epic 仍在积极推进 XR 代码的插件化
- **推荐使用**：作为 XR 生态的基础依赖，虽无需直接操作，但了解其结构有助于理解 UE5 XR 架构

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/XRBase)
- [XRBase 模块文档](XRBase.md)
- [XRBaseEditor 模块文档](XRBaseEditor.md)