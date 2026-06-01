# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（Avalanche）是 Epic Games 为虚拟制片打造的**实时动态图形设计与广播工具**。它在 Unreal 的关卡编辑器之上构建了一套完整的 Motion Design 编辑器框架，使用户能够：

- **合成与设计**：在 3D 场景中创建广播级动态图形（Motion Graphics），支持 3D 文字、SVG 导入、几何形状、材质设计等
- **克隆与效果器**：通过 Cloner/Effector 系统实现大量对象的程序化生成与动画控制
- **属性动画**：基于 Sequencer 的属性动画系统，支持对 Actor 属性进行关键帧动画
- **场景管理**：提供 Scene Tree、Scene Rig 等场景组织工具，以及自定义大纲视图
- **广播控制**：集成 Remote Control 进行远程控制，支持 Rundown Page 播放管理
- **媒体合成**：与 Media IO 和 Media Compositing 集成，支持实时视频输入/输出
- **MRQ 支持**：集成 Movie Render Queue 进行高质量离线渲染输出

本插件从 2025 年 5 月由 `Plugins/Experimental` 迁移至 `Plugins/VirtualProduction`，标志着该工具集已脱离实验阶段，成为 Epic 官方支持的虚拟制片核心工作流之一。

本文档聚焦 **AvalancheEditorCore** 模块，该模块是整个 Motion Design 编辑器框架的**基础设施层**，提供了编辑器扩展系统、选择管理、包围盒计算、关卡编辑器集成等核心能力。

## 使用场景

- 你在做电视/直播虚拟制片，需要实时创建动态图形和字幕条 → 使用 Motion Design
- 你需要在关卡编辑器中直接设计和预览广播级视觉内容 → 使用 Motion Design
- 你需要程序化生成大量克隆对象并用效果器控制动画 → 使用 Cloner/Effector（ClonerEffector 插件）
- 你需要扩展 Motion Design 编辑器功能，添加自定义面板和工具 → 基于 AvalancheEditorCore 的扩展系统开发

## 蓝图用法

AvalancheEditorCore 主要是一个 **C++ 框架模块**，其核心 API 以 C++ 接口为主。以下子系统可通过蓝图访问：

### 核心子系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CacheActorAndChildrenOrientedBounds` | 缓存 Actor 及其子级的有向包围盒 | `UAvaBoundsProviderSubsystem` |
| `GetActorAndChildrenLocalBounds` | 获取 Actor 及子级的本地包围盒 | `UAvaBoundsProviderSubsystem` |
| `GetActorOrientedBounds` | 获取 Actor 的有向包围盒（支持旋转） | `UAvaBoundsProviderSubsystem` |
| `GetSelectionBounds` | 获取选中 Actor 的世界空间包围盒 | `UAvaBoundsProviderSubsystem` |
| `GetSelectionOrientedBounds` | 获取选中 Actor 的有向包围盒 | `UAvaBoundsProviderSubsystem` |
| `ClearCachedBounds` | 清除所有已缓存的包围盒数据 | `UAvaBoundsProviderSubsystem` |
| `GetSelectedActors` | 获取当前选中的 Actor 列表 | `UAvaSelectionProviderSubsystem` |
| `GetSelectedComponents` | 获取当前选中的组件列表 | `UAvaSelectionProviderSubsystem` |
| `GetSelectionTransform` | 获取选区变换（中心点 + 首个 Actor 旋转） | `UAvaSelectionProviderSubsystem` |
| `GetAttachedActors` | 获取 Actor 的附着子 Actor（支持递归） | `UAvaSelectionProviderSubsystem` |
| `GetActiveEditor` | 获取当前活跃的 Motion Design 编辑器实例 | `UAvaEditorSubsystem` |

### 使用示例（蓝图描述）

**获取选中 Actor 的包围盒：**
1. 使用 `Get Game Instance Subsystem` 节点，类设为 `UAvaBoundsProviderSubsystem`
2. 连接到 `CacheActorAndChildrenOrientedBounds`，输入目标 Actor
3. 连接到 `GetActorAndChildrenOrientedBounds`，获取 `FOrientedBox` 输出

**查询选区信息：**
1. 使用 `Get World Subsystem` 节点，类设为 `UAvaSelectionProviderSubsystem`
2. 连接到 `GetSelectedActors` 获取选中 Actor 数组
3. 连接到 `GetSelectionTransform` 获取选区中心变换

## C++ 用法

### 头文件引入

```cpp
#include "Bounds/AvaBoundsProviderSubsystem.h"
#include "Selection/AvaSelectionProviderSubsystem.h"
#include "IAvaEditor.h"
#include "IAvaEditorExtension.h"
#include "AvaEditorBuilder.h"
#include "AvaTabSpawner.h"
```

### 基本用法

**1. 查询 Actor 包围盒**

