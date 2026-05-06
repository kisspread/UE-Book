# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEUtils` (Runtime), `IREEDriverRDG` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREEShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

NNERuntimeIREE 是 Unreal Engine 神经网络引擎（NNE）的一个运行时实现。它的核心能力是将 ONNX 等格式的神经网络模型，通过 IREE（Intermediate Representation Execution Environment）编译成高度优化的原生代码（CPU 共享库或 GPU 着色器），从而在游戏中直接以极低开销执行推理。该插件解决了传统运行时（如 ONNX Runtime）在游戏环境中体积大、启动慢、不便于嵌入的问题，让神经网络推理能够像普通游戏代码一样运行，特别适合移动端和主机平台。

## 使用场景

- 你需要在游戏中使用预训练的神经网络模型（如动作识别、图像生成、字符串处理等），且要求极低的延迟和内存占用。
- 你的项目需要离线编译模型，将编译产物随游戏一起发布，运行时无需加载庞大的推理框架。
- 你希望充分利用 GPU 进行模型推理，且要求与 Unreal 的 RDG（渲染依赖图）无缝集成，避免显存拷贝开销。
- 你正在开发一个对性能极为敏感的实时系统（如 NPC 决策、物理模拟辅助、实时特效控制），需要将推理调用嵌入到每帧逻辑中。

## 蓝图用法

该插件直接实现 NNE 运行时接口，不暴露任何自定义的蓝图函数。所有推理流程均通过 C++ 的 NNE 标准接口完成。蓝图开发者应使用 NNE 系统提供的通用节点（如 `Run Model`），并确保项目设置了正确的运行时优先级。详细蓝图用法请参考 [NNE 插件文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/neural-network-engine-in-unreal-engine)。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeIREE.h"
#include "NNERuntimeIREESettings.h"
#include "NNERuntimeIREEModelData.h"
```

### 基本用法

以下示例展示如何通过 NNE 系统加载一个 ONNX 模型并使用 IREE 运行时进行 CPU 推理。该代码片段源自插件内部测试用例。

```cpp
// 1. 获取 IREE CPU 运行时对象（自动注册）
UNNERuntimeIREECpu* Runtime = Cast<UNNERuntimeIREECpu>(
    GEngine->GetEngineSubsystem<UNNESubsystem>()->GetRuntime(UNNERuntimeIREECpu::GUID));
if (!Runtime) return;

// 2. 加载 ONNX 文件数据
TArray64<uint8> ModelData;
FFileHelper::LoadFileToArray(ModelData, TEXT("Path/To/Model.onnx"));

// 3. 创建模型数据（编译过程会在编辑器或 cook 时触发）
TSharedPtr<UE::NNE::FSharedModelData> SharedData = Runtime->CreateModelData(
    TEXT("onnx"), ModelData, {}, FGuid::NewGuid(), nullptr);

// 4. 创建模型实例
TObjectPtr<UNNEModelData> DataObj = NewObject<UNNEModelData>();
DataObj->SetModelData(SharedData);
TSharedPtr<UE::NNE::IModelCPU> Model = Runtime->CreateModelCPU(DataObj);
TSharedPtr<UE::NNE::IModelInstanceCPU> Instance = Model->CreateModelInstanceCPU();

// 5. 设置输入形状并运行
TArray<UE::NNE::FTensorShape> InputShapes = { ... };
Instance->SetInputTensorShapes(InputShapes);
Instance->RunSync(InputBindings, OutputBindings);
```

**来源文件**: `Source/NNERuntimeIREE/Private/NNERuntimeIREE.h`、`Source/NNERuntimeIREE/Private/NNERuntimeIREEModel.h` 和内部测试用例。

### 进阶用法

#### GPU 推理（Vulkan / RDG）

IREE 同时支持通过 Vulkan 或 RDG 进行 GPU 推理。RDG 版本可以与 Unreal 的渲染管线深度融合，减少显存拷贝。以下示例展示 RDG 推理的基本流程：

```cpp
#include "NNERuntimeRDG.h"

// 获取 RDG 运行时（仅在支持 RDG 的平台上可用）
UNNERuntimeIREERdg* RDGRuntime = Cast<UNNERuntimeIREERdg>(
    GEngine->GetEngineSubsystem<UNNESubsystem>()->GetRuntime(UNNERuntimeIREERdg::GUID));

