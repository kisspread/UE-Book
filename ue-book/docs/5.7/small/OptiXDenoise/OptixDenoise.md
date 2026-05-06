# OptiXDenoise

> Denoising engine for the Unreal Path Tracer based on NVIDIA's OptiX AI-Accelerated Denoiser library.

| 属性 | 值 |
|---|---|
| 中文名 | OptiX降噪引擎 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OptiXDenoise` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise) | |

## 用途

OptiXDenoise 是 Unreal Engine 路径追踪器（Path Tracer）的 AI 加速降噪模块，基于 NVIDIA OptiX 框架和 CUDA。它通过 DX/CUDA 互操作在 RHI 纹理和 CUDA 表面之间高效传递数据，利用 OptiX 深度学习降噪模型对渲染结果进行实时降噪。该插件解决了路径追踪渲染中蒙特卡洛采样不足导致的噪点问题，显著提升画面质量，尤其适用于交互式预览和最终帧输出。

## 使用场景

- 在影视级预可视化或建筑可视化项目中，使用 Unreal 路径追踪器进行光照渲染 → 启用 OptiXDenoise 以获得干净的降噪输出。
- 需要实时或近实时降噪，且目标平台为 Windows x86-64 的桌面应用。
- 对 NVLink / CUDA 环境有控制的离线渲染流程。

## 蓝图用法

该插件为底层渲染模块，**不暴露任何蓝图表面的函数或属性**。所有操作需通过 C++ 代码完成。

## C++ 用法

### 头文件引入

```cpp
#include "OptiXDenoiser.h"          // 核心降噪器
#include "CudaModule.h"             // CUDA 驱动模块
#include "RHIResources.h"           // RHI 纹理资源
```

### 基本用法

1. **初始化 CUDA 模块**
```cpp
ICudaModule& CudaModule = FModuleManager::LoadModuleChecked<ICudaModule>("Cuda");
CudaModule.InitDriver();   // 必须初始化
```

2. **获取 OptiX 降噪器实例**
使用 `UE::OptiXDenoiser::FOptiXImage2D` 包装 CUDA 表面与 OptiX 图像，管理 DX/CUDA 互操作。典型流程：

```cpp
// 假设已有 FRHITexture* 纹理（例如 PathTracer 输出的积累纹理）
FRHITexture* SrcTexture = ...;

// 创建 FOptiXImage2D 并绑定 CUDA 外部对象
UE::OptiXDenoiser::FOptiXImage2D CudaImage;
CudaImage.InitializeFromTexture(SrcTexture);

// 分配 OptiX 降噪内存（内部 OptiX 图像）
CudaImage.AllocateOptiXImage();

// 执行降噪（内部调用 optixDenoise 并将结果写回）
CudaImage.Denoise();
```

完整示例见 `Engine/Plugins/Experimental/OptiXDenoise/Source/OptiXDenoise/Private/OptiXDenoiser.cpp`。

### 进阶用法

**自定义降噪参数**：通过 `FOptiXImage2D::SetDenoiseParams()` 调整降噪强度、时域滤波等（需查阅 OptiX 文档）。**注意**：仅支持单帧独立降噪，暂未开放时序重用 API。

**DX/CUDA 互操作回调**：可注册 `FCUDASurfaceTextureCopyCallback` 在纹理拷贝前后执行额外操作（如自定义后处理）。

## Demo 示例

一个最小 C++ 类，使用 OptiXDenoise 对指定 RHI 纹理进行降噪并输出结果。

```cpp
// MyDenoiser.h
#pragma once
#include "CoreMinimal.h"
#include "RHI.h"
#include "OptiXDenoiser.h"

class FMyDenoiser
{
public:
    void Initialize();
    void DenoiseTexture(FRHITexture* SrcTexture);
    void Shutdown();

private:
    TUniquePtr<UE::OptiXDenoiser::FOptiXImage2D> CudaImage;
    bool bInitialized = false;
};
```

```cpp
// MyDenoiser.cpp
#include "MyDenoiser.h"
#include "CudaModule.h"

void FMyDenoiser::Initialize()
{
    // 加载 CUDA 模块
    ICudaModule& CudaMod = FModuleManager::LoadModuleChecked<ICudaModule>("Cuda");
    CudaMod.InitDriver();
    bInitialized = true;
}

void FMyDenoiser::DenoiseTexture(FRHITexture* SrcTexture)
{
    if (!bInitialized || !SrcTexture) return;

    // 创建 FOptiXImage2D 实例（需确保纹理格式兼容）
    CudaImage = MakeUnique<UE::OptiXDenoiser::FOptiXImage2D>();
    CudaImage->InitializeFromTexture(SrcTexture);

    // 分配 OptiX 降噪内存
    if (CudaImage->AllocateOptiXImage())
    {
        // 执行降噪
        CudaImage->Denoise();
    }
}

void FMyDenoiser::Shutdown()
{
    CudaImage.Reset();
}
```

使用前需在 `.Build.cs` 中添加依赖 `"OptiXDenoise"`（详见模块依赖）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MessageLog` | 输出降噪过程中诊断信息与错误日志 |
| `D3D12RHI` | Windows 平台 DX12 纹理互操作（CUDA 外部内存共享） |

> 还隐式依赖 `Cuda` 模块（通过 ICudaModule 接口加载）和 OptiX SDK（通过 `OptiXDenoiseBase` 第三方库提供）。

## 维护状态

### 近期更新

- 2025-06-04 562eefdb 禁用 OptiXDenoise 在 Windows Arm64 平台上
- 2025-05-09 da955ce5 添加 Windows Arm64 的第三方库（后续被禁用）
- 2024-10-08 54fa3a60 修复非可移植路径问题
- 2024-06-13 bb709276 修复变量名/注释中的微小拼写错误
- 2024-06-13 86ad0353 回滚某个变更

### 维护评价

- **创建时间**：2024-06-13，迄今约 1 年。
- **更新频率**：最近 1 年内有多次提交，但多为平台兼容性调整与细微修复，无重大功能更新。
- **状态**：**实验性**插件（`IsExperimentalVersion=true`），默认不启用。仅在 Windows x86-64 上受支持；Arm64 已被明确禁用。
- **已知限制**：仅支持单帧降噪，无时序重用；需要 NVIDIA GPU 及 OptiX 兼容驱动。
- **推荐度**：对于需要 OptiX 降噪的路径追踪项目，该插件是唯一官方方案，值得试用；但应谨慎在生产环境中启用，需充分测试兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/OptiXDenoise/Tests)（可能为空）
- [NVIDIA OptiX 降噪官方文档](https://developer.nvidia.com/optix-denoiser)