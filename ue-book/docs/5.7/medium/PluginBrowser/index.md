# Plugin Browser

> User interface for managing installed plugins and creating new ones.

| 属性 | 值 |
|---|---|
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PluginBrowser` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2015-04-25 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/PluginBrowser) | |

## 用途

Plugin Browser 是 UE5 编辑器中的核心编辑器插件，提供了一个图形化界面用于：

1. **浏览和管理已安装插件** — 以分类树 + 磁贴列表的形式展示所有可用插件，支持按类别（Built-In、Project、Installed、External、Mods）筛选，支持文本搜索，支持按启用/禁用状态过滤
2. **创建新插件** — 通过向导式界面从内置模板（Blank、Content Only、Blueprint Library、Editor Toolbar Button、Editor Standalone Window、Editor Mode、Third Party Library）快速创建新插件
3. **编辑插件属性** — 打开插件的 `.uplugin` 描述文件进行可视化编辑，包括元数据（名称、描述、版本、分类、作者链接等）和依赖关系
4. **管理外部插件目录** — 配置额外的插件搜索路径（项目级、用户级、命令行、环境变量来源）
5. **打包插件** — 将插件打包为可分发的格式

该插件通过 `EditorFeatures::PluginsEditor` 注册为 Modular Feature，其他模块可以通过 `IPluginsEditorFeature` 接口注册自定义插件模板和编辑器扩展。

## 使用场景

- 你需要启用/禁用某个插件但不想手动编辑 `.uproject` 文件 → 打开 Edit > Plugins
- 你要从零开始创建一个新的 UE 插件 → 使用 New Plugin 向导选择模板
- 你想编辑某个插件的 `.uplugin` 元数据（版本、描述、依赖等）→ 右键插件文件夹选 Edit
- 你需要配置项目使用的外部插件目录 → 打开 Plugin Directories 标签页
- 你要打包一个插件用于 Marketplace 分发 → 右键插件选 Package

## 蓝图用法

Plugin Browser 是纯编辑器 UI 插件，不暴露 BlueprintCallable 节点。它完全通过 Slate UI 和编辑器菜单系统运作。

## C++ 用法

### 头文件引入

```cpp
#include "IPluginBrowser.h"
```

### 基本用法 — 获取模块实例

```cpp
// 检查模块是否可用并获取引用
if (IPluginBrowser::IsAvailable())
{
    IPluginBrowser& PluginBrowser = IPluginBrowser::Get();
}
```

### 注册自定义插件模板

其他模块可以向 Plugin Browser 注册额外的插件模板，这些模板会在 "New Plugin" 向导中显示：

```cpp
// 来自 DefaultPluginWizardDefinition.cpp
// 插件模板通过 FPluginBrowserModule 注册
TSharedRef<FPluginTemplateDescription> Template = MakeShareable(
    new FPluginTemplateDescription(
        FText::FromString(TEXT("My Template")),
        FText::FromString(TEXT("A custom plugin template.")),
        TemplateFolderPath,
        true,   // bSupportsContentOnlyProjects
        EHostType::Runtime
    )
);

FPluginBrowserModule::Get().RegisterPluginTemplate(Template);
```

### 注册插件编辑器扩展

```cpp
FOnPluginBeingEdited Extension;
Extension.BindLambda([](TSharedRef<IPlugin> Plugin, FPluginEditorExtension& OutExtension)
{
    // 添加自定义属性面板等扩展
});

FPluginEditorExtensionHandle Handle = 
    FPluginBrowserModule::Get().RegisterPluginEditorExtension(Extension);

// 取消注册
FPluginBrowserModule::Get().UnregisterPluginEditorExtension(Handle);
```

### 打开插件编辑器

```cpp
TSharedRef<IPlugin> Plugin = IPluginManager::Get().FindPlugin(TEXT("MyPlugin")).ToSharedRef();
FPluginBrowserModule::Get().OpenPluginEditor(Plugin, nullptr, FSimpleDelegate());
```

### 监听插件目录变更

```cpp
FPluginBrowserModule::Get().OnPluginDirectoriesChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Plugin directories changed!"));
});
```

### 监听新插件创建

```cpp
FPluginBrowserModule::Get().OnNewPluginCreated().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("A new plugin was created!"));
});
```

## Demo 示例

### 最小示例 — 自定义 New Plugin 向导

以下示例展示如何通过 `IPluginWizardDefinition` 自定义 "New Plugin" 向导的行为：

```cpp
// MyPluginWizardDefinition.h
#pragma once
#include "IPluginWizardDefinition.h"

class FMyPluginWizardDefinition : public IPluginWizardDefinition
{
public:
    FMyPluginWizardDefinition();

