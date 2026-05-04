# HDRIBackdrop

> HDRI 环境背景放置工具

| 属性 | 值 |
|---|---|
| 分类 | Rendering |
| 默认启用 | ❌ 否（需手动启用） |
| 包含内容 | ✅ 是 |
| 模块 | HDRIBackdrop (Editor) |
| 创建时间 | 2019-08-23 |
| 年龄标签 | 👴 老古董（>5年，约 6.7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HDRIBackdrop) | |

## 用途

HDRIBackdrop 是一个纯蓝图插件，提供一个可以快速在场景中放置 HDRI（高动态范围图像）环境背景的 Actor。它解决了在关卡设计和视觉开发中快速搭建基于 HDRI 的天空/环境背景的需求——不需要手动创建天空球、配置材质和贴图，只需从放置面板拖拽一个 Actor 到场景中即可。

插件本身没有 C++ 业务逻辑，只有三段很小的 C++ 代码负责：将 Blueprint 注册到编辑器的 Placement Mode（放置面板）的 **Lights** 分类下，以及注册 Slate 图标样式。真正的功能全部由蓝图 `HDRIBackdrop.uasset` 和配套的材质、网格体、贴图资产实现。

插件自带了 5 张 4K HDRI 贴图（misty_pines、approaching_storm、ostrich_road、autumn_hockey、circus_maximus_2），3 种投影网格体（Dome、Box、BoxSharp），以及对应的天空和地板材质。

## 使用场景

- **视觉开发（Lookdev）**：在项目早期需要快速搭建带真实环境反射和光照的场景，用 HDRI Backdrop 比放置一个完整的 Sky Light + Sky Atmosphere 更快。
- **产品可视化 / 建筑可视化**：需要在场景背景展示特定环境（如户外风景、摄影棚），拖入 HDRI Backdrop 即可预览。
- **快速原型**：需要临时天空背景但不想配置完整的天空系统时。
- **光照参考**：用真实 HDRI 图像提供场景的基本环境光和反射，方便比对材质效果。

> ⚠️ 该插件默认未启用。使用前需在 Edit → Plugins 中搜索 "HDRIBackdrop" 并启用，重启编辑器后生效。

## 蓝图用法

该插件没有暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性给外部蓝图调用。它的全部功能通过放置到场景后的 Actor 详细面板（Details Panel）来配置。

### 放置方式

1. 启用插件后，在编辑器左侧 **Place Actors** 面板中切换到 **Lights** 分类。
2. 找到 **HDRI Backdrop**，拖拽到场景中即可。
3. 在 Details 面板中配置 HDRI 贴图、投影方式、亮度、旋转等参数。

### 关键资产

| 资产 | 路径 | 说明 |
|---|---|---|
| `HDRIBackdrop` | `/HDRIBackdrop/Blueprints/HDRIBackdrop` | 主 Actor 蓝图 |
| `MI_HDRI_Sky` | `/HDRIBackdrop/Materials/MI_HDRI_Sky` | 天空材质实例 |
| `MI_HDRI_Floor` | `/HDRIBackdrop/Materials/MI_HDRI_Floor` | 地板材质实例 |
| `HDRI_Attributes` | `/HDRIBackdrop/Materials/HDRI_Attributes` | HDRI 属性材质函数/参数 |
| `EnviroDome` | `/HDRIBackdrop/Meshes/EnviroDome` | 穹顶投影网格体 |
| `EnviroBox` | `/HDRIBackdrop/Meshes/EnviroBox` | 盒形投影网格体 |
| `EnviroBoxSharp` | `/HDRIBackdrop/Meshes/EnviroBoxSharp` | 锐边盒形投影网格体 |

### 内置 HDRI 贴图

插件自带 5 张 4K 分辨率的 HDRI 贴图，可直接在 Details 面板中选用：