```cpp
// 来源: Public/Bounds/AvaBoundsProviderSubsystem.h
UAvaBoundsProviderSubsystem* BoundsSubsystem = World->GetSubsystem<UAvaBoundsProviderSubsystem>();

// 缓存并获取 Actor 的本地包围盒
BoundsSubsystem->CacheActorAndChildrenLocalBounds(MyActor);
FBox LocalBounds = BoundsSubsystem->GetActorAndChildrenLocalBounds(MyActor);

// 缓存并获取 Actor 的有向包围盒（支持旋转）
BoundsSubsystem->CacheActorAndChildrenOrientedBounds(MyActor);
FOrientedBox OrientedBounds;
if (BoundsSubsystem->GetActorAndChildrenOrientedBounds(MyActor, OrientedBounds))
{
    // 使用 OrientedBounds 进行碰撞检测或对齐计算
}
```

**2. 查询选区信息**

```cpp
// 来源: Public/Selection/AvaSelectionProviderSubsystem.h
UAvaSelectionProviderSubsystem* SelectionSubsystem = World->GetSubsystem<UAvaSelectionProviderSubsystem>();

TConstArrayView<TWeakObjectPtr<AActor>> SelectedActors = SelectionSubsystem->GetSelectedActors();
FTransform SelectionTransform = SelectionSubsystem->GetSelectionTransform();

// 获取某个 Actor 的递归附着子 Actor
TConstArrayView<TWeakObjectPtr<AActor>> AttachedActors = 
    SelectionSubsystem->GetAttachedActors(MyActor, true /* bRecursive */);
```

**3. 使用选择数据结构**

```cpp
// 来源: Public/Selection/AvaEditorSelection.h
// FAvaEditorSelection 封装了编辑器模式工具的选择状态
FAvaEditorSelection Selection(ModeTools, ChangedSelectionObject);

// 获取所有选中的 UObject（包括 Actor、Component、Object）
TArray<UObject*> AllSelected = Selection.GetSelectedObjects<UObject>();

// 仅获取选中的 Actor
TArray<AActor*> SelectedActors = Selection.GetSelectedObjects<AActor, EAvaSelectionSource::Single>();

// 获取对应的 USelection 对象
USelection* ActorSelection = Selection.GetSelection<AActor>();
```

### 进阶用法

**1. 构建自定义 Motion Design 编辑器扩展**

```cpp
// 来源: Public/IAvaEditorExtension.h, Public/AvaEditorBuilder.h
// 步骤 1: 定义扩展类
class FMyCustomExtension : public FAvaEditorExtension
{
public:
    UE_AVA_INHERITS(FMyCustomExtension, FAvaEditorExtension)

    virtual void Construct(const TSharedRef<IAvaEditor>& InEditor) override
    {
        FAvaEditorExtension::Construct(InEditor);
        // 初始化扩展资源
    }

    virtual void Activate() override
    {
        // 编辑器激活时执行
    }

    virtual void ExtendToolbarMenu(UToolMenu& InMenu) override
    {
        // 向 Motion Design 工具栏添加自定义按钮
    }

    virtual void OnSelectionChanged(const FAvaEditorSelection& InSelection) override
    {
        // 响应选择变化
        TArray<AActor*> SelectedActors = InSelection.GetSelectedObjects<AActor, EAvaSelectionSource::Single>();
        // 处理选择逻辑
    }

    virtual void OnCopyActors(FString& OutCopyData, TConstArrayView<AActor*> InActorsToCopy) override
    {
        // 扩展复制行为，附加自定义数据
    }

    virtual void OnPasteActors(FStringView InPastedData, TConstArrayView<FAvaEditorPastedActor> InPastedActors) override
    {
        // 扩展粘贴行为，恢复自定义数据
    }
};

// 步骤 2: 通过 Builder 注册扩展
FAvaEditorBuilder Builder;
Builder.SetIdentifier(FName("MyMotionDesignEditor"))
    .SetProvider<UMyEditorProvider>()
    .AddExtension<IAvaEditorExtension, FMyCustomExtension>();

TSharedRef<IAvaEditor> Editor = Builder.Build();
Editor->Activate();
```

**2. 注册静态启动/关闭回调**

```cpp
// 来源: Public/AvaEditorExtensionTypeRegistry.h
// 如果扩展需要模块级别的静态初始化（非实例级别），实现静态方法
class FMyStaticExtension : public FAvaEditorExtension
{
public:
    // 模块加载时调用一次
    static void StaticStartup()
    {
        // 注册全局菜单项、命令等
    }

    // 模块卸载时调用一次
    static void StaticShutdown()
    {
        // 清理全局注册
    }
};
// 注册到 FAvaEditorExtensionTypeRegistry::Get().RegisterExtension() 后自动调用
```

**3. 创建自定义 Tab Spawner**

