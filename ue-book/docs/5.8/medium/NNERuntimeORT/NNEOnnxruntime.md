# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | NNE ONNX 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 UE5 神经网络引擎（NNE）的 ONNX Runtime 后端实现。它为 NNE 框架提供实际的模型推理能力，底层依赖 Microsoft 的 ONNX Runtime 库。

该插件解决的核心问题是：**在 UE5 中高效运行 ONNX 格式的神经网络模型**。它封装了 ONNX Runtime 的 C/C++ API，并通过动态加载 DLL 的方式引入 ONNX Runtime 依赖，提供两种执行后端：

- **CPU 执行提供程序**：通过 `OrtSessionOptionsAppendExecutionProvider_CPU` 在 CPU 上运行推理
- **DirectML 执行提供程序**（仅 Windows）：通过 `OrtSessionOptionsAppendExecutionProvider_DML` 利用 GPU 加速推理，兼容所有支持 DirectX 12 的显卡

插件的结构分为两个模块：
- **NNEOnnxruntime**（External）：第三方库包装层，负责 ONNX Runtime DLL 的加载、API 函数指针解析，以及提供 C/C++ 头文件
- **NNERuntimeORT**（Runtime）：实现 NNE 框架定义的运行时接口，将 ONNX Runtime 的能力暴露给上层

该插件处于 **Beta** 阶段，默认未启用，需要手动在项目设置中开启。

## 使用场景

- 你有一个用 PyTorch/TensorFlow 导出的 ONNX 模型 → 用 NNE + NNERuntimeORT 在 UE5 中运行推理
- 你需要在 Windows 上用 GPU 加速神经网络推理 → 用 DirectML 后端，无需 CUDA
- 你在做风格迁移、物体检测、图像分割等 AI 功能 → 通过 NNE 框架使用此运行时
- 你需要跨平台（Win64/Linux/Mac）运行同一模型 → 此插件支持多平台

## 蓝图用法

该插件本身不直接暴露蓝图节点。它作为 NNE 框架的底层运行时后端，蓝图交互通过上层 NNE 插件的 `UNNEModelData` 和推理相关 API 进行。使用时需配合 NNE 核心插件。

### 典型工作流

1. 在项目设置中启用 NNERuntimeORT 插件
2. 将 ONNX 模型文件导入项目
3. 通过 NNE 蓝图/C++ API 加载模型数据
4. 选择 NNERuntimeORT 作为推理后端执行推理

## C++ 用法

### 头文件引入

```cpp
// 引入 NNEOnnxruntime 模块（第三方 ONNX Runtime 封装）
#include "NNEOnnxruntime.h"

// 直接使用 ONNX Runtime C++ API（通过 NNEOnnxruntime 头文件）
#include "onnxruntime_cxx_api.h"
```

### 基本用法：加载 API 函数

```cpp
// 从 NNEOnnxruntime.h 提取的 API 函数加载模式
#include "NNEOnnxruntime.h"

void* DllHandle = FPlatformProcess::GetDllHandle(TEXT("onnxruntime.dll"));
if (DllHandle)
{
    TUniquePtr<UE::NNEOnnxruntime::OrtApiFunctions> ApiFunctions = 
        UE::NNEOnnxruntime::LoadApiFunctions(DllHandle);
    
    if (ApiFunctions.IsValid())
    {
        // 获取 ONNX Runtime API 基础接口
        const OrtApiBase* ApiBase = ApiFunctions->OrtGetApiBase();
        const OrtApi* Api = ApiBase->GetApi(ORT_API_VERSION);
        
        // 使用 API 创建环境、会话等
        // ...
    }
}
```

### 基本用法：创建推理会话

```cpp
// 基于 ONNX Runtime C++ API（通过 NNEOnnxruntime 暴露的头文件）
#include "NNEOnnxruntime.h"

void RunInference()
{
    // 1. 创建环境
    Ort::Env Env(ORT_LOGGING_LEVEL_WARNING, "MyNNEModel");
    
    // 2. 配置会话选项
    Ort::SessionOptions SessionOptions;
    SessionOptions.SetIntraOpNumThreads(1);
    
    // 3. 添加 CPU 执行提供程序（通过 DLL 导出函数）
    // OrtSessionOptionsAppendExecutionProvider_CPU(SessionOptions, 1);
    
    // 4. 创建会话并加载 ONNX 模型
    // Ort::Session Session(Env, ModelPath, SessionOptions);
    
    // 5. 准备输入/输出张量并执行推理
    // Session.Run(RunOptions, InputNames, InputTensors, OutputNames, OutputTensors);
}
```

### 进阶用法：DirectML GPU 加速（仅 Windows）

