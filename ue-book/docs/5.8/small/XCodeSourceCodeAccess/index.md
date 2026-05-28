# XCode Integration

> Allows access to source code in XCode.

| 属性 | 值 |
|---|---|
| 中文名 | XCode 集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `XCodeSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2014-04-23 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/XCodeSourceCodeAccess) | |

## 用途

此插件为 Unreal Engine 编辑器（UnrealFrontend、UnrealInsights）提供了与 macOS 平台上 Xcode IDE 集成的能力。它实现了一个 `ISourceCodeAccessor` 接口，允许编辑器在代码编译错误、断点调试或主动请求时，能够自动在 Xcode 中打开对应的源代码文件并定位到指定行。它解决了 UE 编辑器与 Xcode 之间的代码导航问题，使得 macOS 用户的开发工作流更加顺畅。

## 使用场景

- 你是一名在 macOS 上使用 Xcode 作为主要 IDE 进行 Unreal Engine 项目开发的程序员。
- 当你在 UE 编辑器中遇到编译错误并希望快速查看和修改源代码时，双击错误信息可以直接跳转到 Xcode 中对应的代码行。
- 你希望通过 Unreal Insights 或 Unreal Frontend 等工具分析项目性能，并能快速从分析数据跳转到相关的源代码位置。

## 蓝图用法

此插件不提供任何蓝图可调用的函数或属性。其功能完全在编辑器底层（C++）实现，为上层编辑器 UI（如错误列表、调试器）提供基础能力。

## C++ 用法

### 头文件引入

```cpp
#include "ISourceCodeAccessModule.h"
#include "ISourceCodeAccessor.h"
```

### 基本用法

此插件的核心是实现了 `ISourceCodeAccessor` 接口。通常，开发者无需直接使用此接口，编辑器内部会根据用户设置自动调用。但如果你需要编写自定义的开发工具并希望集成 Xcode，可以手动获取并使用这个访问器。

```cpp
// 来自 Editor/SourceCodeAccess 模块的公共 API
#include "ISourceCodeAccessModule.h"

// 获取当前激活的源代码访问器（在 macOS 上，通常就是 XCodeSourceCodeAccessor）
if (ISourceCodeAccessModule* SourceCodeAccessModule = FModuleManager::GetModulePtr<ISourceCodeAccessModule>(TEXT("SourceCodeAccess")))
{
    ISourceCodeAccessor& Accessor = SourceCodeAccessModule->GetAccessor();

    // 检查是否为 Xcode 访问器
    if (Accessor.GetFName() == FName(TEXT("XCodeSourceCodeAccessor")))
    {
        // 打开指定文件并跳转到某一行
        FString SourceFile = TEXT("/Path/To/Your/SourceFile.cpp");
        int32 LineNumber = 42;
        Accessor.OpenFileAtLine(SourceFile, LineNumber);
    }
}
```

### 进阶用法

结合插件的模块生命周期，可以在插件启动时注册自定义行为，但通常不建议覆盖此插件的功能。

## Demo 示例

这是一个简单的 Actor，其构造函数中尝试通过源代码访问器打开自身头文件。**注意：此功能需要在 macOS 上运行编辑器才能正常工作。**

```cpp
// MyXCodeTestActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyXCodeTestActor.generated.h"

UCLASS()
class AMyXCodeTestActor : public AActor
{
    GENERATED_BODY()

public:
    AMyXCodeTestActor();

protected:
    virtual void BeginPlay() override;
};

// MyXCodeTestActor.cpp
#include "MyXCodeTestActor.h"
#include "ISourceCodeAccessModule.h"

AMyXCodeTestActor::AMyXCodeTestActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyXCodeTestActor::BeginPlay()
{
    Super::BeginPlay();

    // 尝试在 Xcode 中打开此 Actor 的头文件
    if (ISourceCodeAccessModule* SourceCodeAccessModule = FModuleManager::GetModulePtr<ISourceCodeAccessModule>(TEXT("SourceCodeAccess")))
    {
        ISourceCodeAccessor& Accessor = SourceCodeAccessModule->GetAccessor();
        // 获取当前源文件路径（仅作示例，实际路径需根据项目确定）
        FString MyHeaderPath = FPaths::Combine(FPaths::ProjectDir(), TEXT("Source/YourProject/MyXCodeTestActor.h"));
        Accessor.OpenFileAtLine(MyHeaderPath, 0);
    }
}
```

## 模块依赖

从 `XCodeSourceCodeAccess.Build.cs` 分析，该插件依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SourceCodeAccess` | 提供 `ISourceCodeAccessor` 接口定义和基础管理器。 |
| `ApplicationCore` | 提供跨平台的系统级功能（如路径、进程管理）。 |
| `MacPlatformEditor` | macOS 平台编辑器特定的工具和集成。 |
| `DesktopPlatform` | 提供桌面平台通用的功能，如文件对话框、外部程序启动。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏迁移到新的 UE_LOGF 宏。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持可移植工具链的模块。 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复了使用可移植工具链时更多的编译错误。 |
| 2023-11-10 | `2267ffd9` | Improve source code lookup feature, using dsym if exists, and fix file path obtained from build mach | 改进源码查找功能，存在 dsym 文件时使用它，并修复从构建机器获取的文件路径。 |
| 2023-10-13 | `f59750d9` | Fix for NavigateToFunctionSource crash/error, use xcode built in atos instead of UnrealAtoS as it ca | 修复跳转到函数源码时的崩溃/错误，使用 Xcode 内置的 atos 工具替代 UnrealAtoS。 |

### 维护评价

该插件创建于 2014 年，历史悠久。尽管是 “文物” 级别的插件，但根据 git 记录显示，它在 2023 年和 2026 年仍有实质性更新（功能改进、编译修复），表明 Epic Games 仍在积极维护它，以确保其在新版 Xcode 和 UE 版本中的兼容性。作为 macOS 开发工作流的关键一环，其稳定性很高。

**推荐使用**：如果你在 macOS 上使用 Xcode 进行 UE 开发，这是一个必不可少的、维护良好的基础插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/XCodeSourceCodeAccess)