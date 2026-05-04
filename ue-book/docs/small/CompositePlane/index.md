# Composite Plane

> Provides a cine camera actor for projecting textures and videos

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | 否 (`Installed: false`) |
| 包含内容 | 是 |
| 模块 | CompositePlane (Editor) |
| 创建时间 | 2020-02-21 |
| 年龄标签 | 👴 老古董 (>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CompositePlane) | |

## 用途

CompositePlane 插件为虚拟制片 (Virtual Production) 工作流提供了一个**摄像机投影平面**工具。它允许用户将纹理或视频内容通过电影摄像机 (Cine Camera Actor) 投射到场景中的平面上，常用于 LED 墙拍摄、虚拟背景合成、实时合成预览等场景。

核心功能由一个名为 `BP_CineCameraProj` 的蓝图实现，C++ 代码仅负责在编辑器的 Cinematic 放置面板中注册该蓝图，使其可通过拖放方式快速添加到场景中。

插件附带了一套材质资产，支持多种渲染模式和 Alpha 来源配置，涵盖不透明 (Opaque)、遮罩 (Masked)、半透明 (Translucent) 以及带抠像 (Keyed) 等变体。

## 使用场景

- 你需要在虚拟制片场景中将外部视频源投射到平面几何体上，模拟真实的 LED 墙背景 → 用 CompositePlane
- 你需要在编辑器中快速放置一个带投影功能的电影摄像机，用于合成预览 → 用 CompositePlane
- 你在做实时合成 (In-Camera VFX) 项目，需要在场景中添加带材质变体的投影平面 → 用 CompositePlane

## 蓝图用法

本插件的 C++ 层没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有功能封装在蓝图资产 `BP_CineCameraProj` 中。

### 核心资产

| 资产 | 类型 | 说明 |
|---|---|---|
| `BP_CineCameraProj` | Blueprint (Actor) | 带投影功能的电影摄像机 Actor |
| `M_CamProj` | Material | 基础摄像机投影材质 |
| `MF_CamProj` | Material Function | 摄像机投影材质函数（核心逻辑） |
| `MI_CP_Opaque` | Material Instance | 不透明渲染模式 |
| `MI_CP_Masked` | Material Instance | 遮罩渲染模式 |
| `MI_CP_Masked_Keyed` | Material Instance | 遮罩 + 抠像渲染模式 |
| `MI_CP_Trans` | Material Instance | 半透明渲染模式 |
| `MI_CP_Trans_Keyed` | Material Instance | 半透明 + 抠像渲染模式 |
| `E_CamProjRenderingMode` | Enum | 投影渲染模式枚举 |
| `E_CamProjAlphaSrc` | Enum | Alpha 来源枚举 |

### 使用方式

1. 在编辑器中启用 CompositePlane 插件
2. 打开 **Place Actors** 面板，切换到 **Cinematic** 分类
3. 将 **Composite Plane** 拖放到场景中
4. 在 Actor 的细节面板中配置投影参数（纹理/视频源、渲染模式等）

## C++ 用法

本插件的 C++ 代码非常轻量，仅包含编辑器集成逻辑。如果你需要以编程方式与投影平面交互，建议直接操作蓝图 `BP_CineCameraProj` 或引用其材质系统。

### 模块结构

```
Source/CompositePlane/
├── CompositePlane.Build.cs          # 模块构建配置
├── Private/
│   ├── CompositePlane.h             # 模块入口头文件
│   ├── CompositePlane.cpp           # 模块入口实现
│   ├── CompositePlanePlacement.h    # 放置模式注册头文件
│   └── CompositePlanePlacement.cpp  # 放置模式注册实现
```

### 放置模式注册流程

模块启动时，通过 `IPlacementModeModule` 将 `BP_CineCameraProj` 蓝图注册到 Cinematic 放置分类：

```cpp
// CompositePlanePlacement.cpp - 核心注册逻辑
UBlueprint* CompositePlane = Cast<UBlueprint>(
    FSoftObjectPath(TEXT("/CompositePlane/BP_CineCameraProj.BP_CineCameraProj")).TryLoad()
);

FPlaceableItem* BPPlacement = new FPlaceableItem(
    *UActorFactoryBlueprint::StaticClass(),
    FAssetData(CompositePlane, true),
    FName(""), FName(""),
    TOptional<FLinearColor>(),
    TOptional<int32>(),
    NSLOCTEXT("PlacementMode", "Composite Plane", "Composite Plane")
);

IPlacementModeModule::Get().RegisterPlaceableItem(Info->UniqueHandle, MakeShareable(BPPlacement));
```

## Demo 示例

由于本插件的全部功能由蓝图资产实现，没有独立的 C++ API 需要编写代码示例。最佳使用方式是：

1. 启用插件
2. 从 Cinematic 面板拖放 `Composite Plane` 到场景
3. 配置材质实例参数（渲染模式、Alpha 来源）
4. 指定投射的纹理或视频源

如需在 C++ 中引用投影材质函数，可通过以下方式加载：

```cpp
#include "Materials/MaterialInstanceDynamic.h"

// 加载投影材质函数
UMaterialFunction* CamProjMF = LoadObject<UMaterialFunction>(
    nullptr, TEXT("/CompositePlane/MF_CamProj.MF_CamProj")
);

// 创建动态材质实例
UMaterialInterface* BaseMat = LoadObject<UMaterialInterface>(
    nullptr, TEXT("/CompositePlane/MI_CP_Opaque.MI_CP_Opaque")
);
UMaterialInstanceDynamic* DynMat = UMaterialInstanceDynamic::Create(BaseMat, this);
```

## 模块依赖

所有依赖均为 `PrivateDependencyModuleNames`，外部模块无需额外引用本插件。

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `Projects` | 插件/项目管理 |
| `Slate` | UI 框架 |
| `SlateCore` | Slate 核心组件 |
| `EditorFramework` | 编辑器框架（仅编辑器） |
| `UnrealEd` | 编辑器功能（仅编辑器） |
| `PlacementMode` | 放置模式面板（仅编辑器） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2023-01-16 | `7ce67da` | IWYU 更新，减少文件 include 数量 | 代码清理，无功能变更 |
| 2022-11-07 | `0a10c21` | Release-Engine-Staging 批量更新 | 引擎级批量同步，非针对性修改 |
| 2022-11-03 | `049a3a7` | 添加 include 和占位文件 | 为未来变更做准备的基础设施工作 |

### 维护评价

- **创建时间**: 2020 年 2 月，已有 6 年历史
- **Beta 状态**: `.uplugin` 中 `IsBetaVersion: true`，表明 Epic 从未将其标记为正式版
- **默认未启用**: `Installed: false`，需手动启用
- **最近更新**: 最后一次实质性更新在 2022 年底（且仅是基础设施清理），已经超过 3 年没有功能性更新
- **代码量极小**: 仅 4 个源文件，总共约 90 行 C++ 代码，功能完全依赖蓝图资产
- **维护状态**: ⚠️ **维护不活跃** — 作为 Beta 插件长期未有功能迭代，可能存在兼容性风险
- **建议**: 适合在虚拟制片原型阶段快速验证想法；生产环境建议评估其材质系统是否满足需求，或考虑自行实现投影逻辑

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CompositePlane)
- 官方文档（无，`.uplugin` 中 DocsURL 为空）
