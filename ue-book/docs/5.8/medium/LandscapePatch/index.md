# Landscape Patch

> Support for adding landscape patches- components that can be attached to meshes to affect the landscape as the mesh is repositioned.

| 属性 | 值 |
|---|---|
| 中文名 | 地形补丁 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LandscapePatch` (Runtime), `LandscapePatchEditorOnly` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-19 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LandscapePatch) | |

## 用途

LandscapePatch 插件提供了一种动态的地形修改方式。它允许你创建并附加名为“补丁”（Patch）的组件到其他网格体上。当这个网格体在世界中移动时，附加的补丁会实时地、程序化地影响其下方的地形，包括修改地形的高度图和图层权重。这解决了传统地形编辑只能进行静态、预先计算修改的限制，适用于需要与场景中其他物体动态交互的地形效果。

## 使用场景

- **大世界游戏中的动态地形**：当巨型载具（如坦克、飞船）碾过或降落在地面上时，需要实时生成轮迹或压痕。
- **环境交互**：实现地鼠打洞、树根拱起地表等随物体位置变化的地形形变。
- **游戏玩法相关的地形生成**：例如，一个可移动的建造物（如钻机、炮台）需要在其下方创建平整区域或坑洞。
- **电影级场景制作**：需要精确控制某些物体周围地形形态的过场动画。

## 蓝图用法

该插件的核心功能通过蓝图组件暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AttachToLandscape` | 将当前补丁组件附加到指定的地形上 | `ULandscapePatchComponent` |
| `RemoveFromLandscape` | 将补丁组件从其附加的地形上移除 | `ULandscapePatchComponent` |
| `SetHeightPatchMesh` | 设置用于影响地形高度的静态网格体资产 | `ULandscapePatchComponent` |
| `SetEditLayerEnabled` | 启用或禁用此补丁在编辑层中的影响 | `ULandscapePatchComponent` |
| `GetWeightPatchComponent` | 获取用于修改地形图层权重的“权重补丁”子组件 | `ULandscapePatchComponent` |
| `SetWeightPatchTextureAsset` | 为权重补丁设置影响纹理 | `ULandscapeTexturePatch` |
| `SetBlendMode` | 设置权重补丁的混合模式（如混合、替换） | `ULandscapeTexturePatch` |

### 使用示例（蓝图描述）

1.  在场景中放置一个 `Static Mesh Actor`（例如一个轮子的网格体）。
2.  为其添加 `Landscape Patch Component`。
3.  在组件细节面板中，将 `Height Patch Mesh` 设置为一个代表凹陷形状的简单平面网格体。
4.  通过蓝图，在游戏开始时或特定事件后，调用 `AttachToLandscape` 节点，将其连接到场景中的 `Landscape Actor`。
5.  当 `Static Mesh Actor` 在世界中移动时，地形会自动在其当前位置下方根据 `Height Patch Mesh` 的形状进行变形。
6.  若需同时修改地形图层（如绘制草地/裸露土），可使用 `GetWeightPatchComponent` 获取一个 `Landscape Texture Patch`，并为其设置相应的纹理和混合模式。

## C++ 用法

### 头文件引入

```cpp
#include "LandscapePatchComponent.h"
#include "LandscapeTexturePatch.h"
```

### 基本用法

创建并附加一个高度补丁组件到地形。
```cpp
// 在 Actor 构造函数或 BeginPlay 中
UPROPERTY(VisibleAnywhere)
TObjectPtr<ULandscapePatchComponent> MyHeightPatchComponent;

// 创建并配置组件
MyHeightPatchComponent = CreateDefaultSubobject<ULandscapePatchComponent>(TEXT("HeightPatch"));
MyHeightPatchComponent->SetHeightPatchMesh(SomeMeshAsset); // 设置一个平面网格体
// 假设我们已经获取了对 LandscapeActor 的引用
MyHeightPatchComponent->AttachToLandscape(LandscapeActor);
```

### 进阶用法

创建一个纹理权重补丁，用于修改地形图层权重。
```cpp
UPROPERTY(VisibleAnywhere)
TObjectPtr<ULandscapeTexturePatch> MyWeightPatchComponent;

MyWeightPatchComponent = CreateDefaultSubobject<ULandscapeTexturePatch>(TEXT("WeightPatch"));
MyWeightPatchComponent->SetWeightPatchTextureAsset(GrassDirtBlendTexture);
MyWeightPatchComponent->SetBlendMode(ELandscapeTexturePatchBlendMode::Blend);
MyWeightPatchComponent->AttachToLandscape(LandscapeActor);
```

## 模块依赖

你的项目模块如果要使用此插件的功能，通常需要依赖 `LandscapePatch` 模块。对于编辑器扩展开发，可能需要依赖 `LandscapePatchEditorOnly`。

| 模块 | 用途 |
|---|---|
| `Landscape` | 核心地形系统交互 |
| `MeshDescription` | 处理用于补丁的网格体资产数据 |
| `StaticMeshDescription` | 静态网格体描述相关 |

## 维护状态

该插件于2025年9月从实验阶段移出，目前处于活跃维护状态。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-29 | `2037f2f2` | Fixed landscape patch crash when changing BP properties. | 修复了在蓝图中修改属性时导致的崩溃问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移至新式宏，属于代码现代化维护。 |
| 2026-02-26 | `e6de93e0` | Landscape Texture Patch - Added UseWorldPositionSampling flag to allow patches to change texture sampling behavior. | 为纹理补丁添加了新标志，允许改变纹理采样行为。 |
| 2026-02-06 | `bed46c8f` | Landscape Patch - Added GetWeightPatch helper function | 添加了获取权重补丁的辅助函数，方便蓝图调用。 |
| 2026-01-26 | `8987ad88` | Landscape Patch - Added ability for a patch edit layer's heightmap/weightmap alpha values to impact | 增强了编辑层功能，允许补丁的Alpha值影响地形。 |

### 维护评价

**推荐使用**。该插件自移出实验状态后，持续获得功能性更新和稳定性修复（如最新的崩溃修复）。更新频率稳定（约1-2个月），表明 Epic 团队在积极维护。它解决了地形动态修改这一特定需求，是相关项目不可或缺的工具。鉴于其较新的年龄和活跃的更新，建议关注其API的演进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/LandscapePatch)
- [模块文档 (LandscapePatch)](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/LandscapePatch/Source/LandscapePatch/LandscapePatch.md)
- [模块文档 (LandscapePatchEditorOnly)](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Editor/LandscapePatch/Source/LandscapePatchEditorOnly/LandscapePatchEditorOnly.md)