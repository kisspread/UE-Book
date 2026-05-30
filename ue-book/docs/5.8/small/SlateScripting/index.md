# Slate Scripting

> Allows interacting with Slate through scripting

| 属性 | 值 |
|---|---|
| 中文名 | 脚本化 UI 命令 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateScriptingCommands` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-10-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Slate/SlateScripting) | |

## 用途

SlateScripting 插件提供了一个**脚本化的 UI 命令注册系统**。它允许蓝图或 C++ 代码在运行时（Runtime）动态地将自定义命令（例如快捷键操作）注册到 Unreal 编辑器的现有 UI 命令列表中，例如 Sequencer、曲线编辑器、内容浏览器和主框架等。这使得扩展编辑器功能而无需修改引擎核心代码成为可能，是制作编辑器扩展和工具的理想选择。

## 使用场景

- 你正在开发一个编辑器工具，并想为 Sequencer 或 Content Browser 添加自定义的右键菜单操作。
- 你需要在运行时根据特定条件（如加载了某个插件或资产）动态地添加或移除快捷键绑定。
- 你想通过蓝图脚本为编辑器的不同上下文（Context）创建和管理一套完整的命令系统。

## 蓝图用法

核心功能通过 `UUICommandsScriptingSubsystem` 引擎子系统暴露。所有蓝图节点均以此子系统为目标。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register Command` | 注册一个普通的脚本命令 | `UUICommandsScriptingSubsystem` |
| `Register Command Checked` | 注册一个带“能否执行”检查的脚本命令 | `UUICommandsScriptingSubsystem` |
| `Unregister Command` | 注销一个已注册的脚本命令 | `UUICommandsScriptingSubsystem` |
| `Is Command Registered` | 检查指定的命令是否已注册 | `UUICommandsScriptingSubsystem` |
| `Register Command Set` | 注册一个新的命令集合，用于分组管理命令 | `UUICommandsScriptingSubsystem` |
| `Unregister Command Set` | 注销一个命令集合及其所有内部命令 | `UUICommandsScriptingSubsystem` |
| `Get Available Contexts` | 获取所有当前已注册的编辑器上下文（如 `LevelEditor`）的名称列表 | `UUICommandsScriptingSubsystem` |
| `Get Binding Count For Context` | 获取指定上下文中已注册的 UI 命令列表数量 | `UUICommandsScriptingSubsystem` |
| `Set Can Execute Commands` | 全局启用或禁用所有通过此子系统注册的命令的执行 | `UUICommandsScriptingSubsystem` |
| `Get Registered Commands` | 获取所有已注册命令的详细信息列表 | `UUICommandsScriptingSubsystem` |

### 使用示例（蓝图描述）

1.  **注册命令**：
    - 从任何蓝图（如编辑器工具蓝图）中，使用 `Get UICommands Scripting Subsystem` 节点获取子系统实例。
    - 创建一个 `FScriptingCommandInfo` 结构体变量，设置 `ContextName`（例如 `“LevelEditor”`）、`Set`（例如 `“MyPlugin.Commands”`）、`Name`、`Label` 和可选的 `InputChord`。
    - 创建一个自定义事件（带 `FScriptingCommandInfo` 参数）作为命令执行的委托，将其与 `FScriptingCommandInfo` 结构体一起连接到 `Register Command` 节点。

2.  **管理命令集**：
    - 在注册命令前，先调用 `Register Command Set` 节点来创建一个命令集（例如 `“MyPlugin.Commands”`）。这有助于避免命名冲突并能统一管理一组命令的启用/禁用状态。

## C++ 用法

### 头文件引入

```cpp
#include "UICommandsScriptingSubsystem.h"
```

### 基本用法

通过引擎子系统访问功能。来源文件: `UICommandsScriptingSubsystem.h`

```cpp
// 1. 获取子系统实例
UUICommandsScriptingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UUICommandsScriptingSubsystem>();
if (!Subsystem) return;

// 2. 定义命令信息
FScriptingCommandInfo CommandInfo;
CommandInfo.ContextName = TEXT("LevelEditor"); // 注册到关卡编辑器上下文
CommandInfo.Set = TEXT("MyToolkit.Commands"); // 使用一个唯一的命令集
CommandInfo.Name = TEXT("DoSomething");
CommandInfo.Label = NSLOCTEXT("MyToolkit", "DoSomethingLabel", "执行某个操作");
CommandInfo.Description = NSLOCTEXT("MyToolkit", "DoSomethingDesc", "这是一个通过脚本注册的命令示例");
CommandInfo.InputChord = FInputChord(EKeys::G, EModifierKey::Control); // 绑定 Ctrl+G

// 3. 注册命令执行委托
FExecuteCommand ExecuteDelegate;
ExecuteDelegate.BindLambda([CommandInfo]() {
    // 命令执行的逻辑
    UE_LOG(LogTemp, Warning, TEXT("脚本化命令被执行: %s"), *CommandInfo.Name.ToString());
});

// 4. 注册命令
bool bSuccess = Subsystem->RegisterCommand(CommandInfo, ExecuteDelegate);
```

### 进阶用法

管理命令集和上下文。综合自多个函数用途。

