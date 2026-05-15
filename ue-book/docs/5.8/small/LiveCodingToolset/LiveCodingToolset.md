# LiveCodingToolset

> Live Coding compile toolset.

| 属性 | 值 |
|---|---|
| 中文名 | 实时编码工具集 |
| 分类 | Experimental/Toolsets |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveCodingToolset` (Editor), `LiveCodingToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset) | |

## 用途

这是一个面向 **AI 工具调用（MCP）** 的编辑器插件，将 UE5 的 Live Coding 编译功能封装为一个可被 AI 代理调用的工具。它解决的核心问题是：**让 AI 编码助手能够直接触发 Live Coding 编译并获取编译结果**（包括状态、输出、错误和警告）。

Live Coding 允许在编辑器运行时重新编译 C++ 代码而无需重启，本插件将这一能力暴露给 MCP 协议，使得 AI 驱动的工作流（如 Claude、Copilot 等 AI 工具）可以自动完成"修改代码 → 编译 → 检查结果"的循环。

插件通过 `ULiveCodingToolsetSubsystem` 编辑器子系统在编辑器生命周期内自动注册到 `UToolsetRegistry`，并可通过 `LiveCodingToolset.Enable` CVar 在运行时动态启用/禁用。

**使用前提**：
- 仅在编辑器中可用（EditorOnly）
- 目标平台必须支持 Live Coding（`Target.bWithLiveCoding` 为 true）
- 必须在编辑器偏好设置中启用 Live Coding

## 使用场景

- 你正在使用 AI 编码助手（如基于 MCP 协议的 AI 工具）进行 UE5 C++ 开发 → 用 LiveCodingToolset 让 AI 自动触发编译并获取错误信息
- 你需要在 AI 工作流中实现"修改-编译-验证"的自动化闭环 → 用本插件提供编译步骤
- 你正在构建自定义的 AI 辅助开发工具链 → 通过 `UToolsetRegistry` 集成本插件的编译能力

## 蓝图用法

本插件的核心函数标记为 `AICallable`（面向 AI 代理调用），但同样是标准的 `UFUNCTION`，可在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileLiveCoding` | 触发一次 Live Coding 编译并等待结果，返回包含编译状态和输出信息的字符串 | `ULiveCodingToolset` |

### 使用示例（蓝图描述）

1. 在蓝图中使用 **Call Function** 节点搜索 `Compile Live Coding`
2. 该函数为 `static`，无需实例对象，可直接调用
3. 返回值为 `FString`，格式为编译结果状态 + 编译器输出（错误、警告等）
4. 如果 Live Coding 未启用，返回描述性错误信息而非崩溃

典型调用流程：
- 节点：`CompileLiveCoding`（静态调用）
- 输出：连接到 **Print String** 或自定义解析逻辑
- 适用于工具脚本、自动化测试、AI 工作流集成

> **注意**：该函数会阻塞当前线程直到编译完成，编译期间从工作线程捕获的日志通过 `FCriticalSection` 保证线程安全。

## C++ 用法

### 头文件引入

```cpp
#include "LiveCodingToolset/LiveCodingToolset.h"
```

### 基本用法

触发一次 Live Coding 编译并获取结果：

```cpp
// 触发 Live Coding 编译并等待结果
FString Result = ULiveCodingToolset::CompileLiveCoding();

// 结果字符串包含编译状态和任何编译器输出（错误、警告等）
if (!Result.IsEmpty())
{
    UE_LOG(LogTemp, Log, TEXT("Live Coding 结果: %s"), *Result);
}
```

**注意**：返回非空字符串表示有输出信息（可能是成功日志或编译错误）。当目标平台不支持 Live Coding 时，函数会返回描述性错误信息。

### 进阶用法

通过子系统控制工具集的启用/禁用状态：

```cpp
#include "LiveCodingToolset/LiveCodingToolsetSubsystem.h"

// 获取子系统实例
ULiveCodingToolsetSubsystem* Subsystem = GEditor->GetEditorSubsystem<ULiveCodingToolsetSubsystem>();

if (Subsystem)
{
    // 运行时启用/禁用工具集（会注册/注销到 UToolsetRegistry）
    Subsystem->SetToolsetEnabled(true);   // 启用
    Subsystem->SetToolsetEnabled(false);  // 禁用
}
```

也可以通过控制台变量动态切换：

```ini
; 在控制台中输入
LiveCodingToolset.Enable 1   ; 启用
LiveCodingToolset.Enable 0   ; 禁用
```

## Demo 示例

### LiveCodingToolsetDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EditorSubsystem.h"
#include "LiveCodingToolsetDemo.generated.h"

/**
 * 演示如何使用 LiveCodingToolset 进行 AI 辅助编译工作流
 */
UCLASS()
class ULiveCodingToolsetDemoSubsystem : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    /** 演示编译调用 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    FString RunLiveCodingCompileDemo();
};
```

### LiveCodingToolsetDemo.cpp

```cpp
#include "LiveCodingToolsetDemo.h"
#include "LiveCodingToolset/LiveCodingToolset.h"
#include "LiveCodingToolset/LiveCodingToolsetSubsystem.h"
#include "Misc/OutputDeviceRedirector.h"

void ULiveCodingToolsetDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Log, TEXT("LiveCodingToolsetDemo 子系统已初始化"));
}

FString ULiveCodingToolsetDemoSubsystem::RunLiveCodingCompileDemo()
{
    UE_LOG(LogTemp, Log, TEXT("开始 Live Coding 编译演示..."));

    // 检查并确保工具集已启用
    ULiveCodingToolsetSubsystem* ToolsetSubsystem =
        GEditor->GetEditorSubsystem<ULiveCodingToolsetSubsystem>();

    if (ToolsetSubsystem)
    {
        // 确保工具集已注册
        ToolsetSubsystem->SetToolsetEnabled(true);
    }

    // 触发编译并等待结果
    FString CompileResult = ULiveCodingToolset::CompileLiveCoding();

    UE_LOG(LogTemp, Log, TEXT("编译完成，结果: %s"),
        CompileResult.IsEmpty() ? TEXT("(无输出)") : *CompileResult);

    return CompileResult;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | UE5 Live Coding 核心功能，提供运行时编译能力 |
| `ToolsetRegistry` | 插件级依赖，用于注册/管理 MCP 工具定义 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `0d1e3ace` | [LiveCodingToolset] Move the *Live Coding* *MCP* tool into a dedicated Engine plugin under `Engine/Plugins/Experimental/Toolsets/`. Adds LiveCodingToolset plugin… | 首次提交：将 Live Coding MCP 工具从原位置迁移到独立的实验性插件，完整实现编译、输出收集、线程安全和测试 |

### 维护评价

- **创建时间**：2026-04-23，非常新的插件
- **更新频率**：目前仅有一次初始提交
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标记为实验性
- **完整性**：首次提交即包含完整的实现、线程安全修复、UBT 日志隔离和 CQTest 测试模块，代码质量较高
- **推荐程度**：⚠️ **谨慎使用** — 作为实验性插件且仅有一次提交，API 可能发生较大变化。适合在 AI 工具集成开发中试用，但不建议在生产环境中依赖。该插件是 UE5 AI 工具链（MCP）生态的一部分，随着 AI 辅助开发功能的成熟，预计会有持续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset/Source/LiveCodingToolsetTests)