# NNERuntimeBasicCpu

> Performant, cross-platform, CPU runtime for the NNE plugin that supports basic models.

| 属性 | 值 |
|---|---|
| 中文名 | NNE 基础 CPU 运行时 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python 模型导出脚本） |
| 模块 | `NNERuntimeBasicCpu` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeBasicCpu) | |

## 用途

NNERuntimeBasicCpu 是 NNE（Neural Network Engine）框架下的一个**轻量级 CPU 推理运行时**，专门针对简单的神经网络模型（如 MLP 多层感知机）进行优化。

该插件存在的核心目的是：
1. **统 MLDeformer 和 LearningAgents 等模块的自定义推理实现**，避免各模块重复造轮子
2. 提供一个**高性能、跨平台**的 CPU 推理引擎，最小化内存开销和计算开销
3. 支持自定义的 `.ubnne` 模型文件格式，可通过 Python 脚本从 PyTorch 模型导出

**关键限制**：这不是通用推理引擎，只支持基础的前馈网络结构（MLP、GRU、Memory Cell 等），不支持卷积网络、Transformer 等复杂架构。

## 使用场景

- 你在使用 **LearningAgents** 训练强化学习智能体，需要在运行时执行策略网络推理 → 用 NNERuntimeBasicCpu
- 你在使用 **MLDeformer** 进行基于机器学习的变形动画，需要轻量级 CPU 推理 → 用 NNERuntimeBasicCpu
- 你有一个简单的 MLP 模型（多层感知机），需要在游戏运行时进行推理，且追求最小的内存和计算开销 → 用 NNERuntimeBasicCpu
- 你需要在所有平台上（Windows、Linux、Console）运行同一个推理模型，不依赖平台特定的 ML 框架 → 用 NNERuntimeBasicCpu

**不适合的场景**：需要运行复杂深度学习模型（CNN、Transformer、LSTM 完整版等）→ 考虑使用其他 NNE Runtime（如 NNERuntimeRDG、NNEONNXRuntime 等）。

## 蓝图用法

此插件**没有暴露任何蓝图可调用函数**。它是一个纯 C++ 运行时，通过 NNE 框架的统一接口（`INNERuntime`、`INNERuntimeCPU`）被其他插件（如 MLDeformer、LearningAgents）间接使用。

要在蓝图中使用神经网络推理，应通过 LearningAgents 或其他上层插件提供的蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeBasicCpuBuilder.h"
#include "NNERuntimeBasicCpuModel.h"
```

### 基本用法：通过 FModelBuilder 构建模型

`FModelBuilder` 是该插件的核心 API，用于以编程方式构建神经网络模型结构，然后序列化为 `.ubnne` 文件数据。

```cpp
#include "NNERuntimeBasicCpuBuilder.h"

using namespace UE::NNE::RuntimeBasic;

// 创建一个模型构建器
FModelBuilder Builder(42);

// 构建一个简单的 3 层 MLP：输入128维 → 隐藏层256维 → 输出64维，使用 ReLU 激活
FModelBuilderElement MLP = Builder.MakeMLP(
    128,                                              // InputSize
    64,                                               // OutputSize
    256,                                              // HiddenSize
    3,                                                // LayerNum（包含输入层和输出层）
    FModelBuilder::EActivationFunction::ReLU,          // 激活函数
    false                                             // 最后一层不使用激活
);
```

### 进阶用法：构建带记忆的复杂模型

```cpp
#include "NNERuntimeBasicCpuBuilder.h"

using namespace UE::NNE::RuntimeBasic;

FModelBuilder Builder(12345);

// 构建一个带 GRU 记忆单元的网络
FModelBuilderElement GRUCell = Builder.MakeGRUCellLayer(
    32,   // 输入维度
    64    // 输出/记忆维度
);

// 构建一个 Memory Backbone（前缀处理 + 记忆单元 + 后缀处理）
FModelBuilderElement Prefix = Builder.MakeMLP(32, 64, 128, 3, FModelBuilder::EActivationFunction::ReLU);
FModelBuilderElement Postfix = Builder.MakeMLP(64, 16, 128, 3, FModelBuilder::EActivationFunction::ReLU);

FModelBuilderElement MemoryModel = Builder.MakeMemoryBackbone(
    64,         // MemoryNum - 记忆向量维度
    Prefix,     // 前缀处理层
    GRUCell,    // 记忆单元
    Postfix     // 后缀处理层
);
```

### 进阶用法：自定义层组合

```cpp
#include "NNERuntimeBasicCpuBuilder.h"

using namespace UE::NNE::RuntimeBasic;

FModelBuilder Builder;

// 手动构建一个自定义网络结构
FModelBuilderElement Layer1 = Builder.MakeLinearLayer(64, 128);
FModelBuilderElement Act1 = Builder.MakeReLU(128);
FModelBuilderElement Layer2 = Builder.MakeLinearLayer(128, 32);
FModelBuilderElement Act2 = Builder.MakeGELU(32);

// 将层按顺序组合成序列
FModelBuilderElement CustomModel = Builder.MakeSequence({Layer1, Act1, Layer2, Act2});

// 使用压缩线性层节省内存
FModelBuilderElement CompressedLayer = Builder.MakeCompressedLinear(
    64,                          // InputSize
    128,                         // OutputSize
    CompressedWeights,           // TConstArrayView<uint16>
    WeightOffsets,               // TConstArrayView<float>
    WeightScales,                // TConstArrayView<float>
    Biases                       // TConstArrayView<float>
);
```

### 进阶用法：通过 NNE 接口加载并运行模型

```cpp
#include "NNE.h"
#include "NNERuntimeBasicCpuModel.h"

