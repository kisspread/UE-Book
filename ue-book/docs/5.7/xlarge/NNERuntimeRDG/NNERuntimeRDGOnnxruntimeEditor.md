# NNERuntimeRDGOnnxruntimeEditor

> 一个位于插件 NNERuntimeRDG 中的外部模块，封装了 ONNX Runtime C/C++ API，用于在编辑器环境中加载和运行 ONNX 模型。

| 属性 | 值 |
|---|---|
| 中文名 | ONNX 运行时编辑器桥接 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeRDGOnnxruntimeEditor` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Source/ThirdParty/OnnxruntimeEditor) | |

## 用途

本模块提供了一层干净的 C++ 封装，使得在 UE5 编辑器内可以安全、方便地使用 ONNX Runtime 进行模型推理。核心解决的问题包括：

- **DLL 管理**：自动加载 ONNX Runtime 的动态库（`onnxruntime.dll` 等），避免与运行时插件冲突。
- **API 统一**：将 ONNX Runtime 的 C/C++ API 封装为 UE 风格的函数指针结构体，并通过 `UE::NNEOnnxruntime::OrtApiFunctions` 暴露。
- **跨平台兼容**：通过预处理器宏 `UE_ORT_USE_INLINE_NAMESPACE` 控制命名空间，支持同时加载不同版本的 ONNX Runtime。
- **执行提供器**：内置 CPU 和 DML（DirectML）执行提供器的初始化函数，可轻松在 GPU 上加速推理。

它是 NNERuntimeRDG 插件的模型加载后端，主要面向**编辑器工具**（如模型预览、转换器、调试器）的开发者。

## 使用场景

- 你在开发一个编辑器内嵌的 ONNX 模型查看器或调试工具 → 使用该模块加载模型并获取推理结果。
- 你需要在不干扰运行时管线的情况下，在编辑器中快速测试 ONNX 模型的精度 → 使用该模块创建独立的推理会话。
- 你希望复用 ONNX Runtime 的 CPU 或 DirectML 后端进行离线推理 → 直接调用 `OrtApiFunctions` 中的提供器附加函数。

## 蓝图用法

无。本模块仅提供 C++ 接口，不暴露任何 BlueprintCallable 函数或可编辑属性。所有功能需在 C++ 代码中调用。

## C++ 用法

### 头文件引入

```cpp
#include "NNEOnnxruntimeEditor.h"
```

> **注意**：不要直接包含 `onnxruntime_c_api.h`、`onnxruntime_cxx_api.h` 等 ONNX Runtime 官方头文件，应始终通过 `NNEOnnxruntimeEditor.h` 间接引用。

### 基本用法

以下示例演示了如何加载 ONNX Runtime DLL、初始化 C++ API、创建会话并执行推理。

```cpp
// 1. 加载 DLL
void* DllHandle = FPlatformProcess::GetDllHandle(TEXT("onnxruntime.dll"));
check(DllHandle != nullptr);

// 2. 加载 API 函数指针
TUniquePtr<UE::NNEOnnxruntime::OrtApiFunctions> OrtApi = 
    UE::NNEOnnxruntime::LoadApiFunctions(DllHandle);
check(OrtApi.IsValid());

// 3. 初始化 ORT C++ API
Ort::InitApi(OrtApi->OrtGetApiBase()->GetApi(ORT_API_VERSION));

// 4. 创建环境、会话选项、会话
Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "TestSession");
Ort::SessionOptions sessionOptions;
sessionOptions.SetIntraOpNumThreads(1);
sessionOptions.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_EXTENDED);

// 5. 附加 CPU 执行提供器（可选）
OrtApi->OrtSessionOptionsAppendExecutionProvider_CPU(sessionOptions, 1);

// 6. 加载模型并创建会话
const wchar_t* ModelPath = L"path/to/model.onnx";
Ort::Session session(env, ModelPath, sessionOptions);

// 7. 获取模型信息
Ort::AllocatorWithDefaultOptions allocator;
size_t NumInputNodes = session.GetInputCount();
// ... 后续推理代码
```

源码参考：`NNEOnnxruntimeEditor.h`（头部注释中的示例代码）

### 进阶用法

**自定义 DirectML 执行提供器（Windows 仅）**：

```cpp
#if PLATFORM_WINDOWS
// 获取 D3D12 设备与命令队列（需自行实现）
ID3D12Device* D3D12Device = GetD3D12Device();
ID3D12CommandQueue* CmdQueue = GetD3D12CommandQueue();

// 创建 DirectML 设备
IDMLDevice* DMLDevice = nullptr;
DMLCreateDevice(D3D12Device, DML_CREATE_DEVICE_FLAG_NONE, IID_PPV_ARGS(&DMLDevice));

// 附加 DirectML 执行提供器（新 API）
Ort::ThrowOnError(OrtApi->OrtSessionOptionsAppendExecutionProviderEx_DML(
    sessionOptions, DMLDevice, CmdQueue));
