# OptiXDenoise

> Denoising engine for the Unreal Path Tracer based on NVIDIA's OptiX AI-Accelerated Denoiser library.

| 属性 | 值 |
|---|---|
| 中文名 | OptiX 降噪 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OptiXDenoise` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise) | |

## 总体用途

OptiXDenoise 插件为 Unreal Engine 的路径追踪渲染器（Path Tracer）提供基于 NVIDIA OptiX 深度学习加速的降噪后处理功能。路径追踪在低采样数下会产生大量噪点，该插件利用 GPU 实时降噪，在保持图像细节的同时快速清除噪点，大幅缩短渲染迭代时间，使预览更接近最终效果。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [OptixDenoise](./OptixDenoise.md) | Runtime | 集成 OptiX 去噪算法的核心运行时模块，负责渲染线程调度与降噪流程 |
| [OptiXDenoiseBase](./OptiXDenoiseBase.md) | External | 第三方库封装，提供底层 OptiX API 调用、资源管理与版本适配 |

## 使用场景

- **影视预可视化 / 动画渲染** – 在路径追踪预览时实时降噪，快速迭代镜头与材质
- **建筑与产品渲染** – 需要即时反馈的场景中，一键获得接近最终质量的图像
- **科研与基准测试** – 对比不同降噪算法（如 OptiX 与内置降噪）的效果与性能

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise/Tests)（如存在）