| 贴图 | 文件名 |
|---|---|
| 薄雾松林 | `misty_pines_4k.uasset` |
| 风暴将至 | `approaching_storm_4k` |
| 鸵鸟之路 | `ostrich_road_4k` |
| 秋季冰球 | `autumn_hockey_4k` |
| 大竞技场 2 | `circus_maximus_2_4k` |

## C++ 用法

该插件没有提供可供外部 C++ 代码调用的公共 API。它是一个纯编辑器插件（模块类型为 `Editor`），其模块仅在启动时注册放置面板入口和 Slate 样式。

如果你想在自己的编辑器工具中类似地注册自定义放置项，可以参考其代码模式：

### 头文件引入

```cpp
#include "IPlacementModeModule.h"
#include "ActorFactories/ActorFactoryBlueprint.h"
```

### 参考实现：注册自定义 Actor 到放置面板

```cpp
// 来源: Engine/Plugins/Runtime/HDRIBackdrop/Source/HDRIBackdrop/Private/HDRIBackdropPlacement.cpp

// 加载你的 Blueprint 资产
UBlueprint* MyBlueprint = Cast<UBlueprint>(
    FSoftObjectPath(TEXT("/MyPlugin/Blueprints/MyActor.MyActor")).TryLoad()
);
if (MyBlueprint == nullptr) return;

// 获取 PlacementMode 模块并注册到 Lights 分类
IPlacementModeModule& PlacementModeModule = IPlacementModeModule::Get();
FPlacementCategoryInfo Info = *PlacementModeModule.GetRegisteredPlacementCategory(
    FBuiltInPlacementCategories::Lights()
);

FPlaceableItem* BPPlacement = new FPlaceableItem(
    *UActorFactoryBlueprint::StaticClass(),
    FAssetData(MyBlueprint, true),
    FName("MyPlugin.ModesThumbnail"),
    FName("MyPlugin.ModesIcon"),
    TOptional<FLinearColor>(),
    TOptional<int32>(),
    NSLOCTEXT("PlacementMode", "My Actor", "My Actor")
);

PlacementModeModule.RegisterPlaceableItem(Info.UniqueHandle, MakeShareable(BPPlacement));
```

## 模块依赖

由于该插件是 Editor-only 模块，**不适用于运行时模块**。如果你只是在场景中使用 HDRI Backdrop Actor，不需要做任何代码层面的依赖。

以下依赖信息仅供参考（仅适用于扩展该插件本身）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `Projects` | 插件管理（`IPluginManager`） |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心样式 |
| `EditorFramework` | 编辑器框架 |
| `UnrealEd` | 编辑器工具 |
| `PlacementMode` | 放置面板 API |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da71ab9` | IWYU 更新，减少文件包含数量 | 编译优化，无功能变更 |
| 2022-11-07 | `0a10c21ff628` | Release-Engine-Staging 同步更新 | 批量同步，非针对性改动 |
| 2022-11-03 | `049a3a702172` | 添加 includes 为未来变更做准备 | 仅添加头文件包含 |

### 维护评价

- **创建时间**：2019 年 8 月，已有约 6.7 年历史
- **最近实质更新**：最后三次 commit 均为编译/包含优化，无功能更新。**该插件自 2019 年创建后几乎没有功能迭代**
- **维护状态**：⚠️ **维护不活跃**。最后一次 commit 距今超过 2 年，且均为非功能性改动
- **模块类型**：虽然 .uplugin 写的是 `Runtime`，实际模块类型为 `Editor`，这是一个不一致（可能因为蓝图资产需要 Runtime 分类才能打包）
- **推荐**：作为简单的 HDRI 背景展示用途仍然可用，但功能有限。对于正式项目，建议使用 UE5 原生的 **Sky Atmosphere + Sky Light + HDRI** 组合，或通过 Movie Render Queue 的 HDRI 场景功能替代

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HDRIBackdrop)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/HDRIBackdrop)：无独立测试文件
