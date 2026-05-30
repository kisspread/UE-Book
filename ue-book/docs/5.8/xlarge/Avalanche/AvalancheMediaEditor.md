# Motion Design

> Compositing, designer and broadcasting tool.

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

## 用途

Motion Design（动态设计）是 Epic 为虚拟制播和广播场景打造的一站式综合工具，集**合成、动态图形设计和广播输出**于一体。它解决了以下核心问题：

1. **节目编排（Rundown）**：提供完整的节目单管理系统，支持模板页面与实例页面的分离设计。模板定义基础结构和资产绑定，实例页面可在同一模板基础上快速定制远程控制参数值。支持页面的导入/导出（JSON/XML）、拖拽排序、复制粘贴、重编号、组合模板（Combo Template）等操作。

2. **广播输出（Broadcast）**：管理多通道媒体输出，支持 NDI、文件输出等多种媒体输出类型。每个通道可独立配置分辨率、质量设置和渲染目标，支持预览和节目输出分离。

3. **播放图（Playback Graph）**：通过节点图的方式编排复杂的播放逻辑，支持通道源、事件节点、动作节点等类型的连线组合，实现非线性播放流程。

4. **远程控制集成**：与 UE Remote Control 深度集成，在 Rundown 页面详情中可直接编辑 Remote Control Preset 暴露的属性和控制器，支持按页面独立存储远程控制参数值。

5. **Motion Render Queue（MRQ）集成**：支持通过 MRQ 进行离线渲染输出。

该插件从 `Engine/Plugins/Experimental` 迁移而来（CL 42416502），是 Epic 内部多年开发的成熟产品，拥有 43 个模块和超过 2000 个源文件。

## 使用场景

- 你在做电视直播或广播节目 → 用 Rundown 编排节目单，通过 Broadcast 管理多通道输出
- 你需要基于模板快速创建大量相似的动态图形页面 → 用模板页面 + 实例化机制
- 你需要在不同页面间切换远程控制参数 → 用页面详情中的 Remote Control 面板
- 你需要可视化编排复杂播放逻辑 → 用 Playback Graph 节点编辑器
- 你需要在虚拟制片中实时合成动态图形内容 → 用 Motion Design 的全套工具链

## 蓝图用法

Motion Design 的蓝图接口主要集中在 `AvalancheMedia` 和 `AvalancheCore` 模块中。`AvalancheMediaEditor` 作为编辑器模块，主要提供 Slate UI 和工作流工具，其核心交互通过以下机制暴露：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 播放页面 | 从 Rundown 播放指定页面到节目输出 | `FAvaRundownEditor` |
| 预览播放页面 | 在预览模式下播放指定页面 | `FAvaRundownEditor` |
| 停止页面 | 停止当前播放的页面 | `FAvaRundownEditor` |
| 创建实例 | 从模板页面创建实例 | `SAvaRundownTemplatePageList` |
| 导出页面到 Rundown | 将选中页面导出为独立 Rundown 资产 | `SAvaRundownPageList` |
| 导入页面 | 从 JSON/XML 文件导入页面 | `AvaRundownEditorUtils` |
| 广播通道管理 | 添加/删除/配置广播通道 | `FAvaBroadcastEditor` |

### Rundown 宏命令

Motion Design 内置了可绑定的宏命令系统（`FAvaRundownEditor::GetBindableMacroCommands`），支持以下远程控制操作：

| 命令 | 说明 |
|---|---|
| `StartAutoPlay` | 启动自动播放，指定间隔 |
| `StopAutoPlay` | 停止自动播放 |
| `LoadPage` | 加载指定页面 |
| `UnloadPage` | 卸载指定页面 |
| `PlayPage` | 播放指定页面 |
| `ContinuePage` | 继续播放指定页面 |
| `PlayNextPage` | 播放下一页 |
| `StopPage` | 停止指定页面 |
| `TakeToProgram` | 切换到节目输出 |
| `StartChannel` | 启动广播通道 |
| `StopChannel` | 停止广播通道 |

### 使用示例（蓝图描述）

在 Rundown 编辑器中：
1. 创建模板页面，绑定 AVA 播放资产
2. 从模板创建实例页面
3. 在实例页面的 Remote Control 面板中调整参数值
4. 点击 Play 按钮或使用快捷键将页面推送到节目输出
5. 使用 Playback Graph 编排复杂的播放时序和逻辑

## C++ 用法

### 头文件引入

```cpp
#include "IAvaMediaEditorModule.h"
```

### 基本用法

通过模块接口获取编辑器扩展管理器：