```cpp
// 来源: Public/AvaTabSpawner.h, Public/IAvaTabSpawner.h
class FMyMotionDesignTab : public FAvaTabSpawner
{
public:
    FMyMotionDesignTab(const TSharedRef<IAvaEditor>& InEditor)
        : FAvaTabSpawner(InEditor, FName("MyMotionDesignTab"))
    {
        TabLabel = FText::FromString(TEXT("My Custom Panel"));
        TabRole = ETabRole::MajorTab;
    }

    virtual TSharedRef<SWidget> CreateTabBody() override
    {
        return SNew(SVerticalBox)
            + SVerticalBox::Slot()
            [
                SNew(STextBlock).Text(FText::FromString(TEXT("Hello Motion Design!")))
            ];
    }
};

// 注册 Tab
Editor->AddTabSpawner<FMyMotionDesignTab>();
```

## Demo 示例

**自定义编辑器扩展的最小示例**

```cpp
// MyMotionDesignExtension.h
#pragma once

#include "IAvaEditorExtension.h"

class FMyMotionDesignExtension : public FAvaEditorExtension
{
public:
    UE_AVA_INHERITS(FMyMotionDesignExtension, FAvaEditorExtension)

    virtual void Construct(const TSharedRef<IAvaEditor>& InEditor) override;
    virtual void Activate() override;
    virtual void Deactivate() override;
    virtual void Cleanup() override;

    virtual void ExtendToolbarMenu(UToolMenu& InMenu) override;
    virtual void NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection) override;

    static void StaticStartup();
    static void StaticShutdown();

private:
    FDelegateHandle SomeDelegateHandle;
};
```

```cpp
// MyMotionDesignExtension.cpp
#include "MyMotionDesignExtension.h"
#include "IAvaEditor.h"
#include "Selection/AvaSelectionProviderSubsystem.h"
#include "Bounds/AvaBoundsProviderSubsystem.h"
#include "ToolMenus.h"

void FMyMotionDesignExtension::Construct(const TSharedRef<IAvaEditor>& InEditor)
{
    FAvaEditorExtension::Construct(InEditor);
}

void FMyMotionDesignExtension::Activate()
{
    TSharedPtr<IAvaEditor> Editor = GetEditor();
    if (!Editor.IsValid())
    {
        return;
    }

    UWorld* World = GetWorld();
    if (UAvaSelectionProviderSubsystem* SelectionSub = World->GetSubsystem<UAvaSelectionProviderSubsystem>())
    {
        // 扩展激活后可以注册选择变化监听
    }
}

void FMyMotionDesignExtension::Deactivate()
{
    // 清理运行时资源
}

void FMyMotionDesignExtension::Cleanup()
{
    // 彻底清理
    SomeDelegateHandle.Reset();
}

void FMyMotionDesignExtension::ExtendToolbarMenu(UToolMenu& InMenu)
{
    FToolMenuSection& Section = InMenu.AddSection(
        IAvaEditorExtension::DefaultSectionName, 
        FText::FromString(TEXT("My Extensions"))
    );
    // 添加自定义工具栏按钮
}

void FMyMotionDesignExtension::NotifyOnSelectionChanged(const FAvaEditorSelection& InSelection)
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    // 获取选中 Actor 并更新包围盒缓存
    TArray<AActor*> SelectedActors = InSelection.GetSelectedObjects<AActor, EAvaSelectionSource::Single>();
    
    UAvaBoundsProviderSubsystem* BoundsSub = World->GetSubsystem<UAvaBoundsProviderSubsystem>();
    if (BoundsSub)
    {
        for (AActor* Actor : SelectedActors)
        {
            BoundsSub->CacheActorAndChildrenOrientedBounds(Actor);
        }
    }
}

void FMyMotionDesignExtension::StaticStartup()
{
    // 模块级初始化（仅执行一次）
}

void FMyMotionDesignExtension::StaticShutdown()
{
    // 模块级清理（仅执行一次）
}
```

## 模块依赖

AvalancheEditorCore 依赖了大量其他 Avalanche 子模块和 Unreal 引擎模块。以下仅列出**该模块独特**的依赖：

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | Motion Design 核心运行时库，提供基础类型与工具 |
| `AvalancheEditor` | Motion Design 编辑器主模块 |
| `LevelEditor` | 关卡编辑器集成（工具栏扩展、布局定制） |
| `WorkspaceMenuStructure` | 工作区菜单结构（Tab 分类与组织） |
| `EditorFramework` | 编辑器框架（Toolkit、EdMode 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Scene Settings 和 Outliner 面板移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 新增 MRQ 渲染的分析事件追踪 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 新增页面加载选项（全部/下一个/选中） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增项目设置，可强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |

### 维护评价

- **活跃维护中**：最近一次更新距今不到 1 周，更新频率极高（每周多次提交）
- **功能迭代持续**：近期提交涵盖 UI 优化、新功能添加、项目设置扩展等实质性改动
- **Epic 官方维护**：由 Epic Games 核心团队维护，长期支持有保障
- **已脱离实验阶段**：2025 年 5 月从 Experimental 迁移至 VirtualProduction，说明功能已趋于稳定
- **大型代码库**：44 个模块、2060 个源文件，架构成熟但学习曲线较陡
- **推荐使用**：如果你的项目涉及虚拟制片或广播级动态图形制作，强烈推荐使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)