// 创建模型数据（RDG 编译产物包含着色器字节码）
TSharedPtr<UE::NNE::FSharedModelData> RDGData = RDGRuntime->CreateModelData(
    TEXT("onnx"), ModelData, {}, FGuid::NewGuid(), nullptr);

// 创建 RDG 模型实例
TSharedPtr<UE::NNE::IModelRDG> RDGModel = RDGRuntime->CreateModelRDG(DataObj);
TSharedPtr<UE::NNE::IModelInstanceRDG> RDGInstance = RDGModel->CreateModelInstanceRDG();

// 在渲染线程上 Enqueue 推理
RDGInstance->SetInputTensorShapes(InputShapes);
// ...
FRDGBuilder& GraphBuilder = ...;
RDGInstance->EnqueueRDG(GraphBuilder, InputBindings, OutputBindings);
```

**注意**: RDG 推理需要在渲染线程（RHI 线程）上下文中调用，并配合 `FRDGBuilder` 使用。

#### 多线程与任务拓扑配置

IREE 运行时支持通过开发者设置自定义线程亲和性。可在 `Project Settings → NNERuntimeIREE` 中配置编辑器模式与游戏模式下的线程选项：

```cpp
// 在代码中读取设置
const UNNERuntimeIREESettings* Settings = GetDefault<UNNERuntimeIREESettings>();
FNNERuntimeIREEThreadingOptions ThreadOptions = Settings->GameThreadingOptions;

// 自定义设置（运行时加载前）
UNNERuntimeIREESettings* MutableSettings = GetMutableDefault<UNNERuntimeIREESettings>();
MutableSettings->GameThreadingOptions.bIsSingleThreaded = false;
MutableSettings->GameThreadingOptions.TaskTopology.TaskTopologyGroups.Add({ /* affinity */ });
MutableSettings->SaveConfig();
```

## Demo 示例

以下是一个完整的、可编译的最小 C++ 示例，展示如何在游戏模块中使用 IREE 运行时进行 CPU 推理。该示例假设项目已启用 `NNERuntimeIREE` 和 `NNE` 插件。

### DemoGameModule.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "NNERuntimeIREE.h"
#include "NNETypes.h"
#include "Modules/ModuleInterface.h"

DECLARE_LOG_CATEGORY_EXTERN(LogDemoIREE, Log, All);

class FDemoGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    void RunInference();
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

### DemoGameModule.cpp

```cpp
#include "DemoGameModule.h"
#include "Misc/FileHelper.h"
#include "NNEModelData.h"
#include "NNESubsystem.h"

DEFINE_LOG_CATEGORY(LogDemoIREE);

void FDemoGameModule::StartupModule()
{
    // 延迟一帧执行，确保子系统已初始化
    FTSTicker::GetCoreTicker().AddTicker(
        FTickerDelegate::CreateLambda([this](float) -> bool
        {
            RunInference();
            return false;
        }), 1.0f);
}

void FDemoGameModule::ShutdownModule()
{
    ModelInstance.Reset();
}

