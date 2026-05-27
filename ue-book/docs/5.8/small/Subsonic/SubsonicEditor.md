# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音频事件编辑器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产定义，Slate样式） |
| 模块 | `SubsonicEditor` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

**SubsonicEditor** 是 **Subsonic** 音频创作系统的编辑器前端模块。它并非一个独立的运行时系统，而是为音频设计师提供了一套专用的资产编辑器和工具，用于创建、组织、预览和调试由 `SubsonicCore` 定义的 `USubsonicEventCollection` 资产。其核心功能是提供一个类似蓝图的、基于树状结构的事件与动作编辑界面，支持实时预览（Audition）、参数绑定、撤销/重做以及拖放操作，旨在简化复杂音频事件的编辑流程。

## 使用场景

*   你是一名游戏音效设计师，需要为一个复杂的游戏角色（如BOSS）创建一套复杂的、具有多种触发条件和混合逻辑的技能音效组合 → 使用 `SubsonicEditor` 来可视化编辑 `USubsonicEventCollection` 资产。
*   你需要为环境音系统设计一个动态的、由多个事件和动作构成的交互式音频逻辑（例如，根据天气和时间混合不同音效层） → 使用 `SubsonicEditor` 来搭建和预览整个事件树。
*   在开发过程中，你需要快速迭代音频设计，并希望在不运行游戏的情况下直接在编辑器中预听音频效果 → 使用 `SubsonicEditor` 的试听（Audition）功能。

## 蓝图用法

`SubsonicEditor` 主要是一个 C++ 的编辑器扩展模块，其提供的功能（如 `FEventCollectionEditor`）直接在编辑器UI中使用，通常不直接暴露给游戏逻辑蓝图。然而，它引入了 `USubsonicEditorSubsystem`，这是一个编辑器子系统，可能在更高级的编辑器脚本（Editor Utility Widget 或 Python 脚本）中提供辅助功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RebuildActionStructChildCache` | 重新构建动作结构体的缓存，用于在编辑器中快速查找和显示所有可注册的动作类型。通常在加载新模块后调用。 | `USubsonicEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键，选择“音频” -> “Subsonic 事件集合”来创建新的 `USubsonicEventCollection` 资产。
2.  **打开编辑器**：双击新创建的资产，将自动打开 `FEventCollectionEditor` 编辑器窗口。
3.  **编辑与预览**：
    *   左侧面板为事件树（Event Tree），可以添加事件（Event）和动作（Action）。
    *   中间或右侧是细节面板（Details），用于编辑选中事件或动作的属性。
    *   使用工具栏上的“播放”（Play）按钮来试听当前选中的事件。
    *   使用“停止”（Stop）按钮停止所有试听。

## C++ 用法

### 头文件引入

```cpp
#include "SubsonicEventCollectionEditor.h"
#include "SubsonicEditorSubsystem.h"
```

### 基本用法

**场景：通过代码打开一个已有的 `USubsonicEventCollection` 资产进行编辑。**
（基于 `FEventCollectionEditor::Init` 方法的使用模式推断）

```cpp
// 假设你已经获取了一个有效的 USubsonicEventCollection* 指针，例如通过 LoadObject
USubsonicEventCollection* MyEventCollection = LoadObject<USubsonicEventCollection>(nullptr, TEXT("/Game/Audio/MyBossEvents"));
if (MyEventCollection)
{
    // 获取编辑器子系统实例（可选，用于高级功能）
    USubsonicEditorSubsystem* EditorSubsystem = GEditor->GetEditorSubsystem<USubsonicEditorSubsystem>();
    // EditorSubsystem->RebuildActionStructChildCache(); // 如果需要刷新动作类型缓存

    // 创建编辑器实例并初始化
    TSharedRef<UE::Subsonic::Editor::FEventCollectionEditor> EventEditor = MakeShareable(new UE::Subsonic::Editor::FEventCollectionEditor());
    EventEditor->Init(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), *MyEventCollection);
}
```

### 进阶用法

**场景：在编辑器工具栏中注册一个自定义按钮，用于快速打开指定的 Subsonic 事件集合。**
这需要理解如何集成到编辑器的命令和菜单系统。

