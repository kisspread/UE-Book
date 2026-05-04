# File Sandbox

> Core functionality for sandboxing files in the editor.

| 属性 | 值 |
|---|---|
| 分类 | Developer |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FileSandboxCore` (UncookedOnly), `FileSandboxUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Sandbox/FileSandbox) | |

## 用途

File Sandbox 插件为 Unreal Editor 提供了文件操作沙盒化的核心功能。它解决的核心问题是：当多个编辑器系统（如多用户编辑、版本控制集成、或需要隔离文件修改的特定工具）需要同时操作项目文件时，如何避免冲突并管理文件状态。

该插件的核心思想是“沙盒”（Sandbox），即为特定的编辑器操作创建一个隔离的文件操作环境。在这个环境中进行的文件修改（添加、编辑、删除）可以被收集、审查，并最终选择性地“持久化”（Persist）到主文件系统中。这为实现非破坏性编辑、预览更改、以及复杂的版本控制工作流提供了基础架构。

插件本身是**实验性**且**默认禁用**的，表明它是一个面向开发者的底层工具，用于构建更高级的编辑器功能，而非直接面向最终用户。

## 使用场景

- **构建多用户编辑系统**：当多个用户同时编辑同一个项目时，每个用户的修改可以在各自的沙盒中进行，最后通过冲突解决机制合并。
- **开发高级版本控制集成**：在提交（Check-in）前，将所有待提交的文件更改收集到一个沙盒中，进行统一的差异对比和审查。
- **创建非破坏性编辑工具**：例如，一个允许用户尝试多种材质参数组合的工具，每次尝试都在沙盒中进行，用户可以随时回退或保存满意的方案。
- **实现文件操作预览**：在执行批量重命名、移动或删除等高风险操作前，先在沙盒中模拟执行，让用户确认最终结果。

## 蓝图用法

该插件主要提供 C++ 接口和 Slate UI 组件，蓝图可直接调用的节点较少。其 UI 组件（如覆盖层）通常通过 C++ 代码集成到编辑器模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeExternalSandboxActiveOverlay` | 创建一个 Slate 控件，用于在 UI 上覆盖提示信息，告知用户当前操作被另一个系统的沙盒阻塞。 | `UE::FileSandboxUI` (全局函数) |
| `MakeExternalSandboxActiveViewModel` | 创建一个视图模型，用于驱动 `SExternalSandboxActiveOverlay` 控件的显示逻辑。 | `UE::FileSandboxUI` (全局函数) |

### 使用示例（蓝图描述）

由于核心功能是 C++ 接口，典型的蓝图用法是在一个编辑器工具蓝图（Editor Utility Blueprint）中，通过调用 C++ 函数库暴露的节点来集成沙盒状态提示。

1.  在你的编辑器工具 UI 中，放置一个 `SExternalSandboxActiveOverlay` 控件。
2.  在控件初始化时，调用 `MakeExternalSandboxActiveViewModel` 并传入你系统的 `ISandboxEntryPoint` 实例，获取视图模型。
3.  将视图模型传递给覆盖层控件进行构造。
4.  覆盖层会自动监听沙盒状态变化，并在有外部沙盒活动时显示提示和“跳转”按钮。

## C++ 用法

### 头文件引入

```cpp
#include "IFileSandboxUIModule.h"
#include "EntryPoint/ISandboxEntryPoint.h"
#include "EntryPoint/EntryPointWidgetFactory.h"
```

### 基本用法

**1. 注册你的编辑器系统为沙盒入口点**

首先，你的编辑器系统需要实现 `ISandboxEntryPoint` 接口，然后将其注册到全局注册表中。

```cpp
// MyEditorSystem.h
#pragma once
#include "EntryPoint/ISandboxEntryPoint.h"

class FMyEditorSystem : public UE::FileSandboxUI::ISandboxEntryPoint
{
public:
    // 实现 ISandboxEntryPoint 接口
    virtual void SummonProviderUI() override;
    virtual FText GetEntryPointLabel() const override;
    virtual bool OwnsSandbox(const FileSandboxCore::ISandboxInstance& InSandbox) const override;
};
```

```cpp
// MyEditorSystem.cpp
#include "IFileSandboxUIModule.h"

void FMyEditorSystem::Initialize()
{
    if (UE::FileSandboxUI::IFileSandboxUIModule::IsAvailable())
    {
        auto& Registry = UE::FileSandboxUI::IFileSandboxUIModule::Get().GetEntryPointRegistry();
        TSharedRef<FMyEditorSystem> EntryPoint = MakeShared<FMyEditorSystem>();
        Registry.RegisterEntryPoint(EntryPoint);
        // 保存 EntryPoint 引用以便后续注销
    }
}

void FMyEditorSystem::Shutdown()
{
    if (UE::FileSandboxUI::IFileSandboxUIModule::IsAvailable())
    {
        auto& Registry = UE::FileSandboxUI::IFileSandboxUIModule::Get().GetEntryPointRegistry();
        Registry.UnregisterEntryPoint(MyEntryPointRef);
    }
}
```

### 进阶用法

**2. 在你的 UI 中集成外部沙盒活动提示**

当你的功能因其他系统的沙盒而不可用时，使用提供的工厂函数创建提示 UI。

```cpp
// 在你的 Slate UI 构造函数中
void SMyEditorPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            // 创建并嵌入外部沙盒活动覆盖层
            UE::FileSandboxUI::MakeExternalSandboxActiveOverlay(
                UE::FileSandboxUI::MakeExternalSandboxActiveViewModel(MyEntryPointRef)
            )
        ]
        + SVerticalBox::Slot()
        [
            // ... 你的主要 UI 内容 ...
        ]
    ];
}
```

**3. 使用持久化反馈（Persist Feedback）**

在将沙盒中的更改持久化到磁盘时，使用反馈接口来报告进度和错误。

```cpp
#include "Persist/Feedback/SlowTaskPersistFeedback.h"
#include "Persist/Feedback/SummaryPersistFeedback.h"

