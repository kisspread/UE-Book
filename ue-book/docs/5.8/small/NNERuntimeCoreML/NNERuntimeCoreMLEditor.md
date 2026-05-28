# NNERuntimeCoreML

> CoreML backed runtime for the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | CoreML 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeCoreML` (Runtime), `NNERuntimeCoreMLEditor` (Editor), `NNERuntimeCoreMLUtils` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML) | |

## 用途

本插件为 UE5 的神经网络引擎（NNE）提供了基于 Apple CoreML 的推理后端。它解决了在 macOS / iOS 平台上利用 Apple 原生硬件加速（包括 CPU、GPU 及 Neural Engine）运行神经网络模型的需求。

与通用的 NNE 运行时（如 NNERuntimeONNX）不同，CoreML 运行时能够调用 Apple 自研的推理引擎，在 Apple 设备上获得更好的性能和功耗表现。该插件支持导入 `.mlmodelc` 编译模型以及 `.mlpackage` 包格式，在编辑器中提供模型导入工厂，运行时则将 NNE 的推理请求委托给 CoreML 执行。

**当前限制**（基于首次提交信息）：
- 初始版本仅支持 CPU 推理，后续版本扩展了更多硬件接口
- 仅支持 float 类型的 MultiArray 输入输出
- 实验性功能，API 可能发生变化

## 使用场景

- 你正在 macOS / iOS 平台上开发需要实时神经网络推理的游戏或应用 → 使用此插件获得 Apple 硬件加速
- 你有一个使用 Apple 生态工具链（Core ML Tools）训练并导出的 `.mlpackage` / `.mlmodelc` 模型 → 使用此插件在 UE5 中加载和运行
- 你需要在 Apple 设备上进行风格迁移、图像分类等 ML 任务并追求最佳性能 → 优先考虑 CoreML 运行时
- 你希望 NNE 自动选择平台最优运行时 → 启用此插件后，NNE 会将 CoreML 作为一个可选后端注册

## 蓝图用法

本插件主要通过 NNE 框架的统一接口使用，自身的 BlueprintCallable 节点较少。核心交互通过编辑器导入模型和 NNE 运行时接口完成。

### 核心节点

本插件的蓝图能力主要通过 NNE 框架间接暴露：

| 节点 | 说明 | 所在类 |
|---|---|---|
| 模型导入 | 在编辑器内容浏览器中拖入 `.mlmodelc` / `.mlpackage` 文件自动创建模型资产 | `UNNERuntimeCoreMLModelDataFactory` |

### 使用示例（蓝图描述）

1. **导入模型**：在 Content Browser 中直接拖入 CoreML 模型文件（`.mlmodelc` 或 `.mlpackage`），插件会自动识别并创建 NNE 模型数据资产
2. **运行推理**：通过 NNE 的标准 API（`UNNEModelData` → `INNERuntime` → `Run`）进行推理，无需关心底层是否使用 CoreML

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeCoreML/NNERuntimeCoreML.h"
```

### 基本用法

使用 NNE 统一接口，CoreML 运行时作为其中一个后端自动注册：

```cpp
#include "NNE.h"
#include "NNERuntimeCoreML/NNERuntimeCoreML.h"

// 获取 NNE Runtime，CoreML 运行时会在模块启动时自动注册
TArray<INNERuntime*> Runtimes = UE::NNE::GetAllRegisteredRuntimes();

// 查找 CoreML 运行时
INNERuntime* CoreMLRuntime = nullptr;
for (INNERuntime* Runtime : Runtimes)
{
    if (Runtime->GetName().Contains(TEXT("CoreML")))
    {
        CoreMLRuntime = Runtime;
        break;
    }
}
```

### 进阶用法

加载 CoreML 模型数据并创建模型实例进行推理：

```cpp
// 1. 加载已导入的模型资产
UNNEModelData* ModelData = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/Models/MyCoreMLModel"));

// 2. 通过 NNE 创建模型实例（CoreML 运行时会自动被选中）
TObjectPtr<UNNEModel> Model = UNNEModel::CreateModel(ModelData);

// 3. 设置输入输出 Tensor
TArray<float> InputData = { /* 输入数据 */ };
FNNEInferenceContext InferenceContext;
// ... 配置输入 Tensor ...

// 4. 执行推理
Model->Run(InferenceContext);
```

## Demo 示例

一个最小的运行时模型创建和推理示例：

```cpp
// MyMLActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "NNE.h"
#include "MyMLActor.generated.h"

UCLASS()
class AMyMLActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMLActor();

    UPROPERTY(EditAnywhere, Category = "ML")
    TObjectPtr<UNNEModelData> ModelData;

    void RunInference(const TArray<float>& Input, TArray<float>& Output);
};
```

```cpp
// MyMLActor.cpp
#include "MyMLActor.h"

AMyMLActor::AMyMLActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMLActor::RunInference(const TArray<float>& Input, TArray<float>& Output)
{
    if (!ModelData)
    {
        UE_LOG(LogTemp, Error, TEXT("ModelData is null"));
        return;
    }

    // NNE 框架会自动选择可用的运行时（在 macOS 上会优先选择 CoreML）
    // 实际推理代码请参考 NNE 官方文档和示例
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心框架，提供运行时接口和推理基础设施 |
| `CoreML` | Apple 原生 CoreML 框架（通过 Platform 第三方依赖引入） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新版 UE_LOGF 接口 |
| 2026-03-20 | `2724fcee` | [NNERuntimeCoreML] Fix output copy to use logical size from MLMultiArray shape | 修复输出数据拷贝使用 MLMultiArray 逻辑尺寸的问题 |
| 2026-02-09 | `7c2ef798` | [NNE] NNERuntimeCoreML add .mlpackage format support. | 新增 .mlpackage 格式模型支持 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复可移植工具链编译兼容性问题 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 进一步修复可移植工具链编译错误 |

### 维护评价

**活跃维护中** 🟢

- 插件创建于 2025 年 1 月，至今约 1 年，属于较新的实验性插件
- 最近 3 个月内有多次实质性功能更新（新增 `.mlpackage` 支持、修复输出拷贝 bug）
- 持续有编译兼容性和代码质量改进（工具链修复、日志宏迁移）
- 由 Epic Games 官方团队维护，跟进 NNE 框架的整体发展
- **注意事项**：插件标记为 `IsExperimentalVersion = true` 且默认未启用，API 和行为可能在后续版本中发生变化
- **推荐在 Apple 平台项目中尝试使用**，但暂不建议用于生产环境的稳定性关键路径

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [社区支持](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)