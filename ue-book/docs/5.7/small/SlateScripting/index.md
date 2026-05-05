# Slate Scripting

> Allows interacting with Slate through scripting

| 属性 | 值 |
|---|---|
| 分类 | Scripting |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | SlateScriptingCommands (Runtime) |
| 创建时间 | 2021-10-06 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Slate/SlateScripting) | |

## 用途

SlateScripting 为蓝图和其他脚本系统提供了一种动态注册编辑器 UI 命令（UI Commands）的方式。它封装了 UE 底层的 `FInputBindingManager` 和 `FUICommandList` 系统，使得脚本能够：

- **注册和管理命令集（Command Sets）**：将相关命令分组，便于批量启用/禁用
- **动态注册编辑器命令**：绑定键盘快捷键（Input Chord）到自定义回调
- **管理命令上下文（Contexts）**：不同编辑器窗口/视口可以有不同的命令上下文
- **通过蓝图控制命令执行条件**：支持 `CanExecute` 委托，实现条件性命令执行

简单来说，这个 plugin 让你**不需要写 C++ 模块代码**，就能在蓝图中创建带有键盘快捷键的编辑器命令——这在原生 Slate 框架中通常需要 C++ 和 `FUICommandInfo` 的样板代码。

## 使用场景

- 你在做一个编辑器工具插件，需要为自定义操作绑定快捷键，但不想写 C++ → 用 SlateScripting
- 你需要让蓝图脚本能响应编辑器中的键盘输入（如 Ctrl+Shift+X 触发某个操作）→ 用 SlateScripting
- 你需要动态地启用/禁用一组编辑器命令（比如在特定编辑器模式下）→ 用 SlateScripting 的 Command Set 功能
- 你在开发 Editor Utility Widget，需要绑定自定义快捷键 → 用 SlateScripting

## 蓝图用法

### 核心节点

所有蓝图节点都通过 `UUICommandsScriptingSubsystem` 访问，在蓝图中搜索 "Editor Scripting | Commands" 即可找到。

#### 命令集管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register Command Set` | 注册一个新的命令集，必须先于注册命令执行 | `UUICommandsScriptingSubsystem` |
| `Unregister Command Set` | 注销命令集及其所有命令 | `UUICommandsScriptingSubsystem` |
| `Is Command Set Registered` | 检查命令集是否已注册 | `UUICommandsScriptingSubsystem` |
| `Set Can Execute Commands` (Set) | 启用/禁用某个命令集中所有命令的执行 | `UUICommandsScriptingSubsystem` |
| `Can Execute Commands` (Set) | 检查某个命令集是否可执行 | `UUICommandsScriptingSubsystem` |

#### 命令注册

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Register Command` | 注册一个命令，绑定执行回调和可选的快捷键 | `UUICommandsScriptingSubsystem` |
| `Register Command Checked` | 同上，额外支持 `CanExecute` 回调来控制命令是否可执行 | `UUICommandsScriptingSubsystem` |
| `Unregister Command` | 注销一个已注册的命令 | `UUICommandsScriptingSubsystem` |
| `Is Command Registered` | 检查命令是否已注册 | `UUICommandsScriptingSubsystem` |
| `Get Registered Commands` | 获取所有已注册命令的列表 | `UUICommandsScriptingSubsystem` |

#### 全局控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Can Execute Commands` (Global) | 全局启用/禁用所有脚本命令的执行 | `UUICommandsScriptingSubsystem` |
| `Can Execute Commands` (Global) | 检查全局命令执行状态 | `UUICommandsScriptingSubsystem` |
| `Unregister All Sets` | 注销所有命令集及命令 | `UUICommandsScriptingSubsystem` |

#### 上下文查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Available Contexts` | 获取所有已注册的上下文名称列表 | `UUICommandsScriptingSubsystem` |
| `Is Context Registered` | 检查上下文是否已注册 | `UUICommandsScriptingSubsystem` |
| `Get Binding Count For Context` | 获取某个上下文中已绑定的 UI Command List 数量 | `UUICommandsScriptingSubsystem` |
| `Is Input Chord Mapped` | 检查某个快捷键是否已在指定上下文中被映射 | `UUICommandsScriptingSubsystem` |

### 使用示例（蓝图描述）

#### 示例 1：注册一个带快捷键的命令

