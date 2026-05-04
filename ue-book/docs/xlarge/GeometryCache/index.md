# Geometry Cache

> Support for distilled Geometry animations

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCache` (Runtime), `GeometryCacheEd` (Runtime), `GeometryCacheSequencer` (Runtime), `GeometryCacheStreamer` (Runtime), `GeometryCacheTracks` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-04-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache) | |

## 用途

GeometryCache 插件的核心功能是支持**几何缓存动画**。它解决的核心问题是：如何在 Unreal Engine 中高效地播放和渲染由大量顶点逐帧变化构成的复杂动画数据。

传统的骨骼动画适用于角色关节运动，但对于布料飘动、流体模拟、复杂形变（如面部表情捕捉）或从其他DCC软件（如Maya, Houdini）导出的顶点动画，骨骼动画无法胜任。GeometryCache 通过存储每一帧的网格顶点位置数据（通常从 Alembic (.abc) 或其他格式导入），并在运行时按顺序播放这些帧，从而实现了对这类“蒸馏”几何动画的支持。它本质上是一个**顶点动画播放器**。

## 使用场景

- **电影级过场动画**：播放从影视级DCC软件导出的、包含复杂角色变形或环境破坏的动画序列。
- **布料与流体模拟**：实时展示预先计算好的布料、毛发或流体模拟结果。
- **建筑可视化**：展示建筑结构的动态组装过程或复杂的机械运动。
- **特效与环境动画**：播放由粒子系统或物理模拟生成的、无法用骨骼驱动的复杂几何体动画。

## 蓝图用法

本插件主要通过资产（GeometryCache资产）和组件（GeometryCacheComponent）在蓝图中使用。核心操作是控制组件的播放。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 开始或恢复播放几何缓存动画 | `UGeometryCacheComponent` |
| `Stop` | 停止播放 | `UGeometryCacheComponent` |
| `Pause` | 暂停播放 | `UGeometryCacheComponent` |
| `SetPlaybackSpeed` | 设置播放速度倍率 | `UGeometryCacheComponent` |
| `SetStartTimeOffset` | 设置播放的起始时间偏移 | `UGeometryCacheComponent` |
| `GetPlaybackSpeed` | 获取当前播放速度 | `UGeometryCacheComponent` |
| `GetDuration` | 获取动画总时长 | `UGeometryCacheComponent` |
| `SetGeometryCache` | 运行时更换要播放的几何缓存资产 | `UGeometryCacheComponent` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `GeometryCacheComponent` 组件。
2.  在组件的细节面板中，为其指定一个 `GeometryCache` 资产。
3.  通过蓝图事件（如 `BeginPlay`）调用 `Play` 节点开始播放。
4.  可以使用 `SetPlaybackSpeed` 节点动态调整播放速度，或使用 `Stop`/`Pause` 节点控制播放状态。

## C++ 用法

C++ 用法主要围绕 `UGeometryCacheComponent` 类进行控制，以及对 `UGeometryCache` 资产的程序化操作。

### 头文件引入

```cpp
#include "GeometryCacheComponent.h"
#include "GeometryCache.h"
```

### 基本用法

```cpp
// 假设你已经有一个指向 UGeometryCacheComponent 的指针 GeometryCacheComp
// 开始播放
if (GeometryCacheComp)
{
    GeometryCacheComp->Play();
    GeometryCacheComp->SetPlaybackSpeed(1.5f); // 1.5倍速播放
}

// 获取动画时长
float Duration = GeometryCacheComp->GetDuration();
```

### 进阶用法

程序化创建和加载几何缓存资产通常涉及异步加载和序列化，具体实现较为复杂，通常通过编辑器导入流程完成。运行时更换资产：

```cpp
// 异步加载一个新的 GeometryCache 资产
FSoftObjectPath AssetPath(TEXT("/Game/Path/To/NewGeometryCache"));
UAssetManager::GetStreamableManager().RequestAsyncLoad(
    AssetPath,
    FStreamableDelegate::CreateLambda([this, AssetPath]()
    {
        UGeometryCache* NewCache = Cast<UGeometryCache>(AssetPath.ResolveObject());
        if (NewCache && GeometryCacheComp)
        {
            GeometryCacheComp->SetGeometryCache(NewCache);
            GeometryCacheComp->Play();
        }
    })
);
```

## Demo 示例

一个最小可运行示例通常包含：
1.  **资产**：一个导入的 `.abc` 文件生成的 `GeometryCache` 资产。
2.  **蓝图/代码**：一个包含 `GeometryCacheComponent` 的 Actor，并在事件图表或构造函数中调用 `Play()`。
3.  **Build.cs 依赖**：
    ```csharp
    PublicDependencyModuleNames.AddRange(new string[] { "GeometryCache" });
    ```

## 模块依赖

要使用此插件，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `GeometryCache` | 核心运行时模块，包含资产、组件和播放逻辑。 |
| `GeometryCacheTracks` | 提供 Sequencer 动画轨道支持，用于在过场动画中控制几何缓存。 |
| `MeshUtilitiesCommon` | 提供网格处理相关的通用工具函数。 |

## 维护状态

### 近期更新

（基于插件创建时间和一般维护模式推断）
该插件创建于 2018 年，是 UE4 时代引入的功能。作为 Epic 官方维护的运行时插件，它通常会跟随引擎主版本进行维护和更新，以确保兼容性和性能优化，但核心功能已趋于稳定。

### 维护评价

- **创建时间**：2018年，已有约7年历史。
- **维护状态**：作为引擎核心功能的一部分，处于**稳定维护**状态。虽然不常有重大新特性，但会持续修复 bug 和保持与新版引擎的兼容性。
- **推荐使用**：**是**。对于需要播放预计算顶点动画的场景，这是官方推荐且成熟的解决方案。它稳定、集成度高（与Sequencer、蓝图深度集成），是处理此类需求的标准工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/AlembicImporter/#importasgeometrycache)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryCache/Tests)