void FDemoGameModule::RunInference()
{
    // 获取 IREE CPU 运行时
    UNNERuntimeIREECpu* Runtime = Cast<UNNERuntimeIREECpu>(
        GEngine->GetEngineSubsystem<UNNESubsystem>()->GetRuntime(UNNERuntimeIREECpu::GUID));
    if (!Runtime)
    {
        UE_LOG(LogDemoIREE, Error, TEXT("IREE CPU runtime not available."));
        return;
    }

    // 加载 ONNX 模型文件
    TArray64<uint8> ModelData;
    if (!FFileHelper::LoadFileToArray(ModelData, TEXT("Content/Models/SimpleModel.onnx")))
    {
        UE_LOG(LogDemoIREE, Error, TEXT("Failed to load model file."));
        return;
    }

    // 创建模型数据（编辑器下会触发编译）
    TSharedPtr<UE::NNE::FSharedModelData> SharedData =
        Runtime->CreateModelData(TEXT("onnx"), ModelData, {}, FGuid::NewGuid(), nullptr);
    if (!SharedData)
    {
        UE_LOG(LogDemoIREE, Error, TEXT("Failed to create model data."));
        return;
    }

    // 包装为 UNNEModelData
    UNNEModelData* DataObj = NewObject<UNNEModelData>();
    DataObj->SetModelData(SharedData);

    // 创建模型和实例
    TSharedPtr<UE::NNE::IModelCPU> Model = Runtime->CreateModelCPU(DataObj);
    if (!Model)
    {
        UE_LOG(LogDemoIREE, Error, TEXT("Failed to create model."));
        return;
    }

    ModelInstance = Model->CreateModelInstanceCPU();
    if (!ModelInstance)
    {
        UE_LOG(LogDemoIREE, Error, TEXT("Failed to create model instance."));
        return;
    }

    // 准备输入（假设模型有一个 1x3x224x224 的 float 输入）
    NNE::FTensorShape InputShape = NNE::FTensorShape::Make({1, 3, 224, 224});
    TArray<NNE::FTensorShape> InputShapes = {InputShape};
    auto Status = ModelInstance->SetInputTensorShapes(InputShapes);
    if (Status != NNE::IModelInstanceCPU::ESetInputTensorShapesStatus::Ok)
    {
        UE_LOG(LogDemoIREE, Error, TEXT("SetInputTensorShapes failed."));
        return;
    }

    // 创建绑定
    TArray<float> InputData(1 * 3 * 224 * 224, 0.5f);
    TArray<float> OutputData(/* 根据输出形状确定大小 */);
    NNE::FTensorBindingCPU InputBinding{InputData.GetData(), InputData.Num() * sizeof(float)};
    NNE::FTensorBindingCPU OutputBinding{OutputData.GetData(), OutputData.Num() * sizeof(float)};

    // 运行推理
    NNE::IModelInstanceCPU::ERunSyncStatus RunStatus =
        ModelInstance->RunSync(MakeArrayView(&InputBinding, 1), MakeArrayView(&OutputBinding, 1));
    if (RunStatus == NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
    {
        UE_LOG(LogDemoIREE, Log, TEXT("Inference successful!"));
    }
    else
    {
        UE_LOG(LogDemoIREE, Error, TEXT("Inference failed."));
    }
}

IMPLEMENT_MODULE(FDemoGameModule, DemoGame)
```

## 模块依赖

从各模块的 `Build.cs` 及代码引用推断，主要依赖如下（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `NNE` | 核心神经网络引擎接口定义 |
| `NNEUtils` | NNE 工具函数（如 TensorShape 构造） |
| `IREEUtils` | IREE C API 的 Unreal 封装 |
| `IREEDriverRDG` | IREE RDG 驱动程序（GPU 推理） |
| `RenderCore` | RDG 渲染依赖图支持 |
| `RHI` | 渲染硬件接口（GPU 推理时使用） |
| `Projects` | 插件加载与 IREE 动态库路径管理 |
| `DeveloperSettings` | 配置系统（线程选项等） |

**注意**: 若使用 CPU 推理，只需依赖 `NNE`、`NNEUtils`、`IREEUtils`；使用 RDG 推理需额外依赖 `IREEDriverRDG`、`RenderCore`、`RHI`。

## 维护状态

### 近期更新

- 2025-09-26 `e0d52775` — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac for RDG.
- 2025-09-24 `ca784fe6` — [NNE] NNERuntimeIREERdg always prefer wave32 to be consistent with used GPU profiles from IREE.
- 2025-09-24 `1dc2a8b6` — [NNE] NNERuntimeIREE fix typo in Linux build script.
- 2025-09-24 `08183aae` — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac.
- 2025-09-12 `f4a4fff3` — [NNE] NNERuntimeIREE fix onnx importer dependencies not staged for Engine installed build.

### 维护评价

该插件创建于 2025 年 9 月，属于全新功能，更新频率极高（几乎每天都有提交），修复 bug、改进平台兼容性、优化 GPU 配置等。目前处于实验性阶段（`IsExperimentalVersion=true`），但维护活跃，Epic 正在积极推进。已知限制：仅支持 Win64 (x64)、Mac、Linux，不支持 ARM64；GPU 推理目前依赖于 RDG 和 Vulkan；不支持 GPU 回退至 CPU 的混合执行。建议新项目在充分测试后使用，且注意未来 API 可能变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [NNE 官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/neural-network-engine-in-unreal-engine)