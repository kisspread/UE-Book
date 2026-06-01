# Motion Design

> Compositing, designer and broadcasting tool.
> 
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

> **注意**：此插件体积极大（2060 源文件，44 个模块），本文档聚焦于核心模块 **AvalancheMediaEditor**，涵盖 Rundown 编辑器、Broadcast 编辑器、Playback 图编辑器及 Remote Control 集成等核心功能。

---

## 用途

Motion Design 是 UE5 面向虚拟制播场景的**全流程动态图形工具**。它解决的核心问题是：**如何在引擎内完成从内容设计、节目编排、实时播出到远程控制的完整广播级工作流**。

与 Sequencer 面向线性影片不同，Motion Design 围绕 **Rundown（节目单）** 和 **Broadcast（播出通道）** 两个核心概念构建：

- **Rundown**：类似播出系统中的节目单，管理 Template（模板）和 Instance（实例）两种 Page，支持拖拽排序、复制粘贴、导入导出（JSON/XML）、预览播放、自动播放等专业播出操作
- **Broadcast**：管理多路输出通道（Channel），每路通道可挂载多个 Media Output（NDI、文件输出、设备输出等），支持独立的分辨率、质量设置
- **Playback**：节点图式的内容播放流程定义，将 Channel Feed 和 Event 组合成可复用的播放链路
- **Remote Control**：深度集成 Remote Control 插件，允许在 Rundown 的每个 Page 上保存独立的参数值，并通过 Controller 面板批量管理

这个插件从 `Experimental` 目录迁移到 `VirtualProduction`，标志着 Epic 将其定位为**生产就绪的虚拟制播工具**。

---

## 使用场景

- **电视直播/晚会导演台**：你在控制室操控多路输出通道，需要用 Rundown 编排节目顺序，Preview 检查画面后 Take To Program 推到播出 → 用 Motion Design 的 Rundown + Broadcast 工作流
- **虚拟制片 LED 墙内容更新**：你需要实时更换 LED 墙上显示的图形元素，每个场景有不同的参数（颜色、位置、文字） → 用 Rundown Page + Remote Control 属性面板
- **体育赛事转播**：你需要根据赛况实时调出不同的比分牌、统计图表，切换速度快且不能出错 → 用 Rundown 的 Template/Instance 机制 + 自动播放
- **展览/主题公园互动装置**：需要预先编排一系列视觉效果的播放时序，同时通过 Remote Control 暴露参数给外部控制系统 → 用 Playback Graph + Remote Control + Rundown Server
- **后期合成预览**：需要在引擎内快速预览多通道合成效果，检查 alpha 通道、分辨率等 → 用 Broadcast Channel 的质量设置和 Preview 面板

---

## 蓝图用法

Motion Design 的核心交互集中在编辑器内（Rundown 编辑器、Broadcast 编辑器），蓝图可调用的运行时 API 主要通过 Remote Control 和 Rundown Server 暴露。

### 核心节点