```cpp
// 基于 dml_provider_factory.h 提供的接口
#if PLATFORM_WINDOWS
#include "NNEOnnxruntime.h"

void RunInferenceWithDirectML(void* DllHandle, int DeviceId)
{
    Ort::Env Env(ORT_LOGGING_LEVEL_WARNING, "MyNNEModel");
    Ort::SessionOptions SessionOptions;
    
    auto ApiFunctions = UE::NNEOnnxruntime::LoadApiFunctions(DllHandle);
    if (ApiFunctions.IsValid() && ApiFunctions->OrtSessionOptionsAppendExecutionProvider_DML)
    {
        // 使用设备 ID 0（默认 GPU）添加 DirectML 执行提供程序
        OrtStatus* Status = ApiFunctions->OrtSessionOptionsAppendExecutionProvider_DML(
            SessionOptions, DeviceId);
        
        if (Status == nullptr)
        {
            // 成功添加 DML EP，可以创建会话并运行推理
            // Ort::Session Session(Env, ModelPath, SessionOptions);
        }
    }
}
#endif
```

## Demo 示例

以下是一个完整的最小示例，展示如何通过 NNEOnnxruntime 模块使用 ONNX Runtime API：

```cpp
// NNEOrtDemo.h
#pragma once

#include "CoreMinimal.h"

class FNNEOrtDemo
{
public:
    static void RunModelInference(const FString& ModelPath);
};
```

```cpp
// NNEOrtDemo.cpp
#include "NNEOrtDemo.h"
#include "NNEOnnxruntime.h"

void FNNEOrtDemo::RunModelInference(const FString& ModelPath)
{
    // 创建 ONNX Runtime 环境
    Ort::Env Env(ORT_LOGGING_LEVEL_WARNING, "NNEOrtDemo");
    
    // 配置会话选项
    Ort::SessionOptions SessionOptions;
    SessionOptions.SetIntraOpNumThreads(4);
    SessionOptions.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);
    
    // 创建推理会话（注意：UE 使用 TCHAR 路径）
    const FTCHARToUTF8 ModelPathUtf8(*ModelPath);
    Ort::Session Session(Env, ModelPathUtf8.Get(), SessionOptions);
    
    // 获取模型输入信息
    Ort::AllocatorWithDefaultOptions Allocator;
    size_t InputCount = Session.GetInputCount();
    std::string InputName = Session.GetInputNameAllocated(0, Allocator).get();
    
    // 获取输入形状
    Ort::TypeInfo InputTypeInfo = Session.GetInputTypeInfo(0);
    auto InputTensorInfo = InputTypeInfo.GetTensorTypeAndShapeInfo();
    std::vector<int64_t> InputShape = InputTensorInfo.GetShape();
    
    // 创建输入张量（以 float 为例）
    std::vector<float> InputData(/* 填充数据 */);
    Ort::MemoryInfo MemoryInfo = Ort::MemoryInfo::CreateCpu(
        OrtAllocatorType::OrtArenaAllocator, 
        OrtMemType::OrtMemTypeDefault);
    
    Ort::Value InputTensor = Ort::Value::CreateTensor<float>(
        MemoryInfo, InputData.data(), InputData.size(),
        InputShape.data(), InputShape.size());
    
    // 准备输入输出名称
    std::vector<const char*> InputNames = { InputName.c_str() };
    std::vector<const char*> OutputNames = { /* 输出名称 */ };
    
    // 执行推理
    auto OutputTensors = Session.Run(
        Ort::RunOptions{nullptr},
        InputNames.data(), &InputTensor, 1,
        OutputNames.data(), 1);
    
    // 获取输出结果
    float* OutputData = OutputTensors[0].GetTensorMutableData<float>();
    // 处理输出数据...
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 核心框架，定义运行时接口 |
| `Projects` | 插件模块注册与管理 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 日志宏 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退之前的提交 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime（后被回退） |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染资源相关头文件，调整包含关系 |

### 维护评价

- **创建时间**：2023 年 11 月，约 2 年历史
- **维护状态**：**活跃维护中**。最近一次更新在 2026 年 4 月，持续进行 ONNX Runtime 和 DirectML 版本升级
- **更新频率**：约每 2-4 周有提交，主要围绕第三方库版本升级和代码清理
- **Beta 状态**：该插件仍处于 Beta 阶段（`IsBetaVersion=true`），且默认未启用，API 可能在未来版本发生变化
- **平台支持**：Win64、Linux、LinuxArm64、Mac

**推荐使用**：如果你的项目需要在 UE5 中运行 ONNX 模型推理，这是目前官方推荐的 NNE 后端之一。但需注意 Beta 状态意味着未来可能有 API 变动，建议在生产环境中做好兼容性测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)