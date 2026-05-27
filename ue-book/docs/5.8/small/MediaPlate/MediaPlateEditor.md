# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体播放器编辑器 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资源） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate) | |

## 用途

Media Plate 插件不仅仅是一个简单的媒体播放 Actor。它是一个**完整的媒体播放器编辑器扩展套件**。它解决了在 Unreal Editor 内部对媒体内容进行可视化预览、交互控制、时序编辑和资产管理的核心问题。

此插件的主要功能包括：
1.  **自定义细节面板**：为 `UMediaPlateComponent` 提供高度定制的“细节”面板，允许用户直观地配置播放行为、网格形状（平面、球体、自定义）、宽高比等属性。
2.  **Sequencer 集成**：提供专业的 Sequencer 轨道编辑器，让用户能够在 Sequencer 时间线上精确控制媒体播放的启停、进度和循环，实现与场景动画的精确同步。
3.  **编辑器内媒体预览与播放控制**：允许在编辑器视口内实时播放媒体，并提供类似媒体播放器的播放、暂停、快进、快退、切换正反向播放等控制按钮。
4.  **资产工作流**：支持通过拖放媒体文件快速创建媒体源资产，并管理媒体材质模板，简化内容创建工作流。
5.  **多资源支持**：支持从媒体文件路径、媒体源资产或媒体播放列表等多种方式加载媒体内容。

## 使用场景

-   你正在制作一个博物馆或展厅关卡，需要在虚拟屏幕或全息投影仪上播放展品介绍视频 → 使用 Media Plate Actor，并通过 Sequencer 控制播放时序。
-   你正在设计一个游戏内的影院或广告牌，需要实时调整媒体屏幕的形状（如曲面屏、球形屏）和宽高比以适应场景美术需求 → 使用 Media Plate 的细节面板自定义网格和宽高比。
-   你是一位媒体内容创作者或技术美术，需要在 Unreal Editor 中快速预览大量视频或图片素材，并挑选合适的用于场景 → 直接从内容浏览器拖放文件到 Media Plate Actor 上进行预览。
-   你需要一个可以在编辑器内像专业媒体播放器一样控制播放（暂停、逐帧、倒放）的工具，用于调试和对齐动画 → 使用 Media Plate Editor Toolkit。

## 蓝图用法

**重要提示**：Media Plate 插件的核心功能是编辑器集成，其公共蓝图 API 主要集中在运行时组件 `UMediaPlateComponent`（属于 `MediaPlate` 模块）。`MediaPlateEditor` 模块主要提供编辑器内部工具和自定义面板，其暴露给蓝图的函数（如 `UFUNCTION`）通常用于编辑器脚本和扩展，不直接用于游戏逻辑。以下节点基于 `MediaPlateEditor` 模块中可被蓝图调用的编辑器功能。

### 核心节点（编辑器脚本/工具）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HandleMediaPlateEvent` | 静态函数，用于更改选中的 Media Plate 的播放状态（如播放、暂停、停止），并广播事件。常用于编辑器工具或菜单按钮的回调。 | `FMediaPlateCustomization` |
| `IsMediaPlateEventAllowedForPlayer` | 静态函数，检查给定媒体播放器是否允许切换到指定的事件状态（如“正在播放”），用于控制编辑器UI按钮的启用状态。 | `FMediaPlateCustomization` |

### 使用示例（蓝图描述）

在编辑器工具蓝图中，你可能会创建一个按钮来停止所有正在播放的 Media Plate：
1.  创建一个 **Editor Utility Widget** 蓝图。
2.  在按钮的 `OnClicked` 事件中，调用 **“编辑器脚本工具”** 类下的 **“获取所有 MediaPlate 组件”** 类似的节点，获取当前关卡中所有 `UMediaPlateComponent` 的引用。
3.  将这些组件引用转换为弱引用数组（`TWeakObjectPtr`）。
4.  调用 `FMediaPlateCustomization::HandleMediaPlateEvent` 节点，传入弱引用数组和 `EMediaPlateEventState::Stop` 枚举值。

## C++ 用法

Media Plate Editor 模块主要提供编辑器扩展功能，其 API 常用于创建自定义细节面板、扩展 Sequencer 或开发编辑器工具。

### 头文件引入

```cpp
#include "MediaPlateEditorModule.h"
#include "MediaPlateCustomization.h"
#include "MediaPlateTrackEditor.h"
```

### 基本用法：注册自定义细节面板

如果你的插件需要为 Media Plate 组件添加额外的细节面板自定义项，可以通过模块的委托进行注册。

```cpp
// 在你的编辑器模块 StartupModule 中
void FMyPluginModule::StartupModule()
{
    // 获取 Media Plate Editor 模块
    FMediaPlateEditorModule& MediaPlateEditorModule = FModuleManager::LoadModuleChecked<FMediaPlateEditorModule>("MediaPlateEditor");

    // 注册对“获取媒体板材质资产路径”事件的监听，用于提供额外的材质模板
    MediaPlateEditorModule.OnGetMediaPlateMaterialAssetPaths().AddRaw(this, &FMyPluginModule::HandleOnGetMediaPlateMaterialAssetPaths);
}

// 回调函数实现
void FMyPluginModule::HandleOnGetMediaPlateMaterialAssetPaths(TArray<FName>& OutAssetPaths)
{
    // 向列表中添加你的自定义媒体板材质资产路径
    OutAssetPaths.Add(TEXT("/Game/MyPlugins/Materials/M_MyCustomMediaPlate"));
}
```

### 进阶用法：在 Sequencer 中程序化添加媒体轨道

虽然通常通过 UI 操作，但也可以通过代码与 Sequencer 集成进行交互。

