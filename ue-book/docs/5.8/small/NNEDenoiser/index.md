# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 插件为虚幻引擎的路径追踪器（Path Tracer）提供基于神经网络（NNE）的降噪功能。它解决了路径追踪渲染中，为了获得低噪声、高质量图像需要大量采样导致渲染速度极慢的问题。通过训练有素的神经网络模型，该插件能够用较少的采样数快速生成高质量的图像，显著提升渲染效率，特别适合建筑可视化、产品展示等需要快速迭代或实时预览的场景。

## 使用场景

-   你正在使用虚幻引擎的**路径追踪器**进行渲染，但受限于渲染速度（每帧需要大量采样），希望**快速获得低噪声的预览或最终图像**。
-   你需要在保持渲染质量的前提下，**减少路径追踪的采样数以节省时间**，例如在动画预览或设计评审阶段。
-   你为项目的渲染管线集成了神经网络推理（NNE）能力，并希望直接利用其进行**运行时或编辑器内的智能降噪**。

## 模块

| 模块 | 说明 |
|---|---|
| `NNEDenoiser` | 核心运行时模块，包含降噪功能的主要逻辑、NNE插件集成以及渲染资源的调度。 |
| `NNEDenoiserShaders` | 运行时着色器模块，包含降噪过程所需的GPU计算着色器。 |

## 模块依赖

使用此插件需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `NNERuntimeORT` | 提供运行 NNE 模型所需的 OnnxRuntime 推理后端。 |
| `RenderCore`, `RHI`, `Renderer` | 处理渲染资源、RHI 命令和渲染器集成。 |
| `NNE` | 提供与虚幻引擎 NNE 框架交互的接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 简化了GPU命令提交与等待逻辑。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 更新日志宏为新版格式。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染相关头文件的包含与前置声明。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染目标相关类型定义，优化头文件结构。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前查找替换操作引入的错误。 |

### 维护评价

**维护状态：活跃维护**。插件于2024年8月创建，最近一次更新在2026年4月，更新频率稳定。近期提交主要围绕代码质量优化（头文件整理、日志系统迁移）和GPU资源管理逻辑的改进，表明该模块仍处于积极的开发和维护中。作为Beta版功能，其API和实现细节可能会发生变化，但核心方向稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [子模块文档：NNEDenoiser](NNEDenoiser.md)
- [子模块文档：NNEDenoiserShaders](NNEDenoiserShaders.md)