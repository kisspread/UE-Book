# nDisplay Fill Derived Data Cache

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | DDC 预填充 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器后台任务） |
| 模块 | `DisplayClusterFillDerivedDataCache` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterFillDerivedDataCache) | |

## 用途

该模块是 nDisplay 集群渲染系统的一部分，其核心功能是在编辑器启动后，异步地**预填充派生数据缓存（DDC）**。它通过在后台运行一个独立的命令行进程来扫描项目资产，并编译其中的材质和着色器，将结果存入 DDC。此操作旨在减少后续编辑器操作（如打开关卡、编辑材质）时的首次编译卡顿，提升工作流效率。本质上，它是一个**编辑器后台优化工具**，并非用于运行时渲染。

## 使用场景

- 当你的项目包含大量复杂材质和着色器，每次打开编辑器都需要长时间编译时，此模块可以将这个过程提前并后台化。
- 作为 nDisplay 集群部署的前期准备工作，确保所有 PC 节点的 DDC 都已预热，减少集群运行时首次加载的延迟。

## 蓝图用法

该模块主要作为编辑器后台服务运行，其核心逻辑封装在内部工作线程 (`FDisplayClusterFillDerivedDataCacheWorker`) 中，并未暴露 `BlueprintCallable` 或 `BlueprintReadWrite` 函数供蓝图直接调用。其触发通常通过编辑器菜单或自动化测试集成。

## C++ 用法

此模块的设计目标是作为独立的编辑器服务，通常不直接集成到用户游戏代码中。其接口主要用于模块内部生命周期管理及与 nDisplay 系统的集成。

### 头文件引入

```cpp
// 若要检查模块状态或访问其实例
#include "DisplayClusterFillDerivedDataCacheModule.h"
```

### 基本用法（模块访问）

该模块提供了单例访问模式，主要用于其他 nDisplay 模块进行内部通信。

```cpp
#include "DisplayClusterFillDerivedDataCacheModule.h"

// 获取模块实例（通常用于内部集成，而非外部用户代码）
FDisplayClusterFillDerivedDataCacheModule& DDCModule = FDisplayClusterFillDerivedDataCacheModule::Get();
```
*注：模块的 `StartupModule` 会在引擎初始化完成后自动创建异步任务工作线程。*

### 进阶用法（内部工作流程）

模块的核心是 `FDisplayClusterFillDerivedDataCacheWorker`。它实现 `FRunnable` 接口，执行以下关键步骤：
1.  **启动命令行进程**：生成并执行 `UnrealEditor-Cmd.exe` 的 DDC 填充命令（通过 `GetDdcCommandletParams` 和 `GetTargetPlatformParams` 构造参数）。
2.  **解析日志输出**：通过正则表达式 (`RegexParseForEnumerationCount`, `RegexParseForLoadingProgress`, `RegexParseForCompilationProgress`) 读取子进程的管道输出，解析出资产枚举数量、加载进度和编译进度。
3.  **更新通知**：根据解析到的进度信息，在编辑器内更新 `FAsyncTaskNotification` 进度条。
4.  **异常处理**：处理用户取消 (`CancelTask`) 和命令行进程完成 (`CompleteCommandletAndShowNotification`) 的情况。

## Demo 示例

由于此模块主要为后台服务，没有直接的用户 API 可供演示。其典型“用法”是在编辑器中通过 **nDisplay 配置器（Configurator）** 面板触发，或在 nDisplay 集群部署的自动化脚本中调用。当模块激活时，编辑器右下角会出现一个“填充 DDC”的进度通知。

## 模块依赖

此模块依赖关系简单，主要为 nDisplay 核心功能和编辑器基础框架。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加了 EXR 多层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay 影片管线：将 WarpBlendAlpha 模式合并到 WarpBlend 中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机命名问题；修复了 MPCDI/ICVFX 着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退时遵循非默认的显示伽马值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时发生的闪烁问题。 |

### 维护评价

- **创建时间**：该插件创建于 2018 年，已有约 8 年历史。
- **近期更新**：最近一次提交在 2026 年 5 月，更新频繁且集中于功能增强（如 EXR 多层支持）和问题修复，表明插件**处于活跃维护状态**。
- **已知限制**：由于其设计为特定的后台命令行任务，主要限制是增加编辑器启动后的后台 CPU 负载，并依赖于 `UnrealEditor-Cmd.exe` 的正确运行。
- **推荐使用**：如果你的 nDisplay 集群项目在编辑器开发阶段因材质编译而缓慢，启用此模块可以有效预热 DDC，**推荐在开发期间使用**。它并非 nDisplay 渲染运行的必要模块，因此可按需启用。

## 相关链接

- [源码 (模块目录)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterFillDerivedDataCache)
- [源码 (核心 Worker)](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterFillDerivedDataCache/Public/DisplayClusterFillDerivedDataCacheWorker.h)