    // IPluginWizardDefinition 接口实现
    virtual const TArray<TSharedRef<FPluginTemplateDescription>>& GetTemplatesSource() const override;
    virtual void OnTemplateSelectionChanged(TSharedPtr<FPluginTemplateDescription> InSelectedItem, ESelectInfo::Type SelectInfo) override;
    virtual bool HasValidTemplateSelection() const override;
    virtual TSharedPtr<FPluginTemplateDescription> GetSelectedTemplate() const override;
    virtual void ClearTemplateSelection() override;
    virtual bool CanShowOnStartup() const override { return false; }
    virtual bool HasModules() const override;
    virtual bool IsMod() const override { return false; }
    virtual void OnShowOnStartupCheckboxChanged(ECheckBoxState CheckBoxState) override {}
    virtual ECheckBoxState GetShowOnStartupCheckBoxState() const override { return ECheckBoxState::Unchecked; }
    virtual TSharedPtr<SWidget> GetCustomHeaderWidget() override { return nullptr; }
    virtual FText GetInstructions() const override;
    virtual bool GetPluginIconPath(FString& OutIconPath) const override;
    virtual EHostType::Type GetPluginModuleDescriptor() const override;
    virtual ELoadingPhase::Type GetPluginLoadingPhase() const override;
    virtual bool GetTemplateIconPath(TSharedRef<FPluginTemplateDescription> InTemplate, FString& OutIconPath) const override;
    virtual FString GetPluginFolderPath() const override;
    virtual TArray<FString> GetFoldersForSelection() const override;
    virtual void PluginCreated(const FString& PluginName, bool bWasSuccessful) const override;

private:
    TArray<TSharedRef<FPluginTemplateDescription>> TemplateDefinitions;
    TSharedPtr<FPluginTemplateDescription> CurrentTemplateDefinition;
};
```

```cpp
// 使用自定义定义打开向导
FGlobalTabmanager::Get()->TryInvokeTab(
    FPluginBrowserModule::PluginCreatorTabName);
```

### Build.cs 依赖

如果你的模块需要与 PluginBrowser 交互：

```csharp
// MyModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Slate",
    "SlateCore",
});

PrivateDependencyModuleNames.AddRange(new string[]
{
    "PluginBrowser",  // 引用 PluginBrowser 模块
    "Projects",       // IPluginManager
});
```

## 模块依赖

### PluginBrowser 模块自身的依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、字符串、容器 |
| `CoreUObject` | UObject 系统、反射 |
| `InputCore` | 输入系统基础 |
| `Engine` | 引擎核心 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `PluginUtils` | 插件打包等工具函数 |
| `Projects` | IPluginManager、项目描述 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器核心功能 |
| `PropertyEditor` | 属性面板详情视图 |
| `SharedSettingsWidgets` | 设置界面组件 |
| `DirectoryWatcher` | 文件系统监听 |
| `GameProjectGeneration` | 项目生成工具 |
| `MainFrame` | 主窗口管理 |
| `UATHelper` | UAT 构建辅助 |
| `AssetTools` | 资产工具 |
| `Json` | JSON 解析 |
| `ToolWidgets` | 工具界面组件 |
| `ToolMenus` | 菜单扩展系统 |
| `EditorWidgets` | 编辑器通用组件 |
| `ContentBrowser` | 内容浏览器集成 |
| `ContentBrowserData` | 内容浏览器数据层 |

### 插件级依赖

| 插件 | 用途 |
|---|---|
| `PluginUtils` | 插件打包和分发工具 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-09-23 | `3854c186` | Fix: Show template projects from all plugins + update fallback image for template categories | 修复了模板项目展示逻辑，确保来自所有插件的模板都能正确显示，并更新了模板分类的默认图标 |
| 2025-07-31 | `4a0ce30c` | Fix a post build step error in the third party plugin template when the target directory does not exist | 修复第三方库插件模板的构建后步骤在目标目录不存在时报错的问题 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码优化，添加内联生成宏以减少编译时间 |

### 维护评价

- **年龄**：约 11 年（创建于 2015 年 4 月），属于 🏛️ 文物 级别
- **维护频率**：持续活跃维护中，最近 3 次更新在 2025 年 6-9 月，涵盖功能修复和代码优化
- **状态**：✅ 活跃维护 — 作为编辑器核心功能，由 Epic 团队持续维护
- **已知限制**：
  - 没有暴露 BlueprintCallable 节点，不可通过蓝图操作
  - 没有公开的测试用例
  - 对安装版本（Installed Build），不允许创建 Engine 级别的插件
- **推荐使用**：✅ 推荐 — 这是编辑器默认启用的核心插件，所有 UE 项目都会使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/PluginBrowser)
- [PluginUtils 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/PluginUtils) — PluginBrowser 的插件打包依赖
