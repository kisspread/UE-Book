# Geometry Collection Plugin

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据流图、渲染资源、测试资产） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

本插件是 UE5 实验性模块，为“Geometry Collection（几何体集合）”提供全链路支持。Geometry Collection 是一种将破碎几何体（如脆性材料碎片）以集群方式管理的高效数据结构，广泛应用于破坏模拟（Chaos Physics）和程序化几何体处理。该插件通过以下子模块实现：

- **GeometryCollectionNodes** – 数据流（Dataflow）节点，支持几何体集合的创建、转换、材质覆盖等操作。
- **GeometryCollectionDepNodes** – 数据流依赖节点，处理几何体集合之间的依赖关系。
- **GeometryCollectionEditor** – 编辑器工具，提供几何体集合的预览、编辑和导入界面。
- **GeometryCollectionTracks** – 动画轨道，允许在 Sequencer 中直接控制几何体集合属性（如可见性、位置、材质等）。
- **GeometryCollectionSequencer** – Sequencer 集成，为几何体集合轨道注册自定义轨道编辑器，实现在动画序列中编排几何体集合的物理模拟和变形。

该插件解决了 Chaos 破坏模拟中碎片管理、动画编排和程序化修改的复杂性问题，是建筑破坏、环境交互、电影特效等场景的核心工具链。

## 使用场景

- 制作建筑倒塌、物体碎裂的破坏效果（需要搭配 Chaos Physics 和 Geometry Collection 组件）。
- 在 Sequencer 中控制几何体集合的播放顺序、触发时间点及材质切换。
- 使用 Dataflow 编辑器批量处理几何体集合的合并、分割、材质覆盖等操作。
- 开发需要程序化创建/修改复杂几何体集合的工具或游戏机制。

## 蓝图用法

本插件中所有模块均为 C++ 原生实现，未暴露蓝图可调用函数。但 Geometry Collection 的运行时组件（如 `UGeometryCollectionComponent`）及其触发方式（如 `ApplyBreakingForce`）源自 Chaos Physics 插件，不属于本插件范围。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCollectionSequencerModule.h"
#include "GeometryCollectionTrackEditor.h"
```

其中 `GeometryCollectionSequencerModule` 用于模块生命期注册，`GeometryCollectionTrackEditor` 用于自定义轨道编辑器。

### 基本用法

以下示例演示如何在编辑器模块中手动注册几何体集合轨道编辑器（类似 `GeometryCollectionSequencerModule` 所做之事）：

```cpp
// 来源：GeometryCollectionSequencerModule.cpp
void FMyModule::StartupModule()
{
    // 获取 Sequencer 模块
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
    
    // 注册轨道编辑器
    FDelegateHandle Handle = SequencerModule.RegisterTrackEditor(
        FOnCreateTrackEditor::CreateStatic(&FGeometryCollectionTrackEditor::CreateTrackEditor)
    );
}
```

### 进阶用法

自定义轨道编辑器实现关键接口示例：

```cpp
// 来源：GeometryCollectionTrackEditor.h
void FGeometryCollectionTrackEditor::BuildObjectBindingTrackMenu(
    FMenuBuilder& MenuBuilder,
    const TArray<FGuid>& ObjectBindings,
    const UClass* ObjectClass)
{
    // 当绑定对象为 UGeometryCollectionComponent 时添加菜单项
    if (ObjectClass->IsChildOf(UGeometryCollectionComponent::StaticClass()))
    {
        MenuBuilder.AddMenuEntry(
            NSLOCTEXT("GeometryCollectionTrackEditor", "AddTrack", "Geometry Collection"),
            FText::GetEmpty(),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateSP(this, &FGeometryCollectionTrackEditor::BuildGeometryCollectionTrack, ObjectBindings[0], nullptr, nullptr))
        );
    }
}
```

用户可通过继承 `FMovieSceneTrackEditor` 并覆盖 `SupportsType`、`MakeSectionInterface` 等方法来定制轨道的外观与行为。

## Demo 示例

由于插件规模较大且涉及多个模块，提供一个最小但完整的轨道注册与行为实现。

### GeometryCollectionDemoModule.h

```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FGeometryCollectionDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle TrackEditorBindingHandle;
};
```

### GeometryCollectionDemoModule.cpp

```cpp
#include "GeometryCollectionDemoModule.h"
#include "ISequencerModule.h"
#include "GeometryCollectionTrackEditor.h"

void FGeometryCollectionDemoModule::StartupModule()
{
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
    TrackEditorBindingHandle = SequencerModule.RegisterTrackEditor(
        FOnCreateTrackEditor::CreateStatic(&FGeometryCollectionTrackEditor::CreateTrackEditor)
    );
}

void FGeometryCollectionDemoModule::ShutdownModule()
{
    ISequencerModule* SequencerModulePtr = FModuleManager::Get().GetModulePtr<ISequencerModule>("Sequencer");
    if (SequencerModulePtr)
    {
        SequencerModulePtr->UnRegisterTrackEditor(TrackEditorBindingHandle);
    }
}

IMPLEMENT_MODULE(FGeometryCollectionDemoModule, GeometryCollectionDemo);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sequencer` | 提供轨道编辑器和序列化框架 |
| `MovieScene` | 基础电影场景系统 |
| `MovieSceneTracks` | 内置轨道类型支持 |
| `GeometryCollectionTracks` | 定义 `UMovieSceneGeometryCollectionTrack` 和 `UMovieSceneGeometryCollectionSection` |

**注意**：实际使用中还需要依赖 `GeometryCollectionEngine`（位于 Chaos Physics 插件），但本插件自身未直接列出。开发时需手动添加 `GeometryCollectionEngine` 到 Build.cs 中的 `PrivateDependencyModuleNames`。

## 维护状态

### 近期更新

- 2025-09-25 `745ebb56` Add support for override materials for geometry collection root proxies  
- 2025-09-24 `787ab8b2` Geometry collection : add cvar to disable the dialog that ask to create a Dataflow graph when openin  
- 2025-09-23 `29aa54b8` Dataflow : add settings for Dataflow editor  
- 2025-09-16 `9a2a2477` Dataflow : fix Tetrahedron rendering crashing when the source collection was split in multiple geome  
- 2025-09-06 `38d85df2` dataflow : expose all properties of TransformCollection node as inputs  

### 维护评价

该插件创建于 2025-09-06，至今（约 2 个月）仍处于活跃开发阶段，每周都有实质性更新（包括功能添加、Bug 修复和配置优化）。其 `IsBetaVersion` 标记为 `true`，表明仍属实验性质，API 可能发生变更。当前没有观察到已知重大限制或弃用警告。**推荐在实验性项目中尝试使用，生产环境需谨慎评估。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/geometry-collections-in-unreal-engine/)（外部参考）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin/Tests)