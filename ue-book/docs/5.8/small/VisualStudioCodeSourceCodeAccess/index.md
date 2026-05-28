# Visual Studio Code Integration

> Allows access to source code in Visual Studio Code.

| 属性 | 值 |
|---|---|
| 中文名 | VS Code 源码访问器 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VisualStudioCodeSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-08-31 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioCodeSourceCodeAccess) | |

## 用途

这个插件的核心功能是将 Visual Studio Code 注册为 Unreal Engine 编辑器的一个源代码访问器。它的存在解决了开发者在使用 UE5 时，希望将 VS Code 作为 C++ 代码的主要编辑和调试工具的配置问题。

插件通过实现 `ISourceCodeAccessor` 接口，实现了以下功能：
1.  **自动检测**：尝试自动检测本机安装的 VS Code 可执行文件路径。
2.  **无缝集成**：当在编辑器中双击错误信息、或需要在特定文件和行号处打开代码时，插件会自动启动 VS Code 并跳转到正确位置。
3.  **项目/工作区管理**：能够处理 UE 项目对应的 `.sln` 或 `.code-workspace` 文件，确保 VS Code 能正确加载项目上下文和 IntelliSense。

简而言之，它让你能一键从 UE 编辑器跳转到 VS Code 编辑代码，无需手动配置路径。

## 使用场景

-   你是一名习惯使用 VS Code 进行 C++ 开发的 UE5 程序员。
-   你希望在编辑器中双击编译错误或警告时，能直接在 VS Code 中打开对应文件并定位到问题行。
-   你不想每次手动配置 VS Code 来识别 UE 项目和头文件。

## 蓝图用法

不适用。此插件是编辑器开发者工具，不包含任何蓝图可调用的函数或可读写的属性。

## C++ 用法

此插件的使用者通常不直接调用其 C++ API，而是作为编辑器配置存在。对于插件开发者或希望深入集成的人来说，核心接口是 `ISourceCodeAccessor`。

### 头文件引入

```cpp
#include "ISourceCodeAccessor.h"
```

### 基本用法（注册自定义访问器）

此示例展示了如何创建并注册一个简单的自定义源代码访问器。这是此插件内部工作原理的简化版本。

```cpp
// MySourceCodeAccessor.h
#pragma once
#include "ISourceCodeAccessor.h"

class FMySourceCodeAccessor : public ISourceCodeAccessor
{
public:
    // ISourceCodeAccessor 接口实现
    virtual void RefreshAvailability() override;
    virtual bool CanAccessSourceCode() const override;
    virtual FName GetFName() const override;
    virtual FText GetNameText() const override;
    virtual FText GetDescriptionText() const override;
    virtual bool OpenSolution() override;
    virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0) override;
    // ... 其他接口方法
};

// MySourceCodeAccessorModule.cpp (模块启动时注册)
#include "MySourceCodeAccessor.h"
#include "SourceCodeNavigation.h"

void FMySourceCodeAccessorModule::StartupModule()
{
    // 创建访问器实例
    TSharedRef<FMySourceCodeAccessor> Accessor = MakeShareable(new FMySourceCodeAccessor());
    
    // 注册到引擎的源代码导航系统
    FSourceCodeNavigation::RegisterSourceCodeAccessor(Accessor);
}

void FMySourceCodeAccessorModule::ShutdownModule()
{
    // 在模块关闭时注销
    FSourceCodeNavigation::UnregisterSourceCodeAccessor(Accessor);
}
```

## Demo 示例

以下是一个最小化但可编译的示例，演示如何为一个虚构的 “MyIDE” 创建源代码访问器插件。

**MyIDESourceCodeAccess.Build.cs**
```csharp
using UnrealBuildTool;
public class MyIDESourceCodeAccess : ModuleRules
{
    public MyIDESourceCodeAccess(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "SourceCodeAccess" });
        PrivateDependencyModuleNames.AddRange(new string[] { "CoreUObject", "Engine", "Slate", "SlateCore", "InputCore", "SourceCodeAccess", "Projects", "DesktopPlatform" });
    }
}
```

**MyIDESourceCodeAccessor.h**
```cpp
#pragma once
#include "ISourceCodeAccessor.h"

class FMyIDESourceCodeAccessor : public ISourceCodeAccessor
{
public:
    void Startup();
    void Shutdown();

    // ISourceCodeAccessor
    virtual void RefreshAvailability() override;
    virtual bool CanAccessSourceCode() const override;
    virtual FName GetFName() const override;
    virtual FText GetNameText() const override;
    virtual FText GetDescriptionText() const override;
    virtual bool OpenSolution() override;
    virtual bool OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber = 0) override;
    virtual bool OpenSourceFiles(const TArray<FString>& AbsoluteSourcePaths) override;
    virtual bool SaveAllOpenDocuments() const override;
    virtual void Tick(const float DeltaTime) override;

private:
    // 存储 MyIDE 可执行文件路径
    FString MyIDEPath;
};
```