```cpp
// 1. 定义命令（例如在自定义的编辑器模块中）
class FMyAudioToolCommands : public TCommands<FMyAudioToolCommands>
{
public:
    FMyAudioToolCommands() : TCommands<FMyAudioToolCommands>(...) {}
    virtual void RegisterCommands() override
    {
        UI_COMMAND(OpenMyBossEvents, "Boss Events", "Open the Subsonic event collection for the boss", EUserInterfaceActionType::Button, FInputChord());
    }
    TSharedPtr<FUICommandInfo> OpenMyBossEvents;
};

// 2. 在工具栏或菜单中映射命令
// 3. 绑定命令处理函数
void FMyAudioToolModule::OpenMyBossEvents_Execute()
{
    USubsonicEventCollection* BossEvents = LoadObject<USubsonicEventCollection>(...);
    if (BossEvents)
    {
        FAssetEditorManager::Get().OpenEditorForAsset(BossEvents);
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何在编辑器工具栏添加一个按钮，点击后打开一个指定的 Subsonic 事件集合资产。

**MyAudioToolbarExtension.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Framework/Commands/UICommandList.h"

class FMyAudioToolbarExtension
{
public:
    static void Initialize();
    static void Shutdown();

private:
    static void RegisterMenus();
    static void OnOpenEventCollectionClicked();

    static TSharedPtr<FUICommandList> CommandList;
};
```

**MyAudioToolbarExtension.cpp**
```cpp
#include "MyAudioToolbarExtension.h"
#include "SubsonicEventCollection.h"
#include "AssetEditorManager.h"
#include "ToolMenus.h"
#include "Styling/SlateStyleRegistry.h"

TSharedPtr<FUICommandList> FMyAudioToolbarExtension::CommandList;

void FMyAudioToolbarExtension::Initialize()
{
    CommandList = MakeShareable(new FUICommandList);

    // 绑定命令
    CommandList->MapAction(
        FMyAudioToolCommands::Get().OpenMyBossEvents,
        FExecuteAction::CreateStatic(&FMyAudioToolbarExtension::OnOpenEventCollectionClicked),
        FCanExecuteAction());

    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateStatic(&FMyAudioToolbarExtension::RegisterMenus));
}

void FMyAudioToolbarExtension::Shutdown()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
    CommandList.Reset();
}

void FMyAudioToolbarExtension::RegisterMenus()
{
    // 向主菜单的“工具”扩展点添加一个菜单项
    FToolMenuOwnerScoped OwnerScoped(this);
    {
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
        FToolMenuSection& Section = Menu->FindOrAddSection("MyAudioTools");
        Section.AddMenuEntryWithCommandList(FMyAudioToolCommands::Get().OpenMyBossEvents, CommandList);
    }
}

void FMyAudioToolbarExtension::OnOpenEventCollectionClicked()
{
    // 替换为你的资产路径
    static const FSoftObjectPath BossEventCollectionPath("/Game/Audio/BP_BossEvents.BP_BossEvents");
    UObject* LoadedObject = BossEventCollectionPath.TryLoad();

    if (USubsonicEventCollection* EventCollection = Cast<USubsonicEventCollection>(LoadedObject))
    {
        FAssetEditorManager::Get().OpenEditorForAsset(EventCollection);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not load Subsonic Event Collection at %s"), *BossEventCollectionPath.ToString());
    }
}
```

## 模块依赖

从 `SubsonicEditor.Build.cs` 分析，使用者的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 的核心数据结构、类型和运行时逻辑 |
| `AudioWidgets` | 提供用于音频编辑的专业化 UI 控件（如波形、旋钮等） |
| `ToolWidgets` | 提供通用的编辑器工具 UI 控件 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复了合并冲突导致的代码覆盖问题，回退了不当的删除。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默了 PVS Studio 代码分析工具的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“新建”菜单中增加了音频相关资产的分类。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到格式更安全的 UE_LOGF。 |

### 维护评价

*   **活跃维护**：该插件创建于 2026 年初，最近的提交记录（2026年5月）显示 Epic 团队仍在积极进行维护和修复，特别是处理代码合并和编译警告。
*   **实验性警告**：插件明确标记为 `IsExperimentalVersion: true` 且位于 `Experimental` 目录下。这意味着其 API **没有稳定性保证**，可能会在后续版本中发生不兼容的变更、重构甚至移除。
*   **核心功能**：作为音频创作系统的关键编辑工具，只要 `SubsonicCore` 和整体音频系统持续开发，该编辑器模块就有存在的必要。
*   **推荐使用**：**谨慎推荐**。适用于需要强大可视化音频事件编辑功能的音频设计师和相关工具程序员。**强烈建议**在项目中使用时，将其视为“技术预览”或“实验性功能”，并准备好在引擎升级时进行适配工作。不建议用于追求长期稳定性的商业项目核心功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]() （无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest) （位于 SubsonicEngineTest 模块）