```cpp
#include "Sequencer/MediaPlateTrackEditor.h"
#include "ISequencer.h"
#include "MediaPlayer.h"

// 假设你有一个 UMediaPlateComponent* MediaPlateComp 和一个有效的 ISequencer* Sequencer
void AddMediaPlateToSequencerProgrammatically(UMediaPlateComponent* MediaPlateComp, TSharedRef<ISequencer> Sequencer)
{
    // 1. 获取轨道编辑器实例（通常由 Sequencer 内部管理）
    TSharedRef<FMediaPlateTrackEditor> TrackEditor = MakeShared<FMediaPlateTrackEditor>(Sequencer);

    // 2. 准备一个指向 MediaPlateComp 的对象绑定 GUID（Sequencer 需要）
    // 这通常需要访问 Sequencer 的对象绑定数据，此处仅为概念示例
    FGuid ObjectBinding; // 假设已获得

    // 3. 程序化地添加媒体轨道
    TrackEditor->HandleAddMediaTrackToObjectBindingMenuEntryExecute({ObjectBinding});

    // 4. 或者直接使用内部方法（更底层，需谨慎）
    // TrackEditor->AddTrackForComponent(MediaPlateComp, ObjectBinding);
}
```

## Demo 示例

以下是一个最小化的编辑器工具类示例，展示了如何扩展 Media Plate 的细节面板并响应播放事件。

**MyMediaPlateEditorExtension.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MediaPlateCustomization.h"

class FMyMediaPlateEditorExtension
{
public:
    void Initialize();
    void Shutdown();

private:
    // 详情面板扩展代理句柄
    FDelegateHandle DetailsExtensionHandle;

    // 自定义的详情面板行
    void ExtendDetails(IDetailLayoutBuilder& DetailBuilder, UMediaPlateComponent* MediaPlateComp);
};
```

**MyMediaPlateEditorExtension.cpp**
```cpp
#include "MyMediaPlateEditorExtension.h"
#include "DetailLayoutBuilder.h"
#include "DetailCategoryBuilder.h"
#include "MediaPlateComponent.h"
#include "MediaPlateEditorModule.h"

void FMyMediaPlateEditorExtension::Initialize()
{
    // 通过模块委托扩展详情面板
    if (FModuleManager::Get().IsModuleLoaded("MediaPlateEditor"))
    {
        FMediaPlateEditorModule& Module = FModuleManager::LoadModuleChecked<FMediaPlateEditorModule>("MediaPlateEditor");
        // 注意：实际的扩展方式取决于模块提供的具体委托。此处为示意。
        // DetailsExtensionHandle = Module.OnExtendMediaPlateDetails.AddRaw(this, &FMyMediaPlateEditorExtension::ExtendDetails);
    }
}

void FMyMediaPlateEditorExtension::Shutdown()
{
    // 清理委托
}

void FMyMediaPlateEditorExtension::ExtendDetails(IDetailLayoutBuilder& DetailBuilder, UMediaPlateComponent* MediaPlateComp)
{
    if (MediaPlateComp)
    {
        // 添加一个自定义分类
        IDetailCategoryBuilder& MyCategory = DetailBuilder.EditCategory("MyCustomCategory", FText::GetEmpty(), ECategoryPriority::Important);
        
        // 添加一个自定义行（例如，显示组件的某个状态）
        MyCategory.AddCustomRow(FText::FromString("MyCustomRow"))
        .NameContent()
        [
            SNew(STextBlock)
            .Text(FText::FromString("My Custom Label"))
        ]
        .ValueContent()
        [
            SNew(STextBlock)
            .Text(FText::FromString("Custom Value"))
        ];
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaFrameworkUtilities` | 媒体框架的通用工具和辅助功能。 |
| `MediaAssets` | 提供媒体源、媒体播放器、媒体纹理等核心资产类型。 |
| `LevelEditor` | 用于扩展关卡编辑器视口菜单和上下文菜单。 |
| `PropertyEditor` | 用于自定义细节面板（Details Panel）。 |
| `Sequencer` | 用于集成和扩展 Sequencer 编辑器。 |
| `MeshConversion` | 用于在编辑器中生成球体网格。 |
| `GeometryCore` | 提供几何生成器基类，用于创建球体网格。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-04-09 | `17c8eeed` | [MediaPlateEditor] Prevent adding multiple media tracks under the same media plate binding. | 修复了在 Sequencer 中同一 Media Plate 绑定下可能重复添加媒体轨道的问题。 |
| 2026-04-08 | `786c0a7e` | [MediaPlate] Support multiple media textures in the "material instance constant" code path. | 增强了材质实例常量路径，现在支持多个媒体纹理。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一个错误的全局查找替换操作后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了 CL51314860 的更改，可能因为引入了问题。 |

### 维护评价

**维护积极，推荐使用。**

Media Plate 插件虽然标记为 **Beta 版本**，但自 2022 年创建以来一直保持着**非常活跃的开发和维护**。最近的提交（截至 2026 年 4 月）包括功能增强（多纹理支持）、重要的 Bug 修复（防止 Sequencer 轨道重复、修复错误的全局替换）以及持续的代码现代化（日志宏迁移）。

-   **活跃度**：最近 6 个月内有 3 次实质性更新。
-   **内容质量**：更新聚焦于核心功能的完善和稳定性提升，表明插件正从 Beta 向正式版演进。
-   **已知问题**：作为 Beta 软件，可能存在未发现的边界情况或 API 变更。回退操作 (`6759aa54`) 暗示偶尔会引入回归问题。
-   **结论**：该插件是 UE5 媒体工作流的核心组成部分，由 Epic Games 官方维护，功能强大且处于积极开发中。对于需要在编辑器中集成媒体内容的项目，它是**推荐且必备的工具**，但使用时应关注其 Beta 状态带来的潜在风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate/Tests)