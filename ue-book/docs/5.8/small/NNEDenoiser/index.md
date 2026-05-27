# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（降噪模型资产） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 利用 Unreal 的神经网络引擎（NNE）为路径追踪器（Path Tracer）提供基于深度学习的降噪能力。路径追踪渲染需要大量采样才能消除噪点，而该插件通过训练好的神经网络模型，在较少采样数下即可预测并消除噪点，大幅缩短渲染时间。

该插件是 UE5 路径追踪渲染管线的一部分，负责在路径追踪采样不足时介入，用神经网络推断出干净的图像。它依赖 `NNERuntimeORT`（ONNX Runtime 推理后端）来执行模型推理，并配合自定义着色器完成 GPU 端的降噪处理。

## 使用场景

- **建筑可视化 / 影视渲染**：使用路径追踪器输出最终画面时，用较少采样快速获得低噪点结果
- **实时路径追踪预览**：在编辑器中预览路径追踪效果时，加速收敛
- **Lumen 替代方案**：需要物理精确光照但不想等待数百帧采样时，用神经网络降噪补偿

## 模块概览

| 模块 | 类型 | 说明 |
|---|---|---|
| [NNEDenoiser](NNEDenoiser.md) | Runtime | 核心降噪逻辑，包含降噪器实现、模型加载、渲染管线集成 |
| [NNEDenoiserShaders](NNEDenoiserShaders.md) | Runtime | GPU 着色器，负责降噪前后的图像数据处理与调度 |

## 蓝图用法

本插件主要通过渲染管线自动集成，不直接暴露蓝图节点。降噪器在路径追踪器采样不足时自动被路径追踪渲染管线调用，无需手动控制。

配置方式通过项目设置中的路径追踪相关选项完成。

## C++ 用法

本插件的 C++ API 面向引擎渲染模块开发者。详细用法请参阅各子模块文档：

- **渲染管线集成**：参见 [NNEDenoiser 模块文档](NNEDenoiser.md)
- **着色器交互**：参见 [NNEDenoiserShaders 模块文档](NNEDenoiserShaders.md)

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心，提供模型加载与推理抽象层 |
| `NNERuntimeORT` | ONNX Runtime 推理后端，执行实际的神经网络前向推断 |
| `RenderCore` | 渲染核心，用于渲染目标池、着色器绑定等 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 替换已废弃的 GPU 同步 API 为新接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至新格式 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers | 补充缺失的渲染头文件前向声明与包含 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header | 拆分渲染目标池到独立头文件 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换导致的编译问题 |

### 维护评价

该插件于 2024 年 8 月从 Experimental 文件夹迁出并标记为 Beta，至今约 2 年。近期更新（2026 年 2-4 月）均为引擎内部重构的适配工作（API 迁移、头文件整理、日志格式更新），未涉及功能变更或 bug 修复。插件仍处于 **Beta** 状态，功能已基本稳定但尚未正式发布。

由于 IsBetaVersion=true，建议在生产环境中谨慎使用，关注后续正式版本的发布。作为 NNE 生态的重要组成部分，预计会持续随引擎更新维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- 依赖插件：[NNERuntimeORT](../NNERuntimeORT/)（ONNX Runtime 推理后端）