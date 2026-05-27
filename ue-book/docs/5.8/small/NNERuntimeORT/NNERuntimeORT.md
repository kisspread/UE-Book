# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX运行时后端 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 UE5 神经网络引擎（NNE）的 **ONNX Runtime 推理后端**，为 NNE 框架提供基于 [ONNX Runtime](https://onnxruntime.ai/) 的模型推理能力。

它解决的核心问题：NNE 框架本身只定义了统一的神经网络推理接口（IModelCPU/IModelGPU/IModelRDG），而 NNERuntimeORT 负责将 ONNX 格式的模型加载到 ONNX Runtime 引擎中并执行实际的推理计算。它支持两种执行后端：

- **CPU 执行**：使用 ONNX Runtime 的 CPU 执行提供程序，通过 `IModelCPU`/`IModelInstanceCPU` 接口在游戏线程上同步执行推理
- **DirectML GPU 执行**（仅 Windows）：使用 DirectML 加速器，支持同步 GPU 推理（`IModelGPU`）和渲染依赖图集成（`IModelRDG`），后者可将推理嵌入 UE 的 RDG（Render Dependency Graph）渲染管线

简单来说，这是你用 NNE 框架运行 ONNX 模型时必须启用的后端插件——没有它，NNE 框架就缺少实际执行 ONNX 推理的能力。

## 使用场景

- 你需要在 UE5 中运行 ONNX 格式的神经网络模型（如风格迁移、物体检测、超分辨率等）
- 你需要在 CPU 上执行轻量级推理任务 → 使用 `INNERuntimeCPU` 接口
- 你需要在 Windows 上利用 DirectML/GPU 加速推理 → 使用 `INNERuntimeGPU` 或 `INNERuntimeRDG` 接口
- 你需要将 AI 推理嵌入渲染管线（如实时去噪）→ 使用 `INNERuntimeRDG` 接口集成到 RDG
- 你在开发 ML 驱动的游戏功能（NPC 行为预测、程序化生成辅助等）

## 蓝图用法

NNERuntimeORT 不直接暴露任何 `BlueprintCallable` 凑数。它的所有运行时实例类（`FModelORTCpu`、`FModelInstanceORTCpu` 等）均为 C++ 私有实现类，不继承 `UObject`，因此无法直接在蓝图中使用。

**蓝图用户应通过 NNE 主框架的蓝图 API 操作**，NNERuntimeORT 作为底层后端透明工作。相关蓝图节点属于 `NNE` 插件（如 `UNNEModelData`），不在本文档范围内。

## C++ 用法

### 头文件引入

由于 NNERuntimeORT 的类均为内部实现，不直接 include。你通过 NNE 框架的公开接口间接使用：

```cpp
// 通过 NNE 框架接口使用（推荐）
#include "NNE.h"
#include "NNEModelData.h"
```

### 基本用法

以下示例展示如何通过 NNE 框架使用 NNERuntimeORT 后端加载和运行 ONNX 模型：

