# Sandboxed Editing

> Allows editing of files in sandbox enviroments. Edited files can be persisted into your main project files.

| 属性 | 值 |
|---|---|
| 分类 | Developer |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SandboxedEditing` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Sandbox/SandboxedEditing) | |

## 用途

Sandboxed Editing 是一个面向开发者的编辑器工具，它为 Unreal Engine 项目提供了一个安全的、隔离的“沙盒”环境。其核心目的是解决在开发过程中直接修改项目资产可能带来的风险和混乱。

**解决的问题：**
1.  **安全实验**：开发者可以在沙盒中自由地修改、创建或删除资产，而无需担心破坏主项目的稳定性或版本历史。
2.  **变更管理**：所有在沙盒中的修改都被记录和跟踪。开发者可以清晰地看到哪些文件被添加、修改或删除。
3.  **选择性持久化**：实验完成后，开发者可以选择将沙盒中的特定修改（或全部修改）合并回主项目，丢弃不想要的更改。这提供了一种比直接提交更灵活的“试错”工作流。
4.  **工作流隔离**：特别适用于需要并行开发多个功能分支或进行高风险重构的场景，每个沙盒相当于一个轻量级的、工作区级别的分支。

**为什么存在：**
它填补了版本控制系统（如 Git）和 Unreal Engine 编辑器原生工作流之间的一个空白。Git 管理的是文件级别的提交，而 Sandboxed Editing 管理的是编辑器会话级别的、资产感知的变更。它让开发者在不离开编辑器的情况下，就能获得类似“分支”和“合并”的能力，但操作粒度更贴近内容创作（资产、蓝图等）。

## 使用场景

-   **功能原型开发**：你正在尝试一个可能大幅修改现有资产结构的新功能。使用沙盒进行开发，如果效果不佳，可以轻松丢弃整个沙盒，主项目毫发无损。
-   **资产重构**：你需要重命名大量资产或重组文件夹结构。在沙盒中操作，可以逐步验证每一步的影响，最后一次性将成功的重构应用到主项目。
-   **多人协作**：团队成员可以在各自的沙盒中独立工作，避免直接在共享的主项目上产生冲突。完成后，各自将经过验证的更改合并回来。
-   **教学与演示**：在教学或演示环境中，可以创建一个沙盒供学员自由操作，演示结束后重置，不影响原始项目。

## 蓝图用法

根据提供的源码分析，此插件主要通过 C++ 和编辑器 UI 进行交互，未发现直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`。其核心功能（创建、进入、离开、持久化沙盒）通过编辑器菜单和专用的浏览器 UI 面板触发。

### 核心 UI 交互

| 操作 | 说明 | 触发方式 |
|---|---|---|
| 打开沙盒浏览器 | 打开一个用于管理所有沙盒的标签页 | 通过编辑器菜单或命令（`FBrowserCommands::SummonUI`） |
| 创建新沙盒 | 创建一个新的、空的沙盒环境 | 浏览器 UI 中的“创建”按钮或命令 |
| 进入沙盒 | 激活一个沙盒，使编辑器在该沙盒的上下文中工作 | 在浏览器中选择一个沙盒并加载 |
| 离开沙盒 | 退出当前沙盒，返回主项目上下文 | 浏览器 UI 或命令（`FBrowserCommands::LeaveSandbox`） |
| 持久化沙盒 | 将当前沙盒中的更改合并到主项目 | 浏览器 UI 或命令（`FBrowserCommands::PersistSandbox`） |
| 查看文件状态 | 查看当前沙盒或某个未加载沙盒中所有被修改的文件列表 | 浏览器 UI 中的文件状态列表视图 |

## C++ 用法

此插件的 C++ API 主要面向插件内部模块和需要深度集成沙盒系统的开发者。核心交互通过 `FSandboxSystemModel` 进行。

### 头文件引入

```cpp
#include "Features/Browser/ViewModels/BrowserViewModels.h" // 包含所有视图模型
#include "Framework/Models/SandboxSystemModel.h" // 核心沙盒系统模型
```

### 基本用法

以下示例展示了如何通过模型层与沙盒系统交互。注意：实际使用中，这些操作通常由插件的 UI 层（ViewModels）封装和调用。

```cpp
// 假设你已经获取了 FSandboxSystemModel 的共享引用
TSharedRef<UE::SandboxedEditing::FSandboxSystemModel> SandboxModel = ...;

// 1. 获取所有沙盒的列表
TArray<FSandboxInfo> AllSandboxes = SandboxModel->GetAllSandboxes();

// 2. 创建一个新的沙盒
FSandboxInfo NewSandboxInfo;
NewSandboxInfo.Name = TEXT("MyTestSandbox");
NewSandboxInfo.Description = TEXT("用于测试新材质系统");
SandboxModel->CreateSandbox(NewSandboxInfo);

// 3. 加载（进入）一个沙盒
FString SandboxRootPath = TEXT(".../Sandboxes/MyTestSandbox");
SandboxModel->LoadSandbox(SandboxRootPath);

// 4. 检查当前是否在沙盒中
bool bIsSandboxed = SandboxModel->IsSandboxed();

// 5. 获取当前沙盒的文件变更
if (bIsSandboxed)
{
    FileSandboxCore::FGatheredFileChanges Changes = SandboxModel->GatherCurrentSandboxChanges();
    // 处理 Changes 中的文件列表...
}

// 6. 持久化（提交）当前沙盒的更改
SandboxModel->PersistCurrentSandbox();

// 7. 离开（卸载）当前沙盒
SandboxModel->LeaveSandbox();
```

