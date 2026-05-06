# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | NNE 运行时 IREE |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEUtils` (Runtime), `IREEDriverRDG` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREEShader` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕 (约 4 个月) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

---

## 用途

`NNERuntimeIREE` 是实验性的机器学习推理运行时代理，它利用 [IREE](https://iree.dev/)（基于 MLIR 和 LLVM 的编译框架）将 ONNX 神经网络模型直接编译为高度优化的 GPU 或 CPU 可执行代码（如计算着色器），从而在游戏运行时高效执行推理。它实现了 Unreal Engine 的 [Neural Network Engine (NNE)](https://docs.unrealengine.com/5.3/en-US/neural-network-engine-in-unreal-engine/) 接口。

**核心动机**：传统的方法使用 ONNX Runtime 等推理库，但往往依赖外部 DLL 且缺乏深度集成。IREE 将模型编译到 UE 原生的 RDG（Render Dependency Graph）上执行，无需额外运行时库，并且能利用 UE 的 GPU 渲染管线来加速推理，特别适合实时游戏场景。

该插件包含多个子模块：
- **IREEUtils**：提供与 IREE 工具链交互的辅助功能，如运行命令、导入 ONNX 模型到 MLIR、环境变量解析等。
- **IREEDriverRDG**：IREE 的 RDG 驱动，负责将编译后的模型通过 UE 的 RDG 执行。
- **NNERuntimeIREE**：核心 NNE 运行时实现，暴露 NNE API 供蓝图或 C++ 调用加载运行模型。
- **NNERuntimeIREEEditor**：编辑器扩展，用于在编辑器中管理模型和触发编译。
- **NNERuntimeIREEShader**：预编译的着色器和相关资源。

---

## 使用场景

- 你需要在游戏运行时使用神经网络进行实时推断（如人物姿态估计、超分辨率、图像分割）。
- 你的目标平台是 Win64（x86_64）或 Mac（Intel/Apple Silicon），并且希望避免引入 ONNX Runtime 的外部依赖。
- 你希望将模型编译为 UE 原生的 RDG 图，充分利用游戏主线程或渲染线程的 GPU 资源。
- 你正在开发基于 ML 的 NPC 决策、手势识别、或者需要离线训练后嵌入游戏的小型模型。

---

## 蓝图用法

> 目前公开的头文件仅包含 `IREEUtils` 模块的 C++ 实用函数，未提供 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 的节点。NNE 核心运行时（`NNERuntimeIREE`）尚未在源码中暴露蓝图可调用的 API，需要通过 C++ 扩展或后续版本。

| 蓝图节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 当前无公开蓝图节点 | - |

**提示**：你可以通过 C++ 编写 `UFunction` 包装来使用这个插件，然后在 Python/蓝图中间接调用。

---

## C++ 用法

### 头文件引入

```cpp
#include "IREEUtils.h"
#include "IREEUtilsLog.h"   // 可选，用于日志
```

### 基本用法

以下示例演示如何使用 `IREEUtils` 模块中的工具运行 IREE 命令行工具。

#### 运行一个外部命令（如 IREE 编译器）

```cpp
// 设置 IREE 编译器路径
FString IreeCompilerPath = TEXT("D:/tools/iree-compiler.exe");
FString Arguments = TEXT("--input=model.onnx --output=model.vmfb --iree-target-backend=llvm-cpu");
FString WorkingDir = TEXT("C:/MyModel");
// 捕获输出到日志文件
FString LogFile = TEXT("C:/MyModel/iree_compile.log");

// 执行命令（同步阻塞）
UE::IREEUtils::RunCommand(IreeCompilerPath, Arguments, WorkingDir, LogFile);
```

#### 解析 ONNX 模型并导入为 MLIR

假设你有一个 ONNX 模型的字节数组，希望借助 IREE 的导工具转成 MLIR 中间格式：

```cpp
// 假设已有 ONNX 文件内容
TArray64<uint8> OnnxData;
// ... load ONNX data ...

// 导入器命令（通常是 python 脚本或 iree-import-onnx）
FString ImporterCommand = TEXT("iree-import-onnx.exe");
FString ImporterArgs = TEXT("--output-format=mlir-text");

TArray64<uint8> OutMlirData;
FString ModelName = TEXT("my_model");
FString OutputDir = TEXT("C:/Temp/mlir_output");

bool bSuccess = UE::IREEUtils::ImportOnnx(
    ImporterCommand,
    ImporterArgs,
    MakeArrayView(OnnxData),
    ModelName,
    OutputDir,
    OutMlirData
);

if (bSuccess)
{
    // 生成的 MLIR 数据在 OutMlirData 中
    // 可以继续通过 NNERuntimeIREE 加载该 MLIR
}
```

### 环境变量处理

在路径字符串中常常包含 `%VAR%` 形式的转义，使用 `ResolveEnvironmentVariables` 可以展开：

```cpp
FString Path = TEXT("%IREE_TOOLS%/iree-compile.exe");
UE::IREEUtils::ResolveEnvironmentVariables(Path);
// Path 变为实际路径，例如 "C:/Tools/IREE/bin/iree-compile.exe"
```

---

## Demo 示例

一个最小完整示例：编译一个 ONNX 模型并执行推理。该示例只使用 `IREEUtils` 执行编译命令，不涉及完整 NNE 运行时（后者需要更多初始化和模型加载）。

### MyIREEHelper.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FMyIREEHelper
{
public:
    static bool CompileOnnxModel(const FString& OnnxPath, const FString& OutputVmfbPath);
};
```

### MyIREEHelper.cpp

```cpp
#include "MyIREEHelper.h"
#include "IREEUtils.h"

bool FMyIREEHelper::CompileOnnxModel(const FString& OnnxPath, const FString& OutputVmfbPath)
{
    // 假设 iree-compile 在 PATH 或已知位置
    FString Command = TEXT("iree-compile");
    FString Arguments = FString::Printf(TEXT(
        "--iree-input-type=onnx "
        "--iree-hal-target-backends=vulkan-spirv "
        "--o \"%s\" \"%s\""
    ), *OutputVmfbPath, *OnnxPath);

    FString WorkingDir = FPaths::GetPath(OnnxPath);
    FString LogFile = FPaths::ChangeExtension(OutputVmfbPath, TEXT(".log"));

    UE::IREEUtils::RunCommand(Command, Arguments, WorkingDir, LogFile);

    // 简单检查输出文件是否存在
    return FPaths::FileExists(OutputVmfbPath);
}
```

在游戏模块的 `StartupModule()` 中可调用：

```cpp
FMyIREEHelper::CompileOnnxModel(TEXT("Content/Model/model.onnx"), TEXT("Saved/Compiled/model.vmfb"));
```

---

## 模块依赖

（根据 `IREEUtils.Build.cs` 和 `NNERuntimeIREE.Build.cs` 推断，未提供源码时基于常见依赖）

| 模块 | 用途 |
|---|---|
| `IREE` (ThirdParty) | IREE 编译器和运行时库的 C++ 绑定 |
| `NNEMlirTools` (ThirdParty) | MLIR 工具，用于模型导入 |
| `RHI` | GPU 资源创建与绑定（`IREEDriverRDG` 需要） |
| `RenderCore` | RDG 执行基础设施 |
| `Projects` | 加载 ThirdParty 插件 |
| `NNE` | NNE 运行时抽象接口（`NNERuntimeIREE` 需要） |

> **注意**：`IREEUtils` 自身只依赖 `Core`、`CoreUObject`、`Engine`、`IREE` 和 `Projects`，但它在运行时依赖 `iree-compile`、`iree-import-onnx` 等外部工具（需要在系统 PATH 或通过环境变量指定）。

---

## 维护状态

### 近期更新（基于提供的 git log）

```
- 2025-09-26  e0d52775 — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac for RDG.
- 2025-09-24  ca784fe6 — [NNE] NNERuntimeIREERdg always prefer wave32 to be consistent with used GPU profiles from IREE.
- 2025-09-24  1dc2a8b6 — [NNE] NNERuntimeIREE fix typo in Linux build script.
- 2025-09-24  08183aae — [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac.
- 2025-09-12  f4a4fff3 — [NNE] NNERuntimeIREE fix onnx importer dependencies not staged for Engine installed build.
```

日志显示该插件在 9 月中旬至下旬密集更新，修复了 Mac 下的路径空格问题、GPU 事件选择、Linux 构建脚本错误以及打包依赖问题。均为工程实践中的稳定性和兼容性修复。

### 维护评价

- **创建时间**：2025-09-12，距今约 4 个月，属于非常新的插件。
- **最近更新**：上一周仍有提交，活跃度很高。
- **活跃维护**：团队持续修复跨平台和性能问题，预计后续会有更多功能迭代。
- **实验性**：标记为 Experimental，API 和架构可能变动。
- **推荐使用**：适合探索性项目或对最新 ML 推理集成感兴趣的团队；不建议用于正式产品直到稳定版发布。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [IREE 官方文档](https://iree.dev/)
- [Unreal Engine Neural Network Engine (NNE) 文档](https://docs.unrealengine.com/5.3/en-US/neural-network-engine-in-unreal-engine/)
- [测试用例 (推测目录)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE/Tests) **未提供，需在源码中查找**