```cpp
// 来源: 基于 Private/NNERuntimeORT.h 中 UNNERuntimeORTCpu 的接口设计
// 1. 获取 ORT CPU 运行时
TArray<INNERuntime*> Runtimes = UE::NNE::GetAllRuntimes();
INNERuntime* ORTRuntime = nullptr;
for (INNERuntime* Runtime : Runtimes)
{
    if (Runtime->GetRuntimeName() == TEXT("NNERuntimeORTCpu"))
    {
        ORTRuntime = Runtime;
        break;
    }
}

// 2. 加载模型数据
TConstArrayView64<uint8> ModelDataView = /* 你的 ONNX 模型原始字节 */;
TMap<FString, TConstArrayView64<uint8>> AdditionalData;

if (ORTRuntime->CanCreateModelData(TEXT("onnx"), ModelDataView, AdditionalData, FGuid(), nullptr) 
    == INNERuntime::ECanCreateModelDataStatus::Ok)
{
    TSharedPtr<UE::NNE::FSharedModelData> SharedModelData = 
        ORTRuntime->CreateModelData(TEXT("onnx"), ModelDataView, AdditionalData, FGuid(), nullptr);

    // 3. 创建模型实例
    UNNEModelData* ModelData = NewObject<UNNEModelData>();
    // ModelData 通过 NNE 框架管理 SharedModelData
    
    TSharedPtr<UE::NNE::IModelCPU> Model = ORTRuntimeCPU->CreateModelCPU(ModelData);
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Model->CreateModelInstanceCPU();

    // 4. 设置输入形状
    TArray<NNE::FTensorShape> InputShapes;
    // 根据模型需求构建输入形状...
    ModelInstance->SetInputTensorShapes(InputShapes);

    // 5. 执行推理
    TArray<uint8> InputData = /* 准备输入数据 */;
    TArray<uint8> OutputData;
    OutputData.SetNumUninitialized(/* 输出大小 */);

    TArray<NNE::FTensorBindingCPU> InputBindings = {{InputData.GetData(), InputData.Num()}};
    TArray<NNE::FTensorBindingCPU> OutputBindings = {{OutputData.GetData(), OutputData.Num()}};

    auto Status = ModelInstance->RunSync(InputBindings, OutputBindings);
    // Status == ERunSyncStatus::Ok 表示推理成功
}
```

### 进阶用法：线程配置

NNERuntimeORT 提供了详细的线程和执行模式配置（来自 `NNERuntimeORTSettings.h`）：

```cpp
// 来源: Private/NNERuntimeORTSettings.h
// 通过项目设置或代码配置 ONNX Runtime 的线程选项

// 在 DefaultEngine.ini 中配置:
// [/Script/NNERuntimeORT.NNERuntimeORTSettings]
// EditorThreadingOptions=(bUseGlobalThreadPool=true, IntraOpNumThreads=0, InterOpNumThreads=0, ExecutionMode=SEQUENTIAL)
// GameThreadingOptions=(bUseGlobalThreadPool=false, IntraOpNumThreads=1, InterOpNumThreads=1, ExecutionMode=SEQUENTIAL)
```

配置项说明：
- `bUseGlobalThreadPool`：是否使用跨会话共享的全局线程池
- `IntraOpNumThreads`：算子内并行线程数（0=默认，1=单线程）
- `InterOpNumThreads`：算子间并行线程数（仅 PARALLEL 模式有效）
- `ExecutionMode`：`SEQUENTIAL`（顺序执行）或 `PARALLEL`（并行执行，注意 DirectML EP 强制使用顺序模式）

### 进阶用法：DirectML GPU RDG 集成

```cpp
// 来源: Private/NNERuntimeORTModel.h 中 FModelInstanceORTDmlRDG
// 将 ONNX 推理嵌入 UE 的渲染依赖图 (RDG) 中

// 使用 INNERuntimeRDG 接口创建 RDG 模型实例
TSharedPtr<UE::NNE::IModelRDG> RDGModel = ORTRuntimeRDG->CreateModelRDG(ModelData);
TSharedPtr<UE::NNE::IModelInstanceRDG> RDGInstance = RDGModel->CreateModelInstanceRDG();

// 在渲染线程的 RDG Pass 中调度推理
RDGBuilder->AddPass(/* ... */, [&](FRDGBuilder& GraphBuilder)
{
    TArray<NNE::FTensorBindingRDG> Inputs = /* RDG 输入绑定 */;
    TArray<NNE::FTensorBindingRDG> Outputs = /* RDG 输出绑定 */;
    RDGInstance->EnqueueRDG(GraphBuilder, Inputs, Outputs);
});
```

## Demo 示例

```cpp
// MyMLComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "NNE.h"
#include "NNEModelData.h"
#include "MyMLComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyMLComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "ML")
    UNNEModelData* OnnxModelData;

    void InitModel();
    TArray<float> RunInference(TConstArrayView<float> InputData);

private:
    TSharedPtr<UE::NNE::IModelCPU> Model;
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

```cpp
// MyMLComponent.cpp
#include "MyMLComponent.h"
#include "NNE.h"