Motion Design 的编辑器功能主要通过命令系统（`FAvaRundownCommands`）驱动，以下为关键操作：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PlaySelectedPage` | 将选中 Page 播放到 Program 通道 | `FAvaRundownEditor` |
| `PreviewPlaySelectedPage` | 在 Preview 中播放选中 Page | `FAvaRundownEditor` |
| `StopSelectedPage` | 停止选中 Page 的播放 | `FAvaRundownEditor` |
| `TakeToProgram` | 将 Preview 中的 Page 推到 Program | `FAvaRundownEditor` |
| `CreateInstancesFromSelectedTemplates` | 从选中的模板创建实例 | `FAvaRundownEditor` |
| `LoadAllPages` / `LoadNextPages` / `LoadSelectedPages` | 预加载 Page 资源 | `FAvaRundownEditor` |
| `AddChannel` | 添加新的播出通道 | `FAvaBroadcastEditor` |
| `SaveRemoteControlEntitiesToPage` | 将 Remote Control 实体值保存到 Page | `SAvaRundownPageRemoteControlProps` |

### Rundown 命令（Macro Commands）

Rundown 编辑器支持通过控制台命令批量操作，这些命令可通过宏系统绑定：

| 命令 | 说明 |
|---|---|
| `PlayPageCommand` | 播放指定 Page（按 ID） |
| `StopPageCommand` | 停止指定 Page |
| `ContinuePageCommand` | 继续播放 Page |
| `PlayNextPageCommand` | 播放下一个 Page |
| `TakeToProgramCommand` | 推到 Program |
| `LoadPageCommand` / `UnloadPageCommand` | 加载/卸载 Page |
| `StartAutoPlayCommand` / `StopAutoPlayCommand` | 启动/停止自动播放 |
| `StartChannelCommand` / `StopChannelCommand` | 启动/停止播出通道 |

### 使用示例

**创建 Rundown 并编排节目**：

1. 在 Content Browser 右键 → Miscellaneous → Ava Rundown 创建 Rundown 资源
2. 双击打开 Rundown 编辑器，左侧为 Template 列表，右侧为 Instance 列表
3. 将 Motion Design Actor（Avalanche 场景资产）拖入 Template 列表创建模板
4. 从 Template 拖拽到 Instance 列表创建实例
5. 在 Instance 的 Details 面板中修改 Remote Control 参数
6. 选中 Instance → 点击 Preview 按钮预览 → 确认无误后点击 Take To Program

**配置 Broadcast 输出通道**：

1. 打开 Broadcast Editor（工具栏 → Motion Design → Broadcast）
2. 点击 Add Channel 添加输出通道
3. 将 Media Output（如 NDI Output）拖拽到通道上
4. 配置通道的分辨率和质量设置
5. 在 Rundown 中选择页面，点击 Play 输出到指定通道

---

## C++ 用法

### 头文件引入

```cpp
// 访问 Rundown 编辑器模块
#include "IAvaMediaEditorModule.h"

// Rundown 相关
#include "AvaRundownEditor.h"
#include "AvaRundownEditorDefines.h"

// Broadcast 相关
#include "AvaBroadcastEditor.h"
```

### 基本用法：获取编辑器模块

```cpp
// 检查模块是否已加载
if (IAvaMediaEditorModule::IsLoaded())
{
    // 获取模块引用
    IAvaMediaEditorModule& MediaEditorModule = IAvaMediaEditorModule::Get();
    
    // 获取工具栏扩展管理器
    TSharedPtr<FExtensibilityManager> BroadcastToolBar = 
        MediaEditorModule.GetBroadcastToolBarExtensibilityManager();
    
    TSharedPtr<FExtensibilityManager> RundownToolBar = 
        MediaEditorModule.GetRundownToolBarExtensibilityManager();
}
```

> 来源：`Public/IAvaMediaEditorModule.h`

### 基本用法：Rundown 页面操作

```cpp
// 打开 Rundown 编辑器
FAvaRundownEditor* RundownEditor = new FAvaRundownEditor();
RundownEditor->InitRundownEditor(EToolkitMode::Standalone, nullptr, RundownAsset);

// 获取选中的页面
TConstArrayView<int32> SelectedPages = 
    RundownEditor->GetSelectedPagesOnActiveSubListWidget();

// 播放选中页面
if (RundownEditor->CanPlaySelectedPage())
{
    RundownEditor->PlaySelectedPage();
}

// 预览播放
if (RundownEditor->CanPreviewPlaySelectedPage())
{
    RundownEditor->PreviewPlaySelectedPage(false);
}

// 推到 Program
if (RundownEditor->CanTakeToProgram())
{
    RundownEditor->TakeToProgram();
}

// 创建事务并修改
RundownEditor->BeginModify();
// ... 修改操作 ...
RundownEditor->MarkAsModified();
```

> 来源：`Public/Rundown/AvaRundownEditor.h`

### 进阶用法：Remote Control 过滤系统

```cpp
// 实现自定义的 Rundown 过滤表达式工厂
class FMyCustomFilterExpressionFactory : public IAvaRundownFilterExpressionFactory
{
public:
    virtual FName GetFilterIdentifier() const override
    {
        return TEXT("MyCustomFilter");
    }

