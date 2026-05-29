# Geometry Collection Plugin

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合插件 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、蓝图节点） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

基于源码分析，`GeometryCollectionPlugin` 是一个实验性插件，主要用于支持 **Chaos Destruction** 系统。它的核心功能是提供 **Geometry Collection** 容器，用于管理可破坏几何体的层次结构、变换和材质信息。这个插件是 Chaos 物理系统的基础组件，专门处理几何体在破坏过程中的拓扑关系和状态管理。

简单来说：这个插件存在是为了让你能够创建、编辑和控制基于 Chaos 物理的破坏效果。

## 使用场景

- **你需要创建可破坏的物体** → 使用 Geometry Collection 来定义物体的几何结构、碎片层次和破坏阈值。
- **你需要制作电影级的破坏特效** → 结合 Sequencer 和 Chaos 物理系统，通过动画控制破坏的时间线和过程。
- **你需要精细控制碎片** → 管理碎片的材质、碰撞体和父子关系，实现逼真的破碎效果。

## 蓝图用法

由于这是一个实验性插件，且主要通过代码和编辑器界面交互，蓝图用法相对有限。主要的交互通过 **Geometry Collection Component** 完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| (无直接暴露的通用蓝图节点) | 此插件主要提供底层数据结构和编辑器功能，核心交互通过 `UGeometryCollectionComponent` 和 `UGeometryCollection` 资产。 | - |

### 使用示例（蓝图描述）

在蓝图中，你通常会：
1.  创建一个 `UGeometryCollection` 资产（通常在编辑器中通过菜单创建）。
2.  将 `UGeometryCollectionComponent` 添加到你的 Actor。
3.  将创建的 `UGeometryCollection` 资产赋值给该组件。
4.  通过 Chaos Destruction Manager 或其他物理系统触发破坏。

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCollectionSequencerModule.h"
#include "GeometryCollectionTrackEditor.h"
```

### 基本用法

这个模块主要用于扩展 Unreal 的 Sequencer 功能，使其能够支持 Geometry Collection 的动画。

**注册 Sequencer Track Editor (在模块启动时):**
```cpp
// 来源: GeometryCollectionSequencerModule.h
void FGeometryCollectionSequencerModule::StartupModule()
{
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
    // 注册我们自定义的 Track Editor
    TrackEditorBindingHandle = SequencerModule.RegisterTrackEditor(
        FOnCreateTrackEditor::CreateStatic(&FGeometryCollectionTrackEditor::CreateTrackEditor)
    );
}
```

**创建自定义 Track Editor 实例:**
```cpp
// 来源: GeometryCollectionTrackEditor.h
TSharedRef<ISequencerTrackEditor> FGeometryCollectionTrackEditor::CreateTrackEditor(TSharedRef<ISequencer> OwningSequencer)
{
    return MakeShareable(new FGeometryCollectionTrackEditor(OwningSequencer));
}
```

### 进阶用法

**处理 Track 的 Section (用于 Sequencer 中的动画区间):**
```cpp
// 来源: GeometryCollectionTrackEditor.h
// 为 Geometry Collection Track 创建自定义的 Section 界面
TSharedRef<ISequencerSection> FGeometryCollectionTrackEditor::MakeSectionInterface(
    UMovieSceneSection& SectionObject,
    UMovieSceneTrack& Track,
    FGuid ObjectBinding)
{
    return MakeShareable(new FGeometryCollectionTrackSection(SectionObject, GetSequencer()));
}

// 自定义 Section 的绘制和交互逻辑
class FGeometryCollectionTrackSection : public ISequencerSection
{
public:
    // 自定义 Section 标题
    virtual FText GetSectionTitle() const override;
    
    // 自定义 Section 绘制
    virtual int32 OnPaintSection(FSequencerSectionPainter& Painter) const override;
    
    // 处理 Section 的缩放、滑动等操作
    virtual void ResizeSection(ESequencerSectionResizeMode ResizeMode, FFrameNumber ResizeTime) override;
};
```

**在 Sequencer 中添加关键帧:**
```cpp
// 来源: GeometryCollectionTrackEditor.h (概念性代码，实际实现需要更多上下文)
FKeyPropertyResult FGeometryCollectionTrackEditor::AddKeyInternal(
    FFrameNumber KeyTime,
    UObject* Object,
    UGeometryCollectionComponent* GeometryCollectionComponent,
    UMovieSceneTrack* Track)
{
    // 在这里处理为 Geometry Collection Component 添加关键帧的逻辑
    // 例如：记录破坏状态、变换信息等
}
```

## Demo 示例

这是一个创建自定义 Geometry Collection Sequencer Track 的最小示例（概念性）。

**MyGeometryCollectionModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyGeometryCollectionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
    
private:
    FDelegateHandle MyBindingHandle;
};
```

**MyGeometryCollectionModule.cpp**
```cpp
#include "MyGeometryCollectionModule.h"
#include "GeometryCollectionTrackEditor.h" // 假设我们需要扩展这个 Track Editor
#include "SequencerModule.h"

void FMyGeometryCollectionModule::StartupModule()
{
    // 这里我们展示了如何注册一个 Sequencer Track Editor
    // 实际的 GeometryCollectionSequencer 模块内部就做了这件事
    ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
    MyBindingHandle = SequencerModule.RegisterTrackEditor(
        FOnCreateTrackEditor::CreateStatic(&FGeometryCollectionTrackEditor::CreateTrackEditor)
    );
}

void FMyGeometryCollectionModule::ShutdownModule()
{
    ISequencerModule* SequencerModulePtr = FModuleManager::Get().GetModulePtr<ISequencerModule>("Sequencer");
    if (SequencerModulePtr)
    {
        SequencerModulePtr->UnRegisterTrackEditor(MyBindingHandle);
    }
}
```

## 模块依赖

从 GeometryCollectionSequencer 模块的 Build.cs 分析（虽然未提供具体内容，但根据头文件推断）：

| 模块 | 用途 |
|---|---|
| `Sequencer` | 提供 Sequencer 核心功能和接口 |
| `GeometryCollection` | 提供几何体集合的核心数据结构（可能是其他模块的一部分） |

**注意**：其他模块（如 `GeometryCollectionNodes`, `GeometryCollectionTracks`）可能会有额外的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 的本地化警告 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 相关更新 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退了之前的更改 (CL53945814) |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 相关更新 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | Dataflow：添加了一个在几何体集合上创建外部碰撞的节点 |

### 维护评价

- **活跃维护**：该插件目前仍在活跃开发中，最近一周内有多次更新。
- **实验性状态**：标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，表明它仍在开发中，不建议在生产环境使用。
- **功能方向**：近期更新集中在 **Dataflow** 和 **本地化** 方面，表明 Epic 可能正在将其与新的 Dataflow（数据流）系统集成，并准备用于 UE 5.8。
- **推荐使用**：如果你在使用 Chaos Destruction 系统，并且需要 Sequencer 支持，这个插件是必要的。但由于是实验性功能，可能会有变化或 bug。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中发现)