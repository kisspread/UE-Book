# UserToolBoxCore

> Core functionnality to create custom editor tab

| 属性 | 值 |
|---|---|
| 中文名 | 工具箱核心 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UserToolBoxCore` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UserToolBoxCore) | |

## 用途

UserToolBoxCore 是一个编辑器扩展框架，允许用户通过 DataAsset 配置文件快速创建自定义的编辑器标签页（Tab）。它提供了一系列基础类（命令、标签页、UI 模板、图标管理等），使得开发者无需编写大量 Slate UI 代码即可构建可排序、可拖拽、可配置的功能面板。核心价值在于将编辑器功能的组织和管理抽象为“命令-标签页”模型，并支持通过蓝图或 C++ 扩展。

## 使用场景

- 需要将一组编辑器操作（如批量处理资产、启动外部工具、切换 Viewport 模式）整合成可切换的标签页面板。
- 希望允许用户（甚至非程序员）通过编辑 DataAsset 来调整面板内命令的布局、图标、快捷键。
- 制作类似 UMG 控件编辑器中的“调色板”或“工具箱”，但内容可动态编辑且支持拖拽排序。
- 在编辑器模式下快速生成一个带有工具栏按钮的浮动或停靠面板。

## 蓝图用法

以下节点在蓝图中可直接调用，用于管理标签页、执行命令和访问图标资源。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExecuteCommand` | 执行当前命令（触发 `Execute()` 逻辑） | `UUTBBaseCommand` |
| `AddObjectToTransaction` / `AddObjectsToTransaction` | 将对象加入撤销/重做事务，保证命令执行可撤销 | `UUTBBaseCommand` |
| `PickAnIcon` | 弹出图标选择器，返回选中的图标 ID（字符串） | `UUserToolboxSubsystem` |
| `RegisterTabData` | 扫描 Content Browser 中所有 `UUserToolBoxBaseTab` 资产并注册 | `UUserToolboxSubsystem` |
| `GetAvailableTabList` | 获取所有已注册的标签页资产数据（`FAssetData` 数组） | `UUserToolboxSubsystem` |
| `RefreshIcons` | 重新从 DataAsset 加载外部图标，更新 Slate 样式 | `UUserToolboxSubsystem` |
| `GetBrushById` | 根据图标 ID 获取对应的 `SlateBrush`（用于 UI 显示） | `UUserToolBoxFunctionLibrary` |
| `GetAllSlateStyle` | 获取所有已注册的 Slate 样式名称（`FName` 数组） | `UUserToolBoxFunctionLibrary` |
| `GetBrushByStyleAndId` | 按样式名和 ID 获取特定 `SlateBrush` | `UUserToolBoxFunctionLibrary` |

### 使用示例（蓝图描述）

1. **在编辑器启动时注册标签页**：在 `EditorUtilityWidget` 的 `Construct` 事件中，调用 `Get Editor Subsystem (UUserToolboxSubsystem)` → `RegisterTabData`。然后使用 `GetAvailableTabList` 获取所有标签页，遍历并调用 `GenerateUI`（蓝图不可直接调用，但可借助 C++ 函数或 Slate 脚本）显示面板。

2. **执行自定义命令**：创建一个继承自 `UUTBBaseCommand` 的蓝图类，重写 `Execute` 事件。然后在标签页的按钮点击事件中调用 `ExecuteCommand` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "UserToolBoxCoreModule.h"
#include "UTBBaseCommand.h"
#include "UTBBaseTab.h"
#include "UserToolBoxSubsystem.h"
```

### 基本用法

**1. 创建自定义命令类**

```cpp
// MyCommand.h
#pragma once
#include "UTBBaseCommand.h"
#include "MyCommand.generated.h"

UCLASS()
class UMyCommand : public UUTBBaseCommand
{
    GENERATED_BODY()
public:
    virtual void Execute() override
    {
        // 执行具体操作，例如打开一个编辑器窗口
        FGlobalTabmanager::Get()->TryInvokeTab(FName("MyCustomTab"));
    }
};
```

**2. 通过子系统获取标签页并生成 UI**

```cpp
UUserToolboxSubsystem* Subsystem = GEditor->GetEditorSubsystem<UUserToolboxSubsystem>();
if (Subsystem)
{
    TArray<FAssetData> Tabs = Subsystem->GetAvailableTabList();
    for (const FAssetData& TabData : Tabs)
    {
        if (TabData.GetClass() == UUserToolBoxBaseTab::StaticClass())
        {
            // 生成标签页的 Slate Widget
            TSharedPtr<SWidget> TabWidget = Subsystem->GenerateTabUI(TabData);
            // 将 Widget 添加到某个面板中（例如 DockTab 的内容）
        }
    }
}
```

### 进阶用法

**组合使用 SCommandPickMenuWidget 选择命令**

```cpp
// 在某个编辑器 ToolTab 中创建命令选择器
SAssignNew(CommandPicker, SCommandPickMenuWidget)
    .OnCommandSelectionChanged_Lambda([this](UClass* SelectedClass)
    {
        // 根据选中的命令类创建实例，并添加到当前标签页
        UUTBBaseCommand* NewCmd = NewObject<UUTBBaseCommand>(GetTransientPackage(), SelectedClass);
        // 插入到指定 Section
        CurrentTab->AddCommand(NewCmd, "MySection", INDEX_NONE);
    });
