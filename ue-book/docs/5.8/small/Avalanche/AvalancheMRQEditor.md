# Motion Design (Avalanche) - AvalancheMRQEditor 模块

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、编辑器工具） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMRQEditor` (Runtime), 及其他 38 个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

---

## 用途

Motion Design（Avalanche）是 UE5 的**虚拟制播动态设计工具集**，专为广播级实时图形、合成和播出场景设计。它提供了一个完整的非线性编辑工作流，包括：

- **场景设计**：创建和管理广播级动态图形场景（SceneRig）
- **节目编排**：通过 Rundown 系统管理多个页面/段落的播放顺序
- **实时合成**：支持媒体合成、SVG 导入、3D 文字等
- **属性动画**：基于 Sequencer 的属性关键帧动画系统
- **效果器系统**：克隆器和效果器用于批量创建和控制对象
- **材质设计**：动态材质编辑工具
- **遮罩系统**：几何遮罩支持
- **远程控制**：与远程控制系统集成
- **渲染输出**：通过 Movie Render Queue 进行高质量离线渲染（AvalancheMRQEditor 模块的核心功能）

AvalancheMRQEditor 模块专门负责将 Motion Design 的 Rundown 页面与 Movie Render Queue 深度集成，实现从节目编排到最终渲染输出的完整工作流。

---

## 使用场景

- 你需要制作电视新闻频道的**实时动态图形模板** → 用 Motion Design Rundown 管理多个页面
- 你要为虚拟制播项目创建**可切换的场景布局** → 用 SceneRig 和 SceneTree 组织场景
- 你需要对 3D 文字、形状等元素做**关键帧动画** → 用 PropertyAnimator 模块
- 你要将设计好的 Motion Design 页面**批量渲染为视频** → 用 AvalancheMRQEditor 集成 Movie Render Queue
- 你需要通过 Rundown 界面**一键渲染选中的页面** → MRQ Editor 提供了便捷的渲染命令

---

## 蓝图用法

### 核心节点

AvalancheMRQEditor 是纯编辑器集成模块，主要功能通过编辑器 UI 暴露，不提供 BlueprintCallable 节点。

Motion Design 核心模块提供的主要蓝图节点（供参考）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RenderSelectedPages` | 渲染 Rundown 中选中的页面 | `FAvaMRQEditorRundownUtils` (C++ 静态方法) |

---

## C++ 用法

### 模块概述

AvalancheMRQEditor 是一个编辑器扩展模块，负责：
1. 向 Rundown 编辑器工具栏注入 Movie Render Queue 相关按钮
2. 提供 MRQ 渲染配置预设管理
3. 将 Rundown 页面转换为 Movie Render Queue 任务

### 头文件引入

```cpp
// 注意：此模块所有头文件均为 Private，仅供模块内部使用
// 如需渲染功能，请使用公共 API 或通过 Remote Control 模块交互
```

### 核心架构

**命令系统** (`FAvaMRQEditorCommands`)：

```cpp
// 注册编辑器命令 - 将渲染操作绑定到快捷键/按钮
class FAvaMRQEditorCommands : public TCommands<FAvaMRQEditorCommands>
{
public:
    virtual void RegisterCommands() override;
    
    // 渲染选中页面的命令
    TSharedPtr<FUICommandInfo> RenderSelectedPages;
};
```

**工具栏扩展** (`FAvaMRQEditorModule`)：

```cpp
// 扩展 Rundown 编辑器工具栏，添加 MRQ 渲染按钮
static TSharedRef<FExtender> ExtendRundownToolbar(
    const TSharedRef<FUICommandList> InCommandList, 
    const TArray<UObject*> InObjects);

// 创建 Rundown 上下文操作（如渲染选中页面）
static TSharedRef<FUICommandList> CreateRundownActions(
    TSharedRef<FAvaMRQRundownContext> InContext);
```

**渲染工具函数** (`FAvaMRQEditorRundownUtils`)：

