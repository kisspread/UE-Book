# Visual Studio Integration

> Allows access to source code in Visual Studio.

| 属性 | 值 |
|---|---|
| 中文名 | Visual Studio 集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VisualStudioSetup` (External), `VisualStudioSourceCodeAccess` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-04-23 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess) | |

## 用途

本插件的核心功能是作为 Unreal Editor 与 Visual Studio (VS) IDE 之间的桥梁，实现源代码的快速访问。其主要作用包括：
1.  **在 VS 中打开文件与定位代码**：当用户在编辑器中双击编译错误、警告日志或源代码行号时，该插件能够自动启动或激活 Visual Studio，并定位到对应的源文件和行号。
2.  **热重载支持**：与 `HotReload` 模块深度集成，在代码热重载完成后，可以自动将焦点切换回 Visual Studio，便于开发者继续编写代码。
3.  **提供源代码访问抽象层**：作为 `SourceCodeAccess` 模块的扩展实现，它定义了如何与特定 IDE (VS) 交互的标准接口，为其他 IDE（如 Xcode、Rider）的插件化集成提供了参考架构。

简而言之，它解决了在开发过程中频繁切换编辑器和 IDE 的问题，提升了基于 Visual Studio 进行 Unreal 项目开发的效率。

## 使用场景

- 你在使用 **Visual Studio** 作为 C++ 开发环境，并希望从 Unreal Editor 中一键跳转到 VS 对应的代码行。
- 你的项目频繁使用 **热重载（Hot Reload）** 功能，并希望热重载完成后自动回到 VS 继续编码。
- 你需要在编辑器的“源代码访问”设置中，将 **Visual Studio** 配置为首选的代码编辑器。

## 蓝图用法

本插件主要为编辑器内部功能服务，未暴露蓝图接口。

## C++ 用法

该插件的功能通常通过编辑器的内置操作（如双击错误）触发，但也可以通过 C++ 代码直接调用。

### 头文件引入

```cpp
#include "ISourceCodeAccessModule.h"
#include "ISourceCodeAccessor.h"
```

### 基本用法

通过 `SourceCodeAccess` 模块获取当前激活的源代码访问器（在此场景下即为 VS 访问器），并调用其打开文件的方法。
*(来源: 模块设计模式)*

```cpp
// 获取源代码访问模块
ISourceCodeAccessModule& SourceCodeAccessModule = FModuleManager::LoadModuleChecked<ISourceCodeAccessModule>(TEXT("SourceCodeAccess"));
// 获取当前设置的访问器 (通常是 VisualStudioSourceCodeAccess)
ISourceCodeAccessor* Accessor = SourceCodeAccessModule.GetAccessor();

// 检查访问器是否有效，并打开文件
if (Accessor && Accessor->CanAccessSourceCode())
{
    // 打开指定文件并跳转到第 100 行
    Accessor->OpenFileAtLine(TEXT("/Game/Source/MyClass.cpp"), 100);
}
```

### 进阶用法

监听热重载事件，并在热重载完成后自动将焦点交还给 Visual Studio。
*(来源: 与 HotReload 模块交互的逻辑)*

```cpp
// 在某个 Actor 或 EditorSubsystem 中
void AMyClass::BeginPlay()
{
    Super::BeginPlay();

    // 订阅热重载完成事件
    FCoreUObjectDelegates::ReloadCompleteDelegate.AddUObject(this, &AMyClass::OnHotReloadComplete);
}

