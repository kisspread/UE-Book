# Visual Studio Integration

> Allows access to source code in Visual Studio.

| 属性 | 值 |
|---|---|
| 中文名 | Visual Studio 集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `VisualStudioSourceCodeAccess` (Runtime), `VisualStudioSetup` (External) |
| 实验性 | 否 |
| 创建时间 | 2014-04-23 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess) | |

## 用途

该插件实现了 `ISourceCodeAccessor` 接口，为虚幻编辑器提供了与 Microsoft Visual Studio 集成的能力。其核心目的是在开发过程中，实现编辑器与 Visual Studio IDE 之间的无缝代码导航。它解决了编辑器（如蓝图编辑器、输出日志、调试器等）中需要查看或调试特定 C++ 源代码时，能够一键直接跳转到 Visual Studio 中对应文件和行号的需求。该插件是源代码访问插件化架构的一部分，使编辑器能够支持多种第三方 IDE。

## 使用场景

-   你在虚幻编辑器中调试一个蓝图，想查看其背后 C++ 节点的实现。
-   在编辑器输出日志中看到一个代码行号（如断言失败信息），希望直接在 IDE 中定位到该行。
-   需要快速打开项目的 `.sln` 或 `.uproject` 文件并启动 Visual Studio。
-   作为团队中的一名 C++ 程序员，希望保持虚幻编辑器和 Visual Studio 之间的高效工作流。

## 蓝图用法

该插件主要通过编辑器菜单和快捷键提供功能，本身不暴露直接的蓝图节点。其功能通过 `ISourceCodeAccessor` 接口被编辑器的其他部分（如 `FSourceCodeNavigation` 类）调用。在编辑器中，您可以通过以下方式间接使用：
1.  **编辑器菜单**：`Tools` (工具) -> `Open Visual Studio` (打开 Visual Studio)。
2.  **快捷键**：默认情况下，`Ctrl+Shift+O` 会尝试在 Visual Studio 中打开当前编辑器选中的源文件（如果可用）。
3.  **上下文菜单**：在蓝图节点或输出日志条目上右键单击，选择“打开源代码”相关的选项。

## C++ 用法

### 头文件引入

```cpp
#include "ISourceCodeAccessor.h" // 接口
#include "ISourceCodeAccessModule.h" // 模块访问接口
```

### 基本用法

从测试用例中可以看到，主要是通过模块接口获取具体的 `ISourceCodeAccessor` 实例并进行操作。
（来源：`Engine/Tests/SourceCodeAccessTests/`）

```cpp
// 获取源代码访问模块
ISourceCodeAccessModule& SourceCodeAccessModule = FModuleManager::LoadModuleChecked<ISourceCodeAccessModule>("SourceCodeAccess");

// 获取当前活动的访问器 (可能是这个Visual Studio访问器，也可能是其他如Xcode)
TSharedPtr<ISourceCodeAccessor> ActiveAccessor = SourceCodeAccessModule.GetAccessor();

// 检查访问器是否可用 (Visual Studio是否已安装并配置好)
if (ActiveAccessor.IsValid() && ActiveAccessor->CanAccessSourceCode())
{
    // 尝试在Visual Studio中打开一个文件并定位到第42行
    bool bOpened = ActiveAccessor->OpenFileAtLine(TEXT("/Path/To/YourFile.cpp"), 42);
}
```

### 进阶用法

组合使用接口方法，实现打开解决方案和指定文件。
（来源：`Engine/Plugins/Developer/VisualStudioSourceCodeAccess/` 内部逻辑）

```cpp
// 获取访问器并强制刷新其可用性状态
TSharedPtr<ISourceCodeAccessor> Accessor = SourceCodeAccessModule.GetAccessor();
Accessor->RefreshAvailability();

// 检查解决方案是否存在（例如 .sln 文件是否生成）
if (Accessor->DoesSolutionExist())
{
    // 在Visual Studio中打开整个解决方案
    Accessor->OpenSolution();
}

// 打开多个文件
TArray<FString> FilesToOpen;
FilesToOpen.Add(TEXT("/Game/Source/PlayerController.cpp"));
FilesToOpen.Add(TEXT("/Game/Source/PlayerController.h"));
Accessor->OpenSourceFiles(FilesToOpen);

// 向项目中添加新源文件（需要Visual Studio项目已加载）
TArray<FString> NewFiles;
NewFiles.Add(TEXT("/Game/Source/NewComponent.cpp"));
TArray<FString> AvailableModules;
AvailableModules.Add(TEXT("MyGameModule"));
Accessor->AddSourceFiles(NewFiles, AvailableModules);
```

## Demo 示例

一个最小的示例，展示如何在自定义编辑器工具中触发 Visual Studio 打开特定文件。

### MyEditorTool.h
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyEditorTool
{
public:
    static void OpenSelectedSourceFile();
};
```

### MyEditorTool.cpp
```cpp
#include "MyEditorTool.h"
#include "ISourceCodeAccessModule.h"
#include "ISourceCodeAccessor.h"

void FMyEditorTool::OpenSelectedSourceFile()
{
    // 假设你有一个需要打开的文件路径和行号
    const FString FilePath = TEXT("/Game/Source/ImportantActor.cpp");
    const int32 LineNumber = 150;

    // 获取源代码访问模块
    ISourceCodeAccessModule* SourceCodeAccessModule = FModuleManager::GetModulePtr<ISourceCodeAccessModule>("SourceCodeAccess");
    if (SourceCodeAccessModule)
    {
        // 获取当前活动的访问器
        TSharedPtr<ISourceCodeAccessor> Accessor = SourceCodeAccessModule->GetAccessor();
        if (Accessor.IsValid() && Accessor->CanAccessSourceCode())
        {
            // 尝试在Visual Studio中打开该文件
            Accessor->OpenFileAtLine(FilePath, LineNumber);
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("源代码访问器不可用或Visual Studio未安装。"));
        }
    }
}
```

## 模块依赖

该插件的运行时模块 `VisualStudioSourceCodeAccess` 依赖于以下非通用模块：

| 模块 | 用途 |
|---|---|
| `HotReload` | 用于支持热重载功能，这是 Visual Studio 与虚幻编辑器交互的关键部分，允许在不重启编辑器的情况下加载代码更改。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `270dc64a` | Fix unreachable code warnings | 修复编译器警告，提升代码规范性 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的UE_LOGF格式 |
| 2026-03-09 | `2be8aeed` | Remove experimental from Visual Studio 2026 support | 正式移除VS2026支持的实验性标记 |
| 2025-09-11 | `2b3128b4` | Experimental Visual Studio 2026 support | 实验性添加对VS2026的支持 |
| 2025-06-17 | `a2f48da5` | Fixed circular includes across the engine | 修复了引擎范围内的循环包含问题 |

### 维护评价

**活跃维护**。尽管该插件创建于2014年（约12年前），但其维护状态非常活跃。从近期的 git 历史可以看出，Epic 持续为其添加新功能（如对 Visual Studio 2026 的支持）并进行底层维护（修复警告、重构日志、解决编译问题）。最近的更新集中在2025和2026年，表明它仍然是虚幻引擎工作流中一个核心且受支持的组件。作为编辑器与核心IDE集成的基础插件，其稳定性和持续更新对C++开发者至关重要。

**推荐使用**：强烈推荐所有使用 Visual Studio 进行虚幻引擎 C++ 开发的开发者启用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/VisualStudioSourceCodeAccess)