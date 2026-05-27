# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（神经网络模型资产） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

该插件提供了一个基于深度学习（神经网络）的实时降噪解决方案，专门用于UE5的路径追踪器（Path Tracer）。它解决了路径追踪在低采样数下产生的噪点问题，允许在更少的采样迭代次数后获得清晰、收敛的图像，显著提升了路径追踪的实用性和性能。

## 使用场景

*   **建筑可视化/产品渲染**：使用路径追踪获得高质量光影效果，同时通过神经网络降噪器实时或近实时查看最终结果，无需长时间等待渲染完成。
*   **影视预览与虚拟制片**：在LED墙或虚拟摄像机视图中，需要快速预览带光线追踪的场景时，提供快速的降噪反馈。
*   **游戏开发**：在编辑器中预览使用硬件光追或路径追踪的游戏场景，加速迭代流程。

## 蓝图用法

主要通过引擎设置进行配置，而非直接调用蓝图函数。核心功能由渲染系统在后台自动集成和执行。

### 配置入口

1.  **项目设置**：`项目设置 -> 引擎 -> 渲染 -> 后处理`。
2.  **选择降噪器**：在“路径追踪器”部分，可以将“降噪器”选项从“无”或“默认”切换为 `NNEDenoiser`。
3.  **选择模型**：插件内置了默认模型，也支持在“降噪器模型”设置中指定自定义的、已训练好的 ONNX 神经网络模型资产。

## C++ 用法

主要通过渲染子系统集成使用，普通游戏逻辑中较少直接调用。高级用法涉及与渲染线程交互。

### 头文件引入

```cpp
// 用于降噪器核心接口
#include "NeuralNetwork/NNEDenoiser.h"
#include "NeuralNetwork/NNEDenoiserModel.h"

// 用于与渲染器交互
#include "RenderGraphUtils.h"
#include "PostProcess/SceneRenderTargets.h"
```

### 基本用法（测试用例风格）

以下代码展示了如何初始化一个降噪器实例并对其输入缓冲区进行降噪（概念性流程，需在渲染线程中执行）。

*来源文件：`Engine/Plugins/NNE/NNEDenoiser/Tests/NNEDenoiserTest.cpp`*

```cpp
// 1. 获取降噪器实例
UNNEDenoiser* Denoiser = NewObject<UNNEDenoiser>();
Denoiser->Init(DenoiserModel); // 使用指定的神经网络模型初始化

// 2. 准备输入（带噪声的路径追踪结果）和输出缓冲区
FRDGBuilder GraphBuilder(...);
FRDGTextureRef NoisyInput = ...; // 带噪声的输入纹理
FRDGTextureRef DenoisedOutput = GraphBuilder.CreateTexture(...); // 创建输出纹理

// 3. 配置降噪参数
FNNEDenoiserExecuteParameters ExecuteParams;
ExecuteParams.InputTexture = NoisyInput;
ExecuteParams.OutputTexture = DenoisedOutput;
ExecuteParams.TemporalStability = 0.9f; // 时间稳定性参数

// 4. 执行降噪
Denoiser->Execute(GraphBuilder, ExecuteParams);

// 5. 提交图形命令并等待完成（在测试中常见）
GraphBuilder.Execute();
FlushRenderingCommands();
```

### 进阶用法（自定义集成）

在自定义渲染通道中集成降噪器，需要手动管理缓冲区交换和时序稳定性。

```cpp
// 在自定义的后处理通道中
void FMyCustomRenderPass::AddPasses(FRDGBuilder& GraphBuilder)
{
    // ... 准备当前帧的带噪声路径追踪结果 ...
    
    // 如果有时序数据，读取上一帧的降噪输出作为参考
    FRDGTextureRef PreviousDenoised = ...;
    
    // 配置并执行降噪，利用时序信息提升稳定性
    FNNEDenoiserExecuteParameters Params;
    Params.InputTexture = CurrentNoisyFrame;
    Params.OutputTexture = GraphBuilder.CreateTexture(...);
    Params.TemporalInputTexture = PreviousDenoised; // 传入上一帧结果
    
    Denoiser->Execute(GraphBuilder, Params);
    
    // 将输出传递给后续通道或保存为下一帧的时序参考
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNERuntimeORT` | 用于在运行时执行 ONNX 格式的神经网络模型，是插件的前置依赖项 |
| `RenderCore` | 渲染核心，用于创建和管理渲染资源（如纹理、缓冲区） |
| `RHI` | 渲染硬件接口，用于底层的 GPU 命令提交和同步 |
| `NNE` | 神经网络引擎核心框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 优化 GPU 命令提交和同步方式 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 统一日志宏为 UE_LOGF |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have ... | 修复编译问题，完善头文件依赖 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu ... | 重构渲染资源分配相关代码的头文件结构 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换操作 |

### 维护评价

*   **状态**：**维护中**。插件在 2026 年仍有活跃的代码更新，主要集中在渲染后端优化、代码规范和编译兼容性修复上。
*   **稳定性**：功能已较为稳定，但作为 **Beta 版本**（IsBetaVersion=true），API 和行为在后续版本中可能发生变化。
*   **推荐度**：**推荐用于实验和开发阶段**。它是 UE5 路径追踪工作流中提升交互体验的重要工具，适合对实时性有要求的渲染任务。由于是 Beta 版，在生产环境中使用时需注意其稳定性并做好备份。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
*   [官方文档]()（暂无）
*   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser/Tests)