```cpp
// 实际执行渲染选中页面的逻辑
struct FAvaMRQEditorRundownUtils
{
    static void RenderSelectedPages(
        TConstArrayView<TWeakPtr<const FAvaRundownEditor>> InRundownEditors);
};
```

**配置设置** (`UAvaMRQEditorSettings`)：

```cpp
// 项目级别的 MRQ 渲染预设配置
UCLASS(config=EditorPerProjectUserSettings, meta=(DisplayName="Movie Render Queue"))
class UAvaMRQEditorSettings : public UDeveloperSettings
{
    // 可配置的渲染预设
    UPROPERTY(Config, EditAnywhere, Category="Motion Design")
    TSoftObjectPtr<UMoviePipelinePrimaryConfig> PresetConfig;
};
```

### 基本用法

从源码分析的工作流程：

1. **模块启动时**：注册命令、扩展 Rundown 编辑器工具栏
2. **用户操作**：在 Rundown 编辑器中选择页面，点击渲染按钮
3. **渲染执行**：调用 `RenderSelectedPages` 将选中页面转换为 MRQ 任务
4. **配置应用**：使用项目设置中预配置的渲染预设

---

## Demo 示例

由于 AvalancheMRQEditor 是纯编辑器集成模块（所有头文件均为 Private），不直接提供公共 API。以下是其内部架构参考：

```cpp
// 模块启动（简化示意）
void FAvaMRQEditorModule::StartupModule()
{
    // 注册 MRQ 编辑器命令
    FAvaMRQEditorCommands::Register();
    
    // 绑定命令到动作
    TSharedPtr<FExtensibilityManager> ToolbarManager = /* 获取 Rundown 工具栏管理器 */;
    FToolMenuOwnerScoped OwnerScoped(this);
    
    // 扩展工具栏
    ToolbarManager->AddExtender(
        FExtensibilityManager::FExtender::CreateStatic(
            &FAvaMRQEditorModule::ExtendRundownToolbar));
}

void FAvaMRQEditorModule::ShutdownModule()
{
    FAvaMRQEditorCommands::Unregister();
}
```

---

## 模块依赖

### AvalancheMRQEditor 模块依赖

| 模块 | 用途 |
|---|---|
| `AvalancheMedia` | Rundown 核心功能（页面管理、节目编排） |
| `AvalancheMediaEditor` | Rundown 编辑器 UI 和交互 |
| `MovieRenderPipeline` | Movie Render Queue 核心框架 |
| `MovieRenderPipelineEditor` | Movie Render Queue 编辑器集成 |
| `ToolMenus` | UE5 工具栏/菜单扩展系统 |
| `EditorStyle` | 编辑器样式 |

### Motion Design 整体独特依赖

| 模块 | 用途 |
|---|---|
| `Text3D` | 3D 文字渲染 |
| `SVGImporter` | SVG 矢量图形导入 |
| `GeometryCache` | 几何缓存系统 |
| `GeometryScripting` | 几何脚本工具 |
| `MediaCompositing` | 媒体合成 |
| `RemoteControl` | 远程控制系统 |
| `ActorModifierCore` | Actor 修改器框架 |
| `Sequencer` | 序列器动画系统 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将场景设置和大纲视图面板独立分组显示 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加 MRQ 渲染使用统计分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added | 在控制工具栏新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes | 新增项目设置可强制禁用 3D 文字和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with | 重构视口客户端关联/断开通知机制 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2025年5月从 Experimental 迁移至 VirtualProduction（实际开发历史更长）
- **更新频率**：几乎每天都有更新，开发极为活跃
- **开发团队**：Epic Games 官方团队（juan portillo 等）
- **近期重点**：
  - MRQ 集成持续增强（新增渲染分析、页面加载选项）
  - UI/UX 优化（面板分组、工具栏改进）
  - 性能优化（碰撞控制、视口重构）
