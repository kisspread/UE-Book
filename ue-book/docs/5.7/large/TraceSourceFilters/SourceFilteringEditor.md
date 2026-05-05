# SourceFilteringEditor 模块

> 编辑器 UI：在 Unreal Insights 中提供过滤器管理面板、TreeView 和 Session 服务。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | Editor |
| LoadingPhase | PreDefault |

## 职责

SourceFilteringEditor 是插件的编辑器模块，提供：

1. **Insights 集成面板** — 在 Unreal Insights 中嵌入 Source Filtering 页签
2. **TreeView UI** — 可视化展示和编辑过滤器层级
3. **Session 服务** — 管理与运行时实例的通信
4. **World 过滤 UI** — 按 World 类型和网络模式过滤
5. **类过滤 UI** — 按 Actor 类快速过滤
6. **拖放操作** — 支持过滤器的拖放重排
7. **Blueprint 删除处理** — 当 Blueprint 过滤器类被删除时优雅降级

## 源文件

| 文件 | 说明 |
|---|---|
| `SourceFilteringEditorModule.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SourceFilteringEditorModule.h) — 模块入口 |
| `ISessionSourceFilterService.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/ISessionSourceFilterService.h) — Session 服务接口 |
| `EditorSessionSourceFilterService.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/EditorSessionSourceFilterService.h) — 编辑器 Session 实现 |
| `SourceFilterService.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SourceFilterService.h) — 分析会话服务 |
| `STraceSourceFilteringWidget.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/STraceSourceFilteringWidget.h) — 主面板 Widget |
| `SSourceFilteringTreeview.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SSourceFilteringTreeview.h) — TreeView Widget |
| `SClassTraceFilteringWidget.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SClassTraceFilteringWidget.h) — Actor 类过滤 Widget |
| `SWorldTraceFilteringWidget.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SWorldTraceFilteringWidget.h) — World 过滤 Widget |
| `SUserTraceFilteringWidget.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SUserTraceFilteringWidget.h) — 用户过滤 Widget |
| `SFilterObjectWidget.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SFilterObjectWidget.h) — 单个过滤器 Widget |
| `SWorldObjectWidget.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SWorldObjectWidget.h) — World 对象 Widget |
| `FilterObject.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/FilterObject.h) — 过滤器 UI 数据模型 |
| `FilterSetObject.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/FilterSetObject.h) — FilterSet UI 数据模型 |
| `IFilterObject.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/IFilterObject.h) — 过滤器对象接口 |
| `ClassFilterObject.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/ClassFilterObject.h) — 类过滤 UI 模型 |
| `WorldObject.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/WorldObject.h) — World 对象 UI 模型 |
| `WorldFilters.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/WorldFilters.h) — World 过滤器实现 |
| `FilterDragDropOperation.h` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/FilterDragDropOperation.h) — 拖放操作 |
| `TreeViewBuilder.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/TreeViewBuilder.h) — TreeView 数据构建 |
| `SourceFilterStyle.h/cpp` | [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Developer/TraceSourceFiltering/Source/SourceFilteringEditor/Private/SourceFilterStyle.h) — UI 样式 |

## 核心接口

### ISessionSourceFilterService

与运行时 Trace 实例通信的抽象接口。每个连接的 Trace Session 对应一个服务实例。

```cpp
class ISessionSourceFilterService
{
public:
    // 数据变更通知
    virtual FOnSessionStateChanged& GetOnSessionStateChanged() = 0;

    // 过滤器管理
    virtual void AddFilter(const FString& FilterClassName) = 0;
    virtual void RemoveFilter(TSharedRef<const IFilterObject> InFilter) = 0;
    virtual void AddFilterToSet(TSharedRef<const IFilterObject> FilterSet,
                                const FString& FilterClassName) = 0;
    virtual void MakeTopLevelFilter(TSharedRef<const IFilterObject> Filter) = 0;
    virtual void MakeFilterSet(TSharedRef<const IFilterObject> Filter,
                               EFilterSetMode Mode) = 0;
    virtual void SetFilterState(TSharedRef<const IFilterObject> Filter, bool bState) = 0;
    virtual void SetFilterSetMode(TSharedRef<const IFilterObject> Filter,
                                  EFilterSetMode Mode) = 0;
    virtual void ResetFilters() = 0;

    // 设置管理
    virtual void UpdateFilterSettings(UTraceSourceFilteringSettings* InSettings) = 0;
    virtual UTraceSourceFilteringSettings* GetFilterSettings() = 0;

    // TreeView
    virtual void PopulateTreeView(FTreeViewDataBuilder& InBuilder) = 0;

    // 选择器 Widget
    virtual TSharedRef<SWidget> GetFilterPickerWidget(FOnFilterClassPicked Delegate) = 0;
    virtual TSharedRef<SWidget> GetClassFilterPickerWidget(FOnFilterClassPicked Delegate) = 0;

    // World 管理
    virtual void GetWorldObjects(TArray<TSharedPtr<FWorldObject>>& OutWorldObjects) = 0;
    virtual void SetWorldTraceability(TSharedRef<FWorldObject> WorldObject, bool bState) = 0;
    virtual const TArray<TSharedPtr<IWorldTraceFilter>>& GetWorldFilters() = 0;

    // 类过滤
    virtual void AddClassFilter(const FString& ActorClassName) = 0;
    virtual void RemoveClassFilter(TSharedRef<FClassFilterObject> ClassFilterObject) = 0;
    virtual void GetClassFilters(TArray<TSharedPtr<FClassFilterObject>>& OutClasses) const = 0;
    virtual void SetIncludeDerivedClasses(TSharedRef<FClassFilterObject> ClassFilterObject,
                                          bool bIncluded) = 0;
};
```

