# Geometry Collection Plugin

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合插件 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（几何集合容器资产，相关编辑器工具） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

此插件为虚幻引擎的 **大规模可破坏物体** 提供了核心的 **几何集合（Geometry Collection）** 容器和系统。它最初与Chaos物理系统（原Apeiron）一同开发，是实现程序化、基于物理的破坏效果（如墙体破碎、载具解体）的基础设施。

它的核心价值在于：
1.  **结构化破坏**：将一个完整的几何体（如一栋建筑）分解为多个独立的“块”（Geometry），并存储它们之间的父子关系、变换、材质等信息。
2.  **物理模拟集成**：这些“块”可以作为独立的刚体参与物理模拟，在受到足够冲击力时从父级分离，实现真实的破坏效果。
3.  **与Sequencer动画系统集成**：允许通过Sequencer时间轴精确控制破坏过程的关键帧，例如控制何时开始破碎、破碎的速度和效果。

插件名称中的“Container”强调了它是一个**数据容器**，负责存储和管理破坏物体的结构化数据，具体的模拟和渲染由其他系统（如GeometryCollectionComponent）处理。

## 使用场景

- **电影预渲染**：在Sequencer中精确编排一个建筑物被摧毁的动画序列，每一帧的破碎状态都可控制。
- **游戏中的动态破坏**：玩家使用火箭筒轰击墙壁，Chaos物理系统读取Geometry Collection数据，实时模拟墙壁的碎裂和坍塌。
- **复杂的破碎资产制作**：美术师在DCC工具（如Houdini）中预破碎模型，通过Geometry Collection流程导入引擎，保留层级和材质信息，用于高品质的实时破坏。

## 蓝图用法

该插件的核心是 **运行时数据容器** 和 **编辑器集成**。在蓝图中直接使用其功能通常通过 `GeometryCollectionComponent`（属于Chaos物理系统，不在本插件定义）来完成。本插件提供的蓝图节点主要用于**数据创建和编辑器交互**。

### 核心节点

此插件模块本身主要提供 C++ 类和 Sequencer 编辑器集成，未暴露大量 `BlueprintCallable` 节点。其核心价值在于为底层 `GeometryCollection` 数据结构提供支持。

## C++ 用法

本插件的API主要面向引擎底层开发者和高级插件开发者，用于构建和操作几何集合数据。

### 头文件引入

```cpp
#include "GeometryCollection/GeometryCollection.h"
// 以及对应模块的头文件，例如 Sequencer 集成:
#include "GeometryCollectionSequencerModule.h"
#include "GeometryCollectionTrackEditor.h"
```

### 基本用法

以下是创建和操作一个简单 `GeometryCollection` 对象的示例代码逻辑（基于源码推断）：
```cpp
// 创建一个几何集合对象
UGeometryCollection* MyGeometryCollection = NewObject<UGeometryCollection>();

// 通过其内部的ManagedArray系统添加变换、几何体等数据
// 例如，添加一个根变换
int32 TransformIndex = MyGeometryCollection->AddElements(1, EGeometryCollection::TransformGroup);
// 设置该变换的位置、旋转
MyGeometryCollection->Transform[TransformIndex] = FTransform(FRotator(0, 45, 0), FVector(100, 0, 0), FVector(1.0f));

// 添加几何体数据（顶点、索引等）通常通过GeometryCollectionComponent或编辑器流程完成
```

### 进阶用法：集成Sequencer

插件中的 `GeometryCollectionSequencer` 模块提供了 `FGeometryCollectionTrackEditor`，用于在Sequencer中创建和编辑几何集合的动画轨道。这是实现电影级破坏动画的关键。

```cpp
// 注册TrackEditor（通常在模块Startup中自动完成，见模块代码）
ISequencerModule& SequencerModule = FModuleManager::Get().LoadModuleChecked<ISequencerModule>("Sequencer");
FDelegateHandle TrackEditorBindingHandle = SequencerModule.RegisterTrackEditor(
    FOnCreateTrackEditor::CreateStatic(&FGeometryCollectionTrackEditor::CreateTrackEditor)
);
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个基础的 `GeometryCollection` 并为其添加一个变换（块）。

```cpp
// MyGeometryCollectionDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GeometryCollection/GeometryCollection.h"

class FMyGeometryCollectionDemo
{
public:
    static UGeometryCollection* CreateSimpleDemoCollection(UObject* Outer);
};

// MyGeometryCollectionDemo.cpp
#include "MyGeometryCollectionDemo.h"
#include "GeometryCollection/ManagedArrayAccessor.h" // 用于访问ManagedArray

UGeometryCollection* FMyGeometryCollectionDemo::CreateSimpleDemoCollection(UObject* Outer)
{
    UGeometryCollection* Collection = NewObject<UGeometryCollection>(Outer);
    if (!Collection) return nullptr;

    // 确保有一个根节点
    GeometryCollectionAlgo::EnsureSingleRoot(Collection);

    // 添加一个子变换（一个立方体块）
    const int32 ChildBoneIndex = Collection->AddElements(1, EGeometryCollection::TransformGroup);
    Collection->BoneHierarchy[ChildBoneIndex] = 0; // 0 通常是根节点索引

    // 设置局部变换
    Collection->Transform[ChildBoneIndex] = FTransform(FVector(0, 0, 100)); // 放在根节点上方100单位

    // 为这个变换分配一个简单的几何体（此处仅为示意，实际需要顶点/索引数据）
    // ... 添加几何体数据的代码 ...

    return Collection;
}
```

## 模块依赖

要使用此插件及其功能，你的项目模块通常需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `GeometryCollection` | 几何集合的核心数据结构定义。是所有相关模块的基础。 |
| `GeometryCollectionEngine` | 包含 `UGeometryCollectionComponent` 等运行时组件，是与物理和渲染系统交互的桥梁。 |
| `Chaos` | Chaos物理系统。Geometry Collection的数据最终由Chaos驱动进行破碎模拟。 |
| `Sequencer` | 使用 `GeometryCollectionSequencer` 模块功能时，需要依赖虚幻的序列器系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复UE 5.8中的本地化警告，表明为新版本引擎做兼容性适配。 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | 与数据流（Dataflow）系统相关的更新。 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 撤销了编号为CL53945814的更改。 |
| 2026-05-14 | `88fb5004` | Dataflow: | 继续数据流系统的相关工作。 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增一个数据流节点，用于在几何集合上创建外部碰撞体。 |

### 维护评价

该插件自2018年创建以来，作为虚幻引擎Chaos破坏系统的核心组成部分，经历了长期的开发和维护。虽然它仍被标记为“实验性”且默认未启用，但其代码库是成熟且持续更新的。

**近期活动表明它仍在活跃维护中**，主要更新集中在：
1.  **引擎版本兼容性**（如修复5.8的警告）。
2.  **系统功能增强**（如与数据流系统的集成，增加新节点）。

**建议**：对于需要实现高级、可控物理破坏效果的项目（如电影、高品质游戏），可以考虑启用和使用此插件。但由于其“实验性”状态，在生产环境中使用需进行充分测试，并准备好应对潜在的API变动。它不是一个独立的蓝图友好型插件，而是深度集成在引擎底层，主要面向C++开发者和技术美术。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档](https://docs.unrealengine.com) （官方文档链接为空，需查阅虚幻引擎官方文档关于Chaos破坏系统的部分）