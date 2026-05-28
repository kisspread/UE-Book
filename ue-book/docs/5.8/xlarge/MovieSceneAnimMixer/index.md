# Sequencer Anim Mixer

> System for mixing layered animation in sequences

| 属性 | 值 |
|---|---|
| 中文名 | Sequencer 动画混合器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画混合相关资产） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `MovieSceneAnimMixerEditor` (Runtime), `MovieSceneAnimMixerScripting` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer) | |

## 用途

为 Sequencer 中的骨骼动画处理提供了一条全新的模块化路径。传统 Sequencer 动画轨道中，动画的生产和混合逻辑耦合在 Skeletal Animation System 内部，难以扩展。此插件将动画生产与混合彻底解构为两个独立阶段：

1. **动画生产阶段**：不同类型的轨道（动画序列、ControlRig、未来还可扩展至空闲动画、面部动画、注视、动作匹配等）各自生成"评估任务"（Evaluation Task），描述需要评估什么动画数据。
2. **动画混合阶段**：Anim Mixer 系统收集所有评估任务，按优先级编排为一个"评估程序"（Evaluation Program），发送到目标动画系统统一执行混合。

评估程序基于 AnimNext 的任务系统实现，使用共享虚拟机内存管理"姿态关键帧栈"（Pose Keyframe Stack），每个关键帧可包含骨骼姿态、曲线值、属性值和根运动。这种架构使得混合、遮罩、仅评估子集（如只评估根运动）等操作成为可能。

## 使用场景

- 你需要在 Sequencer 中同时混合多个动画源（如动画序列 + ControlRig + 面部动画）并精确控制优先级和权重
- 你需要将根运动处理与姿态评估解耦，在动画 Tick 之前独立处理根运动混合
- 你正在使用 AnimNext 生态，希望 Sequencer 动画能通过评估程序注入 AnimNext 管线
- 你需要自定义动画目标（Anim Target），将混合结果输出到自定义 AnimInstance、蓝图插槽或 AnimNext 注入点

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`MovieSceneAnimMixer`](MovieSceneAnimMixer.md) | Runtime | 核心混合系统：ECS 系统、评估程序构建、根运动处理、动画目标管理 |
| [`MovieSceneAnimMixerEditor`](MovieSceneAnimMixerEditor.md) | Runtime | 编辑器集成：Sequencer 轨道 UI、Section Gizmo、关键帧交互等 |
| [`MovieSceneAnimMixerScripting`](MovieSceneAnimMixerScripting.md) | Runtime | 脚本绑定层：蓝图和脚本可访问的混合器 API |

## 蓝图用法

> 详细 API 请参阅各子模块文档。以下为核心概念概览。

### 核心概念节点

| 概念 | 说明 |
|---|---|
| **MixedAnimationPriority** | 动画 Section 上的优先级字段，控制多个动画源在评估程序中的排序 |
| **MixedAnimationTarget** | 动画 Section 上的目标标识，决定评估程序发送到哪个动画目标系统 |
| **AnimMixerPoseProducer** | ECS 标签组件，标记实体由 AnimMixer 管理（替代原 SkeletalAnimationSystem） |

### 工作流描述

1. 在 Sequencer 中为骨骼网格体添加动画轨道（如 Animation Track）
2. 在 Section 属性中设置 `MixedAnimationPriority`（数值越小优先级越高）和 `MixedAnimationTarget`
3. AnimMixer 系统在运行时自动收集同目标的所有 Section，按优先级编排评估程序
4. 评估程序被发送到对应的目标系统（如 AnimInstanceTarget）执行混合

## C++ 用法

### 核心 ECS 系统

此插件完全基于 UE5 的 ECS（Mass Entity）架构，核心交互通过 ECS 系统和组件完成：

| ECS 系统 | 职责 |
|---|---|
| **Mixed Skeletal Animation System** | 接收动画 Section 创建的实体，为其生成评估任务并发送给 Mixer |
| **Anim Mixer System** | 接收评估任务组件，构建评估程序，分发到目标系统 |
| **Anim Instance Target System** | 接收评估程序，存入自定义 AnimInstance Proxy，应用混合姿态 |
| **Root Motion System** | 单独评估程序中的根运动属性，提前于动画 Tick 处理根运动混合 |

### 模块依赖

| 模块 | 用途 |
|---|---|
| `Settings` | 插件配置管理 |
| MovieScene 相关模块 | Sequencer 轨道和 Section 支持 |
| MassEntity / MassGameplay | ECS 框架（实体、组件、系统） |
| AnimationCore / AnimNext 相关 | 评估任务系统和动画运行时 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `00f154d0` | Sequencer Anim Mixer: fix root motion pop at boundary between a KeepState section and an Accumulated | 修复 KeepState 与 Accumulated Section 边界处根运动跳变问题 |
| 2026-05-26 | `8905e197` | Sequencer: Fix Anim Mixer section gizmo freezing when dragged with AutoKey Off | 修复 AutoKey 关闭时拖拽 Section Gizmo 冻结的问题 |
| 2026-05-22 | `5f14e324` | Sequencer: Anim Mixer: force-link CachePreAnimatedStateSystem from AnimMixerSystem | 从 AnimMixerSystem 强制链接 CachePreAnimatedStateSystem |
| 2026-05-22 | `5515824d` | Sequencer: Anim mixer fix InitialRoot mismatch between cache and runtime that slid character across | 修复缓存与运行时 InitialRoot 不匹配导致角色滑移的问题 |
| 2026-05-22 | `5c05fad6` | Sequencer: Anim mixer- fix issue where following a section with an anim with rotation in the offset | 修复前序 Section 带有旋转偏移时的混合问题 |

### 维护评价

**活跃维护** 🟢

- 插件创建于 2025 年初，至今约 1.4 年，属于较新的实验性插件
- 最近更新密集（2026 年 5 月连续多次修复），说明核心团队正在积极开发和打磨
- 目前处于 **IsExperimentalVersion = true** 状态，API 和行为可能在后续版本中有较大变动
- 从首次提交的 TODO 列表来看，仍在持续扩展动画轨道类型（ControlRig 等）和动画目标支持
- **建议**：适合提前研究和原型验证，不建议作为生产管线的核心依赖。关注 AnimNext 生态发展后再决定是否正式采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MovieSceneAnimMixer)
- [MovieSceneAnimMixer 模块文档](MovieSceneAnimMixer.md)
- [MovieSceneAnimMixerEditor 模块文档](MovieSceneAnimMixerEditor.md)
- [MovieSceneAnimMixerScripting 模块文档](MovieSceneAnimMixerScripting.md)