# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照贴图 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPULightmass 是一个使用 DirectX 12 和 DXR（DirectX Raytracing）硬件加速的静态光照构建与实时预览系统。它旨在作为传统 CPU 光照贴图烘焙（Lightmass）的替代方案，通过利用现代 GPU 的并行计算和光线追踪能力，大幅缩短光照构建时间，并为编辑器提供近乎实时的光照预览，从而加速关卡美术和设计师的迭代流程。

## 使用场景

- 你在制作一个包含大量静态光照的场景（如建筑可视化、大型开放世界关卡），但厌倦了等待长达数小时的 CPU 光照烘焙过程。
- 你需要在编辑器中快速查看光照和阴影的最终效果，以便进行即时调整和优化。
- 你的开发环境配备了支持硬件光线追踪的显卡（如 NVIDIA RTX 系列）。

## 蓝图用法

此插件的使用主要通过编辑器菜单和面板进行，不直接暴露蓝图函数节点。核心交互通过编辑器UI完成。

### 核心节点

*本插件无暴露的 `BlueprintCallable` 函数。所有功能均通过编辑器集成实现。*

## C++ 用法

### 模块依赖

| 模块 | 用途 |
|---|---|
| `RenderCore`, `RHI`, `RHICore` | 底层渲染硬件接口和核心渲染功能 |
| `D3D12RHI` | DirectX 12 渲染硬件接口实现 |
| `RayTracing` | UE 的硬件光线追踪抽象层 |
| `Projects` | 插件项目系统 |

*注：依赖项基于对模块功能的推断，实际依赖请以 `GPULightmass.Build.cs` 文件为准。*

## 模块列表

- **`GPULightmass`** (UncookedOnly)
  - **核心光照构建模块**。包含 DXR 光线追踪器、光照累积算法、光照贴图的生成与管理等所有核心计算逻辑。
- **`GPULightmassEditor`** (Editor)
  - **编辑器集成模块**。负责将核心功能与 Unreal Editor 结合，提供构建菜单、设置面板、进度显示、预览交互等用户界面和工作流支持。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 修复缓存场景销毁时的着色器绑定表内存释放问题 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 重构硬件光线追踪动态几何更新参数，统一网格批次管理 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager. | 重构动态光线追踪几何的顶点缓冲区管理逻辑 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 清理GPU同步API，用新函数替换旧函数 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统日志宏迁移至新的格式化日志宏 |

### 维护评价

**状态：活跃维护的实验性功能。**

该插件创建于2020年，已存在约6年。从Git提交历史看，其底层光线追踪（HWRT）部分与UE引擎核心渲染代码一同**持续获得更新和优化**（最近一次更新在2026年5月），主要涉及内存管理、API重构和底层性能改进。

**结论与建议：**
- **优点**：核心代码仍在维护和迭代，并未被废弃。对于希望利用硬件光追加速光照构建的团队，它仍然是一个有潜力的选择。
- **风险**：插件长期处于 **Beta/实验性**状态且**默认未启用**，表明其稳定性、功能完整性和生产就绪程度未经 Epic 官方完全验证。API 和行为可能随引擎版本变化而改变。
- **推荐**：建议在**非生产项目**或**研发测试环境**中试用，并密切关注每个引擎版本的更新日志。不推荐直接用于需要高稳定性的商业项目核心管线。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)
- 官方文档：无
- 测试用例：无（插件内未发现）