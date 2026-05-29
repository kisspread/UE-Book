# IREEUtils

> IREE 工具函数库

| 属性 | 值 |
|---|---|
| 中文名 | IREE 工具库 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEUtils` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE/Source/IREEUtils) | |

## 用途

`IREEUtils` 是 `NNERuntimeIREE` 插件的核心支撑模块，提供了一系列底层的工具函数。它解决了在集成 IREE（一个基于 MLIR 和 LLVM 的神经网络编译器）时所需的通用操作问题，包括：
- **路径与环境解析**：解析 SDK 路径和环境变量，确保编译工具链能正确找到 IREE 相关的外部程序。
- **进程管理**：启动并运行外部命令行工具（如 IREE 的编译器）。
- **模型转换**：将 ONNX 格式的神经网络模型导入并转换为 IREE 可使用的 MLIR 中间表示。
- **文件校验**：通过计算文件的哈希值（MD5）来实现缓存或版本校验，避免不必要的重复编译。

简而言之，它为 `NNERuntimeIREE` 主模块处理模型编译和准备的“脏活累活”提供了可靠的基础设施。

## 使用场景

- **当你需要将 ONNX 模型编译成可在 UE 中高效运行的代码时**：`IREEUtils` 模块负责调用 IREE 编译器工具链，并处理输入输出文件。
- **当你需要确保构建环境（如 SDK 路径）正确配置时**：可以使用路径解析函数来定位 IREE 相关的工具和库。
- **当插件或工具需要对资源文件（如模型、配置文件）进行缓存或变更检查时**：文件哈希函数为此提供了基础支持。

## 蓝图用法

该模块主要为底层 C++ 逻辑服务，提供的函数均为 `IREEUTILS_API` 导出，但并未发现标记为 `BlueprintCallable` 的公开蓝图节点。其功能通常由更高层的 `NNERuntimeIREE` 模块在内部调用，以完成模型编译和资源管理的流程。

## C++ 用法

### 头文件引入

```cpp
#include "IREEUtils/Internal/IREEUtils.h"
```

### 基本用法

以下示例展示了如何使用 `IREEUtils` 提供的核心功能：

1.  **解析 SDK 路径和环境变量**
    ```cpp
    #include "IREEUtils/Internal/IREEUtils.h"
    #include "Misc/Paths.h"

    // 解析一个包含环境变量和特殊路径标记的字符串
    FString RawPath = TEXT("${MY_SDK_DIR}/iree/tools/iree-compile");
    if (UE::IREEUtils::ResolveEnvironmentVariables(RawPath) && UE::IREEUtils::ResolveSdkPaths(RawPath))
    {
        // 此时 RawPath 已被替换为完整的、有效的文件系统路径
        UE_LOG(LogTemp, Log, TEXT("Resolved IREE Compiler Path: %s"), *RawPath);
    }
    ```

2.  **运行外部命令**
    ```cpp
    // 假设已通过上面的函数解析出 CompilerPath
    FString CompilerPath = TEXT("...");
    FString Arguments = TEXT("--iree-hal-target-backends=cpu --mlir-print-ir-after-all");
    FString WorkingDir = FPaths::ProjectDir();
    FString LogFile = FPaths::ProjectLogDir() / TEXT("IREECompile.log");

    // 同步执行编译命令，并将日志输出到文件
    UE::IREEUtils::RunCommand(CompilerPath, Arguments, WorkingDir, LogFile);
    ```

3.  **哈希文件以实现缓存**
    ```cpp
    FMD5 ModelHash;
    const FString ModelPath = FPaths::ProjectContentDir() / TEXT("MyModel.onnx");

    // 方法一：哈希文件内容（准确但可能较慢）
    if (UE::IREEUtils::HashAppendFile(ModelHash, ModelPath))
    {
        // 将哈希值转换为十六进制字符串用于比较
        uint8 Digest[16];
        ModelHash.Final(Digest);
        FString HashString = BytesToHex(Digest, 16);
        UE_LOG(LogTemp, Log, TEXT("Model content hash: %s"), *HashString);
    }

    // 方法二：哈希文件状态（修改时间和大小，快速）
    FMD5 ModelStatHash;
    if (UE::IREEUtils::HashAppendFileStat(ModelStatHash, ModelPath))
    {
        // ... 类似处理，通常用于快速检查文件是否被修改
    }
    ```

### 进阶用法

这些工具函数通常组合使用，构成一个完整的模型编译工作流。一个典型的流程可能如下：

1.  解析并验证 IREE 编译器和导入工具的路径。
2.  读取原始的 `.onnx` 模型文件数据。
3.  调用 `ImportOnnx` 将 ONNX 模型转换为 IREE 的 MLIR 表示（`.mlir` 文件）。
4.  使用 `RunCommand` 调用 IREE 编译器，将 `.mlir` 文件编译为特定后端（如 CPU、GPU）可执行的 `.vmfb` 文件。
5.  在整个过程中，可以使用哈希函数对输入模型文件进行校验，或者对编译产物进行缓存判断，避免重复劳动。

## Demo 示例

一个使用 `IREEUtils` 辅助完成简单模型处理的控制台命令示例。

**IREEUtilsDemoCommand.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ConsoleCommand.h"

class FIREEUtilsDemoCommand : public FConsoleCommand
{
public:
    FIREEUtilsDemoCommand();
    virtual ~FIREEUtilsDemoCommand() = default;
    virtual void Execute(const TArray<FString>& Args, UWorld* InWorld) override;
};
```

