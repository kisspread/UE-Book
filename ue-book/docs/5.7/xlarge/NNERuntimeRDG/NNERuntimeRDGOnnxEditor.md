# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络运行时(RDG) |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（ONNX 解析/检查/形状推断库，HLSL 着色器，运行时数据模型） |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram), `NNERuntimeRDG` (RuntimeAndProgram), `NNERuntimeRDGData` (RuntimeAndProgram), `NNERuntimeRDGUtils` (EditorAndProgram), `NNERuntimeRDGOnnxEditor` (External), `NNERuntimeRDGOnnxruntimeEditor` (External), `NNERuntimeRDGProtobufEditor` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

`NNERuntimeRDG` 是 Unreal Engine 中 **神经网络推理 (NNE)** 框架的 RDG（渲染依赖图）实现。它利用 GPU 管线（通过 RDG 和 HLSL 着色器）高效执行 ONNX 模型。插件内含完整的 ONNX 协议缓冲区库和模型验证工具，支持在编辑器环境中加载、检查并运行 ONNX 模型。

主要解决：
- 将 ONNX 模型以 GPU 加速方式集成到 UE 项目中。
- 提供与 NNE API 兼容的运行时后端，支持模型的加载、形状推断和推理执行。
- 为编辑器提供模型验证和导入支持（通过 `NNERuntimeRDGOnnxEditor` 等第三方模块）。

## 使用场景

- 你需要使用预训练的 ONNX 模型（如图像分类、对象检测）在 UE 中实时运行推理 → 启用本插件并使用 NNE 的 C++ API。
- 你正在开发一个需要 AI 推理功能的游戏或仿真，且希望利用 GPU 性能 → `NNERuntimeRDG` 提供基于 RDG 的 GPU 执行路径。
- 你需要在编辑器中对 ONNX 模型进行语法检查、形状推断和调试 → 使用 `NNERuntimeRDGOnnxEditor` 提供的 ONNX 验证工具。

## 蓝图用法

本插件**不直接暴露蓝图可调用节点**。所有 NNERT 运行时操作必须通过 C++ 完成。蓝图用户需要封装一个 C++ `BlueprintFunctionLibrary` 来间接使用。

如果需要蓝图交互，建议创建一个继承 `UBlueprintFunctionLibrary` 的类，包装 `UNNEModelData` 和 `UNNERuntimeRDG` 的相关函数。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeRDG.h"          // 主运行时模块
#include "NNEModelData.h"           // 模型数据
#include "NNERuntimeRDGUtils.h"     // 工具函数
// 如果直接使用 ONNX 库（仅编辑器）
#include "onnx/checker.h"
#include "onnx/defs/schema.h"
```

### 基本用法

以下示例展示加载一个 ONNX 模型并运行推理（基于 `NNERuntimeRDG` 主模块，非第三方 ONNX 库）：

```cpp
// 假设已有模型字节数据
TArray<uint8> ModelData = /* 从文件或资源加载 */;

// 创建模型数据对象
UNNEModelData* ModelDataObj = NewObject<UNNEModelData>();
ModelDataObj->Init(ModelData);

// 获取 RDG 运行时
UNNERuntimeRDG* Runtime = NewObject<UNNERuntimeRDG>();
Runtime->Initialize();

// 创建推理会话
TUniquePtr<INNERuntimeRDGInferenceSession> Session = Runtime->CreateInferenceSession(ModelDataObj);

// 准备输入张量（以 float 为例）
TArray<float> InputData = { /* 输入数据 */ };
TArray<int32> InputShape = {1, 3, 224, 224}; // 例如 image

// 执行推理
TArray<float> OutputData;
TArray<int32> OutputShape;
Session->Run(InputData, InputShape, OutputData, OutputShape);
```

**文件来源**：`NNERuntimeRDG/Public/NNERuntimeRDG.h`、`NNERuntimeRDG/Public/NNERuntimeRDGInferenceSession.h`

### 进阶用法（ONNX 模型验证）

在编辑器模块中，可以使用 `NNERuntimeRDGOnnxEditor` 提供的 ONNX 检查器验证模型：

```cpp
#include "onnx/checker.h"
#include "onnx/common/status.h"

using namespace ONNX_NAMESPACE::checker;

// 加载 ONNX 模型 Proto
ModelProto model;
if (!ParseProtoFromBytes(&model, ModelBytes, ModelSize)) {
    // 解析失败
}

