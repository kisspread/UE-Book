# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 中文名 | 次声波音频系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产类型、样式资产） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个为游戏音频设计的**高级可视化编辑与播放系统**。它并非传统的音频波形编辑器，而是提供了一套结构化的事件驱动框架，用于组织和管理游戏中的复杂音频逻辑。

其核心思想是将音频的播放逻辑抽象为可配置的“事件集合”（Event Collection）。开发者或音频设计师可以在专用的资产编辑器中，以树形结构定义一系列“事件”（Event），每个事件下包含多个有序的“动作”（Action）。这些动作可以播放特定的音效、应用效果、设置参数等。该系统解决了游戏音频中逻辑复杂、难以维护和调试的问题，通过提供结构化、数据驱动的创作环境来提升音频工作流的效率。

## 使用场景

-   当你的游戏包含大量触发点、角色状态变化或环境交互，需要复杂的音频逻辑（如：受到攻击时播放受击音效、根据材质播放不同脚步声、伴随动态音乐层叠加）时，可以使用 Subsonic 来可视化地编排这些音频事件和播放序列。
-   当音频设计师需要与程序员协作，将音频参数（如音量、音调、效果器强度）与游戏状态动态绑定时，Subsonic 提供的属性绑定系统能简化这一过程。
-   当你需要在编辑器中快速预览和迭代音频效果组合，而无需进入游戏模式反复测试时，Subsonic 的编辑器内试听功能（Audition）可以大幅提高效率。

## 蓝图用法

根据源码分析，`SubsonicEditor` 模块主要提供编辑器内的工具和资产支持，核心的蓝图可调用功能（如播放事件）预计封装在 `SubsonicCore` 或 `SubsonicEngine` 模块中。当前模块中暴露的类主要用于编辑器扩展。

### 核心节点（编辑器子系统）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RebuildActionStructChildCache` | 重建可用动作类型的缓存列表，当加载新模块后可调用此函数刷新 | `USubsonicEditorSubsystem` |

### 使用示例（蓝图描述）

由于 `SubsonicEditor` 主要为编辑器提供服务，在常规游戏逻辑蓝图中可能不会直接使用。其主要功能体现在创建的“Subsonic Event Collection”资产上，该资产可通过其他模块提供的节点进行播放。

## C++ 用法

C++ 用法主要涉及编辑器的扩展和自定义。

### 头文件引入

```cpp
#include "SubsonicEditorSubsystem.h"
#include "SubsonicEventCollectionEditor.h"
```

### 基本用法

获取编辑器子系统并刷新动作缓存。
*（来源：SubsonicEditorSubsystem.h）*

```cpp
// 在适当的时机（如模块加载后）刷新动作列表缓存
USubsonicEditorSubsystem* SubEditorSystem = GEditor->GetEditorSubsystem<USubsonicEditorSubsystem>();
if (SubEditorSystem)
{
    SubEditorSystem->RebuildActionStructChildCache();
}
```

### 进阶用法

创建一个资产编辑器（IToolkit）来编辑自定义资产。
*（来源：SubsonicEventCollectionEditor.h）*

```cpp
// 假设已有一个 USubsonicEventCollection 资产实例
USubsonicEventCollection* MyEventCollection = /* ... */;

// 初始化并打开资产编辑器
TSharedRef<FEventCollectionEditor> Editor = MakeShareable(new FEventCollectionEditor());
Editor->Init(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), *MyEventCollection);
```

## Demo 示例

以下示例展示了如何创建一个简单的资产编辑器外壳。这通常在处理自定义资产类型时使用。
*(文件：MyAssetEditor.h / MyAssetEditor.cpp)*

```cpp
// MyAssetEditor.h
#pragma once
#include "AssetEditorToolkit.h"

class UMyCustomAsset;

class FMyAssetEditor : public FAssetEditorToolkit
{
public:
    // IToolkit Interface
    virtual void RegisterTabSpawners(const TSharedRef<FTabManager>& TabManager) override;
    virtual void UnregisterTabSpawners(const TSharedRef<FTabManager>& TabManager) override;
    virtual FName GetToolkitFName() const override;
    virtual FText GetBaseToolkitName() const override;
    virtual FString GetWorldCentricTabPrefix() const override;
    virtual FLinearColor GetWorldCentricTabColorScale() const override;

    // 自定义初始化函数
    void InitEditor(const EToolkitMode::Type Mode, const TSharedPtr<IToolkitHost>& InitToolkitHost, UMyCustomAsset* Asset);
};
```