**IREEUtilsDemoCommand.cpp**
```cpp
#include "IREEUtilsDemoCommand.h"
#include "IREEUtils/Internal/IREEUtils.h"
#include "HAL/FileManager.h"

FIREEUtilsDemoCommand::FIREEUtilsDemoCommand()
{
    // 注册一个控制台命令，例如 “IREEUtils.Demo”
}

void FIREEUtilsDemoCommand::Execute(const TArray<FString>& Args, UWorld* InWorld)
{
    // 1. 模拟一个需要解析的包含环境变量的工具路径
    FString ImporterPath = TEXT("${IREE_TOOLS_DIR}/iree-import-onnx");
    if (!UE::IREEUtils::ResolveEnvironmentVariables(ImporterPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to resolve IREE tools environment variable."));
        return;
    }

    // 2. 模拟读取一个 ONNX 文件（这里用一个虚拟的数据源）
    TArray64<uint8> OnnxData;
    OnnxData.Add(0x08); // 占位数据，实际应从文件读取

    // 3. 定义输出目录和模型名
    FString OutputDir = FPaths::ProjectSavedDir() / TEXT("IREECache");
    FString ModelName = TEXT("SimpleModel");
    IFileManager::Get().MakeDirectory(*OutputDir, true);

    // 4. 调用导入函数
    TArray64<uint8> MlirData;
    FString ImporterArgs = TEXT("--some-importer-flag");
    bool bSuccess = UE::IREEUtils::ImportOnnx(
        ImporterPath,
        ImporterArgs,
        OnnxData,
        ModelName,
        OutputDir,
        MlirData
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully imported ONNX to MLIR. Output data size: %lld bytes"), MlirData.Num());
        // 此处可以进一步使用 MlirData 或将其保存为文件
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("ONNX import failed."));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库，提供基础类型、文件操作、日志等。 |

该模块的依赖非常基础，主要依赖 UE 核心的 `Core` 模块，用于文件 I/O、路径操作、进程管理和日志记录。其自身不依赖 NNE 或其他运行时模块，是一个独立的工具库。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复了 RDG 驱动模块在着色器编译期间的跨线程资源使用后释放问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了 64 位环境下日志格式说明符的匹配错误。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构了 GPU 命令提交接口，简化了等待 GPU 空闲的逻辑。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 `UE_LOGF` 格式。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 优化了着色器任务结构的内存管理。 |

### 维护评价

- **年龄**：创建于 2023 年 11 月，插件整体较为年轻（约 2 年）。
- **活跃度**：从 git 历史看，该插件（包括其子模块）在 2026 年 4 月至 5 月仍有密集的提交，涉及安全修复、代码规范化、API 重构和性能优化。这表明插件处于**非常活跃**的开发和维护阶段。
- **稳定性**：存在已知问题（如跨线程安全）但已被修复。作为实验性功能，其 API 和实现细节可能会发生变化。
- **推荐度**：该插件代表了 UE 在机器学习推理方向的前沿探索（基于 LLVM/MLIR），对于有高性能、跨平台神经网络推理需求的项目，尤其是在 CPU 后端上，**值得密切关注和评估**。但由于其`实验性`标签和快速的迭代节奏，在生产环境中使用需谨慎，并准备好跟进版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE/Source/IREEUtils)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE/Tests)（插件级别测试）