void PersistSandboxChanges(const FileSandboxCore::FGatheredFileChanges& Changes)
{
    // 1. 创建带进度条的反馈对象
    UE::FileSandboxUI::FSlowTaskPersistFeedback ProgressFeedback(Changes.NonSandboxPaths.Num());
    
    // 2. 创建用于收集结果的摘要反馈对象
    UE::FileSandboxUI::FSummaryPersistFeedback SummaryFeedback(Changes);
    
    // 3. 执行持久化操作（假设有一个 SandboxInstance 对象）
    // SandboxInstance->PersistChanges(ProgressFeedback, SummaryFeedback);
    
    // 4. 检查结果
    const UE::FileSandboxUI::FPersistSummary& Summary = SummaryFeedback.Summary;
    if (Summary.FailedFiles.Num() > 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to persist %d files."), Summary.FailedFiles.Num());
    }
}
```

## Demo 示例

以下是一个最小化的编辑器模块示例，演示如何将一个简单的编辑器系统注册为沙盒入口点。

**MySandboxEditorModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"
#include "EntryPoint/ISandboxEntryPoint.h"

class FMySandboxEditorModule : public IModuleInterface, public UE::FileSandboxUI::ISandboxEntryPoint
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    // ISandboxEntryPoint Interface
    virtual void SummonProviderUI() override;
    virtual FText GetEntryPointLabel() const override;
    virtual bool OwnsSandbox(const FileSandboxCore::ISandboxInstance& InSandbox) const override;

private:
    TSharedPtr<UE::FileSandboxUI::ISandboxEntryPoint> RegisteredEntryPoint;
};
```

**MySandboxEditorModule.cpp**
```cpp
#include "MySandboxEditorModule.h"
#include "IFileSandboxUIModule.h"

#define LOCTEXT_NAMESPACE "FMySandboxEditorModule"

void FMySandboxEditorModule::StartupModule()
{
    if (UE::FileSandboxUI::IFileSandboxUIModule::IsAvailable())
    {
        RegisteredEntryPoint = MakeShared<FMySandboxEditorModule>(*this);
        UE::FileSandboxUI::IFileSandboxUIModule::Get().GetEntryPointRegistry().RegisterEntryPoint(RegisteredEntryPoint.ToSharedRef());
    }
}

void FMySandboxEditorModule::ShutdownModule()
{
    if (RegisteredEntryPoint.IsValid() && UE::FileSandboxUI::IFileSandboxUIModule::IsAvailable())
    {
        UE::FileSandboxUI::IFileSandboxUIModule::Get().GetEntryPointRegistry().UnregisterEntryPoint(RegisteredEntryPoint.ToSharedRef());
        RegisteredEntryPoint.Reset();
    }
}

void FMySandboxEditorModule::SummonProviderUI()
{
    // 打开你的编辑器窗口或面板
    UE_LOG(LogTemp, Log, TEXT("Summoning My Sandbox Editor UI..."));
}

FText FMySandboxEditorModule::GetEntryPointLabel() const
{
    return LOCTEXT("EntryPointLabel", "My Sandbox Tool");
}

bool FMySandboxEditorModule::OwnsSandbox(const FileSandboxCore::ISandboxInstance& InSandbox) const
{
    // 根据你的沙盒实例判断是否属于本系统
    return false; // 示例中总是返回 false
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMySandboxEditorModule, MySandboxEditor)
```

## 模块依赖

从 `Build.cs` 文件分析，使用该插件时，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DirectoryWatcher` | `FileSandboxCore` 模块依赖此模块来监控文件系统变化，这是沙盒功能的基础。 |

**注意**：`FileSandboxUI` 模块没有列出特殊的依赖项，它主要依赖标准的 Slate/UMG 模块来构建 UI。

## 维护状态

### 近期更新

- 2026-04-24 `0b495ee3` Sandbox: Add support for reloading levels that are WP based.
- 2026-04-23 `d023aa3e` Close editors and deselect after iteration is complete ? doing this inside
- 2026-04-17 `c812283d` Fix spurious check that was occurring inside FNewSandboxArgs from within AI Assistant Sandbox Automa
- 2026-04-16 `bf487acb` File Sandbox: Fix not being able to persist files in Lyra. The fix is to flush the file perform atte
- 2026-04-16 `6ca4de07` File Sandbox: Fix file disappearing from content browser after persist.

### 维护评价

- **创建时间**：2026年4月，是一个非常新的插件。
- **状态**：**实验性** (`IsBetaVersion=true`) 且**默认禁用** (`EnabledByDefault=false`)。这表明它是一个面向开发者的、尚未稳定的底层功能。
- **维护活跃度**：作为新创建的实验性插件，预计会有活跃的开发，但接口和功能可能发生较大变化。
- **已知限制**：作为实验性功能，可能存在未发现的 Bug，且 API 不保证向后兼容。
- **推荐使用**：**仅推荐给需要构建高级文件沙盒化工作流的插件或工具开发者**。不建议在面向最终用户的稳定项目中直接依赖此插件。使用前应充分评估其稳定性和是否符合你的需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Sandbox/FileSandbox)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中找到)