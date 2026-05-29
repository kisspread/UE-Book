# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络RDG运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram), `NNERuntimeRDG` (RuntimeAndProgram), `NNERuntimeRDGData` (RuntimeAndProgram), `NNERuntimeRDGUtils` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-06 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

NNERuntimeRDG 是 UE5 神经网络引擎（NNE）的一个 GPU 后端运行时，利用 RDG（Render Dependency Graph）在 GPU 上执行神经网络推理。它通过 UE5 原生的渲染管线和 HLSL 着色器来实现神经网络算子，而非依赖第三方推理库（如 ONNX Runtime 或 DirectML）。

该插件的核心价值在于：
- **GPU 原生推理**：利用 UE5 的 RDG 框架调度神经网络计算到 GPU 上，复用引擎已有的渲染资源和管线
- **ONNX 模型支持**：内嵌 ONNX 库，支持加载和解析 ONNX 格式的神经网络模型
- **跨平台**：支持 Win64、Linux、Mac 平台
- **与其他 NNE 后端互斥可选**：与 NNERuntimeORTCpu（CPU 后端）、NNERuntimeDml（DirectML 后端）等并列，用户可按需启用

插件在创建时从 NNE 核心仓库拆分出来（commit `6a8af24f`），体现了 NNE 模块化设计——核心 API 与各运行时后端解耦。

## 使用场景

- 你需要在 UE5 项目中运行推理延迟敏感的神经网络模型 → 用 NNERuntimeRDG（GPU 加速）
- 你的目标平台是 Win64/Linux/Mac 且需要利用 GPU 进行神经网络推理 → 用此插件而非 ORTCpu
- 你需要加载 ONNX 格式模型并在游戏中实时推理（如风格迁移、物体检测等）→ 配合 NNE API 使用此运行时
- 你已有 HLSL 着色器知识，需要自定义或调试神经网络 GPU 计算流程 → 该插件直接使用 HLSL 着色器实现算子

## 蓝图用法

该插件作为 NNE 运行时后端注册，不直接暴露蓝图节点。实际的推理 API 通过 NNE 核心插件（`NNE`）的蓝图接口访问。选择 RDG 运行时后端是通过 NNE 的运行时注册机制自动完成的。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| NNE API 节点（来自 NNE 核心插件） | 加载模型、创建推理实例、运行推理 | `UNNEModelData`, `INNERuntime` |

### 使用示例（蓝图描述）

1. 在项目设置中启用 `NNERuntimeRDG` 插件
2. 导入 ONNX 模型资产到项目中
3. 使用 NNE 核心 API 的蓝图节点加载模型数据
4. NNE 框架会自动检测并选择可用的 RDG 运行时后端
5. 创建推理实例并执行推理，输入/输出通过 Tensor 数据传递

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeRDG.h"
#include "NNE.h"
#include "NNERuntime.h"
```

### 基本用法

该插件作为 NNE 后端运行时，通过 NNE 的运行时注册系统工作。以下为典型的 C++ 集成方式：

```cpp
// NNE 运行时注册机制（插件内部自动完成）
// 用户代码通过 NNE 核心 API 使用，RDG 运行时在后台被自动选择

// 1. 获取 NNE Runtime
TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime<INNERuntime>();

// 2. 从模型数据创建模型实例
TObjectPtr<UNNEModelData> ModelData = /* 从资产加载 */;
auto Model = Runtime->CreateModel(ModelData);

// 3. 创建推理实例
auto ModelInstance = Model->CreateModelInstance();

// 4. 设置输入 Tensor
TArray<float> InputData = { /* 神经网络输入数据 */ };
// 准备输入 Tensor 并绑定

// 5. 运行推理
// ModelInstance->RunSync() 或 RunAsync()

// 6. 获取输出
// 从输出 Tensor 读取推理结果
```

### 进阶用法

RDG 运行时内部使用 HLSL 着色器实现神经网络算子（在 `NNEHlslShaders` 模块中）。各模块协作关系：

- **NNERuntimeRDGData**：负责 ONNX 模型的加载、解析和转换
- **NNERuntimeRDG**：核心运行时，实现 NNE 的 `INNERuntime` 接口，将模型计算图映射到 RDG pass
- **NNEHlslShaders**：提供各个神经网络算子的 HLSL 着色器实现
- **NNERuntimeRDGUtils**：编辑器工具模块，提供模型导入和转换辅助功能

## Demo 示例

```cpp
// MyNNEComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NNE.h"
#include "NNERuntime.h"
#include "MyNNEComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyNNEComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyNNEComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    bool LoadAndRunModel(UObject* ModelDataAsset);

private:
    TWeakInterfacePtr<INNERuntime> Runtime;
};
```

```cpp
// MyNNEComponent.cpp
#include "MyNNEComponent.h"
#include "NNEModelData.h"

UMyNNEComponent::UMyNNEComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyNNEComponent::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取 NNE 运行时（RDG 后端会在插件启用时自动注册）
    Runtime = UE::NNE::GetRuntime<INNERuntime>();
    
    if (!Runtime.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("No NNE runtime available. Ensure NNERuntimeRDG plugin is enabled."));
    }
}

bool UMyNNEComponent::LoadAndRunModel(UObject* ModelDataAsset)
{
    if (!Runtime.IsValid())
    {
        return false;
    }

    // 从资产获取模型数据
    // UNNEModelData* ModelData = Cast<UNNEModelData>(ModelDataAsset);
    // auto Model = Runtime->CreateModel(ModelData);
    // ... 设置输入/输出并执行推理
    
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 核心 API 和运行时注册框架 |
| `MetalRHI` | Metal 渲染硬件接口（Mac 平台 RDG 执行） |
| `VulkanRHI` | Vulkan 渲染硬件接口（Linux 平台 RDG 执行） |
| `RenderCore` | RDG 框架核心（Render Dependency Graph） |
| `RHI` | 渲染硬件接口抽象层 |
| `protobuf` | ONNX 模型格式的序列化/反序列化 |

> **注意**：NNERuntimeRDG 模块依赖 `MetalRHI` 和 `VulkanRHI` 用于跨平台 GPU 计算；NNERuntimeRDGData 依赖内置的 ONNX 第三方库（`NNERuntimeRDGOnnxEditor`、`NNERuntimeRDGOnnxruntimeEditor`、`NNERuntimeRDGProtobufEditor`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的编译警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复32位/64位格式说明符与参数类型不匹配的问题 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一GPU空闲等待API，替换为SubmitAndBlockUntilGPUIdle |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移到UE_LOGF格式 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧版GPU性能分析相关宏 |

### 维护评价

NNERuntimeRDG 是一个**活跃维护中**的实验性插件：

- **创建时间**：2023 年 6 月，约 2 年历史
- **更新频率**：近期有稳定的维护性更新（2026 年 1-5 月多次提交），说明仍在持续维护
- **更新内容**：近期以编译警告修复、API 迁移、平台兼容性修复为主，属于工程健壮性维护
- **实验性标记**：`IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能发生变化
- **已知限制**：
  - 仅支持 Win64、Linux、Mac 平台
  - 作为实验性功能，不建议用于生产环境
  - GPU RDG 推理路径可能受限于特定的神经网络算子支持范围

**建议**：适合用于实验和原型验证。如果需要生产级神经网络推理，考虑同时关注 NNE 核心 API 的稳定性和其他后端（如 ORT CPU）的成熟度。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- [官方文档]()（暂无）
- NNE 核心插件：`Engine/Plugins/NNE`
- 其他 NNE 运行时后端：`Engine/Plugins/NNERuntimeORTCpu`、`Engine/Plugins/NNERuntimeDml`