### IWorldTraceFilter

World 过滤器的 UI 接口：

```cpp
class IWorldTraceFilter : public TSharedFromThis<IWorldTraceFilter>
{
public:
    virtual FText GetDisplayText() = 0;
    virtual FText GetToolTipText() = 0;
    virtual TSharedRef<SWidget> GenerateWidget() = 0;
};
```

内置实现：
- **FWorldTypeTraceFilter** — 按 `EWorldType`（Editor、PIE、Game 等）过滤
- **FWorldNetModeTraceFilter** — 按 `ENetMode`（Standalone、DedicatedServer、Client 等）过滤

## UI 架构

```
STraceSourceFilteringWidget (主面板)
├── SUserTraceFilteringWidget (用户自定义过滤器面板)
│   └── SSourceFilteringTreeview (过滤器 TreeView)
│       ├── SFilterObjectWidget (单个过滤器节点)
│       └── SFilterObjectWidget (FilterSet 节点)
├── SClassTraceFilteringWidget (Actor 类过滤面板)
│   └── FClassFilterObject (类过滤条目)
└── SWorldTraceFilteringWidget (World 过滤面板)
    ├── SWorldObjectWidget (World 实例条目)
    ├── FWorldTypeTraceFilter (按类型过滤)
    └── FWorldNetModeTraceFilter (按网络模式过滤)
```

### 面板布局

1. **Source Filtering** 主面板嵌入 Insights 的 Major Tab
2. 通过 `FSourceFilteringEditorModule::RegisterLayoutExtensions` 注册到 Insights 布局
3. 面板可通过菜单 Toggle 显示/隐藏

### TreeView 交互

- **拖放**：支持通过 `FFilterDragDropOperation` 在 TreeView 中拖放重排过滤器
- **右键菜单**：通过 `FExtender` 机制扩展上下文菜单
- **类选择器**：`GetFilterPickerWidget` 提供可用过滤器类的选择弹窗
- **Actor 类选择器**：`GetClassFilterPickerWidget` 提供 Actor 类的选择弹窗

## Session 通信

### EditorSessionSourceFilterService

`ISessionSourceFilterService` 的编辑器实现，通过 Trace 命令通道与运行时实例通信：

1. 编辑器 UI 操作 → `ISessionSourceFilterService` 方法调用
2. 方法调用 → 构造 Trace 命令
3. Trace 命令 → 通过 `FTraceSourceFiltering::ProcessRemoteCommand` 在运行时执行
4. 运行时状态变更 → 通过 Trace 事件回传到编辑器
5. Trace 事件 → 重建编辑器 UI 状态

### SourceFilterService

工厂类，为每个 Trace 分析会话创建对应的 `ISessionSourceFilterService`：

```cpp
class FSourceFilterService
{
public:
    static TSharedRef<ISessionSourceFilterService>
        GetFilterServiceForSession(uint32 InHandle,
                                   TSharedRef<const TraceServices::IAnalysisSession> AnalysisSession);
};
```

## Blueprint 过滤器删除处理

当用户在编辑器中删除一个 Blueprint 过滤器类时，`SourceFilteringEditorModule` 会：

1. 通过 `OnAssetsPendingDelete` 回调检测即将删除的资产
2. 检查 `USourceFilterCollection` 中是否有使用该类的过滤器实例
3. 将受影响的过滤器替换为 `UEmptySourceFilter`（占位符，始终返回 `true`）
4. 记录 `MissingClassName` 以便用户知道原始类名

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Slate` / `SlateCore` / `InputCore` | UI 框架 |
| `TraceServices` | Trace 分析服务 |
| `TraceInsights` | Insights 集成 |
| `TraceAnalysis` | Trace 分析引擎 |
| `WorkspaceMenuStructure` | 编辑器菜单注册 |
| `SourceFilteringCore` | 核心接口 |
| `PropertyPath` | 属性路径 |
| `GameplayInsights` | Gameplay Insights 页签扩展 |
| `Engine`（条件） | 引擎类型（bCompileAgainstEngine） |
| `SourceFilteringTrace`（条件） | 运行时过滤（bCompileAgainstEngine） |
| `EditorFramework`（条件） | 编辑器框架（bBuildEditor） |
| `UnrealEd`（条件） | 编辑器工具（bBuildEditor） |
