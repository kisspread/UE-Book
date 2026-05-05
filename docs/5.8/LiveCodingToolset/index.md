# LiveCodingToolset

> Live Coding compile toolset.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveCodingToolset` (Editor), `LiveCodingToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset) | |

## 用途

该插件是 Unreal Engine **Live Coding（实时编码）** 功能的配套工具集。它并非 Live Coding 的核心实现，而是为其提供辅助工具和扩展能力。其主要目的是为开发者在使用 Live Coding 进行热重载时，提供额外的编译控制、状态监控或调试支持，从而优化实时编码的工作流。它依赖于 `ToolsetRegistry` 插件来注册和管理这些工具。

## 使用场景

- 你正在使用 UE5 的 Live Coding 功能进行 C++ 代码的实时编译和热重载，并希望获得更精细的编译过程控制或状态反馈。
- 你需要为 Live Coding 流程开发自定义的工具或扩展，并希望通过一个标准的工具集框架来集成它们。
- 你正在编写或测试与 Live Coding 相关的编辑器功能，需要一个独立的、实验性的模块来承载这些代码。

## 蓝图用法

该插件主要面向 C++ 开发，其核心功能（如工具注册）通常在编辑器启动时通过 C++ 代码完成。目前未发现暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 接口。其使用和配置主要在 C++ 层面进行。

## C++ 用法

### 头文件引入

```cpp
#include "LiveCodingToolset.h"
```

### 基本用法

该插件的核心是通过 `ToolsetRegistry` 注册 Live Coding 相关的工具。以下是一个概念性示例，展示了如何注册一个自定义的 Live Coding 工具（具体实现需参考插件内部逻辑）。

```cpp
// 假设在某个 Editor 模块的启动函数中
#include "ToolsetRegistry.h"
#include "LiveCodingToolset.h"

void FMyEditorModule::StartupModule()
{
    // 获取工具集注册表
    IToolsetRegistry& ToolsetRegistry = IToolsetRegistry::Get();

    // 注册一个与 Live Coding 相关的工具
    // 具体的工具类需要实现 IToolsetTool 接口
    ToolsetRegistry.RegisterTool<FLiveCodingToolsetModule>(
        TEXT("MyLiveCodingHelper"),
        MakeUnique<FMyLiveCodingTool>()
    );
}
```

### 进阶用法

结合 `LiveCodingToolsetTests` 模块的测试用例，可以了解该插件如何被验证和使用。测试通常会模拟 Live Coding 的编译过程，并验证工具集是否按预期工作。

## Demo 示例

以下是一个最小化的示例，展示如何创建一个依赖于 `LiveCodingToolset` 的编辑器模块，并注册一个简单的工具。

**MyLiveCodingTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ToolsetRegistry/ToolsetTool.h"

class FMyLiveCodingTool : public IToolsetTool
{
public:
    virtual ~FMyLiveCodingTool() = default;

    // IToolsetTool 接口实现
    virtual void Activate() override;
    virtual void Deactivate() override;
    virtual bool CanActivate() const override;
};
```

**MyLiveCodingTool.cpp**
```cpp
#include "MyLiveCodingTool.h"

void FMyLiveCodingTool::Activate()
{
    UE_LOG(LogTemp, Log, TEXT("My Live Coding Tool Activated!"));
    // 在此处添加工具激活时的逻辑，例如监听编译事件
}

void FMyLiveCodingTool::Deactivate()
{
    UE_LOG(LogTemp, Log, TEXT("My Live Coding Tool Deactivated!"));
    // 清理工作
}

bool FMyLiveCodingTool::CanActivate() const
{
    // 可以在此检查 Live Coding 是否可用等条件
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | Live Coding 功能的核心模块，本插件为其提供扩展工具。 |
| `ToolsetRegistry` | 工具集注册表插件，用于管理本插件提供的工具。 |

## 维护状态

### 近期更新

（由于插件为实验性且创建时间较近，暂无历史提交记录可供分析。）

### 维护评价

- **实验性插件**：该插件被明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明它处于早期开发阶段，API 和功能可能不稳定，不建议在生产项目中直接依赖。
- **创建时间**：插件创建于 2026 年，非常新，属于实验性探索阶段。
- **维护状态**：作为实验性插件，其维护状态和未来路线图尚不明确。它可能随着 Live Coding 功能的演进而更新，也可能被合并或废弃。
- **推荐使用**：仅推荐给希望研究或扩展 UE5 Live Coding 内部机制的高级开发者。对于普通项目，应使用引擎内置的 Live Coding 功能，而无需启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset/Source/LiveCodingToolsetTests)