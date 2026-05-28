# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | RDG 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram), `NNERuntimeRDG` (RuntimeAndProgram), `NNERuntimeRDGData` (RuntimeAndProgram), `NNERuntimeRDGUtils` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-06 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

NNERuntimeRDG 是 UE5 神经网络引擎（NNE）的一个**基于 GPU 的推理运行时**。它利用引擎的 **Render Dependency Graph (RDG)** 系统在 GPU 上执行神经网络推理，通过 HLSL Compute Shader 实现张量运算。

这个插件解决的核心问题是：**如何在 UE5 的渲染管线内高效地执行机器学习模型推理**。与 CPU 推理不同，它将推理操作作为 GPU Compute Shader 插入渲染图中，可以与渲染管线并行执行，避免 CPU-GPU 同步开销。

插件支持 **ONNX 格式**的模型加载和推理，内部集成了 protobuf 和 ONNX 相关库用于模型解析。主要面向 Windows（DX11/DX12）、Linux（Vulkan）和 macOS（Metal）平台。

## 使用场景

- 你需要在 UE5 游戏中运行实时机器学习推理（如风格迁移、物体检测、图像增强）
- 你的项目使用 GPU 密集型的 ML 模型，需要利用 RDG 获得低延迟的推理性能
- 你想在渲染管线中直接嵌入神经网络计算，避免额外的 CPU-GPU 拷贝

## 蓝图用法

该插件作为 NNE 运行时注册，通过 NNE 核心插件的蓝图 API 间接使用。使用者通常通过 NNE 的统一接口加载模型和执行推理，而 NNERuntimeRDG 作为底层运行时自动被调度。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 通过 NNE 核心 API 加载模型 | 加载 ONNX 模型并选择 RDG 运行时 | `UNNEModelData` |
| 通过 NNE 核心 API 运行推理 | 在 GPU 上通过 RDG 执行推理 | `INNERuntime` 实现 |

### 使用示例（蓝图描述）

1. 创建 `UNNEModelData` 资产（导入 ONNX 模型）
2. 通过 NNE 的 `GetAllModelDataFormat` 检查支持的格式
3. 调用 `GetAllCompatibleRuntimes` 获取 RDG 运行时
4. 使用运行时创建模型实例并执行推理

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeRDG.h"
```

### 基本用法

通过 NNE 核心 API 选择 RDG 运行时并执行推理（基于 NNE 架构推断）：

```cpp
// 获取所有兼容的运行时
TArray<INNERuntime*> Runtimes = UNNE::GetAllCompatibleRuntimes(ModelData);

// 找到 RDG 运行时
INNERuntime* RDGRuntime = nullptr;
for (INNERuntime* Runtime : Runtimes)
{
    // RDG 运行时会在名称中包含 "RDG" 或 "HLSL" 标识
    RDGRuntime = Runtime;
    break;
}

// 创建模型实例
TWeakInterfacePtr<INNERuntimeGPU> GPURuntime = Cast<INNERuntimeGPU>(RDGRuntime);
if (GPURuntime.IsValid())
{
    // 使用运行时执行推理
    // 具体 API 取决于 NNE 核心接口定义
}
```

## Demo 示例

由于该插件作为 NNE 的底层运行时，没有独立的示例类。使用者通过 NNE 核心插件的统一接口来调用。可参考 Engine 内的 NNE 测试用例了解完整用法。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 核心 API 和运行时注册机制 |
| `MetalRHI` | macOS 平台 GPU 计算支持 |
| `VulkanRHI` | Linux 平台 GPU 计算支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一 GPU 同步 API，替换旧接口为 SubmitAndBlockUntilGPUIdle |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧版 GPU 性能分析宏 |

### 维护评价

- **状态**：活跃维护中。2026 年仍有持续更新，包括 API 迁移、编译修复和基础设施改进
- **实验性**：`.uplugin` 标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`，需要手动启用
- **依赖**：依赖大量第三方库（Protobuf、ONNX Runtime），模块数量多（含外部模块），集成复杂度较高
- **平台**：NNERuntimeRDGUtils 限制为 Win64/Linux/Mac，核心运行时使用 MetalRHI 和 VulkanRHI
- **建议**：适合**高级用户和前沿项目**。由于是实验性插件且 API 可能变动，生产环境使用需谨慎。建议配合 NNE 核心插件的文档一起参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- [NNE 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE)