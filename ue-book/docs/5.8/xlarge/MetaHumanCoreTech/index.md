# MetaHuman Core Tech

> The core technology behind the MetaHuman Creator and MetaHuman Animator plugins.

| 属性 | 值 |
|---|---|
| 中文名 | 元人类核心引擎 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（二进制库、神经网络模型、捕获数据资产） |
| 模块 | `MetaHumanBodyTrackerInterface` (Runtime), `MetaHumanCaptureData` (Runtime), `MetaHumanCoreTech` (Runtime), `MetaHumanCoreTechLib` (Runtime), `MetaHumanImageViewer` (Runtime), `MetaHumanPipelineCore` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2022-01-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib) | |

## 用途

MetaHumanCoreTech 是 MetaHuman Creator 和 MetaHuman Animator 的底层引擎插件，提供了从面部/身体追踪到图像处理、从数据捕获到管线调度的全套核心能力。它本身不直接面向终端用户，而是作为上层 MetaHuman 工具链的基础设施存在——封装了高性能的身体追踪算法、OpenCV 驱动的图像处理管线、捕获数据的管理与序列化，以及用于协调各处理阶段的 Pipeline 框架。

该插件默认不启用（`EnabledByDefault: false`），通常由 MetaHuman Creator 或 MetaHuman Animator 插件自动拉入，或在需要自定义 MetaHuman 处理管线时手动启用。

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| `MetaHumanBodyTrackerInterface` | Runtime | 身体追踪器的抽象接口层，定义身体姿态估计的统一 API |
| `MetaHumanCaptureData` | Runtime | 捕获数据的管理与序列化，处理来自深度摄像头/视频的原始捕获数据 |
| `MetaHumanCoreTech` | Runtime | 核心算法封装，包含面部与身体追踪的核心计算逻辑 |
| `MetaHumanCoreTechLib` | Runtime | 核心技术库，封装底层二进制计算库（含第三方依赖 OnlineSubsystem） |
| `MetaHumanImageViewer` | Runtime | 图像查看与预处理工具，用于捕获帧的可视化与格式转换 |
| `MetaHumanPipelineCore` | Runtime | 处理管线框架，基于 OpenCV 的可扩展 Pipeline 调度系统 |

### 模块依赖关系

```
MetaHumanPipelineCore ──→ OpenCV, OpenCVHelper
MetaHumanCaptureData  ──→ MetaHumanImageViewer, DirectoryWatcher
MetaHumanCoreTechLib  ──→ UnrealEd, OnlineSubsystem
```

## 使用场景

- **你正在使用 MetaHuman Animator** → 此插件作为底层依赖自动加载，提供面部/身体追踪引擎
- **你正在使用 MetaHuman Creator** → 此插件提供身体追踪和数据处理的基础设施
- **你需要自定义面部/身体追踪管线** → 可以基于 `MetaHumanPipelineCore` 构建自定义处理管线
- **你需要处理深度摄像头捕获数据** → `MetaHumanCaptureData` 提供数据管理与序列化支持
- **你需要集成第三方身体追踪方案** → `MetaHumanBodyTrackerInterface` 提供标准化接口

## 模块文档

| 模块 | 文档 |
|---|---|
| MetaHumanBodyTrackerInterface | [MetaHumanBodyTrackerInterface.md](MetaHumanBodyTrackerInterface.md) |
| MetaHumanCaptureData | [MetaHumanCaptureData.md](MetaHumanCaptureData.md) |
| MetaHumanCoreTech | [MetaHumanCoreTech.md](MetaHumanCoreTech.md) |
| MetaHumanCoreTechLib | [MetaHumanCoreTechLib.md](MetaHumanCoreTechLib.md) |
| MetaHumanImageViewer | [MetaHumanImageViewer.md](MetaHumanImageViewer.md) |
| MetaHumanPipelineCore | [MetaHumanPipelineCore.md](MetaHumanPipelineCore.md) |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | Titan 引擎升级至 v9.0.8 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | Titan 引擎升级至 v9.0.7 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | Titan 引擎升级至 v9.0.6 |
| 2026-05-20 | `c5214fb2` | [MetaHumanBodyTracker] allow foot-locking to be toggled on or off | 身体追踪器新增脚部锁定开关功能 |
| 2026-05-19 | `a29cddd9` | [MHA] Crash during MHC assembly with body performance | 修复 MetaHuman Creator 身体装配时的崩溃问题 |

### 维护评价

- **维护状态**：🟢 **活跃维护**
- 近期更新非常频繁（2026 年 5 月内有多次 Titan 引擎版本升级和功能改进），表明 Epic 对 MetaHuman 技术栈持续投入
- Titan 引擎快速迭代（v9.0.6 → v9.0.8 仅 5 天），说明底层追踪算法仍在积极优化
- 作为 MetaHuman Creator 和 Animator 的基础依赖，属于 Epic 核心技术路线的一部分，长期维护有保障
- **推荐使用**：如果你的项目涉及 MetaHuman 工作流，此插件是必选依赖；如果需要自定义追踪管线，可以通过接口层接入

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCoreTechLib)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/meta-humans-in-unreal-engine/)