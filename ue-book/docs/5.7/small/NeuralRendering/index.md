# Neural Rendering

> Enable neural rendering features including: neural post processing

| 属性 | 值 |
|---|---|
| 中文名 | 神经渲染 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NeuralPostProcessing` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NeuralRendering) | |

## 用途

该插件基于 [NNE（Neural Network Engine）](https://dev.epicgames.com/documentation/en-us/unreal-engine/nne-in-unreal-engine) 提供了 GPU 加速的**神经网络后处理**能力。它允许开发者将训练好的神经网络模型应用于屏幕后处理管线，实现传统后处理难以达到的视觉效果（例如基于深度学习的风格迁移、去噪、超分辨率等）。插件封装了模型加载、运行时管理、GPU 缓冲区创建及执行等底层细节，将神经网络推理无缝集成到延迟渲染的 RDG（Render Dependency Graph）中。

## 使用场景

- 制作基于 AI/ML 的实时后处理效果（如光流引导的插帧、基于深度学习的美化滤镜）
- 需要在不损失帧率的前提下将小尺寸输入（如低分辨率图）通过神经网络放大、修复，再合成到屏幕输出
- 探索实验性渲染功能，评估神经网络在现有渲染管线中的可行性

## 蓝图用法

该插件当前**未暴露任何蓝图可调用节点**。所有与模型实例的交互都需要在 C++ 中完成，并通过自定义材质函数/后期处理材质间接使用其结果。

## C++ 用法

### 头文件引入

```cpp
#include "NeuralPostProcessModelInstance.h"
```

### 基本用法

以下示例演示如何创建一个 `UNeuralPostProcessModelInstance`，加载模型数据并执行推理。

```cpp
// 创建一个模型数据资产（需提前准备 .onnx 文件并通过 UNNEModelData 导入）
UNNEModelData* ModelData = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/Models/MyModel.MyModel"));

// 创建实例（通常作为某个 Actor/Component 的成员）
UNeuralPostProcessModelInstance* PostProcessInstance = NewObject<UNeuralPostProcessModelInstance>(this);

// 更新模型（会检查是否需要重新创建内部模型实例）
FString RuntimeName = TEXT("NNERuntimeORTDml"); // 使用 DirectML 后端
PostProcessInstance->Update(ModelData, RuntimeName);

// 在渲染线程的 RDG Builder 中调用（例如在自定义 Scene ViewExtension 或 Post Process Pass）
FRDGBuilder& GraphBuilder = ...; // 已有的 GraphBuilder

PostProcessInstance->CreateRDGBuffers(GraphBuilder);          // 创建输入/输出 RDG 缓冲区
PostProcessInstance->Execute(GraphBuilder);                    // 执行神经网络推理

// 获取输出缓冲区以供后续着色器使用
FRDGBufferRef OutputBuffer = PostProcessInstance->GetOutputBuffer();
```

### 进阶用法

`UNeuralPostProcessModelInstance` 支持**分块处理（Tiling）**，允许模型在较小的输入尺寸下推理，由插件自动进行拼接和重叠区域的融合，以减少显存占用。

```cpp
// 设置分块参数
FIntPoint TileDim(256, 256);          // 每块大小
FIntPoint TileOverlap(32, 32);        // 重叠区域
PostProcessInstance->UpdateTileDimension(TileDim);
PostProcessInstance->UpdateTileOverlap(TileOverlap);
PostProcessInstance->UpdateModelTileType(ENeuralModelTileType::OverlapAndResolve);

// 创建带分块的缓冲区
PostProcessInstance->CreateRDGBuffersIfNeeded(GraphBuilder, true);
// 获取分块输出
FRDGBufferRef TiledOutput = PostProcessInstance->GetTiledOutputBuffer();
```

此外，插件的 shader 类（如 `FDownScaleTextureCS`、`FUpscaleTextureCS`）也可直接复用，以实现自定义的编解码或特征图处理。

## Demo 示例

以下是一个最小化的 C++ 类，展示如何在自定义的 `PostProcessPass` 中使用 Neural Rendering 插件。

```cpp
// NeuralPostProcessDemo.h
#pragma once
#include "CoreMinimal.h"
#include "PostProcess/PostProcessPass.h"
#include "NeuralPostProcessModelInstance.h"

class FNeuralPostProcessDemo : public ISceneViewExtension
{
public:
    FNeuralPostProcessDemo();
    virtual ~FNeuralPostProcessDemo() override;

    virtual void SetupViewFamily(FSceneViewFamily& InViewFamily) override {}
    virtual void SetupView(FSceneViewFamily& InViewFamily, FSceneView& InView) override {}
    virtual void BeginRenderViewFamily(FSceneViewFamily& InViewFamily) override;