// 执行检查
CheckerContext ctx;
LexicalScopeContext lex_ctx;
try {
    CheckModel(model, ctx, lex_ctx);
    // 检查通过
} catch (const ValidationError& e) {
    UE_LOG(LogTemp, Error, TEXT("ONNX validation failed: %s"), UTF8_TO_TCHAR(e.what()));
}
```

## Demo 示例

完整的可编译示例需要参考 UE 官方 NNE 示例（位于 `Samples/NNE`）。这里提供最小化的 C++ 类头文件示例：

**MyNNEComponent.h**

```cpp
#pragma once
#include "Components/ActorComponent.h"
#include "NNERuntimeRDG.h"
#include "MyNNEComponent.generated.h"

UCLASS(ClassGroup=(NNE), meta=(BlueprintSpawnableComponent))
class UMyNNEComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="NNE")
    bool LoadModel(const TArray<uint8>& ModelData);

    UFUNCTION(BlueprintCallable, Category="NNE")
    bool RunInference(const TArray<float>& Input, TArray<float>& Output);

private:
    UNNEModelData* ModelDataObj;
    UNNERuntimeRDG* Runtime;
    TSharedPtr<INNERuntimeRDGInferenceSession> Session;
};
```

**MyNNEComponent.cpp**

```cpp
#include "MyNNEComponent.h"

bool UMyNNEComponent::LoadModel(const TArray<uint8>& ModelData)
{
    ModelDataObj = NewObject<UNNEModelData>(this);
    ModelDataObj->Init(ModelData);
    Runtime = NewObject<UNNERuntimeRDG>(this);
    Runtime->Initialize();
    Session = Runtime->CreateInferenceSession(ModelDataObj);
    return Session.IsValid();
}

bool UMyNNEComponent::RunInference(const TArray<float>& Input, TArray<float>& Output)
{
    if (!Session) return false;
    TArray<int32> Shape;
    // 假设输入为 1D 张量，长度即为数据个数
    Shape.Add(Input.Num());
    TArray<int32> OutShape;
    return Session->Run(Input, Shape, Output, OutShape);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心接口定义 |
| `NNEHlslShaders` | HLSL 着色器集合（用于 GPU 算子执行） |
| `NERuntimeRDGUtils` | 运行时工具函数（模型加载、内存管理等） |
| `RenderCore` | 渲染核心（RDG 依赖） |
| `RHI` | 硬件接口层（MetalRHI/VulkanRHI 等） |
| `Projects` | 插件加载系统 |
| `DeveloperSettings` | 开发者设置界面 |

**第三方依赖**（不直接暴露给用户）：
| 依赖 | 用途 |
|---|---|
| `NNERuntimeRDGOnnxEditor` | 编辑器下的 ONNX 模型解析与检查 |
| `NNERuntimeRDGOnnxruntimeEditor` | ONNX Runtime 编辑器集成（可选） |
| `NNERuntimeRDGProtobufEditor` | 编辑器下的 Protobuf 序列化支持 |

## 维护状态

### 近期更新

```
- 2025-07-24 2412ec9 调整 TArrayView/Invoke constexpr，修复 GetData 未定义行为，废弃数组 Alignment
- 2025-06-12 9ce28ae 更新数值限制为使用 std 库（解决新 Windows 编译问题）
- 2025-06-12 d9dba26 添加 NNERuntimeRDGHlsl arm64 支持
- 2025-06-03 d31855b 修复 libprotobuf-lite 构建脚本，添加 windows arm64 版本
- 2025-05-29 8cfef61 添加 Greater.h 包含（为即将到来的 TGreater 更改做准备）
```

### 维护评价

- **创建时间**：2025-05-29，不足 1 年。
- **近期更新频率**：每 2-3 周有提交，包含架构调整、平台支持增强和编译修复。
- **活跃度**：活跃维护。项目处于实验阶段，但提交频率表明团队正在积极开发。
- **已知问题/限制**：实验性标记，API 可能变化；目前仅支持部分 ONNX 算子；编辑器工具依赖第三方库。
- **推荐使用**：✅ 推荐用于需要 GPU 加速推理的 UE 项目。但需注意其为实验性功能，生产使用前应进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/neural-network-engine-in-unreal-engine/)（NNE 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Tests)（实验性目录下的测试）