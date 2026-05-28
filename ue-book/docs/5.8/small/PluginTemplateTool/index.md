# Plugin Template Tool

> Editor plugin for managing plugin template content folders.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 插件模板工具 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginTemplateTool` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-05-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PluginTemplateTool) | |

## 用途

这个插件是一个编辑器内的工具，旨在解决插件模板内容管理的特定问题。它允许开发者在 Unreal Editor 中临时“挂载”一个插件模板的内容目录，从而可以安全地对模板中的资产（如材质、蓝图等）进行移动、编辑或检查，而不会直接修改原始模板文件。这对于基于模板创建新插件或调试模板内容非常有用。

## 使用场景

- 你正在基于一个已有的插件模板开发新的插件，并希望安全地查看或修改模板中的资产。
- 你需要将模板中的某些资产移动或复制到你自己的项目中，同时保持模板结构的完整性。
- 你是模板的维护者，需要在编辑器环境中对模板内容进行调试或验证。

## 蓝图用法

该插件主要提供一个 Slate UI 工具窗口，其核心功能未通过 `UFUNCTION` 暴露为蓝图可调用节点。

### 核心节点

无直接的蓝图节点。该工具通过编辑器菜单或命令进行访问。

### 使用示例（蓝图描述）

不适用。该插件的交互完全在编辑器 UI 层面完成。

## C++ 用法

该插件的核心是一个 Slate UI 工具类 `SPluginTemplateBrowser`。它的使用主要体现在编辑器 UI 的构建和生命周期管理中，而非作为底层库被其他模块广泛调用。

### 头文件引入

```cpp
// 注意：SPluginTemplateBrowser 是私有类，通常不直接在外部模块中包含。
// 如果要在插件内部扩展或修改此工具，可参考其结构。
#include "Private/SPluginTemplateBrowser.h"
```

### 基本用法

该插件的源码较少，`SPluginTemplateBrowser` 是其核心 UI 组件。一个简化的示例展示了如何构建一个包含模板列表和操作按钮的 Slate 控件。（来源：`SPluginTemplateBrowser.h`）

```cpp
// 创建并显示插件模板浏览器窗口
void FMyEditorModule::ShowPluginTemplateTool()
{
    // 创建 Slate 控件实例
    TSharedRef<SPluginTemplateBrowser> TemplateBrowser = SNew(SPluginTemplateBrowser);

    // 可以将此控件添加到编辑器的某个 Tab 或窗口中
    // 例如: MyTabManager->RegisterTabSpawner(...).SetContent(TemplateBrowser);
}
```

### 进阶用法

该插件的进阶用法在于理解并扩展 `FPluginTemplateListItem` 逻辑。每个列表项代表一个模板，它封装了挂载/卸载状态和路径逻辑。要添加新的模板源或改变行为，需要修改此结构及其相关函数。

```cpp
// 扩展 FPluginTemplateListItem 以支持新的模板发现逻辑
void AddCustomTemplateToList(TArray<TSharedPtr<FPluginTemplateListItem>>& ListItems, const FString& CustomTemplatePath)
{
    // 验证路径是否有效
    if (FPaths::DirectoryExists(CustomTemplatePath))
    {
        // 获取模板名称，例如从路径解析
        FText TemplateName = FText::FromString(FPaths::GetCleanFilename(CustomTemplatePath));
        // 创建列表项并添加
        ListItems.Add(MakeShared<FPluginTemplateListItem>(TemplateName, CustomTemplatePath));
    }
}
```

## Demo 示例

以下是一个最小化的编辑器模块示例，演示了如何集成 `SPluginTemplateBrowser` 控件。（注意：实际集成通常通过编辑器工具栏命令或 Tab 系统触发）

**MyPluginTemplateModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyPluginTemplateModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

    /** 切换插件模板工具窗口的可见性 */
    void TogglePluginTemplateTool();

private:
    /** 指向模板浏览器控件的弱指针，用于管理其生命周期 */
    TWeakPtr<SWidget> PluginTemplateToolWidget;
};
```

**MyPluginTemplateModule.cpp**
```cpp
#include "MyPluginTemplateModule.h"
#include "Private/SPluginTemplateBrowser.h" // 注意：路径需根据实际情况调整
#include "Widgets/Docking/SDockTab.h"
#include "Toolkits/AssetEditorManager.h"

static const FName PluginTemplateToolTabName("PluginTemplateTool");

void FMyPluginTemplateModule::StartupModule()
{
    // 可以在此处注册 Tab 生成器
    // FGlobalTabmanager::Get()->RegisterNomadTabSpawner(PluginTemplateToolTabName, FOnSpawnTab::CreateRaw(this, &FMyPluginTemplateModule::SpawnPluginTemplateTab))
    //     .SetDisplayName(FText::FromString(TEXT("Plugin Template Tool")))
    //     .SetMenuType(ETabSpawnerMenuType::Hidden);
}

void FMyPluginTemplateModule::ShutdownModule()
{
    // 注销 Tab 生成器
    // FGlobalTabmanager::Get()->UnregisterNomadTabSpawner(PluginTemplateToolTabName);
}

void FMyPluginTemplateModule::TogglePluginTemplateTool()
{
    // 尝试查找已打开的 Tab
    // TSharedPtr<SDockTab> ExistingTab = FGlobalTabmanager::Get()->FindExistingLiveTab(PluginTemplateToolTabName);
    // if (ExistingTab.IsValid())
    // {
    //     ExistingTab->DrawAttention();
    //     ExistingTab->ActivateInParent(ETabActivationCause::SetDirectly);
    //     return;
    // }
    //
    // // 如果未打开，则创建新的 Tab
    // FGlobalTabmanager::Get()->TryInvokeTab(PluginTemplateToolTabName);
}

// 假设的 Tab 生成函数
// TSharedRef<SDockTab> FMyPluginTemplateModule::SpawnPluginTemplateTab(const FSpawnTabArgs& Args)
// {
//     return SNew(SDockTab)
//         .TabRole(NomadTab)
//         [
//             SNew(SPluginTemplateBrowser)
//         ];
// }

IMPLEMENT_MODULE(FMyPluginTemplateModule, MyPluginTemplateModule)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-05-01 | `a2b56134` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. ItemHeight and ItemWidth are only us | Slate 框架 API 弃用更新，可能影响内部列表视图实现。 |
| 2023-05-03 | `f5bc7442` | Fixing localization build warning | 修复本地化构建警告。 |
| 2023-05-02 | `3cd62302` | Adding a new Plugin Template Tool to assist in managing content belonging to a PluginTemplate. The t | 首次提交，创建插件模板工具。 |

### 维护评价

**总体评价：实验性工具，维护不活跃。**

- **创建时间**：插件于 2023 年 5 月创建，年龄较短。
- **最近更新**：核心功能在 2023 年 5 月创建后，最近一次实质性相关更新（针对 Slate 弃用警告）发生在 2024 年 5 月，已超过一年。之后无活跃的功能开发或错误修复记录。
- **状态**：该插件标记为 **BetaVersion** 且 **EnabledByDefault: false**，表明它仍处于实验阶段，Epic 官方可能未将其作为最终解决方案推广。
- **使用建议**：由于其明确的实验状态和较低的维护频率，**不建议在生产环境的插件中直接依赖此工具**。它更适合用于学习 Slate UI 开发或作为特定工作流（如模板管理）的临时脚手架。如果需要生产级的插件模板管理功能，可能需要自行开发或寻找社区解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PluginTemplateTool)
- 官方文档：无