void UMyMLComponent::InitModel()
{
    if (!OnnxModelData) return;

    // 获取 NNE 所有运行时，筛选出 ORT CPU 后端
    TConstArrayView<INNERuntime*> Runtimes = UE::NNE::GetAllRuntimes();
    INNERuntimeCPU* ORTRuntime = nullptr;
    for (INNERuntime* Runtime : Runtimes)
    {
        ORTRuntime = Cast<INNERuntimeCPU>(Runtime);
        if (ORTRuntime && ORTRuntime->GetRuntimeName().Contains(TEXT("ORT")))
            break;
        ORTRuntime = nullptr;
    }

    if (!ORTRuntime) return;

    Model = ORTRuntime->CreateModelCPU(OnnxModelData);
    if (Model.IsValid())
    {
        ModelInstance = Model->CreateModelInstanceCPU();
    }
}

TArray<float> UMyMLComponent::RunInference(TConstArrayView<float> InputData)
{
    if (!ModelInstance.IsValid()) return {};

    // 根据模型输入描述设置形状（此处假设已知）
    TArray<NNE::FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs().Array();
    TArray<NNE::FTensorShape> InputShapes;
    for (const auto& Desc : InputDescs)
    {
        InputShapes.Add(NNE::FTensorShape::MakeFromSymbolic(Desc.GetShape()));
    }
    ModelInstance->SetInputTensorShapes(InputShapes);

    // 准备输入输出缓冲区
    TArray<float> OutputData;
    OutputData.SetNumZeroed(1024); // 根据模型输出大小调整

    NNE::FTensorBindingCPU InputBinding = {
        reinterpret_cast<const uint8*>(InputData.GetData()),
        static_cast<uint64>(InputData.Num() * sizeof(float))
    };
    NNE::FTensorBindingCPU OutputBinding = {
        reinterpret_cast<uint8*>(OutputData.GetData()),
        static_cast<uint64>(OutputData.Num() * sizeof(float))
    };

    if (ModelInstance->RunSync({InputBinding}, {OutputBinding}) 
        == IModelInstanceCPU::ERunSyncStatus::Ok)
    {
        return OutputData;
    }
    return {};
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 框架核心，提供 IModelCPU/IModelGPU/IModelRDG 等推理接口 |
| `NNECore` | NNE 核心类型定义（FTensorDesc、FTensorShape 等） |
| `NNEOnnxruntime` | 第三方 ONNX Runtime 静态库封装 |

无其他特殊依赖（仅标准 Core/Engine 等）。

> ⚠️ 注意：`NNEOnnxruntime` 是一个 External 模块，位于 `Source/ThirdParty/Onnxruntime/` 目录下，封装了 ONNX Runtime 和 DirectML 的二进制文件。它以静态库形式链接，打包时会自动包含。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 新格式 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退一次提交 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | ONNX Runtime 升级尝试（后被回退） |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 拆分渲染相关头文件，修正包含依赖 |

### 维护评价

NNERuntimeORT 是 **活跃维护** 的插件。从 2023 年 11 月创建至今约 2 年，近期（2026 年 3-4 月）仍有持续的功能更新，主要集中在第三方库版本升级（ONNX Runtime 1.24.3、DirectML 1.15.4）和代码质量维护。

**注意事项**：
- 当前仍为 **Beta 状态**（`IsBetaVersion=true`），API 可能发生变化
- **默认未启用**（`EnabledByDefault=false`），需在项目设置中手动启用
- 仅支持 **桌面平台**（Win64、Linux、LinuxArm64），不支持移动端和主机
- DirectML GPU 路径仅限 **Win64**，其他平台只能使用 CPU 后端

**推荐使用**：如果你需要在 UE5 中运行 ONNX 模型且可以接受 Beta 风险，推荐启用。NNE 框架是 Epic 官方推动的 ML 推理方案，NNERuntimeORT 是其最核心的运行时后端之一。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)