### 进阶用法

插件内部采用了 MVVM 模式，ViewModels 处理复杂的 UI 逻辑和状态管理。例如，`FLeaveSandboxViewModel` 封装了离开沙盒时可能涉及的多步工作流（询问脏包、询问是否持久化等）。

```cpp
// 通过 FBrowserViewModels 访问更高级的 UI 逻辑
TSharedRef<UE::SandboxedEditing::FBrowserViewModels> BrowserViewModels = ...;

// 监听沙盒加载/离开事件
BrowserViewModels->ActiveSandboxTrackerViewModel->OnLoadSandbox().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("已进入沙盒模式"));
});
BrowserViewModels->ActiveSandboxTrackerViewModel->OnLeaveSandbox().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("已离开沙盒模式"));
});

// 触发离开沙盒的流程（会处理脏包和持久化询问）
BrowserViewModels->LeaveViewModel->LeaveSandbox();
```

## Demo 示例

由于此插件主要提供编辑器工具和内部 C++ 模型，没有独立的运行时组件。一个最小的集成示例是创建一个自定义编辑器按钮来触发沙盒浏览器。

```cpp
// MySandboxCommands.h
#pragma once
#include "Framework/Commands/Commands.h"

class FMySandboxCommands : public TCommands<FMySandboxCommands>
{
public:
    FMySandboxCommands();
    virtual void RegisterCommands() override;
    TSharedPtr<FUICommandInfo> OpenSandboxBrowser;
};

// MySandboxCommands.cpp
#include "MySandboxCommands.h"
#include "SandboxedEditing.h" // 插件主模块头文件

#define LOCTEXT_NAMESPACE "MySandboxCommands"

FMySandboxCommands::FMySandboxCommands()
    : TCommands<FMySandboxCommands>(
        TEXT("MySandboxCommands"),
        LOCTEXT("MySandboxCommands", "My Sandbox Commands"),
        NAME_None,
        FAppStyle::GetAppStyleSetName())
{
}

void FMySandboxCommands::RegisterCommands()
{
    UI_COMMAND(OpenSandboxBrowser, "Sandbox Browser", "Open the Sandboxed Editing browser", EUserInterfaceActionType::Button, FInputChord());
}

#undef LOCTEXT_NAMESPACE

// 在你的编辑器模块启动时注册命令和按钮
void FMyEditorModule::StartupModule()
{
    FMySandboxCommands::Register();
    
    TSharedPtr<FUICommandList> CommandList = MakeShareable(new FUICommandList);
    CommandList->MapAction(
        FMySandboxCommands::Get().OpenSandboxBrowser,
        FExecuteAction::CreateLambda([]()
        {
            // 通过插件模块接口打开浏览器
            if (UE::SandboxedEditing::ISandboxedEditingModule::IsAvailable())
            {
                // 假设插件模块提供了获取 BrowserFeature 的方法
                // UE::SandboxedEditing::ISandboxedEditingModule::Get().GetBrowserFeature()->SummonUI();
            }
        }),
        FCanExecuteAction());
    
    // 将 CommandList 注册到编辑器工具栏...
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FileSandbox` | 提供底层的文件系统沙盒隔离和文件变更跟踪核心功能。 |
| `NamingTokens` | 可能用于处理沙盒路径或名称中的变量/标记替换。 |

## 维护状态

### 近期更新

-   `f0484590` 2026-04-22 — 修复进入沙盒时未能正确清除（purge）包的问题。
-   `75ea6cb1` 2026-04-22 — 用户更改默认沙盒文件夹后，刷新沙盒列表。
-   `237fa750` 2026-04-22 — 防止用户在 PIE（Play In Editor）或 SIE（Simulate In Editor）期间离开沙盒，避免热重载引发问题。
-   `35e60df1` 2026-04-14 — 将 UE_LOG 迁移至 UE_LOGF（可能是格式化日志宏）。
-   `616903db` 2026-04-13 — 为沙盒文件添加内容浏览器徽章功能。

### 维护评价

-   **创建时间**：插件非常新（创建于 2026 年 4 月）。
-   **更新频率**：在创建后的一周内有多次提交，表明处于**积极开发**阶段。
-   **维护状态**：**活跃维护中**。最近的提交修复了关键功能问题（如脏包处理、PIE 兼容性），并添加了新功能（内容浏览器徽章）。
-   **已知限制**：`.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着它仍处于实验阶段，API 和功能可能不稳定，不建议在生产项目中依赖。
-   **推荐使用**：**推荐用于实验和开发测试**。对于希望尝试沙盒化工作流的开发者，这是一个值得关注的前沿工具。但由于其实验性质，使用时需做好备份，并预期可能遇到未解决的问题。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Sandbox/SandboxedEditing)
-   [官方文档]() （暂无）
-   [测试用例]() （未在提供的源码片段中发现）