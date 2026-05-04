# LiveCodingToolset

> Live Coding compile toolset.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveCodingToolset` (Editor), `LiveCodingToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset) | |

## 用途

该插件为 Unreal Engine 的 **Live Coding** 功能提供了一个可编程的工具集接口。它的核心目的是将“触发 Live Coding 编译并获取结果”这一操作封装成一个可被 AI 助手（通过 `AICallable` 元数据）或自动化脚本调用的函数。这解决了在 AI 辅助开发或自动化流程中，需要实时编译代码并验证结果，但又无法直接操作编辑器 UI 的问题。它本质上是一个连接 Live Coding 系统与外部调用者（特别是 AI）的桥梁。

## 使用场景

- **AI 辅助开发**：当你正在使用一个 AI 助手（如基于 MCP 的工具）来修改 C++ 代码时，AI 可以在修改后自动调用此插件触发编译，并根据返回的编译状态和错误信息决定下一步操作（如修复错误）。
- **自动化测试与集成**：在持续集成（CI）或自动化测试流程中，需要验证代码修改是否能通过 Live Coding 编译，可以使用此插件作为编译步骤的调用接口。
- **自定义编辑器工具**：开发需要与 Live Coding 系统交互的自定义编辑器工具或脚本时，可以使用此插件提供的标准化接口。

## 蓝图用法

此插件主要面向 AI 和自动化调用，其核心函数通过 `AICallable` 元数据暴露，而非传统的蓝图节点。在蓝图中，它可能通过特定的 AI 工具调用节点来使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileLiveCoding` | 触发一次 Live Coding 编译并同步等待结果，返回包含编译状态和任何编译器输出（错误、警告等）的字符串。 | `ULiveCodingToolset` |

### 使用示例（蓝图描述）

在蓝图中，此函数通常不会直接拖拽使用。它被设计为由 AI 系统（如 `UToolsetRegistry` 管理的工具）调用。一个典型的 AI 工作流可能是：AI 修改了源代码文件 -> AI 调用 `CompileLiveCoding` 工具 -> 根据返回的字符串判断编译是否成功及错误详情 -> AI 决定下一步动作。

## C++ 用法

### 头文件引入

```cpp
#include "LiveCodingToolset.h"
```

### 基本用法

直接调用静态函数来触发编译并获取结果。调用前需确保 Live Coding 已在编辑器偏好设置中启用。

```cpp
// 触发 Live Coding 编译并获取结果
FString CompileResult = ULiveCodingToolset::CompileLiveCoding();

// 解析结果（示例）
if (CompileResult.Contains(TEXT("Succeeded")))
{
    UE_LOG(LogTemp, Log, TEXT("Live Coding compile succeeded!"));
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Live Coding compile failed. Output:\n%s"), *CompileResult);
}
```

### 进阶用法

通过 `ULiveCodingToolsetSubsystem` 管理工具集的注册状态。这允许在运行时动态启用或禁用此工具集。

```cpp
// 获取编辑器子系统
ULiveCodingToolsetSubsystem* Subsystem = GEditor->GetEditorSubsystem<ULiveCodingToolsetSubsystem>();
if (Subsystem)
{
    // 禁用工具集（从 ToolsetRegistry 中注销）
    Subsystem->SetToolsetEnabled(false);
    
    // ... 一些操作后 ...
    
    // 重新启用工具集
    Subsystem->SetToolsetEnabled(true);
}
```

## Demo 示例

以下是一个最小化的编辑器工具类示例，演示如何在 C++ 中调用 Live Coding 编译功能。

**MyEditorTool.h**
```cpp
// MyEditorTool.h
#pragma once

#include "CoreMinimal.h"

class FMyEditorTool
{
public:
    static void TriggerAndCheckLiveCoding();
};
```

**MyEditorTool.cpp**
```cpp
// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "LiveCodingToolset.h"
#include "Misc/MessageDialog.h"

void FMyEditorTool::TriggerAndCheckLiveCoding()
{
    // 调用 Live Coding 编译
    FString Result = ULiveCodingToolset::CompileLiveCoding();
    
    // 简单的结果检查与提示
    if (Result.Contains(TEXT("Succeeded")))
    {
        FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(TEXT("Live Coding 编译成功！")));
    }
    else
    {
        FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(FString::Printf(TEXT("Live Coding 编译失败。\n\n输出:\n%s"), *Result)));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 核心依赖，提供 Live Coding 编译功能的底层 API。 |
| `ToolsetRegistry` | 插件依赖，用于将本工具集注册到全局工具注册表中，供 AI 或其他系统发现和调用。 |

## 维护状态

### 近期更新

由于未提供具体的 Git 提交历史，无法列出近期更新记录。

### 维护评价

- **创建时间**：插件创建于 2024 年，相对年轻。
- **状态**：插件标记为 **实验性** (`IsExperimentalVersion: true`) 且 **默认未启用** (`EnabledByDefault: false`)，表明它仍处于早期开发或测试阶段，API 和功能可能发生变化。
- **维护活跃度**：无法从给定信息判断。作为实验性插件，其更新频率和稳定性可能不如正式插件。
- **推荐使用**：**谨慎使用**。适合在开发环境、实验性项目或 AI 工具链集成中尝试。不建议在需要高度稳定性的生产环境中依赖此插件。使用前请确认其与当前引擎版本的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset)