# Live Coding Toolset

> Live Coding compile toolset.

| 属性 | 值 |
|---|---|
| 中文名 | 实时编码工具集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveCodingToolset` (Editor), `LiveCodingToolsetTests` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset) | |

## 用途

该插件将 Unreal Engine 的 **Live Coding** 功能封装为一个 **工具集 (Toolset)**。其主要目的是通过 **MCP (Model Context Protocol)** 或其他 AI 工具链，使编译过程能够被程序化触发。它暴露了一个名为 `CompileLiveCoding` 的可调用函数，使得外部工具（如 AI 代码助手）能够请求并执行一次代码的热重载编译，从而实现自动化的“编码-编译-验证”循环。

它解决的问题是：在 AI 辅助开发的工作流中，缺乏一个标准化的接口来启动引擎的实时编译过程。

## 使用场景

-   **AI 辅助开发**：当使用 AI 工具（如 MCP 服务器）生成或修改 C++ 代码后，需要自动触发一次编译来验证代码的正确性。
-   **自动化构建流程**：集成到自定义的构建或部署脚本中，在特定事件发生时触发热重载。
-   **快速原型验证**：在迭代 UI 或逻辑时，通过外部命令快速编译并查看效果，无需手动切换到编辑器。

## 蓝图用法

该插件主要提供面向 MCP/AI 工具的函数接口，其核心功能并非设计为常规的蓝图节点。但其核心函数仍以 `UFUNCTION` 形式存在。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileLiveCoding` | 触发一次 Live Coding 编译。如果成功，返回空字符串；如果失败或平台不支持，则返回错误信息。 | `ULiveCodingToolset` (工具集定义) |

### 使用示例（蓝图描述）

该插件的功能主要通过 MCP 协议调用，而非直接在蓝图中使用。在蓝图中，可以通过获取 `ULiveCodingToolsetSubsystem` 子系统来间接访问其功能，但这通常不是推荐用法。

1.  **获取子系统**：使用 `Get Game Instance Subsystem` 节点，选择 `LiveCodingToolsetSubsystem` 类。
2.  **（理论上的）调用**：虽然存在子系统，但直接调用 `CompileLiveCoding` 的蓝图接口可能未完全暴露。更推荐通过 MCP 协议进行调用。

## C++ 用法

### 头文件引入

```cpp
#include "LiveCodingToolset.h"
#include "Subsystems/LiveCodingToolsetSubsystem.h"
```

### 基本用法

该插件的核心逻辑被包裹在 `WITH_LIVE_CODING` 预处理器宏中，因为它依赖于平台特定的 Live Coding 功能。在使用前应进行检查。

```cpp
// 示例：检查并触发 Live Coding 编译（来源：LiveCodingToolset.cpp 核心逻辑）
#if WITH_LIVE_CODING
    // 获取 Live Coding 子系统并调用编译
    if (ULiveCodingToolsetSubsystem* Subsystem = GEngine->GetEngineSubsystem<ULiveCodingToolsetSubsystem>())
    {
        // 实际调用工具集中的函数
        ULiveCodingToolset* Toolset = Subsystem->GetToolset();
        if (Toolset)
        {
            FString Result = Toolset->CompileLiveCoding();
            if (Result.IsEmpty())
            {
                UE_LOG(LogLiveCodingToolset, Log, TEXT("Live Coding compile triggered successfully."));
            }
            else
            {
                UE_LOG(LogLiveCodingToolset, Error, TEXT("Live Coding compile failed: %s"), *Result);
            }
        }
    }
#else
    UE_LOG(LogLiveCodingToolset, Warning, TEXT("Live Coding is not supported on this platform/target."));
#endif
```

### 进阶用法

了解 CVar 控制。该插件提供了一个 CVar 来全局启用或禁用该工具集。

```cpp
// 通过 CVar 控制工具集的启用状态（来源：LiveCodingToolsetSubsystem.cpp）
static TAutoConsoleVariable<bool> CVarEnableLiveCodingToolset(
    TEXT("LiveCodingToolset.Enable"),
    true, // 默认值
    TEXT("Enable or disable the Live Coding Toolset for MCP/AI calls."),
    ECVF_Default);

// 在代码中读取该 CVar 的值
bool bIsToolsetEnabled = CVarEnableLiveCodingToolset.GetValueOnGameThread();
```

## Demo 示例

一个最小的、验证插件子系统是否可用的示例。

```cpp
// LiveCodingToolsetDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "LiveCodingToolsetDemo.generated.h"

UCLASS()
class ULiveCodingToolsetDemoSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    
    void TestLiveCodingToolset();
};

// LiveCodingToolsetDemo.cpp
#include "LiveCodingToolsetDemo.h"
#include "Subsystems/LiveCodingToolsetSubsystem.h"
#include "LiveCodingToolset.h"

void ULiveCodingToolsetDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Log, TEXT("LiveCodingToolsetDemo Subsystem Initialized."));
}

void ULiveCodingToolsetDemoSubsystem::Deinitialize()
{
    UE_LOG(LogTemp, Log, TEXT("LiveCodingToolsetDemo Subsystem Deinitialized."));
    Super::Deinitialize();
}

void ULiveCodingToolsetDemoSubsystem::TestLiveCodingToolset()
{
    // 检查 LiveCodingToolset 子系统是否存在
    if (ULiveCodingToolsetSubsystem* LCSubsystem = GEngine->GetEngineSubsystem<ULiveCodingToolsetSubsystem>())
    {
        UE_LOG(LogTemp, Log, TEXT("LiveCodingToolsetSubsystem found. The toolset is registered."));
        // 在实际应用中，这里会通过 MCP 调用 CompileLiveCoding，而非直接 C++ 调用
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("LiveCodingToolsetSubsystem not found! Is the plugin enabled?"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | 提供底层的 Live Coding 编译引擎接口和功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `0d1e3ace` | [LiveCodingToolset] Move the *Live Coding* *MCP* tool into a dedicated Engine plugin under `Engine/Plugins/Experimental/Toolsets/`. | 首次提交，将 Live Coding 的 MCP 工具功能独立成一个实验性插件。 |

### 维护评价

该插件**刚刚创建（2026-04-23）**，目前仅有一次提交，属于**实验性功能**。
- **优点**：解决了 AI 工具链与引擎编译能力对接的实际问题，设计模式清晰（使用 Toolset 和子系统）。
- **风险**：作为实验性插件，API 和行为可能发生重大变化。目前功能较为单一。
- **建议**：如果您的工作流需要集成 AI 自动编译，可以尝试使用。但需关注其后续更新，并注意它**默认未启用** (`EnabledByDefault: false`)，需要在插件管理器中手动启用。在稳定的生产环境中使用需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset/Source/LiveCodingToolsetTests)