```cpp
// 来源：Public/IAvaMediaEditorModule.h
// 检查模块是否已加载
if (IAvaMediaEditorModule::IsLoaded())
{
    IAvaMediaEditorModule& MediaEditorModule = IAvaMediaEditorModule::Get();
    
    // 获取广播编辑器工具栏扩展管理器
    TSharedPtr<FExtensibilityManager> BroadcastToolbarManager = 
        MediaEditorModule.GetBroadcastToolBarExtensibilityManager();
    
    // 获取播放编辑器工具栏扩展管理器
    TSharedPtr<FExtensibilityManager> PlaybackToolbarManager = 
        MediaEditorModule.GetPlaybackToolBarExtensibilityManager();
    
    // 获取 Rundown 工具栏扩展管理器
    TSharedPtr<FExtensibilityManager> RundownToolbarManager = 
        MediaEditorModule.GetRundownToolBarExtensibilityManager();
    
    // 获取 Rundown 页面右键菜单扩展管理器
    TSharedPtr<FExtensibilityManager> RundownMenuManager = 
        MediaEditorModule.GetRundownMenuExtensibilityManager();
}
```

### Rundown 过滤表达式

```cpp
// 来源：Private/Rundown/Factories/Filters/IAvaRundownFilterExpressionFactory.h
// 自定义过滤器工厂
class FMyRundownFilterFactory : public IAvaRundownFilterExpressionFactory
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
        return InArgs.ItemRundown != nullptr;
    }
    
    virtual bool SupportsComparisonOperation(
        ETextFilterComparisonOperation InComparisonOperation,
        EAvaRundownSearchListType InRundownSearchListType) const override
    {
        return true;
    }
};
```

### 进阶用法

页面导入导出工具类（来自 `AvaRundownEditorUtils.h`）：

```cpp
// 来源：Private/Rundown/AvaRundownEditorUtils.h
// 序列化页面为 JSON
FString JsonString = UE::AvaRundownEditor::Utils::SerializePagesToJson(
    Rundown, SelectedPageIds);

// 从 JSON 反序列化页面
TArray<FAvaRundownPage> Pages = 
    UE::AvaRundownEditor::Utils::DeserializePagesFromJson(JsonString);

// 导出页面到独立 Rundown 资产
TStrongObjectPtr<UAvaRundown> ExportedRundown = 
    UE::AvaRundownEditor::Utils::ExportPagesToRundown(SourceRundown, PageIds);

// 保存 Rundown 为 XML
bool bSaved = UE::AvaRundownEditor::Utils::SaveRundownToXml(
    Rundown, FilePath, EXmlSerializationEncoding::Utf8);

// 导入模板页面
UE::AvaRundownEditor::FImportTemplateMap TemplateMap;
TArray<int32> ImportedTemplateIds = 
    UE::AvaRundownEditor::Utils::ImportTemplatePages(
        Rundown, SourceTemplates, TemplateMap);

// 合并另一个 Rundown 的页面
TArray<int32> MergedPageIds = 
    UE::AvaRundownEditor::Utils::ImportInstancedPagesFromRundown(
        DestinationRundown, SourceRundown, InsertPosition);

// 保存为重复的 Rundown
UAvaRundown* Duplicate = UE::AvaRundownEditor::Utils::SaveDuplicateRundown(
    SourceRundown, NewAssetName, NewPackagePath);
```

Remote Control 值保存到页面：

```cpp
// 来源：Private/Rundown/DetailsView/RemoteControl/Properties/SAvaRundownPageRemoteControlProps.h
// 将 Remote Control Preset 的实体值保存到指定页面
TSet<FGuid> EntityIds = /* 获取要保存的实体 ID 集合 */;
bool bSuccess = SAvaRundownPageRemoteControlProps::SaveRemoteControlEntitiesToPage(
    Preset, EntityIds, Rundown, PageId);
```

## 模块依赖

Motion Design 依赖以下非标准模块（来自 .uplugin Description 和各 Build.cs）：

| 模块 | 用途 |
|---|---|
| `AdvancedRenamer` | 高级重命名功能 |
| `CustomDetailsView` | 自定义详情面板视图 |
| `DynamicMaterial` | 动态材质系统 |
| `GeometryCache` | 几何缓存 |
| `GeometryScripting` | 几何脚本 |
| `MediaCompositing` | 媒体合成 |
| `MediaIOFramework` | 媒体 IO 框架 |
| `MeshModelingToolsetExp` | 网格建模工具集（实验性） |
| `RemoteControl` | 远程控制 |
| `SVGImporter` | SVG 导入器 |
| `Text3D` | 3D 文本 |
| `ActorModifierCore` | Actor 修改器核心 |
| `Sequencer` | 序列器（AvalanchePropertyAnimator 依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将动态设计的场景设置和大纲面板标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 Rundown 页面设置使用 MRQ 时添加分析统计 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在节目控制工具栏添加页面加载选项（全部/下一个/已选） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口：重构客户端关联/取消关联时的通知机制 |