```cpp
UUICommandsScriptingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UUICommandsScriptingSubsystem>();
if (!Subsystem) return;

// 注册一个命令集
FName SetName = TEXT("MyToolkit.Commands");
if (!Subsystem->IsCommandSetRegistered(SetName))
{
    Subsystem->RegisterCommandSet(SetName);
}

// 注册一个带“能否执行”检查的命令
FScriptingCommandInfo CmdInfo;
CmdInfo.ContextName = TEXT("ContentBrowser");
CmdInfo.Set = SetName;
CmdInfo.Name = TEXT("PreviewAsset");
CmdInfo.Label = NSLOCTEXT("MyToolkit", "PreviewAsset", "预览资产");

FExecuteCommand ExecuteDelegate;
ExecuteDelegate.BindLambda([CmdInfo]() { /* ... */ });

FCanExecuteCommand CanExecuteDelegate;
CanExecuteDelegate.BindLambda([Subsystem]() {
    // 全局开关 + 自定义逻辑
    return Subsystem->CanExecuteCommands() && /* 你的条件 */;
});

Subsystem->RegisterCommandChecked(CmdInfo, ExecuteDelegate, CanExecuteDelegate);

// 查询当前可用的上下文
TArray<FName> Contexts = Subsystem->GetAvailableContexts();
for (const FName& Ctx : Contexts)
{
    UE_LOG(LogTemp, Log, TEXT("可用上下文: %s"), *Ctx.ToString());
}

// 禁用整个命令集的执行
Subsystem->SetCanSetExecuteCommands(SetName, false);
```

## Demo 示例

一个最小的编辑器工具蓝图或 C++ 类的代码片段，用于注册一个命令。

**MyEditorCommands.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "UICommandsScriptingSubsystem.h" // 关键头文件
#include "MyEditorCommands.generated.h"

UCLASS(BlueprintType)
class UMyEditorCommands : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Editor Tools")
    void RegisterMyCommand();

    UFUNCTION(BlueprintCallable, Category = "Editor Tools")
    void UnregisterMyCommand();

private:
    // 存储命令信息以便注销
    FScriptingCommandInfo StoredCommandInfo;
    bool bIsRegistered = false;
};
```

**MyEditorCommands.cpp**
```cpp
#include "MyEditorCommands.h"
#include "UICommandsScriptingSubsystem.h"

void UMyEditorCommands::RegisterMyCommand()
{
    UUICommandsScriptingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UUICommandsScriptingSubsystem>();
    if (!Subsystem || bIsRegistered) return;

    // 填充命令信息
    StoredCommandInfo.ContextName = TEXT("LevelEditor");
    StoredCommandInfo.Set = TEXT("Demo.Commands");
    StoredCommandInfo.Name = TEXT("MySimpleCommand");
    StoredCommandInfo.Label = NSLOCTEXT("Demo", "MyCmdLabel", "Demo Command");
    StoredCommandInfo.InputChord = FInputChord(EKeys::K);

    // 注册一个简单的命令集（如果尚未注册）
    if (!Subsystem->IsCommandSetRegistered(StoredCommandInfo.Set))
    {
        Subsystem->RegisterCommandSet(StoredCommandInfo.Set);
    }

    // 注册命令
    FExecuteCommand ExecuteDelegate;
    ExecuteDelegate.BindLambda([StoredCommandInfo = this->StoredCommandInfo]() {
        UE_LOG(LogTemp, Display, TEXT("Demo command executed! Context: %s, Set: %s, Name: %s"),
            *StoredCommandInfo.ContextName.ToString(),
            *StoredCommandInfo.Set.ToString(),
            *StoredCommandInfo.Name.ToString());
    });

    bIsRegistered = Subsystem->RegisterCommand(StoredCommandInfo, ExecuteDelegate);
}

void UMyEditorCommands::UnregisterMyCommand()
{
    UUICommandsScriptingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UUICommandsScriptingSubsystem>();
    if (!Subsystem || !bIsRegistered) return;

    Subsystem->UnregisterCommand(StoredCommandInfo);
    bIsRegistered = false;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件模块 (`SlateScriptingCommands`) 自身依赖于核心的 Slate 和输入绑定管理模块，但作为使用者，你只需在你的 `.Build.cs` 中依赖 `SlateScriptingCommands` 模块即可访问其 API。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的 `UE_LOGF` 宏 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏以优化编译 |
| 2025-06-11 | `b978b4ff` | Replace some usages of FORCEINLINE with inline in Slate modules. | 将部分 `FORCEINLINE` 替换为 `inline`，属于代码规范调整 |
| 2025-05-31 | `2739c3d3` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 使用工具更新头文件，修正 DLL 导出/导入声明 |
| 2023-11-22 | `79234582` | Typo fixes in comments | 修复注释中的拼写错误 |

### 维护评价

- **创建时间**：2021 年创建，年龄约 4 年。
- **维护频率**：最后一次**功能性**更新是插件创建时（2021年）。从 2023 年开始，所有提交均为代码维护性更新（格式、宏、注释修复），未引入新功能或修复已知缺陷。
- **维护状态**：处于**维护不活跃**状态。核心功能已稳定，但缺乏活跃的功能迭代。
- **已知限制**：插件默认未启用（`EnabledByDefault: false`），需要手动在项目中启用。它主要面向编辑器扩展场景，仅在编辑器运行时有效。
- **推荐度**：**推荐使用**。对于需要在运行时动态扩展编辑器 UI 命令的场景，这是一个官方提供的、结构清晰的解决方案。尽管没有活跃的功能更新，但其核心 API 稳定，足以满足常见需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Slate/SlateScripting)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的信息中找到明确的测试文件路径)