void AMyClass::OnHotReloadComplete(EReloadCompleteReason Reason)
{
    if (Reason == EReloadCompleteReason::HotReloadAutomatic)
    {
        // 热重载自动完成后，尝试激活 VS
        ISourceCodeAccessModule& SourceCodeAccessModule = FModuleManager::LoadModuleChecked<ISourceCodeAccessModule>(TEXT("SourceCodeAccess"));
        ISourceCodeAccessor* Accessor = SourceCodeAccessModule.GetAccessor();
        if (Accessor)
        {
            Accessor->OpenSolution(); // 通常这会激活已打开的 VS 窗口
        }
    }
}
```

## Demo 示例

一个完整的最小示例，演示如何编写一个简单的编辑器工具按钮，用于在 Visual Studio 中打开当前关卡蓝图关联的 C++ 文件。

**MyEditorTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyEditorTool.generated.h"

UCLASS()
class UMyEditorTool : public UObject
{
    GENERATED_BODY()

public:
    /** 在 Visual Studio 中打开与当前关卡关联的第一个 C++ 类 */
    UFUNCTION(BlueprintCallable, Category="EditorTool")
    void OpenLevelCodeInVS();
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "ISourceCodeAccessModule.h"
#include "ISourceCodeAccessor.h"
#include "Kismet/GameplayStatics.h"

void UMyEditorTool::OpenLevelCodeInVS()
{
    // 获取源代码访问器
    ISourceCodeAccessModule& SourceCodeAccessModule = FModuleManager::LoadModuleChecked<ISourceCodeAccessModule>(TEXT("SourceCodeAccess"));
    ISourceCodeAccessor* Accessor = SourceCodeAccessModule.GetAccessor();

    if (!Accessor || !Accessor->CanAccessSourceCode())
    {
        UE_LOG(LogTemp, Warning, TEXT("Cannot access source code (VS integration not found?)"));
        return;
    }

    // 获取当前世界（关卡）关联的第一个 Actor 的类源文件路径
    UWorld* World = GEditor->GetEditorWorldContext().World();
    AActor* SomeActor = UGameplayStatics::GetActorOfClass(World, AActor::StaticClass());

    if (SomeActor)
    {
        FString SourceFile = SomeActor->GetClass()->ClassGeneratedBy ? 
            *SomeActor->GetClass()->ClassGeneratedBy->GetPathName() : // 蓝图
            *SomeActor->GetClass()->GetPathName(); // 原生C++类

        // 对于原生类，尝试获取头文件路径（简化示例）
        // 在实际使用中，你可能需要更精确的路径解析逻辑
        SourceFile = FPaths::GetPath(SourceFile) / FPaths::GetBaseFilename(SourceFile) + TEXT(".h");
        
        UE_LOG(LogTemp, Log, TEXT("Attempting to open: %s"), *SourceFile);
        Accessor->OpenFileAtLine(SourceFile, 1);
    }
}
```

## 模块依赖

从 `VisualStudioSourceCodeAccess.Build.cs` 的依赖项分析，要使用或扩展此插件的功能，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `HotReload` | 核心依赖，用于在热重载事件发生后与 Visual Studio 进行同步交互 |

其他如 `Core`, `CoreUObject`, `Engine`, `Slate`, `InputCore` 等为标准依赖，无需特别列出。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复了不可达代码的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-09 | `2be8aeed` | Remove experimental from Visual Studio 2026 support | 移除对 Visual Studio 2026 支持的实验性标记。 |
| 2025-09-11 | `2b3128b4` | Experimental Visual Studio 2026 support | 添加了对 Visual Studio 2026 的实验性支持。 |
| 2025-06-17 | `a2f48da5` | Fixed circular includes across the engine | 修复了引擎范围内的循环包含问题。 |

### 维护评价

该插件自2014年创建，历史悠久，是 Unreal 编辑器核心开发工作流的一部分。近期的提交（2025-2026年）表明 Epic 仍在对其进行维护，主要是**编译警告修复**、**日志宏现代化**以及**对新VS版本（2026）的支持**。更新频率较低，属于典型的“维护性”而非“特性开发”状态。

**综合评价**：**稳定可用，但非活跃开发**。它是一个成熟且必不可少的基础设施插件，对于使用 Visual Studio 的开发者是默认启用的。虽然不会有频繁的功能更新，但 Epic 会确保其与新引擎版本和新 VS 版本的兼容性。可以放心使用，无需担心被废弃。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess/Tests)