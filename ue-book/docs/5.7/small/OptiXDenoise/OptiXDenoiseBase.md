# OptiXDenoise

> Denoising engine for the Unreal Path Tracer based on NVIDIA's OptiX AI-Accelerated Denoiser library.

| 属性 | 值 |
|---|---|
| 中文名 | OptiX 降噪 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OptiXDenoise` (RuntimeAndProgram), `OptiXDenoiseBase` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise) | |

---

## 用途

OptiXDenoise 是一个基于 NVIDIA OptiX AI-Accelerated Denoiser 库的降噪引擎，专门用于 Unreal Engine 的路径追踪渲染器（Path Tracer）。路径追踪渲染会产生大量噪声（尤其是蒙特卡洛噪声），该插件通过 CUDA 加速的 OptiX 降噪器，实时对渲染结果进行降噪处理，同时支持引导层（法线、反照率）和时间性降噪（Temporal Denoising），以保留更多细节并减少闪烁。

**意义**：在保持实时交互性的同时，大幅提升路径追踪的视觉质量，是影视级预演或高质量离线渲染场景下的关键组件。

---

## 使用场景

- 使用 Unreal Engine 的路径追踪渲染器进行全动态光照的实时预览或最终帧渲染
- 需要高帧率且无噪声的交互式光线追踪预览（如汽车配置器、建筑可视化）
- 对质量要求较高的影视级序列渲染（结合输出通道进行后期合成）

---

## 蓝图用法

此插件为**纯 C++ 插件**，不暴露任何 BlueprintCallable 函数或蓝图中可读写的属性。所有功能仅能通过 C++ 或编辑器内部的渲染管线调用。因此，在蓝图工作流中无法直接使用该插件。

---

## C++ 用法

### 头文件引入

```cpp
#include "OptiXDenoiseBase.h"
#include "OptiXCudaFunctionList.h"
#include "OptiXDenoiserFunctionList.h"   // 内含 CUDA 内核加载宏
```

### 基本用法

以下示例基于官方接口，展示如何初始化一个降噪上下文并执行一次降噪。

```cpp
// 1. 初始化 CUDA 模块（前提：系统已安装 CUDA 驱动）
FCUDAModule& CudaModule = FModuleManager::GetModuleChecked<FCUDAModule>("CUDA");
CUcontext CudaContext = CudaModule.GetCudaContext();
CUstream CudaStream;
CUDA_CHECK(CudaModule.cuStreamCreate(&CudaStream, 0));

// 2. 创建并初始化降噪上下文
FOptiXDenoiseContext DenoiseContext;
EOptiXDenoiseResult Result;

Result = DenoiseContext.InitOptiX();
// 检查 Result == 0

// 注册日志回调（可选）
Result = DenoiseContext.CreateContext(CudaContext, MyLogCallback, 4);

// 3. 配置降噪器（开启法线引导、反照率引导、时间模式）
DenoiseContext.InitializeDenoiser(true, true, true);

// 4. 分配内存资源
uint32 OutputWidth = 1920, OutputHeight = 1080;
DenoiseContext.ComputeMemoryResource(OutputWidth, OutputHeight);

// 5. 准备输入输出图像数据（以 FOptiXImageData 结构体描述）
FOptiXImageData InputLayer, OutputLayer;
// ... 填充 Data、Width、Height、RowStrideInBytes、PixelStrideInBytes、Format

DenoiseContext.SetLayerInput(InputLayer);
DenoiseContext.SetLayerOutput(OutputLayer);

// 设置引导层（法线、反照率、光流）
FOptiXImageData NormalGuide, AlbedoGuide, FlowGuide;
// ... 填充
DenoiseContext.SetGuideLayerNormal(NormalGuide);
DenoiseContext.SetGuideLayerAlbedo(AlbedoGuide);
DenoiseContext.SetGuideLayerFlow(FlowGuide);

// 6. 分配 CUDA 状态和临时缓冲区
size_t StateSize = DenoiseContext.GetStateSizeInBytes();
size_t ScratchSize = DenoiseContext.GetWithoutOverlapScratchSizeInBytes();
CUdeviceptr StatePtr, ScratchPtr;
CUDA_CHECK(CudaModule.cuMemAlloc(&StatePtr, StateSize));
CUDA_CHECK(CudaModule.cuMemAlloc(&ScratchPtr, ScratchSize));

// 7. 设置降噪器
DenoiseContext.SetupDenoiser(CudaStream, InputLayer.Width, InputLayer.Height,
                             StatePtr, StateSize, ScratchPtr, ScratchSize);

// 8. 执行降噪（非重叠模式）
DenoiseContext.InvokeOptiXDenoise(CudaStream, StatePtr, StateSize,
                                  ScratchPtr, ScratchSize,
                                  0, 0, InputLayer.Width, InputLayer.Height);

// 9. 清理
CudaModule.cuStreamDestroy(CudaStream);
CudaModule.cuMemFree(StatePtr);
CudaModule.cuMemFree(ScratchPtr);
DenoiseContext.Destroy();
```

**来源**：`OptiXDenoiseBase.h`、`OptiXDenoiserFunctionList.h`（内核加载宏 `CUDA_CHECK`）

### 进阶用法

#### 时间性降噪（Temporal Denoising）

```cpp
// 在每一帧中保持状态并重复使用
DenoiseContext.SetTemporalModeUsePreviousLayers(true);

// 第一帧：
DenoiseContext.SetLayerInput(CurrentFrameInput);
DenoiseContext.SetLayerOutput(CurrentFrameOutput);
DenoiseContext.SetPreviousOutputInternalGuideLayer(PreviousFrameInternalGuide);