#endif
```

**同时加载多个 ONNX Runtime 版本**（通过 `UE_ORT_INLINE_NAMESPACE`）：

在模块的 `Build.cs` 中设置：
```cpp
PublicDefinitions.Add("UE_ORT_USE_INLINE_NAMESPACE=1");
PublicDefinitions.Add("UE_ORT_INLINE_NAMESPACE_NAME=Ort011401");
```
之后，不同版本的 ONNX Runtime 会被隔离到不同的内联命名空间，避免符号冲突。

## Demo 示例

以下是一个完整的控制台模块示例，演示在编辑器外使用本模块加载 ONNX 模型并运行简单推理。

**MyOnnxTest.h**：
```cpp
#pragma once

#include "CoreMinimal.h"
#include "NNEOnnxruntimeEditor.h"

class FMyOnnxTest
{
public:
    static bool RunInference();
};
```

**MyOnnxTest.cpp**：
```cpp
#include "MyOnnxTest.h"
#include "HAL/PlatformProcess.h"
#include "Misc/Paths.h"

bool FMyOnnxTest::RunInference()
{
    // 加载 ONNX Runtime DLL
    FString DllPath = FPaths::Combine(FPaths::EngineDir(), TEXT("Binaries/ThirdParty/OnnxRuntime/Win64/onnxruntime.dll"));
    void* DllHandle = FPlatformProcess::GetDllHandle(*DllPath);
    if (!DllHandle)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load ONNX Runtime DLL"));
        return false;
    }

    // 加载 API 函数
    TUniquePtr<UE::NNEOnnxruntime::OrtApiFunctions> OrtApi = UE::NNEOnnxruntime::LoadApiFunctions(DllHandle);
    if (!OrtApi.IsValid())
    {
        FPlatformProcess::FreeDllHandle(DllHandle);
        return false;
    }

    // 初始化 C++ API
    Ort::InitApi(OrtApi->OrtGetApiBase()->GetApi(ORT_API_VERSION));

    // 创建环境与会话
    Ort::Env env(ORT_LOGGING_LEVEL_WARNING, "Demo");
    Ort::SessionOptions sessionOptions;
    sessionOptions.SetIntraOpNumThreads(1);

    // 附加 CPU 提供器
    OrtApi->OrtSessionOptionsAppendExecutionProvider_CPU(sessionOptions, 1);

    // 加载模型（假设存在测试模型）
    FString ModelPath = FPaths::Combine(FPaths::ProjectDir(), TEXT("Models/simple_model.onnx"));
    try
    {
        Ort::Session session(env, *ModelPath, sessionOptions);
        // 简单打印输入/输出信息
        Ort::AllocatorWithDefaultOptions allocator;
        UE_LOG(LogTemp, Log, TEXT("Model loaded. Input count: %zu"), session.GetInputCount());
        return true;
    }
    catch (const Ort::Exception& e)
    {
        UE_LOG(LogTemp, Error, TEXT("ONNX Runtime error: %s"), UTF8_TO_TCHAR(e.what()));
        return false;
    }
    finally
    {
        FPlatformProcess::FreeDllHandle(DllHandle);
    }
}
```

## 模块依赖

本模块为 External 类型，不产生运行时依赖，但使用者在连接时需要确保以下库可用：

| 模块/库 | 用途 |
|---|---|
| `ONNX Runtime` | 核心推理引擎（动态链接） |
| `DirectML`（Windows 仅） | DirectML 执行提供器（若使用 GPU） |
| `D3D12`（Windows 仅） | DirectML 所需的 D3D12 设备与命令队列 |

注：本模块头文件内部已处理了平台相关包含，使用者无需额外引入 `d3d12.h` 或 `DirectML.h`。

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 |
|---|---|---|
| 2025-07-24 | `2412ec9f` | Made TArrayView and Invoke constexpr. Fixed UB GetData and deprecated Alignment in TStaticArray |
| 2025-06-12 | `9ce28ae0` | Update numeric limits to use std lib instead of macro because it fails to compile on newer Windows 1 |
| 2025-06-12 | `d9dba260` | [NNE] NNERuntimeRDGHlsl arm64 support |
| 2025-06-03 | `d31855b9` | Fixup build script for libprotobuf-lite & add windows arm64 version |
| 2025-05-29 | `8cfef610` | Added Greater.h include to files which use TGreater, which will break with an upcoming change |

### 维护评价

本模块随 NNERuntimeRDG 插件一同维护，**创建于 2025 年 5 月，在 6 月仍有针对性更新（arm64 支持、编译修复）**，表明其在积极开发中。尚未发现废弃标记或已知限制。由于插件仍处于实验阶段（`IsExperimentalVersion=true`），API 和功能可能在未来版本中发生变化。综合来看，**推荐在新编辑器工具中使用**，但应关注后续版本更新。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Source/ThirdParty/OnnxruntimeEditor)
- [核心头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Source/ThirdParty/OnnxruntimeEditor/NNEOnnxruntimeEditor.h)
- [NNE 官方文档（Epic 开发者社区）](https://dev.epicgames.com/documentation/en-us/unreal-engine/neural-network-engine-in-unreal-engine)
- [ONNX Runtime 官方文档](https://onnxruntime.ai/docs/)