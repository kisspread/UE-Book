# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作实用工具 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产、蓝图、材质） |
| 模块 | `VPUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

---

## 用途

`VPUtilities` 是虚拟制作工作流的核心工具集，提供实用类、蓝图函数库和组件，用于简化虚拟制片场景中的常见任务，例如：

- **场景标记（书签）**：创建可定位的视角书签，支持捕获快照、颜色标记和收藏，方便多用户协作时快速跳转。
- **全屏 UI 叠加**：将 UMG 控件以全屏形式渲染到视口（支持编辑器/游戏/后处理/PIE），适用于在 Live Link、Pixel Streaming 等场景上叠加信息。
- **场景根 Actor**：统一场景的参考坐标系，关联绑定的电影摄像机，支持一键将关卡移动至根位置，便于 LED 墙等物理布景对齐。
- **视口 Tick 基类**：提供可在编辑器视口中持续 Tick 的 Actor 基类，用于实现实时预览行为（如仪表盘、场景探针）。
- **时间码同步**：基于 TimecodeProvider 的自定义时间步，使引擎帧率与外部时间码同步，支持硬件 Genlock。
- **渲染辅助**：生成视口类型的 Scene View Extension 激活判定器，方便在特定视口（PIE/SIE/编辑器活动）中开启后处理效果。
- **资产缩略图包装**：在打包游戏中也能够显示资产缩略图（编辑器中使用 UAssetThumbnailWidget，打包后回退到静态图片）。
- **编辑命令库**：在蓝图中调用刷新视口、撤销/重做、跳转到书签等编辑器操作。
- **已弃用的 VR 功能**：部分 VR 编辑器相关接口已被标记为弃用，建议迁移至 XR Creative Framework 插件。

该插件解决了虚拟制作场景中**编辑器运行时混合**、**多用户协作**、**时间同步**和**UI 叠加**的关键需求。

---

## 使用场景

- **虚拟拍摄现场**：使用 `AVPRootActor` 统一场景零点和绑定的电影摄像机，方便物理摇臂与虚拟相机对齐。
- **LED 墙/绿幕**：通过 `UVPTimecodeCustomTimeStep` 接收外部时间码（如 HD-SDI），实现帧精确的合成拍摄。
- **现场直播叠加**：利用 `UVPFullScreenUserWidget` 将实时数据（如比分、字幕）渲染到全屏（可忽略变形挤压），适用于 Pixel Streaming 或直接输出到录播系统。
- **多用户协作标记**：导演和摄影指导在编辑器中用 `AVPBookmarkActor` 标记关键视角，共享至多用户会话，并一键跳转。
- **场景预可视化**：基于 `AVPViewportTickableActorBase` 编写在编辑器下持续运行的脚本，例如自动巡游相机或实时反馈控制器状态。
- **打包游戏的展示台**：使用 `UVPAssetThumbnailWrapperWidget` 在打包 UI 中显示资产缩略图，降低对编辑器功能的依赖。

---

## 蓝图用法

### 核心工具函数（UVPBlueprintLibrary）

位于 `VPBlueprintLibrary.h`，封装了编辑器操作、书签管理、VR 调试（已弃用）等。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Refresh3DEditorViewport` | 强制刷新 3D 视口，即使未开启实时 | `UVPBlueprintLibrary` |
| `SpawnVPBookmarkAtCurrentLevelEditorPosition` | 在当前编辑器视角位置生成书签 | `UVPBlueprintLibrary` |
| `JumpToBookmarkInLevelEditor` | 跳转到指定的书签视角 | `UVPBlueprintLibrary` |
| `GetVirtualProductionRole` | 获取当前机器在虚拟制作中的角色标签（GameplayTag） | `UVPBlueprintLibrary` |
| `GetEditorViewportTransform` | 获取 2D 视口相机的变换 | `UVPBlueprintLibrary` |
| `EditorUndo` / `EditorRedo` | 触发编辑器的撤销/重做 | `UVPBlueprintLibrary` |
| `CallInEditor` 装饰的函数 | 所有标记了 `CallInEditor` 的函数均可在编辑器细节面板中直接点击执行 | 多个类 |

> **注意**：`GetEditorVRHeadTransform`、`IsVREditorModeActive` 等 VR 函数已在 5.7 弃用，请迁移至 XR Creative Framework。

### 书签 Actor（AVPBookmarkActor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateBookmarkColor` | 更新书签的 Mesh 颜色和 `BookmarkColor` 变量 | `AVPBookmarkActor` |
| `CaptureSnapshot` | 通过 SceneCaptureComponent 捕获当前视点快照到 `SnapshotTexture` | `AVPBookmarkActor` |
| `UpdateTimestamp` | 更新 `Timestamp` 为当前时间 | `AVPBookmarkActor` |
| `OnBookmarkActivation` | 书签激活/停用回调（需要实现 `IVPBookmarkProvider`） | `AVPBookmarkActor` |