// 执行降噪后，将当前输出保存为下一帧的 previous
DenoiseContext.GetOutputInternalGuideLayer(/* 保存到 FOptiXImageData */);

// 后续帧：设置前一帧的输出作为 PreviousOutputLayer
DenoiseContext.SetLayerPreviousOutput(PreviousFrameOutput);
```

#### 流式平铺降噪（支持重叠区域）

```cpp
// 对于大图像，可分割为多个 tile 处理
uint32 TileWidth = 512, TileHeight = 512;
uint32 Overlap = DenoiseContext.GetOverlapWindowSizeInPixels();

// 逐 tile 调用
DenoiseContext.InvokeOptiXDenoise(CudaStream, StatePtr, StateSize,
                                  ScratchPtr, ScratchSize,
                                  Overlap, TileWidth, TileHeight);
```

#### CUDA Kernel 加载（由 `FOptiXDenoiserFunctionInstance` 管理）

`FOptiXDenoiserFunctionInstance` 继承自 `FOptiXCudaFunctionInstance`，负责从 PTX 文件加载自定义 CUDA kernel（如拷贝 Surface、转换 RGBA 等）。用户可通过 `FOptiXCudaFunctionList::Get().RegisterFunctionInstance<T>()` 注册自定义实例，但通常情况下无需手动处理。

---

## Demo 示例

以下是一个最小化的控制台应用程序示例，展示如何在编辑器中嵌入降噪调用（需运行于 UE 编辑器或独立程序）。

**FooDenoiseDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "OptiXDenoiseBase.h"

class FDenoiseDemo
{
public:
    void RunDenoiseDemo();
};
```

**FooDenoiseDemo.cpp**
```cpp
#include "FooDenoiseDemo.h"
#include "OptiXDenoiserFunctionList.h"
#include "CUDA/Module.h"  // FCUDAModule

void FDenoiseDemo::RunDenoiseDemo()
{
    // 初始化 CUDA
    FCUDAModule& CUDA = FModuleManager::GetModuleChecked<FCUDAModule>("CUDA");
    CUcontext Ctx = CUDA.GetCudaContext();
    CUstream Stream;
    CUDA_CHECK(CUDA.cuStreamCreate(&Stream, 0));

    // 创建降噪上下文
    FOptiXDenoiseContext Denoiser;
    Denoiser.InitOptiX();
    Denoiser.CreateContext(Ctx, nullptr, 0);
    Denoiser.InitializeDenoiser(true, true, false); // 无时间模式

    // 模拟 512x512 输入
    FOptiXImageData Input, Output;
    Input.Width = Output.Width = 512;
    Input.Height = Output.Height = 512;
    Input.Format = EOptiXImageFormat::CUDA_A32B32G32R32_F;
    // 分配 CUDA 内存并填充数据（略）
    CUDA_CHECK(CUDA.cuMemAlloc(&Input.Data, 512*512*4*sizeof(float)));
    CUDA_CHECK(CUDA.cuMemAlloc(&Output.Data, 512*512*4*sizeof(float)));

    Denoiser.SetLayerInput(Input);
    Denoiser.SetLayerOutput(Output);

    // 计算资源
    Denoiser.ComputeMemoryResource(512, 512);
    size_t StateSize = Denoiser.GetStateSizeInBytes();
    size_t ScratchSize = Denoiser.GetWithoutOverlapScratchSizeInBytes();
    CUdeviceptr State, Scratch;
    CUDA_CHECK(CUDA.cuMemAlloc(&State, StateSize));
    CUDA_CHECK(CUDA.cuMemAlloc(&Scratch, ScratchSize));

    Denoiser.SetupDenoiser(Stream, 512, 512, State, StateSize, Scratch, ScratchSize);
    Denoiser.InvokeOptiXDenoise(Stream, State, StateSize, Scratch, ScratchSize, 0, 512, 512);

    // 清理（略）

    Denoiser.Destroy();
    CUDA.cuStreamDestroy(Stream);
}
```

---

## 模块依赖

**公共依赖（需在其模块的 Build.cs 中添加）**：

| 模块 | 用途 |
|---|---|
| `CUDA` | CUDA 驱动 API（核心依赖） |
| `D3D12RHI` | D3D12 渲染基础设施，用于 Surface 到 CUDA 的拷贝 |
| `MessageLog` | 日志输出支持 |

**省略常见依赖**（Core, Engine 等自动包含）。

---

## 维护状态

### 近期更新

- 2025-06-04 `562eefdb` — disable OptiXDenoise on Windows Arm64
- 2025-05-09 `da955ce5` — Adding Windows Arm64 libraries for OptiXDenoise
- 2024-10-08 `54fa3a60` — Fix nonportable paths for UnrealEditor
- 2024-06-13 `bb709276` — Path Tracer: Fix minor typos in variable names/comments
- 2024-06-13 `86ad0353` — [Backout] - CL34349901

### 维护评价

- **创建时间**：2024年6月，约1年历史。
- **更新频率**：最近一年内有三次正式更新：2024-10 路径修复，2025-05 添加 Arm64 支持，2025-06 禁用 Arm64（兼容性调整）。符合**活跃维护**标准（6 个月内有功能性更新）。
- **已知问题**：目前仅支持 Win64 (x64)，不支持 Arm64；标记为实验性插件，默认未启用。
- **推荐使用**：适合需要集成 OptiX AI 降噪的路径追踪管线，但需注意其实验性状态，可能在未来版本中 API 或依赖发生变化。

---

## 相关链接

- [源码根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise)
- [OptiX 官方文档](https://developer.nvidia.com/optix)
- [测试用例（若有）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise/Tests)