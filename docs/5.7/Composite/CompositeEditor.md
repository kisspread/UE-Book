# CompositeEditor 模块（Editor）

> 编辑器模块，提供合成管线的 UI 面板、属性自定义、Actor 工厂和 Multi-User 集成。

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | `CompositeEditor` |
| 类型 | Editor |
| LoadingPhase | Default |
| 源码路径 | `Source/CompositeEditor/` |

## 功能概览

CompositeEditor 模块为 Composite 运行时模块提供完整的编辑器集成：

1. **合成编辑器面板** — 专用的编辑器 Tab，提供层树、Pass 管理和 Actor 选择器
2. **属性自定义** — 为每种 Layer 类型提供定制的 Details 面板
3. **Actor 工厂** — 创建 `ACompositeActor` 时自动配置默认层
4. **Multi-User 支持** — 通过 Concert 集成同步合成状态
5. **Holdout 组件警告** — 检测并警告冲突的 HoldoutCompositeComponent

## UI 组件

### SCompositeEditorPanel

主编辑器面板，提供完整的合成管线编辑界面。通过编辑器菜单或命令打开。

### SCompositePanelLayerTree

层树视图，显示 `ACompositeActor` 中所有层的列表。支持：
- 层的拖拽排序
- 层的启用/禁用/独奏切换
- 层的添加/删除

### SCompositePassTree

Pass 树视图，显示当前选中层的所有 Pass。支持 Pass 的添加、删除和排序。

### SCompositePlatePassPanel

Plate 层专用的 Pass 管理面板，区分 Media Passes、Scene Passes 和 Layer Passes 三个阶段。

### SCompositeActorPickerTable / SCompositeActorPickerSceneOutliner

Actor 选择器组件，用于为 Layer 选择引用的 Actor（如 Composite Mesh Actor、Shadow Caster Actor 等）。提供表格视图和场景大纲视图两种选择方式。

## 属性自定义

### FCompositeActorCustomization

`ACompositeActor` 的 Details 面板自定义：
- 自定义层列表的编辑界面
- 摄像机选择器集成

### FCompositeLayerPlateCustomization

`UCompositeLayerPlate` 的属性自定义：
- Plate 模式相关属性的条件显示
- Composite Mesh 列表编辑

### FCompositeLayerSceneCaptureCustomization

`UCompositeLayerSceneCapture` 的属性自定义：
- Scene Capture 相关属性的条件显示
- Actor 列表编辑

### FCompositeLayerShadowReflectionCustomization

`UCompositeLayerShadowReflection` 的属性自定义：
- Shadow/Reflection Catcher 相关属性

### FCompositeLayerSingleLightShadowCustomization

`UCompositeLayerSingleLightShadow` 的属性自定义：
- 光源选择器
- 阴影参数调整

## Actor 工厂

### UCompositeActorFactory

`ACompositeActor` 的工厂类，放置到关卡时自动创建三个默认层：

1. **MainRenderLayer**（`UCompositeLayerMainRender`）— 主渲染层，启用
2. **ShadowReflectionLayer**（`UCompositeLayerShadowReflection`）— 阴影/反射层，**默认禁用**（因性能开销较大）
3. **PlateLayer**（`UCompositeLayerPlate`）— 媒体板层，启用

同时记录 `Editor.Usage.Composite.PostSpawnActor` 分析事件。

## 编辑器命令与样式

### FCompositeEditorCommands

注册编辑器命令（如打开合成面板的快捷键）。

### FCompositeEditorStyle

注册编辑器 UI 样式（图标、颜色等）。

## Multi-User 集成

通过 `ConcertSyncClient` 集成 Multi-User 编辑：

- `HandleWorkspaceStartup()` — 工作区启动时绑定回调
- `HandleWorkspaceShutdown()` — 工作区关闭时清理
- `HandleFinalizeWorkspaceSyncCompleted()` — 同步完成后触发 `ACompositeActor::PostJoinConcertSession()`

## Holdout 组件警告

当检测到 `UHoldoutCompositeComponent` 在包含 `ACompositeActor` 的关卡中创建时，会触发警告通知。这是因为两个系统可能产生功能冲突。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心 |
| `Composite` | 运行时合成模块 |
| `ApplicationCore` | 应用核心 |
| `CompositeCore` | 合成核心框架 |
| `ConcertSyncClient` | Multi-User 同步客户端 |
| `CoreUObject` | UObject 系统 |
| `EditorWidgets` | 编辑器控件 |
| `Engine` | 引擎基础 |
| `InputCore` | 输入核心 |
| `LevelEditor` | 关卡编辑器集成 |
| `MediaAssets` | 媒体资产 |
| `MediaFrameworkUtilities` | 媒体框架工具 |
| `Projects` | 项目管理 |
| `PropertyEditor` | 属性编辑器 |
| `UnrealEd` | Unreal 编辑器框架 |
| `SceneOutliner` | 场景大纲视图 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolMenus` | 工具菜单 |
| `ToolWidgets` | 工具控件 |
| `WorkspaceMenuStructure` | 工作区菜单结构 |