    virtual bool FilterExpression(const FAvaRundownPage& InItem, 
        const FAvaRundownTextFilterArgs& InArgs) const override
    {
        // 自定义过滤逻辑
        return InItem.GetPageName().Contains(InArgs.ValueToCheck.ToString());
    }

    virtual bool SupportsComparisonOperation(
        ETextFilterComparisonOperation InComparisonOperation,
        EAvaRundownSearchListType InRundownSearchListType) const override
    {
        return InComparisonOperation == ETextFilterComparisonOperation::Equal;
    }
};

// 实现自定义建议工厂
class FMyCustomSuggestionFactory : public IAvaRundownFilterSuggestionFactory
{
public:
    virtual FName GetSuggestionIdentifier() const override
    {
        return TEXT("MySuggestion");
    }

    virtual bool IsSimpleSuggestion() const override { return true; }

    virtual void AddSuggestion(
        const TSharedRef<FAvaRundownFilterSuggestionPayload>& InPayload) override
    {
        InPayload->PossibleSuggestions.Add(
            FAssetSearchBoxSuggestion{ TEXT("my_suggestion"), FText::FromString(TEXT("My Suggestion")) });
    }

    virtual bool SupportSuggestionType(EAvaRundownSearchListType InSuggestionType) const override
    {
        return true;
    }
};
```

> 来源：`Private/Rundown/Factories/Filters/IAvaRundownFilterExpressionFactory.h`, `IAvaRundownFilterSuggestionFactory.h`

### 进阶用法：Playback 图编辑器

```cpp
// 创建 Playback 图编辑器
FAvaPlaybackGraphEditor* PlaybackEditor = new FAvaPlaybackGraphEditor();
PlaybackEditor->InitPlaybackEditor(EToolkitMode::Standalone, nullptr, PlaybackGraph);

// 创建节点图
UEdGraph* Graph = PlaybackEditor->CreatePlaybackGraph(PlaybackGraph);

// 设置节点
PlaybackEditor->SetupPlaybackNode(Graph, PlaybackNode, true);

// 编译
PlaybackEditor->CompilePlaybackNodesFromGraphNodes(PlaybackGraph);
```

> 来源：`Private/Playback/AvaPlaybackGraphEditor.h`

---

## Demo 示例

以下示例展示如何通过 C++ 创建一个自定义的 Rundown 页面视图列（Column）：

```cpp
// MyCustomRundownColumn.h
#pragma once

#include "Rundown/Pages/Columns/IAvaRundownPageViewColumn.h"

class FMyCustomRundownColumn : public IAvaRundownPageViewColumn
{
public:
    UE_AVA_INHERITS(FMyCustomRundownColumn, IAvaRundownPageViewColumn);

    virtual FText GetColumnDisplayNameText() const override
    {
        return NSLOCTEXT("MyColumn", "DisplayName", "Custom");
    }

    virtual FText GetColumnToolTipText() const override
    {
        return NSLOCTEXT("MyColumn", "ToolTip", "Custom status column");
    }

    virtual SHeaderRow::FColumn::FArguments ConstructHeaderRowColumn() override
    {
        return SHeaderRow::Column(GetColumnId())
            .DefaultLabel(GetColumnDisplayNameText())
            .ToolTipText(GetColumnToolTipText())
            .FillWidth(0.5f);
    }