### 维护评价

- **创建时间**：2025-05-09，约 1 年前从 Experimental 迁移到 VirtualProduction
- **维护频率**：**非常活跃**。近期内有密集的功能更新和改进，几乎每天都有提交
- **维护内容**：涵盖功能增强（页面加载选项、MRQ 分析）、UI 改进（标签页重组）、设置扩展（碰撞禁用）、架构重构等
- **代码规模**：2060 个源文件，43 个模块，属于大型专业工具
- **状态**：从 Experimental 正式迁移到 VirtualProduction，表明已达到生产就绪状态
- **推荐使用**：✅ 强烈推荐。这是 Epic 为虚拟制播场景打造的核心工具，活跃维护，功能完善。但需注意插件默认不启用，需要手动开启，且依赖较多其他插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- 官方文档：无

---

*本文档基于 AvalancheMediaEditor 模块及插件整体结构生成。由于插件包含 43 个模块、2060 个源文件，属于 xlarge 级别，以下为各子模块概要：*

## 子模块索引

| 模块 | 类型 | 职责 |
|---|---|---|
| `Avalanche` | Runtime | 核心运行时模块，主入口 |
| `AvalancheAttribute` | Runtime | 属性系统 |
| `AvalancheAttributeEditor` | Runtime | 属性编辑器 |
| `AvalancheCamera` | Runtime | 相机功能 |
| `AvalancheComponentVisualizers` | Runtime | 组件可视化器 |
| `AvalancheCore` | Runtime | 核心功能库 |
| `AvalancheEditor` | Runtime | 编辑器主模块 |
| `AvalancheEditorCore` | Runtime | 编辑器核心功能 |
| `AvalancheEffectors` | Runtime | 效果器系统 |
| `AvalancheEffectorsEditor` | Runtime | 效果器编辑器 |
| `AvalancheFunctionalTest` | Runtime | 功能测试 |
| `AvalancheInteractiveTools` | Runtime | 交互工具 |
| `AvalancheInteractiveToolsRuntime` | Runtime | 交互工具运行时 |
| `AvalancheLevelViewport` | Runtime | 关卡视口集成 |
| `AvalancheMRQ` | Runtime | Motion Render Queue 集成 |
| `AvalancheMRQEditor` | Runtime | MRQ 编辑器 |
| `AvalancheMask` | Runtime | 遮罩系统 |
| `AvalancheMaskEditor` | Runtime | 遮罩编辑器 |
| `AvalancheMaterial` | Runtime | 材质系统 |
| `AvalancheMedia` | Runtime | 媒体核心模块 |
| **`AvalancheMediaEditor`** | **Runtime** | **媒体编辑器（本文档主要分析对象）** |
| `AvalancheModifiers` | Runtime | 修改器系统 |
| `AvalancheModifiersEditor` | Runtime | 修改器编辑器 |
| `AvalancheOutliner` | Runtime | 大纲视图 |
| `AvalanchePropertyAnimator` | Runtime | 属性动画器（依赖 Sequencer） |
| `AvalanchePropertyAnimatorEditor` | Runtime | 属性动画器编辑器 |
| `AvalancheRemoteControl` | Runtime | 远程控制集成 |
| `AvalancheRemoteControlEditor` | Runtime | 远程控制编辑器 |
| `AvalancheSVGEditor` | Runtime | SVG 编辑器 |
| `AvalancheSceneRig` | Runtime | 场景装备 |
| `AvalancheSceneRigEditor` | Runtime | 场景装备编辑器 |
| `AvalancheSceneTree` | Runtime | 场景树 |
| `AvalancheSequence` | Runtime | 序列系统 |
| `AvalancheSequencer` | Runtime | 序列器集成 |
| `AvalancheShapes` | Runtime | 形状系统 |
| `AvalancheShapesEditor` | Runtime | 形状编辑器 |
| `AvalancheTag` | Runtime | 标签系统 |
| `AvalancheTagEditor` | Runtime | 标签编辑器 |
| `AvalancheText` | Runtime | 文本系统 |
| `AvalancheTextEditor` | Runtime | 文本编辑器 |
| `AvalancheTransition` | Runtime | 过渡系统 |
| `AvalancheTransitionEditor` | Runtime | 过渡编辑器 |
| `AvalancheViewport` | Runtime | 视口系统 |

---

# AvalancheMediaEditor 模块详解

## 模块用途

`AvalancheMediaEditor` 是 Motion Design 插件的**媒体编辑器核心模块**，主要提供三大编辑器工具的 UI 和业务逻辑：