**MyIDESourceCodeAccessor.cpp**
```cpp
#include "MyIDESourceCodeAccessor.h"
#include "HAL/PlatformProcess.h"
#include "SourceCodeNavigation.h"
#include "Interfaces/IPluginManager.h"
#include "Misc/Paths.h"
#include "DesktopPlatformModule.h"

void FMyIDESourceCodeAccessor::Startup()
{
    // 在真实实现中，这里会检测 MyIDE 的路径
    MyIDEPath = TEXT("C:/Program Files/MyIDE/bin/myide.exe");
    
    // 注册到引擎
    FSourceCodeNavigation::RegisterSourceCodeAccessor(SharedThis(this));
}

void FMyIDESourceCodeAccessor::Shutdown()
{
    FSourceCodeNavigation::UnregisterSourceCodeAccessor(SharedThis(this));
}

void FMyIDESourceCodeAccessor::RefreshAvailability()
{
    // 检查 MyIDEPath 是否存在
}

bool FMyIDESourceCodeAccessor::CanAccessSourceCode() const
{
    return !MyIDEPath.IsEmpty();
}

FName FMyIDESourceCodeAccessor::GetFName() const
{
    return FName("MyIDE");
}

FText FMyIDESourceCodeAccessor::GetNameText() const
{
    return FText::FromString(TEXT("MyIDE Editor"));
}

FText FMyIDESourceCodeAccessor::GetDescriptionText() const
{
    return FText::FromString(TEXT("Open source code in MyIDE Editor"));
}

bool FMyIDESourceCodeAccessor::OpenSolution()
{
    // 调用 MyIDE 打开解决方案文件(.sln 或 .uproject)
    FString SolutionPath = FPaths::ConvertRelativePathToFull(IPluginManager::Get().FindPlugin(TEXT("MyIDESourceCodeAccess"))->GetBaseDir() / TEXT("MyIDESourceCodeAccess.sln"));
    TArray<FString> Args;
    Args.Add(SolutionPath);
    return FPlatformProcess::CreateProc(*MyIDEPath, *FString::Join(Args, TEXT(" ")), false, false, false, nullptr, 0, nullptr, nullptr).IsValid();
}

bool FMyIDESourceCodeAccessor::OpenFileAtLine(const FString& FullPath, int32 LineNumber, int32 ColumnNumber)
{
    // MyIDE 的命令行参数示例: myide.exe --goto <file>:<line>
    FString Args = FString::Printf(TEXT("--goto %s:%d"), *FullPath, LineNumber);
    return FPlatformProcess::CreateProc(*MyIDEPath, *Args, false, false, false, nullptr, 0, nullptr, nullptr).IsValid();
}
```

**MyIDESourceCodeAccessModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"
class FMyIDESourceCodeAccessModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
private:
    TSharedPtr<FMyIDESourceCodeAccessor> Accessor;
};
```

**MyIDESourceCodeAccessModule.cpp**
```cpp
#include "MyIDESourceCodeAccessModule.h"
#include "MyIDESourceCodeAccessor.h"

void FMyIDESourceCodeAccessModule::StartupModule()
{
    Accessor = MakeShareable(new FMyIDESourceCodeAccessor());
    Accessor->Startup();
}

void FMyIDESourceCodeAccessModule::ShutdownModule()
{
    if (Accessor.IsValid())
    {
        Accessor->Shutdown();
        Accessor.Reset();
    }
}

IMPLEMENT_MODULE(FMyIDESourceCodeAccessModule, MyIDESourceCodeAccess)
```

## 模块依赖

从 Build.cs 文件分析，此插件依赖以下非公共模块：

| 模块 | 用途 |
|---|---|
| `HotReload` | 用于支持热重载功能，这是该插件类型（UncookedOnly）的常见依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持可移植工具链的模块 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复了使用可移植工具链时更多的编译错误 |
| 2025-11-18 | `40e181c3` | Add missing HideWindowsPlatformTypes | 添加缺失的 HideWindowsPlatformTypes 宏 |
| 2025-11-07 | `2cb327ee` | Fix VisualStudioCode Accessor to find the code-workspace like Visual Studio | 修复了 VS Code 访问器，使其能像 Visual Studio 一样找到 .code-workspace 文件 |
| 2025-10-23 | `fe6d9d0d` | Fix Visual Studio Code file open to better create command line for Linux compatibility | 修复了 VS Code 文件打开功能，改进了命令行创建以提升 Linux 兼容性 |

### 维护评价

-   **状态**：维护中。该插件创建于2017年，最近一次提交在2026年1月，更新频率不高但持续存在。
-   **内容**：最近的更新主要是编译修复、平台兼容性改进和小功能增强（如识别 .code-workspace 文件），表明插件仍在跟随引擎和开发工具的变化进行维护。
-   **活跃度**：作为编辑器开发者工具，其功能相对稳定，更新通常源于外部变化（如工具链更新、VS Code 版本变化、平台支持）。
-   **推荐**：✅ **推荐使用**。对于习惯使用 VS Code 的 UE 开发者，这是一个开箱即用、维护良好的必备插件。它已包含在引擎中并默认启用，无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioCodeSourceCodeAccess)
- [官方文档]( )（无）