1. **BeginPlay** 中，使用 `Register Command Set` 节点注册一个名为 `"MyToolCommands"` 的命令集
2. 创建一个 `FScriptingCommandInfo` 结构体：
   - `ContextName` = `"LevelEditor"` （编辑器关卡视口的上下文）
   - `Set` = `"MyToolCommands"`
   - `Name` = `"MyCustomAction"`
   - `Label` = `"执行自定义操作"`
   - `Description` = `"触发自定义工具操作"`
   - `InputChord` = 设置你想要的快捷键（如 Ctrl+Shift+T）
3. 使用 `Register Command` 节点，传入上面的 CommandInfo 和一个 `FExecuteCommand` 委托
4. 在委托回调中实现你的逻辑

#### 示例 2：带条件检查的命令

1. 同上注册命令集
2. 使用 `Register Command Checked` 节点，额外传入 `FCanExecuteCommand` 委托
3. 在 `CanExecute` 回调中返回 true/false 来控制命令是否可用（例如：只在选中特定 Actor 时可用）

## C++ 用法

### 头文件引入

```cpp
#include "UICommandsScriptingSubsystem.h"
```

### 基本用法

以下代码展示了如何在 C++ 中通过子系统注册命令：

```cpp
// 获取子系统实例
UUICommandsScriptingSubsystem* Subsystem = GEngine->GetEngineSubsystem<UUICommandsScriptingSubsystem>();

// 1. 注册命令集
Subsystem->RegisterCommandSet(FName("MyPluginCommands"));

// 2. 构建命令信息
FScriptingCommandInfo CommandInfo;
CommandInfo.ContextName = FName("LevelEditor");
CommandInfo.Set = FName("MyPluginCommands");
CommandInfo.Name = FName("MyAction");
CommandInfo.Label = NSLOCTEXT("MyPlugin", "MyAction", "My Custom Action");
CommandInfo.Description = NSLOCTEXT("MyPlugin", "MyActionDesc", "Executes a custom action");
CommandInfo.InputChord = FInputChord(EKeys::T, EModifierKey::Control | EModifierKey::Shift);

// 3. 注册命令（蓝图/脚本风格的委托）
FExecuteCommand OnExecute;
OnExecute.BindDynamic(/* your delegate */);
Subsystem->RegisterCommand(CommandInfo, OnExecute);
```

### 进阶用法

使用 `RegisterCommandChecked` 注册带条件检查的命令：

```cpp
FScriptingCommandInfo CommandInfo;
CommandInfo.ContextName = FName("LevelEditor");
CommandInfo.Set = FName("MyPluginCommands");
CommandInfo.Name = FName("ConditionalAction");
CommandInfo.Label = NSLOCTEXT("MyPlugin", "CondAction", "Conditional Action");
CommandInfo.InputChord = FInputChord(EKeys::G, EModifierKey::Control);

FExecuteCommand OnExecute;
OnExecute.BindDynamic(/* execute delegate */);

FCanExecuteCommand OnCanExecute;
OnCanExecute.BindDynamic(/* can-execute delegate, returns bool */);

// 注册带条件检查的命令
Subsystem->RegisterCommandChecked(CommandInfo, OnExecute, OnCanExecute);
```

手动管理命令列表（对于 C++ 模块开发者）：

```cpp
// 如果你的模块有自己的 FUICommandList，可以将其暴露给子系统
TSharedRef<FUICommandList> MyCommandList = MakeShareable(new FUICommandList());
Subsystem->RegisterCommandListForContext(FName("MyCustomContext"), MyCommandList);
```

### 数据结构说明

#### FScriptingCommandInfo

脚本命令的核心数据结构，所有字段均为 `BlueprintReadWrite`：

| 字段 | 类型 | 说明 |
|---|---|---|
| `ContextName` | `FName` | 命令绑定的编辑器上下文（如 `"LevelEditor"`） |
| `Set` | `FName` | 命令所属的集合，用于避免冲突 |
| `Name` | `FName` | 命令名称，在同一 Set 中必须唯一 |
| `Label` | `FText` | 显示名称 |
| `Description` | `FText` | 命令描述 |
| `InputChord` | `FInputChord` | 绑定的键盘快捷键 |

命令的全名格式为 `ContextName.Set.Name`，用于在 InputBindingManager 中唯一标识。

#### 委托类型

| 委托 | 签名 | 说明 |
|---|---|---|
| `FExecuteCommand` | `void(FScriptingCommandInfo)` | 命令执行时的回调 |
| `FCanExecuteCommand` | `bool(FScriptingCommandInfo)` | 检查命令是否可执行的回调 |