    virtual TSharedRef<SWidget> ConstructRowWidget(
        const FAvaRundownPageViewRef& InPageView,
        const TSharedPtr<SAvaRundownPageViewRow>& InRow) override
    {
        return SNew(STextBlock)
            .Text(FText::FromString(TEXT("Custom Value")));
    }
};
```

---

## 模块依赖

Motion Design 插件依赖大量的外部插件（详见 .uplugin Description），以下为独特依赖：

| 模块 | 用途 |
|---|---|
| `Remote Control` | Remote Control Preset 集成，用于 Page 参数管理和远程控制 |
| `MediaCompositing` | 媒体合成，处理多路媒体输出 |
| `MediaIOFramework` | 媒体 IO 框架，设备输入输出抽象 |
| `Text3D` | 3D 文本渲染 |
| `GeometryCache` | 几何缓存，用于场景资产播放 |
| `GeometryScripting` | 几何脚本，程序化几何操作 |
| `AdvancedRenamer` | 高级重命名工具 |
| `CustomDetailsView` | 自定义 Details 面板 |
| `DynamicMaterial` | 动态材质系统 |
| `SVGImporter` | SVG 导入 |
| `ActorModifierCore` | Actor 修改器核心 |
| `Sequencer` | 序列器集成（AvalanchePropertyAnimator 依赖） |

> **注意**：此插件有大量内部模块互相依赖（44 个模块），文档中只列出了外部依赖。内部模块依赖关系请参见各模块的 `Build.cs` 文件。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将动态设计的 Scene Settings 和 Outliner 标签页迁移到独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 使用 Rundown Page 设置时增加 MRQ 分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏中添加页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构 Viewport 客户端关联/解除关联的通知机制 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

Motion Design 是 Epic Games 重点维护的虚拟制播工具：

- **活跃度**：最近 1 周内有多次功能性更新，包括 UI 改进、新功能添加、分析统计等
- **成熟度**：2025 年 5 月从 Experimental 迁移到 VirtualProduction，标志着进入生产就绪阶段
- **团队投入**：由 Epic 官方团队持续开发，有明确的 JIRA 任务追踪（UE-207892）
- **生态系统**：深度集成多个 UE 子系统（Remote Control、Sequencer、Media IO 等），是虚拟制播管线的核心组件
- **已知限制**：插件体积极大（2060 文件、44 模块），学习曲线较陡；依赖众多外部插件，需要完整安装 Motion Design 工作空间

**推荐使用**：如果你的工作涉及虚拟制播、广播级内容生产或 LED 墙内容管理，强烈推荐使用此插件。它是 UE5 在虚拟制播领域最完整的解决方案。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)

---

## 子模块索引

本文档覆盖了 AvalancheMediaEditor 模块的核心功能。Motion Design 插件的完整模块列表：

| 模块 | 职责 |
|---|---|
| **AvalancheMediaEditor** | Rundown 编辑器、Broadcast 编辑器、Playback 图编辑器（本文档重点） |
| **AvalancheMedia** | 运行时媒体管理核心 |
| **AvalancheCore** | 核心框架和基础设施 |
| **AvalancheEditor** / **AvalancheEditorCore** | 通用编辑器支持 |
| **AvalancheAttribute** / **AvalancheAttributeEditor** | Actor 属性系统 |
| **AvalancheEffectors** / **AvalancheEffectorsEditor** | 效果器系统（Cloner/Effector） |
| **AvalancheModifiers** / **AvalancheModifiersEditor** | Actor 修改器 |
| **AvalancheShapes** / **AvalancheShapesEditor** | 基本形状创建 |
| **AvalancheText** / **AvalancheTextEditor** | 3D 文本 |
| **AvalancheMaterial** | 动态材质 |
| **AvalancheMask** / **AvalancheMaskEditor** | 遮罩系统 |
| **AvalancheTransition** / **AvalancheTransitionEditor** | 页面过渡效果 |
| **AvalanchePropertyAnimator** / **AvalanchePropertyAnimatorEditor** | 属性动画器 |
| **AvalancheRemoteControl** / **AvalancheRemoteControlEditor** | 远程控制 |
| **AvalancheSequencer** / **AvalancheSequence** | Sequencer 集成 |
| **AvalancheSceneRig** / **AvalancheSceneRigEditor** | 场景装配 |
| **AvalancheSceneTree** | 场景树 |
| **AvalancheOutliner** | 大纲视图 |
| **AvalancheCamera** | 摄像机系统 |
| **AvalancheTag** / **AvalancheTagEditor** | 标签系统 |
| **AvalancheMRQ** / **AvalancheMRQEditor** | Movie Render Queue 集成 |
| **AvalancheLevelViewport** / **AvalancheViewport** | 视口管理 |
| **AvalancheInteractiveTools** / **AvalancheInteractiveToolsRuntime** | 交互式工具 |
| **AvalancheSVGEditor** | SVG 导入编辑器 |
| **AvalancheComponentVisualizers** | 组件可视化 |
| **AvalancheFunctionalTest** | 功能测试 |