- **推荐使用**：✅ 强烈推荐用于虚拟制播和广播级动态图形项目
- **注意事项**：这是 UE5.5+ 的新功能，仍在快速迭代中，部分 API 可能变化

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [AvalancheMRQEditor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheMRQEditor)

---

## Motion Design 完整模块列表

本插件包含 42 个模块，按功能领域组织：

| 模块 | 类型 | 说明 |
|---|---|---|
| **核心框架** | | |
| `AvalancheCore` | Runtime | 核心基础库 |
| `Avalanche` | Runtime | 主运行时模块 |
| `AvalancheEditorCore` | Runtime | 编辑器核心库 |
| `AvalancheEditor` | Runtime | 主编辑器模块 |
| **场景管理** | | |
| `AvalancheSceneRig` | Runtime | 场景装备系统 |
| `AvalancheSceneRigEditor` | Runtime | 场景装备编辑器 |
| `AvalancheSceneTree` | Runtime | 场景树管理 |
| `AvalancheOutliner` | Runtime | 大纲视图 |
| **媒体与渲染** | | |
| `AvalancheMedia` | Runtime | 媒体管理核心 |
| `AvalancheMediaEditor` | Runtime | 媒体编辑器 |
| `AvalancheMRQ` | Runtime | Movie Render Queue 集成 |
| `AvalancheMRQEditor` | Runtime | MRQ 编辑器集成 |
| `AvalancheCamera` | Runtime | 摄像机系统 |
| **动画与效果** | | |
| `AvalancheSequence` | Runtime | 序列器集成 |
| `AvalancheSequencer` | Runtime | 序列器扩展 |
| `AvalanchePropertyAnimator` | Runtime | 属性动画系统 |
| `AvalanchePropertyAnimatorEditor` | Runtime | 属性动画编辑器 |
| `AvalancheTransition` | Runtime | 转场效果 |
| `AvalancheTransitionEditor` | Runtime | 转场编辑器 |
| **形状与图形** | | |
| `AvalancheShapes` | Runtime | 基础形状生成 |
| `AvalancheShapesEditor` | Runtime | 形状编辑器 |
| `AvalancheText` | Runtime | 3D 文字处理 |
| `AvalancheTextEditor` | Runtime | 文字编辑器 |
| `AvalancheSVGEditor` | Runtime | SVG 导入编辑器 |
| **材质与遮罩** | | |
| `AvalancheMaterial` | Runtime | 动态材质系统 |
| `AvalancheMask` | Runtime | 几何遮罩系统 |
| `AvalancheMaskEditor` | Runtime | 遮罩编辑器 |
| **效果器与修改器** | | |
| `AvalancheEffectors` | Runtime | 效果器系统 |
| `AvalancheEffectorsEditor` | Runtime | 效果器编辑器 |
| `AvalancheModifiers` | Runtime | 修改器系统 |
| `AvalancheModifiersEditor` | Runtime | 修改器编辑器 |
| `AvalancheAttribute` | Runtime | 属性系统 |
| `AvalancheAttributeEditor` | Runtime | 属性编辑器 |
| **集成与工具** | | |
| `AvalancheRemoteControl` | Runtime | 远程控制集成 |
| `AvalancheRemoteControlEditor` | Runtime | 远程控制编辑器 |
| `AvalancheTag` | Runtime | 标签系统 |
| `AvalancheTagEditor` | Runtime | 标签编辑器 |
| **视口与UI** | | |
| `AvalancheViewport` | Runtime | 自定义视口 |
| `AvalancheLevelViewport` | Runtime | 关卡视口集成 |
| `AvalancheInteractiveTools` | Runtime | 交互式工具 |
| `AvalancheInteractiveToolsRuntime` | Runtime | 交互工具运行时 |
| `AvalancheComponentVisualizers` | Runtime | 组件可视化器 |
| **测试** | | |
| `AvalancheFunctionalTest` | Runtime | 功能测试 |