### 全屏用户控件（UVPFullScreenUserWidget）

该组件负责将 UMG 控件渲染到视口。需要先创建 `UVPFullScreenUserWidget` 对象并调用 `Display` 和 `Hide`。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Display (World)` | 在指定世界中显示控件 | `UVPFullScreenUserWidget` |
| `Hide` | 隐藏控件并清理资源 | `UVPFullScreenUserWidget` |
| `SetDisplayTypes` | 设置编辑器/游戏/PIE 下的显示方式（Viewport / PostProcessWithBlendMaterial / PostProcessSceneViewExtension） | `UVPFullScreenUserWidget` |
| `SetCustomPostProcessSettingsSource` | 指定后处理设置来源（例如特定 CineCamera） | `FVPFullScreenUserWidget_PostProcess` |
| `GetUserWidget` | 返回内部持有的 UMG 控件实例 | `AFullScreenUserWidgetActor` |

### 资产缩略图包装（UVPAssetThumbnailWrapperWidget）

可在蓝图中直接使用，无需 C++ 依赖编辑器模块。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAsset`（FAssetData） | 设置要显示的资产 | `UVPAssetThumbnailWrapperWidget` |
| `SetAssetByObject` | 通过对象设置资产 | `UVPAssetThumbnailWrapperWidget` |
| `SetFallbackBrush` | 设置打包环境下的回退图片 | `UVPAssetThumbnailWrapperWidget` |
| `SetDisplayMode` | 强制使用回退模式（仅在编辑器下有效） | `UVPAssetThumbnailWrapperWidget` |
| `GetEditorAssetWidget` | 获取编辑器缩略图控件（需转换为 UAssetThumbnailWidget） | `UVPAssetThumbnailWrapperWidget` |

### 渲染工具（UVRenderingBlueprintLibrary）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateSceneViewExtensionIsActiveFunctorForViewportType` | 生成一个判断 SVE 是否活跃的 functor，指定视口类型（PIE/SIE/编辑活动/primary） | `UVRenderingBlueprintLibrary` |

---

## C++ 用法

### 头文件引入

```cpp
#include "VPBlueprintLibrary.h"                // 编辑器命令库
#include "Actors/VPBookmarkActor.h"            // 书签 Actor
#include "Actors/VPRootActor.h"                // 根 Actor
#include "Actors/VPViewportTickableActorBase.h"// 基类
#include "Widgets/VPFullScreenUserWidget.h"    // 全屏控件
#include "VPTimecodeCustomTimeStep.h"          // 时间步
#include "VPGameMode.h"                        // 游戏模式
#include "Widgets/VPAssetThumbnailWrapperWidget.h"
```

### 基本用法：创建书签并跳转

```cpp
// 在编辑器模块中调用（需要 Editor Subsystem）
FVPBookmarkCreationContext Context;
Context.bIsDefault = true;
AActor* BookmarkActor = UVPBlueprintLibrary::SpawnBookmarkAtCurrentLevelEditorPosition(
    AVPBookmarkActor::StaticClass(),
    Context,
    FVector::ZeroVector,
    true
);

// 跳转到某书签
const UVPBookmark* Bookmark = ...; // 获取书签对象
UVPBlueprintLibrary::JumpToBookmarkInLevelEditor(Bookmark);
```

### 基本用法：使用 AVPViewportTickableActorBase 实现编辑器实时行为

```cpp
// MyVPActor.h
UCLASS()
class AMyVPActor : public AVPViewportTickableActorBase
{
    GENERATED_BODY()
public:
    virtual void EditorTick_Implementation(float DeltaSeconds) override
    {
        // 仅在编辑器视口中执行
        float Yaw = GetActorRotation().Yaw + DeltaSeconds * 30.0f;
        SetActorRotation(FRotator(0, Yaw, 0));
    }
};
```

### 基本用法：配置时间码自定义时间步

```cpp
// 在 GameInstance 或设置层中
UVPTimecodeCustomTimeStep* CustomTimeStep = NewObject<UVPTimecodeCustomTimeStep>(GetTransientPackage());
CustomTimeStep->bErrorIfFrameAreNotConsecutive = true;
CustomTimeStep->MaxDeltaTime = 0.5f;

UEngine* Engine = GEngine;
Engine->SetCustomTimeStep(CustomTimeStep);
```

### 基本用法：全屏控件叠加