    // 注册到渲染管线
    static void RegisterPass();
    static void UnregisterPass();

private:
    TStrongObjectPtr<UNeuralPostProcessModelInstance> ModelInstance;
};
```

```cpp
// NeuralPostProcessDemo.cpp
#include "NeuralPostProcessDemo.h"
#include "RenderGraphBuilder.h"
#include "ScreenPass.h"
#include "NNEModelData.h"

FNeuralPostProcessDemo* GDemo = nullptr;

FNeuralPostProcessDemo::FNeuralPostProcessDemo()
{
    // 创建模型实例
    ModelInstance = TStrongObjectPtr<UNeuralPostProcessModelInstance>(
        NewObject<UNeuralPostProcessModelInstance>());

    UNNEModelData* ModelData = LoadObject<UNNEModelData>(nullptr,
        TEXT("/Game/NeuralModels/MyStyleTransfer.MyStyleTransfer"));
    if (ModelData)
    {
        ModelInstance->Update(ModelData, TEXT("NNERuntimeORTDml"));
    }
}

FNeuralPostProcessDemo::~FNeuralPostProcessDemo()
{
    ModelInstance.Reset();
}

void FNeuralPostProcessDemo::BeginRenderViewFamily(FSceneViewFamily& InViewFamily)
{
    // 在渲染线程的 RDG 执行中加入自定义 Pass
    ENQUEUE_RENDER_COMMAND(NeuralPostProcess)(
        [this](FRHICommandListImmediate& RHICmdList)
        {
            FRDGBuilder GraphBuilder(RHICmdList);
            // 注意：这里需要从 ViewFamily 获取场景颜色等纹理
            // 示例简化，实际需集成到 PostProcess 管线中
            // ModelInstance->CreateRDGBuffers(GraphBuilder);
            // ModelInstance->Execute(GraphBuilder);
            GraphBuilder.Execute();
        });
}

void FNeuralPostProcessDemo::RegisterPass()
{
    if (!GDemo)
    {
        GDemo = new FNeuralPostProcessDemo();
        // 添加到 ViewExtension 列表（省略注册细节）
    }
}

void FNeuralPostProcessDemo::UnregisterPass()
{
    if (GDemo)
    {
        delete GDemo;
        GDemo = nullptr;
    }
}
```

**说明**：实际集成需要结合 UE 的后期处理框架（如 `FPostProcessPass` 或自定义 `IViewExtension`），此处仅展示核心流程。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNERuntimeORT` | 提供 ONNX Runtime 的 GPU 推理后端（DirectML） |
| `NNE` | 神经网络引擎核心库，负责模型加载与推理抽象 |
| `NNERuntimeRDG` | 将 NNE 推理与 Render Dependency Graph 集成 |
| `NNEModelData` | 模型数据资产类 |

> 注：`Core`、`CoreUObject`、`Engine`、`RenderCore` 等标准模块已省略。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 摘要 |
|---|---|---|
| 2025-09-12 | c392e3a1 | 修复 Debug 构建中为后处理材质分配神经配置时导致的 GPU 崩溃；停止…… |
| 2024-12-18 | 0af1d8de | 修复 `DECLARE_GPU_STAT` 在 `RHI_NEW_GPU_PROFILER=1` 时的用法 |
| 2024-09-02 | 9fb339dd | 修复 RDG GPU 统计宏以适应新的 GPU 分析器 |
| 2024-03-11 | d702a0b9 | [NNE] 切换到 NNERuntimeORTDml（RDG），即将删除 NNERuntimeRDGDml |
| 2024-02-13 | 39196f86 | 修复 DX11 下未指定 `CFLAG_AllowTypedUAVLoads` 导致的着色器编译错误 |

### 维护评价

- **创建时间**：2024-02-13，约 1.7 年
- **最近更新**：2025-09-12（3 个月前），表明仍在修复关键 bug 和适配新 API
- **维护活跃度**：中等，更新时间间隔不固定，但持续有功能性修复和迁移工作
- **已知限制**：
  - 高度实验性，API 可能不稳定
  - 仅支持 Win64/Linux/Mac 且需兼容 DX11/DX12/Vulkan 的 GPU 驱动
  - 无蓝图节点，需 C++ 深度集成
- **推荐度**：⚠️ 如果正在研发基于 AI 的后处理且愿意承担实验性风险，可使用；生产项目建议等待进一步稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NeuralRendering)
- [官方文档（NNE 概述）](https://dev.epicgames.com/documentation/en-us/unreal-engine/nne-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NeuralRendering/Source/NeuralPostProcessing/Private)