// 通过 NNE 框架获取运行时
TArray<INNERuntime*> Runtimes = UE::NNE::Get()->GetAllRuntimes();
INNERuntimeCPU* BasicCPURuntime = nullptr;
for (INNERuntime* Runtime : Runtimes)
{
    if (Runtime->GetRuntimeName() == TEXT("NNERuntimeBasicCpu"))
    {
        BasicCPURuntime = static_cast<INNERuntimeCPU*>(Runtime);
        break;
    }
}

// 从 ModelData 创建模型
TSharedPtr<UE::NNE::IModelCPU> Model = BasicCPURuntime->CreateModelCPU(ModelData);

// 创建模型实例
TSharedPtr<UE::NNE::IModelInstanceCPU> Instance = Model->CreateModelInstanceCPU();

// 设置输入形状
TArray<UE::NNE::FTensorShape> InputShapes = {UE::NNE::FTensorShape::Make({1, 128})};
Instance->SetInputTensorShapes(InputShapes);

// 执行推理
TArray<float> InputData(128, 1.0f);
TArray<float> OutputData;
OutputData.SetNumZeroed(64);

TArray<UE::NNE::FTensorBindingCPU> InputBindings = {{InputData.GetData(), InputData.Num() * sizeof(float)}};
TArray<UE::NNE::FTensorBindingCPU> OutputBindings = {{OutputData.GetData(), OutputData.Num() * sizeof(float)}};

Instance->RunSync(InputBindings, OutputBindings);
```

## Demo 示例

### 构建并序列化一个 MLP 模型

```cpp
// MyMLPModelBuilder.h
#pragma once

#include "CoreMinimal.h"
#include "NNERuntimeBasicCpuBuilder.h"

class FMyMLPModelBuilder
{
public:
    /** 构建一个简单的 MLP 并获取序列化数据 */
    static TArray<uint8> BuildSimpleMLP()
    {
        using namespace UE::NNE::RuntimeBasic;
        
        FModelBuilder Builder(42);
        
        // 构建一个 3 层 MLP：8 → 16 → 4
        FModelBuilderElement MLP = Builder.MakeMLP(
            8,                                                  // InputSize
            4,                                                  // OutputSize
            16,                                                 // HiddenSize
            3,                                                  // LayerNum
            FModelBuilder::EActivationFunction::ReLU,           // 激活函数
            false                                               // 最后一层不使用激活
        );
        
        // 获取序列化所需的大小
        uint64 Size = 0;
        MLP.SerializationSize(Size);
        
        // 序列化到字节数组
        TArray<uint8> Data;
        Data.SetNumUninitialized(Size);
        uint64 Offset = 0;
        MLP.SerializationSave(Offset, Data);
        
        return Data;
    }
    
    /** 构建一个带归一化的 Skip MLP */
    static TArray<uint8> BuildSkipMLPWithNorm()
    {
        using namespace UE::NNE::RuntimeBasic;
        
        // 配置线性层使用 Kaiming 初始化
        FModelBuilder::FLinearLayerSettings Settings;
        Settings.Type = FModelBuilder::ELinearLayerType::Normal;
        Settings.WeightInitializationSettings.Type = FModelBuilder::EWeightInitializationType::KaimingGaussian;
        Settings.WeightInitializationSettings.Scale = 0.5f;
        
        FModelBuilder Builder;
        
        // 构建带 Skip 连接和 LayerNorm 的 MLP
        FModelBuilderElement Model = Builder.MakeSkipMLPWithLayerNorm(
            32,                                                  // InputSize
            8,                                                   // OutputSize
            64,                                                  // HiddenSize
            4,                                                   // LayerNum
            FModelBuilder::EActivationFunction::GELU,            // 激活函数
            false,                                               // 最后一层不使用激活
            Settings                                             // 线性层设置
        );
        
        // 序列化
        uint64 Size = 0;
        Model.SerializationSize(Size);
        TArray<uint8> Data;
        Data.SetNumUninitialized(Size);
        uint64 Offset = 0;
        Model.SerializationSave(Offset, Data);
        
        return Data;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine 核心框架，提供 `IModelCPU`、`IModelInstanceCPU` 等接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `825ce71c` | NNERuntimeBasicCpu: Some more minor optimizations | 继续进行小规模性能优化 |
| 2026-05-01 | `da0756fe` | NNERuntimeBasicCpu: Minor linear layer optimizations | 线性层计算的小幅优化 |
| 2026-04-27 | `f9c58df6` | NNERuntimeBasicCpu: Changed default weight init style to match PyTorch | 将默认权重初始化方式改为与 PyTorch 一致 |
| 2026-04-24 | `b899ef60` | NNERuntimeBasicCpu: Allowed MLP creation for single layer | 支持创建单层 MLP |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到 UE_LOGF 宏 |

### 维护评价

**活跃维护中** ⭐⭐⭐⭐

该插件近期（2026 年 4-5 月）有密集的更新活动，主要集中在：
1. **性能优化**：线性层和其他层的计算优化，表明 Epic 正在积极打磨推理性能
2. **兼容性改进**：将默认权重初始化与 PyTorch 对齐，说明正在改善与 Python 训练流程的兼容性
3. **功能完善**：支持单层 MLP 创建等边界情况

**注意事项**：
- 标记为 `IsExperimentalVersion=true`，API 可能在未来版本发生变化
- `EnabledByDefault=false`，需要手动在 .uproject 中启用
- 作为 LearningAgents 和 MLDeformer 的底层支撑，不太可能被废弃
- **推荐使用**：如果你的项目依赖 LearningAgents 或需要轻量级 CPU 推理，建议启用此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeBasicCpu)
- 官方文档（无）