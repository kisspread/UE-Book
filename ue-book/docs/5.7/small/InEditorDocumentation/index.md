# In-Editor Documentation

> Navigate a configured tutorial within the Unreal Editor as you explore a project.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器内文档 |
| 分类 | Learning |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Settings 类、Slate UI、WebBrowser 集成） |
| 模块 | `InEditorDocumentation` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-30 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InEditorDocumentation) | |

## 用途

该插件为 Unreal Editor 提供**内嵌的文档浏览器**，允许用户在编辑器内直接打开并导航预设的教程页面（基于 Web 技术），同时**实验性地支持根据选中的 Actor 自动搜索官方文档**。它解决的是传统开发过程中频繁切换编辑器与外部浏览器查阅文档的痛点，通过将文档集成到编辑器窗口和快捷菜单中，提升学习与工作的连贯性。

## 使用场景

- 你正在制作一个新手引导项目，希望玩家或同事在编辑器内直接访问官方教程 → 配置 `TutorialUrl` 后点击“Open Tutorial”即可打开
- 你希望根据当前选中的 Actor（如 `StaticMeshActor`）快速查看对应的官方文档 → 启用搜索功能，自动调用 EDC（Epic Developer Community）API 获取结果
- 你需要为特定的 Actor 类型预设自定义文档链接 → 编辑 `DocumentationPages` 映射表即可

## 蓝图用法

该插件目前**不提供任何公开的蓝图可调用节点**（无 `UFUNCTION(BlueprintCallable)` 或无 `UPROPERTY(BlueprintReadWrite)`）。所有功能均通过编辑器菜单、命令绑定和 C++ 接口实现。若你需要在蓝图项目中触发文档打开或搜索，可以考虑通过自定义蓝图函数库封装该插件的 C++ API。

### C++ 接口暴露给蓝图

暂无可直接调用的蓝图函数，所有功能由编辑器模块自动提供。

## C++ 用法

### 头文件引入

```cpp
#include "InEditorDocumentation.h"
#include "InEditorDocumentationSettings.h"
#include "DocumentationCommands.h"
```

### 基本用法

该插件主要作为编辑器模块运行，开发者通常只需在项目设置中配置 URL 和搜索选项即可。以下是从 `InEditorDocumentation.cpp` 中提取的初始化流程（部分简化）：

```cpp
// InEditorDocumentation.cpp

void FInEditorDocumentationModule::StartupModule()
{
    // 注册 Slate 样式
    FCommandsStyle::Initialize();
    FCommandsStyle::ReloadTextures();

    // 注册命令
    FDocumentationCommands::Register();

    // 绑定命令到 UI
    PluginCommands = MakeShareable(new FUICommandList);
    PluginCommands->MapAction(
        FDocumentationCommands::Get().OpenTutorial,
        FExecuteAction::CreateRaw(this, &FInEditorDocumentationModule::OnToggleTutorialClicked),
        FCanExecuteAction()
    );

    // 注册设置页面
    ModuleConfigSettings = RegisterSettings();

    // 将“Open Tutorial”按钮添加到主菜单（Level Editor 菜单栏）
    // 详见 AddMenuEntry() 实现

    // 若启用搜索，注册 Actor 选择变化时的回调
    if (USelection::SelectionChangedEvent.IsBound())
    {
        USelection::SelectionChangedEvent.AddRaw(this, &FInEditorDocumentationModule::OnActorSelectionChanged);
    }
}
```

### 进阶用法

#### 自定义 Actor 文档映射

在 `DefaultEngine.ini` 或项目设置中配置 `DocumentationPages`，指定某个 Actor 类对应的文档 URL：

```ini
[/Script/InEditorDocumentation.InEditorDocumentationSettings]
+DocumentationPages=(Key="StaticMeshActor", Value="https://dev.epicgames.com/documentation/unreal-engine/static-mesh-actors")
+DocumentationPages=(Key="BlueprintActor", Value="https://dev.epicgames.com/documentation/unreal-engine/blueprint-actors")
```

然后在 C++ 中可获取该映射：

```cpp
#include "InEditorDocumentationSettings.h"

UInEditorDocumentationSettings* Settings = GetMutableDefault<UInEditorDocumentationSettings>();
if (Settings->DocumentationPages.Contains("StaticMeshActor"))
{
    FString URL = Settings->DocumentationPages["StaticMeshActor"];
    // 打开该 URL
}
```

#### 开启 EDC 搜索

在项目设置中（Editor → Plugins → In-Editor Documentation）将 **Enable Edc Search** 设为 true。之后在视口中选择一个 Actor，插件会自动向配置的 `EdcSearchApiEndpoint` 发送搜索请求，并在一个浮动窗口中显示结果。

## Demo 示例

以下是一个最小的 C++ 模块示例，它展示了如何在编辑器启动后立即打开一个自定义文档页面。假设你已经启用了该插件。

```cpp
// MyDocumentationOpener.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FMyDocumentationOpenerModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
};
```

```cpp
// MyDocumentationOpener.cpp
#include "MyDocumentationOpener.h"
#include "InEditorDocumentation.h"   // 引用插件模块

void FMyDocumentationOpenerModule::StartupModule()
{
    // 获取插件模块实例并调用其内部方法来打开特定 URL
    FInEditorDocumentationModule& DocModule = FModuleManager::LoadModuleChecked<FInEditorDocumentationModule>("InEditorDocumentation");
    // 注意：该插件未公开 OpenURL 方法，此示例仅为概念演示。实际需通过 Slate 窗口或命令触发。
    // 正确的做法是触发已注册的 OpenTutorial 命令：
    if (FDocumentationCommands::Get().OpenTutorial->CanExecute())
    {
        FDocumentationCommands::Get().OpenTutorial->Execute();
    }
}

IMPLEMENT_MODULE(FMyDocumentationOpenerModule, MyDocumentationOpener)
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `WebBrowserWidget` | 在 Slate UI 中嵌入 Chromium Web 浏览器，用于显示文档页面 |
| `Projects` | 读取 `UProject` 配置及插件列表 |
| (标准 Editor 模块) | `UnrealEd`, `LevelEditor`, `Settings` 等由插件隐式使用 |

> 你自身的模块若想使用该插件功能，只需在 `Build.cs` 中添加 `PublicDependencyModuleNames.AddRange(new string[] { "InEditorDocumentation" });` 即可。

## 维护状态

### 近期更新

- 2026-01-23 `a44e02a1` [InEditorDocumentation] Limit URLs opened to EDC URLs  
- 2025-10-17 `e942014b` #jira AUTODOC-1187  
- 2025-10-03 `09d046d9` Fix potential issue with top-level const declaration, and update comment.  
- 2025-10-03 `ca29c62d` Change some elements of page styling to match the editor a little more closely: font size also over  
- 2025-09-30 `4d215ed0` InEditorDocumentation Plugin  

### 维护评价

插件创建于 2025-09-30，至今（2026-10）约 1 年，属于**新插件**。从历史提交看，早期集中在界面样式和功能实现（2025-10），2026-01 有一个安全限制（限制只能打开 EDC URL）。此后 9 个月无更新，可能**维护不活跃**。当前仍标记为“实验性”，说明 Epic 尚未完全稳定。对于需要集成官方文档的编辑器工具场景，推荐使用，但需关注后续更新，避免因 API 变更导致兼容问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InEditorDocumentation)
- [官方文档](https://dev.epicgames.com/documentation/unreal-engine/)（插件内配置的默认文档地址）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/InEditorDocumentation/Tests/)（当前插件内无独立测试目录，但可参考主仓库的自动化测试）