```cpp
// 创建并显示
UVPFullScreenUserWidget* FullScreen = NewObject<UVPFullScreenUserWidget>(GetTransientPackage());
FullScreen->SetDisplayTypes(
    EVPWidgetDisplayType::PostProcessSceneViewExtension,
    EVPWidgetDisplayType::PostProcessSceneViewExtension,
    EVPWidgetDisplayType::PostProcessSceneViewExtension
);

UWorld* World = GetWorld();
FullScreen->Display(World);

// 每帧 Tick（通常由 Actor 或 Manager 调用）
FullScreen->Tick(DeltaSeconds);

// 隐藏
FullScreen->Hide();
```

### 进阶用法：为 SVE 注册自定义激活判定

```cpp
// 使用 UVPRenderingBlueprintLibrary 生成 Functor 并组合
FSceneViewExtensionIsActiveFunctor Functor;
UVPFullScreenUserWidget_PostProcessWithSVE* SVEImpl = ...; // 从 FVPFullScreenUserWidget 内访问
SVEImpl->RegisterIsActiveFunctor(MoveTemp(Functor));

// 或者手动构造 Functor
FSceneViewExtensionIsActiveFunctor MyFunctor;
MyFunctor.IsActiveFunction = [](const FSceneViewExtensionContext& Context) -> TOptional<bool>
{
    if (Context.Viewport && Context.Viewport->IsPlayInEditorViewport())
    {
        return true; // 只在 PIE 视口激活
    }
    return {}; // 无意见
};
```

### 进阶用法：创建全屏控件的包装 Actor

继承 `AFullScreenUserWidgetActor` 即可自动获得全屏控件生命周期，无需手动管理 `UVPFullScreenUserWidget`。

```cpp
// 蓝图实现：在 Class Defaults 中设置 "Screen User Widget" 的 WidgetClass 属性
// 然后直接在关卡中放置，运行时自动显示。
```

---

## Demo 示例（最小 C++ 实现）

### 示例：在编辑器中生成一个带 Tick 的书签根 Actor

```cpp
// MyVPRootWithTick.h
#pragma once
#include "CoreMinimal.h"
#include "Actors/VPRootActor.h"
#include "MyVPRootWithTick.generated.h"

UCLASS(Blueprintable)
class AMYVPRootWithTick : public AVPRootActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override { Super::BeginPlay(); }
    virtual void Tick(float DeltaSeconds) override
    {
        Super::Tick(DeltaSeconds);
        // 游戏世界中的更新逻辑
    }
#if WITH_EDITOR
    virtual bool ShouldTickIfViewportsOnly() const override { return true; }
    virtual void EditorTick_Implementation(float DeltaSeconds) override
    {
        // 编辑器视口下的更新逻辑
    }
#endif
};
```

```cpp
// 头文件包含自己的实现，无需额外代码。
```

该示例展示了如何结合 `AVPRootActor`（场景定位）与 `AVPViewportTickableActorBase` 的 Tick 能力（实际上 `AVPRootActor` 已继承自 AActor，并非 `AVPViewportTickableActorBase`，但可以通过实现 `EditorTick` 类似行为）。更直接的做法是继承 `AVPViewportTickableActorBase` 获得完整的 EditorTick 支持。

---

## 模块依赖（VPUtilities 模块）

当你的模块启用 `VPUtilities` 后，以下为独有的公共依赖（标准 Core/Engine/UMG 等略去）：

| 模块 | 用途 |
|---|---|
| `VPBookmark` | 书签数据结构、接口 `IVPBookmarkProvider` |
| `CinematicCamera` | `UCineCameraComponent` 等电影相机类型 |
| `AssetRegistry` | 资产缩略图包装中使用的资产数据 |
| `GameplayTags` | 虚拟制作角色标签 (`GetVirtualProductionRole`) |

**注意**：`VPUtilities` 本身不直接依赖编辑器模块；其编辑器相关功能在 `VPUtilitiesEditor` 模块中。

---

## 维护状态

### 近期更新

- 2025-10-03 — 修复全屏控件用于媒体输出提供者（Full screen widget for media output providers）。
- 2025-09-25 — OSC 服务器允许指定地址覆盖（OSC server - Allow specifying an override for the server address）。
- 2025-09-23 — 弃用 ViewportInteraction 模块（紧随 VR Editor 弃用）。
- 2025-09-10 — 弃用 VR Editor 模式及大部分相关类。
- 2025-08-27 — 初始创建，修复静态分析警告和弃用警告。

### 维护评价

该插件仍处于**积极维护**阶段，最近一个月有功能性修复和新增（OSC 地址覆盖）。但大量 VR 相关接口已被弃用，计划在 5.7 移除，建议新项目不要依赖这些功能。整体稳定，适合虚拟制作场景使用，但需要留意弃用标记并迁移。

> ⚠️ 警告：`VPCameraBlueprintLibrary` 和 `IVPInteraction` 中的函数将在 UE5.7 中删除，请避免使用。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities)
- [VPUtilities 模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities/Source/VPUtilities/Public)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/VirtualProductionUtilities/Tests)（若有，路径参考）