## Demo 示例

以下是一个完整的最小示例，展示如何在 Editor Utility 蓝图中注册一个带快捷键的命令。

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Slate",
    "SlateCore",
    "Engine",
    "SlateScriptingCommands"
});
```

### C++ 最小示例

```cpp
// MyEditorTool.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "UICommandsScriptingSubsystem.h"
#include "MyEditorTool.generated.h"

UCLASS()
class UMyEditorToolCommands : public UEditorSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override
    {
        Super::Initialize(Collection);

        UUICommandsScriptingSubsystem* CmdSubsystem = GEngine->GetEngineSubsystem<UUICommandsScriptingSubsystem>();
        if (!CmdSubsystem) return;

        // 注册命令集
        CmdSubsystem->RegisterCommandSet(FName("MyEditorTool"));

        // 注册命令
        FScriptingCommandInfo Info;
        Info.ContextName = FName("LevelEditor");
        Info.Set = FName("MyEditorTool");
        Info.Name = FName("SayHello");
        Info.Label = NSLOCTEXT("MyTool", "SayHello", "Say Hello");
        Info.Description = NSLOCTEXT("MyTool", "SayHelloDesc", "Prints a hello message");
        Info.InputChord = FInputChord(EKeys::H, EModifierKey::Control | EModifierKey::Alt);

        FExecuteCommand OnExecute;
        OnExecute.BindDynamic(this, &UMyEditorToolCommands::HandleSayHello);

        CmdSubsystem->RegisterCommand(Info, OnExecute);
    }

    virtual void Deinitialize() override
    {
        if (GEngine)
        {
            UUICommandsScriptingSubsystem* CmdSubsystem = GEngine->GetEngineSubsystem<UUICommandsScriptingSubsystem>();
            if (CmdSubsystem)
            {
                CmdSubsystem->UnregisterCommandSet(FName("MyEditorTool"));
            }
        }
        Super::Deinitialize();
    }

    UFUNCTION()
    void HandleSayHello(FScriptingCommandInfo CommandInfo)
    {
        UE_LOG(LogTemp, Display, TEXT("Hello from SlateScripting! Command: %s"), *CommandInfo.GetFullName().ToString());
    }
};
```

## 模块依赖

从 `SlateScriptingCommands.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统（反射、序列化） |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心类型和渲染 |
| `Engine` | 引擎核心（Subsystem 系统等） |
| `InputCore` (Private) | 输入系统核心（按键定义等） |

使用者需要在自己的模块中依赖 `SlateScriptingCommands` 模块才能使用 `UUICommandsScriptingSubsystem`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `9803c443` | Added `UE_INLINE_GENERATED_CPP_BY_NAME` to source files | 代码生成优化，自动工具批量修改，非功能性变更 |
| 2025-06-11 | `b978b4ff` | Replace some usages of `FORCEINLINE` with `inline` in Slate modules | 代码规范统一，非功能性变更 |
| 2025-05-30 | `2739c3d3` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types | DLL 导出规范化，非功能性变更 |

### 维护评价

- **创建时间**：2021-10-06，约 4.5 年前
- **最近更新**：最近 3 次 commit（2025 年 5-7 月）均为工具驱动的代码规范化修改，非功能性更新
- **实质性功能更新**：未在近期 commit 中发现功能性变更，表明该 plugin 已处于**稳定状态**
- **启用状态**：`EnabledByDefault: false`，需要手动在项目设置中启用
- **已知限制**：
  - 没有找到测试用例
  - 无官方文档链接（`DocsURL` 为空）
  - 功能相对单一，仅封装了命令注册/注销流程
- **推荐程度**：✅ 推荐使用。这是一个小而稳定的工具 plugin，适合需要在蓝图中快速注册编辑器命令的场景。代码质量良好，结构清晰。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Slate/SlateScripting)
- [UICommandsScriptingSubsystem.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Slate/SlateScripting/Source/SlateScriptingCommands/Public/UICommandsScriptingSubsystem.h)
- [UICommandsScriptingSubsystem.cpp](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Slate/SlateScripting/Source/SlateScriptingCommands/Private/UICommandsScriptingSubsystem.cpp)
- [FInputBindingManager](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Slate/Public/Framework/Commands/InputBindingManager.h) — 底层命令绑定管理器
- [FUICommandInfo](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Slate/Public/Framework/Commands/UICommandInfo.h) — UI 命令信息
