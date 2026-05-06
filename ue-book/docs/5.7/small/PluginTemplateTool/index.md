# Plugin Template Tool

> Editor plugin for managing plugin template content folders.

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
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PluginTemplateTool) | |

---

## 用途

该插件为编辑器提供一个用于管理插件模板内容文件夹的工具。在 Unreal Engine 的插件模板系统中，开发者可以为自己的插件定义模板内容（例如默认资源、蓝图、材质等），这些内容存放在固定的文件夹中。`PluginTemplateTool` 提供了一个 Slate UI 界面，允许开发者浏览所有已知的插件模板，并手动挂载（Mount）或卸载（Unmount）其内容文件夹，以便在编辑器中访问或隐藏这些模板资源。

**解决什么问题？**  
当你有多个自定义插件模板，每个模板带有大量示例内容时，这些内容可能会在内容浏览器中造成混乱。该工具提供集中管理入口，让你灵活控制哪些模板内容对当前项目可见。

---

## 使用场景

- **模板开发阶段**：在开发插件模板时，需要频繁挂载/卸载测试内容，验证模板结构。
- **项目协作**：团队成员同时使用多个模板，每个成员只需挂载自己需要的模板内容，避免无关资源干扰。
- **内容整理**：在项目交付前，统一卸载所有模板内容，确保最终包体不包含多余模板资源。

---

## 蓝图用法

该插件未暴露任何蓝图可调用节点，所有功能仅在 C++ / Slate 编辑器界面中使用。

---

## C++ 用法

### 头文件引入

```cpp
#include "SPluginTemplateBrowser.h"
```

### 基本用法

核心类 `SPluginTemplateBrowser` 是一个 Slate 复合控件，可直接嵌入到编辑器选项卡或窗口。以下示例演示如何创建并显示该浏览器（来源：`SPluginTemplateBrowser.h`）：

```cpp
// 创建浏览器实例
TSharedRef<SPluginTemplateBrowser> Browser = SNew(SPluginTemplateBrowser);

// 将浏览器添加到某个父容器（例如 SDockTab 的内容）
ChildSlot
[
    Browser
];
```

### 进阶用法

`SPluginTemplateBrowser` 内部维护了一个 `FPluginTemplateListItem` 列表，每个列表项代表一个已知的插件模板文件夹。你可以通过扩展插件注册系统（`IPluginTemplateManager`）来添加自定义模板列表项，但该插件当前未提供公开接口，主要依赖内部收集逻辑（根据引擎中已加载的插件模板元数据自动填充）。

**模板项操作方法**：

- `OnMountClicked()` — 挂载该模板的内容文件夹到项目，使其在内容浏览器中可见。
- `OnUnmountClicked()` — 卸载该模板的内容文件夹。
- `GetVisibilityBasedOnMountedState()` — 返回 `EVisibility::Visible` 或 `EVisibility::Hidden`，用于 UI 按钮的可见性切换（挂载状态时显示“卸载”按钮，反之显示“挂载”按钮）。

这些方法是 `FPluginTemplateListItem` 的成员，通常通过 Slate 绑定到按钮的 `OnClicked` 事件。

---

## Demo 示例

以下为一个完整的最小可编译示例，展示如何在编辑器模块中注册一个选项卡并显示 `SPluginTemplateBrowser`。

**MyPluginToolModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"

class FMyPluginToolModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FTabManager> TabManager;
};
```

**MyPluginToolModule.cpp**
```cpp
#include "MyPluginToolModule.h"
#include "Widgets/Docking/SDockTab.h"
#include "SPluginTemplateBrowser.h"

IMPLEMENT_MODULE(FMyPluginToolModule, MyPluginTool)

void FMyPluginToolModule::StartupModule()
{
    // 注册编辑器选项卡
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner(
        "PluginTemplateBrowser",
        FOnSpawnTab::CreateLambda([](const FSpawnTabArgs&)
        {
            return SNew(SDockTab)
                .Label(NSLOCTEXT("PluginTemplateTool", "TabTitle", "Template Browser"))
                [
                    SNew(SPluginTemplateBrowser)
                ];
        })
    ).SetDisplayName(NSLOCTEXT("PluginTemplateTool", "TabDisplayName", "Plugin Template Browser"));
}

void FMyPluginToolModule::ShutdownModule()
{
    FGlobalTabmanager::Get()->UnregisterNomadTabSpawner("PluginTemplateBrowser");
}
```

*注：实际使用时需要确保 `PluginTemplateTool` 插件已启用且模块已加载。*

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

该插件未引入额外第三方依赖，`SPluginTemplateBrowser` 仅使用 Slate 和 Engine 核心库。

---

## 维护状态

### 近期更新

- 2024-05-01 a2b56134 — Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight. 全局 Slate 重构，影响所有 ListView 子类。非功能性更新。
- 2023-05-03 f5bc7442 — Fixing localization build warning. 修复本地化编译警告。
- 2023-05-02 3cd62302 — Adding a new Plugin Template Tool to assist in managing content belonging to a PluginTemplate. 初始创建。

### 维护评价

- **创建时间**：2023-05-02，距今约2年。
- **更新频率**：初始提交后仅有一次编译修复和一次全局 Slate 重构影响，无功能性更新超过1年。
- **活跃程度**：**维护不活跃**。尽管引擎整体仍在迭代，该插件自创建以来未增加新功能或修复用户报告的问题。
- **已知问题**：文档和测试用例缺失；仅支持 Slate UI，未暴露蓝图接口；可能与其他实验性插件存在交互问题。
- **推荐使用**：⚠️ 谨慎推荐。如果需要在编辑器内管理插件模板内容，该工具提供基础功能，但缺乏长期维护和文档。适合临时开发环境，不建议用于生产项目。

> **警告**：超过1年无实质性更新，且被标记为实验性（`IsBetaVersion=true`），可能在未来引擎版本中被移除或重构。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PluginTemplateTool)
- 官方文档：无（`DocsURL` 为空）
- 测试用例：无（未发现测试文件）