```cpp
// MyAssetEditor.cpp
#include "MyAssetEditor.h"
#include "MyCustomAsset.h"

void FMyAssetEditor::RegisterTabSpawners(const TSharedRef<FTabManager>& TabManager)
{
    // 在此注册你的编辑器面板（Tab），例如详情面板、自定义视图等
    WorkspaceMenuCategory = TabManager->AddLocalWorkspaceMenuCategory(NSLOCTEXT("MyAssetEditor", "WorkspaceMenu_MyAssetEditor", "My Asset Editor"));
}

void FMyAssetEditor::UnregisterTabSpawners(const TSharedRef<FTabManager>& TabManager)
{
    FAssetEditorToolkit::UnregisterTabSpawners(TabManager);
}

FName FMyAssetEditor::GetToolkitFName() const
{
    return FName("MyAssetEditor");
}

FText FMyAssetEditor::GetBaseToolkitName() const
{
    return NSLOCTEXT("MyAssetEditor", "AppLabel", "My Asset");
}

FString FMyAssetEditor::GetWorldCentricTabPrefix() const
{
    return NSLOCTEXT("MyAssetEditor", "WorldCentricTabPrefix", "MyAsset ").ToString();
}

FLinearColor FMyAssetEditor::GetWorldCentricTabColorScale() const
{
    return FLinearColor::White;
}

void FMyAssetEditor::InitEditor(const EToolkitMode::Type Mode, const TSharedPtr<IToolkitHost>& InitToolkitHost, UMyCustomAsset* Asset)
{
    // 创建编辑器布局（Layout），定义各个面板的位置
    const TSharedRef<FTabManager::FLayout> StandaloneDefaultLayout = FTabManager::NewLayout("Standalone_MyAssetEditor_v1")
        ->AddArea
        (
            FTabManager::NewPrimaryArea()
            ->SetOrientation(Orient_Vertical)
            ->Split
            (
                FTabManager::NewStack()
                ->SetSizeCoefficient(0.1f)
                ->AddTab(GetToolbarTabId(), ETabState::OpenedTab)
            )
            ->Split
            (
                FTabManager::NewSplitter()
                ->SetOrientation(Orient_Horizontal)
                ->Split
                (
                    // 主内容区
                    FTabManager::NewStack()
                    ->SetSizeCoefficient(0.7f)
                )
                ->Split
                (
                    // 详情面板
                    FTabManager::NewStack()
                    ->SetSizeCoefficient(0.3f)
                )
            )
        );

    InitAssetEditor(Mode, InitToolkitHost, TEXT("MyAssetEditorApp"), StandaloneDefaultLayout, true, true, Asset);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 的核心类型定义和运行时逻辑 |
| `SubsonicEngine` | Subsonic 引擎集成，提供播放等运行时功能 |
| `AssetDefinition` | UE5 新版资产定义系统，用于定义“Subsonic Event Collection”资产的显示和行为 |
| `PropertyBinding` | 用于在编辑器中实现属性到参数的绑定功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `0ad6a1ff` | [Audio, CIS] Fixup bad merge: Revert wholesale Subsonic Subscriber stomp; apply minimal non-deprecat | 修复了音频合并冲突，回退了对 Subscriber 的破坏性改动，并应用了最小化的非废弃修复。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 `FSoundWaveData` API 废弃相关的合并冲突。 |
| 2026-04-23 | `129c3dc2` | Fix/silence PVS warnings | 修复或静默了 PVS 静态分析工具的警告。 |
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中新增了音频相关的子菜单。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏 `UE_LOG` 迁移至新的 `UE_LOGF`。 |

### 维护评价

Subsonic 是一个**非常新**的实验性插件，于 2026 年初创建。从 git 记录看，它**仍在积极维护中**，近期有多次提交，主要聚焦于修复合并问题、代码质量警告（PVS）以及与 UE5 其他系统（如 Content Browser、`FSoundWaveData`）的适配更新。

由于其 `IsExperimentalVersion` 标记为 true，Epic 官方明确表示不保证向后兼容性。这意味着该插件的 API 和资产格式在未来版本中可能发生重大变更。目前适合在新项目或实验性项目中学习和评估，但不建议在需要长期稳定维护的生产项目中深度依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic/Source/SubsonicEngineTest)