```

## Demo 示例

以下是一个完整的、可编译的演示模块，展示如何创建自定义标签页并添加命令。

### MyToolBoxModule.h

```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "UTBBaseCommand.h"

DECLARE_LOG_CATEGORY_EXTERN(LogMyToolBox, Log, All);

class FMyToolBoxModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### MyToolBoxModule.cpp

```cpp
#include "MyToolBoxModule.h"
#include "UserToolBoxSubsystem.h"
#include "UTBBaseTab.h"
#include "UTBBaseCommand.h"

IMPLEMENT_MODULE(FMyToolBoxModule, MyToolBox);
DEFINE_LOG_CATEGORY(LogMyToolBox);

// 自定义命令：打印 Hello World
UCLASS()
class UHelloWorldCommand : public UUTBBaseCommand
{
    GENERATED_BODY()
public:
    virtual void Execute() override
    {
        UE_LOG(LogMyToolBox, Log, TEXT("Hello from UserToolBox!"));
    }
};

void FMyToolBoxModule::StartupModule()
{
    // 注册自定义命令到资产注册表（可选，用于显示在命令选择器中）
    // 实际使用中通常在 Content Browser 中创建 UUserToolBoxBaseTab 资产并手动添加命令

    // 示例：在编辑器启动后注册并显示一个标签页
    if (GEditor)
    {
        UUserToolboxSubsystem* Subsystem = GEditor->GetEditorSubsystem<UUserToolboxSubsystem>();
        if (Subsystem)
        {
            // 假设 Content Browser 中已存在一个名为 "MyToolTab" 的 UUserToolBoxBaseTab 资产
            FStringAssetReference TabRef(TEXT("/Game/Toolbox/MyToolTab.MyToolTab"));
            UUserToolBoxBaseTab* Tab = Cast<UUserToolBoxBaseTab>(TabRef.Resolve());
            if (Tab)
            {
                // 添加一个 HelloWorld 命令到默认 section
                UHelloWorldCommand* Cmd = NewObject<UHelloWorldCommand>(Tab);
                Cmd->Name = "Say Hello";
                Tab->AddCommand(Cmd, UUserToolBoxBaseTab::PlaceHolderSectionName, 0);
                
                // 强制刷新子系统
                Subsystem->RegisterTabData();
            }
        }
    }
}

void FMyToolBoxModule::ShutdownModule() {}
```

## 模块依赖

使用 UserToolBoxCore 插件时，你的模块需要添加以下依赖（省略常见 Core/Engine 等依赖）：

| 模块 | 用途 |
|---|---|
| `UserToolBoxCore` | 提供核心框架类（命令、标签页、UI 模板、子系统） |
| `SlateScripting` | 提供 Slate 脚本化支持，用于动态构建 UI |

## 维护状态

### 近期更新

| 日期 | Hash | Commit 说明 |
|---|---|---|
| 2025-02-13 | ec3fb596 | 替换 Engine 其余部分的 `IsValid(this)` 调用 |
| 2025-01-23 | 9d5c13a9 | 移除导致 MAC 编译失败的 inline 关键字 |
| 2024-11-15 | a2c3875d | 清理解决方案中使用了字体路径的 FSlateFontInfo 构造函数 |
| 2024-07-15 | a0b97622 | 当新增/移除/更新 UIconsTracker 资产时刷新图标 |
| 2024-05-02 | e0464783 | 弃用 SListView::ItemHeight 和 STreeViewItemHeight，改用 ItemWidth |

### 维护评价

- **创建时间**：2024-05-02，距今约 1 年。
- **近期更新**：最近 2 个月（2025 年 2 月）仍有功能性清理和编译修复，更新频率较高。
- **活跃度**：活跃维护中，Epic 持续进行代码现代化和问题修复。
- **已知问题**：实验性插件（`IsExperimentalVersion=true`），可能 API 尚未稳定，未来版本可能有重大变更。
- **推荐使用**：✅ 推荐。功能实用，架构清晰，适合快速构建编辑器面板。但需注意实验性状态，生产环境请评估风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UserToolBoxCore)
- [官方文档](https://docs.unrealengine.com/)（未提供专页，可参考 UE5 编辑器扩展文档中的“工具盒”相关章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UserToolBoxCore/Tests)（如存在）