1. **Rundown Editor（节目单编辑器）**：完整的节目编排系统，管理模板页面和实例页面
2. **Broadcast Editor（广播编辑器）**：多通道媒体输出管理界面
3. **Playback Graph Editor（播放图编辑器）**：基于节点图的播放逻辑编排

## 架构概览

### Rundown 系统

```
FAvaRundownEditor (主编辑器)
├── SAvaRundownTemplatePageList (模板页面列表)
├── SAvaRundownInstancedPageList (实例页面列表)
│   └── 多个子列表 Tab（可自定义视图）
├── SAvaRundownPageDetails (页面详情面板)
│   ├── SAvaRundownPageRemoteControlProps (RC 属性面板)
│   └── SAvaRundownRCControllerPanel (RC 控制器面板)
└── SAvaRundownPagePreview (页面预览)
```

### 核心类说明

| 类 | 职责 |
|---|---|
| `FAvaRundownEditor` | Rundown 编辑器主类，管理页面操作和工作流 |
| `SAvaRundownPageList` | 页面列表基类，提供通用的页面列表交互逻辑 |
| `SAvaRundownTemplatePageList` | 模板页面列表，支持创建模板和组合模板 |
| `SAvaRundownInstancedPageList` | 实例页面列表，支持播放、预览、加载等操作 |
| `SAvaRundownPageDetails` | 页面详情面板，展示和编辑选中页面的属性 |
| `SAvaRundownPageRemoteControlProps` | 远程控制属性编辑面板 |
| `SAvaRundownRCControllerPanel` | 远程控制控制器面板 |
| `FAvaBroadcastEditor` | 广播编辑器主类 |
| `SAvaBroadcastChannel` | 广播通道 Widget |
| `SAvaBroadcastChannels` | 广播通道网格布局 |
| `FAvaPlaybackGraphEditor` | 播放图编辑器主类 |
| `UAvaPlaybackEditorGraphSchema` | 播放图 Schema，定义节点和连接规则 |
| `UAvaPlaybackEditorGraphNode` | 播放图节点 |
| `IAvaMediaEditorModule` | 模块公共接口 |

### 页面操作流程

1. **创建模板**：`SAvaRundownTemplatePageList::AddTemplate()` → 创建基础页面模板
2. **创建实例**：`SAvaRundownTemplatePageList::CreateInstance()` → 从模板实例化页面
3. **编辑参数**：通过 `SAvaRundownPageRemoteControlProps` 调整远程控制值
4. **预览播放**：`FAvaRundownEditor::PreviewPlaySelectedPage()` → 在预览模式下测试
5. **节目输出**：`FAvaRundownEditor::TakeToProgram()` → 切换到正式输出
6. **加载管理**：支持 `LoadAllPages`、`LoadNextPages`、`LoadSelectedPages` 三种加载策略

### 过滤系统

Rundown 支持可扩展的文本过滤系统：

- `IAvaRundownFilterExpressionFactory`：定义过滤表达式的工厂接口
- `IAvaRundownFilterSuggestionFactory`：定义搜索建议的工厂接口
- `FAvaRundownPageFilterExpressionContext`：表达式求值上下文，支持基础字符串匹配和复杂键值比较

### 拖拽系统

页面列表支持丰富的拖拽操作：

| 拖拽源 | 目标 | 行为 |
|---|---|---|
| 资产 | 模板列表 | 创建新模板页面 |
| 资产 | 实例列表 | 创建新实例页面 |
| Rundown 资产 | 任意列表 | 合并 Rundown 页面 |
| 页面 | 模板列表 | 重新排序 |
| 页面 | 实例列表 | 重新排序或跨列表移动 |
| 外部文件 | 任意列表 | 导入 JSON/XML |

### Broadcast 系统

广播系统管理多通道媒体输出：

- **通道管理**：添加/删除/重命名通道，每通道可配置多个媒体输出
- **配置文件**：支持多配置文件切换（`SAvaBroadcastProfileEntry`）
- **输出设备**：树形视图展示可用输出设备（`SAvaBroadcastOutputDevices`）
- **质量设置**：每通道独立的质量/分辨率设置
- **预览**：实时预览通道输出

### Playback Graph 系统

播放图提供可视化节点编排：

- **节点类型**：通道源（Channel Feed）、事件（Event）、动作（Action）、播放器（Player）
- **连接规则**：通过 `UAvaPlaybackEditorGraphSchema` 定义合法连接
- **自定义绘制**：`FAvaPlaybackConnectionDrawingPolicy` 用颜色区分活动/非活动连线
- **节点覆盖**：支持通过 `OverrideNodeClasses` 自定义节点图形表示