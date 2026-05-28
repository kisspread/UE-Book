# Virtual Production Utilities

> Utility classes and functions for Virtual Production

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制作工具集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、静态网格体） |
| 模块 | `VPBookmark` (Runtime), `VPBookmarkEditor` (Runtime), `VPUtilities` (Runtime), `VPUtilitiesEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities) | |

## 用途

该插件为虚拟制作（Virtual Production）工作流提供了一套核心的实用工具和框架。其主要目标是在编辑器环境中增强虚拟制作的能力，解决以下问题：

1.  **编辑器增强**：为虚拟制作人员提供在编辑器视口内进行高效交互的工具，如刷新非实时视口、执行撤销/重做/复制/删除等操作。
2.  **场景定位与管理**：引入了“书签”（Bookmark）系统，允许用户在场景中创建带有元数据（如颜色、时间戳、快照）的定位点，并能在编辑器视图中快速导航至这些位置。
3.  **Actor 生命周期扩展**：提供了可在编辑器视口中进行Tick的Actor基类（`AVPViewportTickableActorBase`），使得自定义逻辑（如实时UI、标记更新）能在编辑器预览窗口中持续运行，无需进入PIE。
4.  **场景根节点管理**：通过`AVPRootActor`为虚拟制作场景提供一个中心参考点，包含场景大小表示和电影摄像机，便于协调大型虚拟场景。
5.  **后处理与渲染辅助**：提供了简化的后处理Volume和渲染相关的蓝图库，用于获取干净的直通渲染或控制场景视图扩展的激活条件。
6.  **旧API过渡**：包含了大量已标记为`DEPRECATED`的VR编辑器和摄像机轨道相关函数，表明该插件曾深度集成旧版VR编辑器，并正在逐步迁移至更通用的XR框架。

## 使用场景

-   **虚拟制片现场指导**：你在UE编辑器中进行虚拟拍摄准备，需要在不同机位间快速跳转、标记重要位置，并记录拍摄参数 → 使用书签（Bookmark）系统。
-   **开发自定义编辑器工具**：你需要编写一个在编辑器视口中实时显示信息（如测量工具、自定义网格）的工具 → 继承自 `AVPViewportTickableActorBase`。
-   **构建虚拟场景框架**：你正在搭建一个大型虚拟场景，需要一个代表真实世界比例的参考点和主摄像机 → 使用 `AVPRootActor` 作为场景根节点。
-   **实现跨平台资产预览**：你需要在编辑器中显示资产缩略图，同时确保游戏包体中也能有合适的回退显示 → 使用 `UVPAssetThumbnailWrapperWidget`。
-   **高级渲染控制**：你需要针对特定视口类型（如PIE、编辑器活动视口）选择性启用场景视图扩展 → 使用 `UVPRenderingBlueprintLibrary`。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Refresh3DEditorViewport` | 强制刷新编辑器3D视口，使其在非“实时”模式下也能更新更改。 | `UVPBlueprintLibrary` |
| `SpawnBookmarkAtCurrentLevelEditorPosition` | 在当前关卡编辑器摄像机位置生成一个书签Actor。 | `UVPBlueprintLibrary` |
| `JumpToBookmarkInLevelEditor` | 将编辑器视口摄像机跳转到指定书签的位置。 | `UVPBlueprintLibrary` |
| `GetVirtualProductionRole` | 获取当前机器在虚拟制作中的角色（标签容器）。 | `UVPBlueprintLibrary` |
| `GetEditorViewportTransform` | 获取编辑器2D视口摄像机的变换。 | `UVPBlueprintLibrary` |
| `EditorUndo` / `EditorRedo` | 触发编辑器的撤销/重做操作。 | `UVPBlueprintLibrary` |
| `SortActorsByName` | 按Actor标签名称对Actor数组进行排序。 | `UVPBlueprintLibrary` |
| `SortVPBookmarkActorsByTimestamp` | 按时间戳对书签Actor数组进行排序。 | `UVPBlueprintLibrary` |
| `UpdateBookmarkColor` | 更新书签Actor的网格颜色。 | `AVPBookmarkActor` |
| `CaptureSnapshot` | 使用书签Actor内置的场景捕获组件拍摄一张快照纹理。 | `AVPBookmarkActor` |
| `GenerateSceneViewExtensionIsActiveFunctorForViewportType` | 生成一个场景视图扩展激活函数，用于根据视口类型（PIE/SIE/编辑器/主游戏）控制扩展是否激活。 | `UVPRenderingBlueprintLibrary` |
| `SetAsset` / `SetAssetByObject` | 为资产缩略图包装控件设置要显示的资产。 | `UVPAssetThumbnailWrapperWidget` |

### 使用示例（蓝图描述）

1.  **创建并跳转到书签**：
    *   从 `UVPBlueprintLibrary` 拖出 `SpawnBookmarkAtCurrentLevelEditorPosition` 节点。
    *   为 `ActorClass` 选择一个书签Actor类（如 `AVPBookmarkActor` 或其子类）。
    *   将 `CreationContext` 结构体连接，可设置书签的初始属性。
    *   调用该节点后，将返回的Actor引脚连接到 `JumpToBookmarkInLevelEditor` 节点，即可立即跳转至该书签位置。

2.  **实现一个在编辑器视口实时旋转的标记Actor**：
    *   创建一个继承自 `AVPViewportTickableActorBase` 的蓝图Actor。
    *   在蓝图中，实现 `EditorTick` 事件。在该事件中添加逻辑，例如每帧调用 `AddActorLocalRotation` 使Actor自身旋转。
    *   将此Actor放入场景，当编辑器视口可见时，即使未进入游戏，该Actor也会持续旋转。

3.  **在UI中显示资产图标**：
    *   在UMG设计器中，放置一个 `Asset Thumbnail Widget (Editor & Game)` 控件（即 `UVPAssetThumbnailWrapperWidget`）。
    *   在蓝图中，通过 `SetAsset` 或 `SetAssetByObject` 为其绑定一个资产（如静态网格体）。在编辑器中，它会显示资产的缩略图；在打包后的游戏中，它会显示你设置的回退图像。

## C++ 用法

### 头文件引入

```cpp
// 核心工具库
#include "Libraries/VPBlueprintLibrary.h"
// 书签相关
#include "Actors/VPBookmarkActor.h"
#include "VPBookmark.h"
#include "IVPBookmarkProvider.h"
// 可视口Tick的Actor基类
#include "Actors/VPViewportTickableActorBase.h"
// 场景根节点
#include "Actors/VPRootActor.h"
```

### 基本用法

**1. 创建一个自定义的书签Actor**

你需要继承 `AVPBookmarkActor` 并实现 `IVPBookmarkProvider` 接口，以提供书签数据。

```cpp
// MyCustomBookmarkActor.h
#pragma once
#include "Actors/VPBookmarkActor.h"
#include "MyCustomBookmarkActor.generated.h"

UCLASS()
class AMyCustomBookmarkActor : public AVPBookmarkActor
{
    GENERATED_BODY()

public:
    // 实现 IVPBookmarkProvider 接口
    virtual UVPBookmark* GetBookmark() const override { return BookmarkObject; }
    
    // 可以重写其他虚函数，如 UpdateBookmarkName_Implementation
    virtual void GenerateBookmarkName_Implementation() override;
};
```

**2. 使用蓝图库函数**

在自定义的编辑器工具或蓝图节点中调用静态函数。

```cpp
// 刷新编辑器视口
UVPBlueprintLibrary::Refresh3DEditorViewport();

// 在摄像机位置生成一个书签
FVPBookmarkCreationContext Context;
Context.bFlattenRotation = true;
AActor* NewBookmark = UVPBlueprintLibrary::SpawnBookmarkAtCurrentLevelEditorPosition(
    AMyCustomBookmarkActor::StaticClass(),
    Context,
    FVector::ZeroVector
);
```

### 进阶用法

**1. 利用 `AVPViewportTickableActorBase` 制作实时编辑器指示器**

创建一个继承自 `AVPViewportTickableActorBase` 的类，重写 `EditorTick` 来实现每帧更新的逻辑。

```cpp
// MyRealtimeIndicator.h
#pragma once
#include "Actors/VPViewportTickableActorBase.h"
#include "MyRealtimeIndicator.generated.h"

UCLASS()
class AMyRealtimeIndicator : public AVPViewportTickableActorBase
{
    GENERATED_BODY()

public:
    AMyRealtimeIndicator()
    {
        // 确保在编辑器视口 Tick
        ViewportTickType = EVPViewportTickableFlags::Editor;
    }

    // 每帧执行，即使在编辑器中
    virtual void EditorTick_Implementation(float DeltaSeconds) override
    {
        // 例如：更新一个动态材质参数，或绘制调试信息
        SetActorLocation(GetActorLocation() + FVector(0, 0, DeltaSeconds * 10.0f));
    }
};
```

**2. 实现场景视图扩展的条件激活**

使用渲染库函数来创建激活逻辑，避免在不必要的视口中启用昂贵的渲染扩展。

```cpp
FSceneViewExtensionIsActiveFunctor IsActiveFunctor;
UVPBlueprintLibrary::GenerateSceneViewExtensionIsActiveFunctorForViewportType(
    IsActiveFunctor,
    true,  // bPIE: 在PIE中激活
    false, // bSIE
    false, // bEditorActive
    false  // bGamePrimary
);

// 将此 IsActiveFunctor 传递给你自定义的 SceneViewExtension
```

## Demo 示例

一个最小示例：创建一个在编辑器视口中浮动的文字标签的Actor。

**FloatingLabel.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Actors/VPViewportTickableActorBase.h"
#include "FloatingLabel.generated.h"

class UTextRenderComponent;

UCLASS()
class AFloatingLabel : public AVPViewportTickableActorBase
{
    GENERATED_BODY()
    
public:
    AFloatingLabel();
    
    virtual void EditorTick_Implementation(float DeltaSeconds) override;

protected:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UTextRenderComponent> LabelComponent;
    
    UPROPERTY(EditAnywhere, Category = "Animation")
    float FloatSpeed = 1.0f;
    
    UPROPERTY(EditAnywhere, Category = "Animation")
    float FloatHeight = 10.0f;
    
private:
    FVector OriginalLocation;
};
```

**FloatingLabel.cpp**
```cpp
#include "FloatingLabel.h"
#include "Components/TextRenderComponent.h"

AFloatingLabel::AFloatingLabel()
{
    PrimaryActorTick.bCanEverTick = true; // 基类需要开启Tick
    
    LabelComponent = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Label"));
    LabelComponent->SetText(FText::FromString(TEXT("Floating Label")));
    LabelComponent->SetWorldSize(30.0f);
    RootComponent = LabelComponent;
    
    // 默认仅在编辑器视口Tick
    ViewportTickType = EVPViewportTickableFlags::Editor;
}

void AFloatingLabel::EditorTick_Implementation(float DeltaSeconds)
{
    if (OriginalLocation.IsZero())
    {
        OriginalLocation = GetActorLocation();
    }
    
    // 简单的正弦浮动效果
    const float Time = GetWorld()->GetRealTimeSeconds();
    const float Offset = FMath::Sin(Time * FloatSpeed) * FloatHeight;
    SetActorLocation(OriginalLocation + FVector(0, 0, Offset));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | 该插件的公共依赖均为UE核心模块，如Core, CoreUObject, Engine, Slate, UMG, InputCore等。用户模块若要使用此插件，只需在Build.cs中添加对 `VPUtilities` 模块的依赖即可。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `02b15f1b` | Remove redundant texture update call so that snapshot texture is always updated properly | 移除冗余的纹理更新调用，确保快照纹理总能被正确更新。 |
| 2026-04-20 | `766d0ed3` | [VPUtilities & TimeManagement] Moved Timecode custom timestep to the TimeManagement engine module so | 将时间码自定义时间步长功能从本插件迁移到引擎的TimeManagement模块。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移至UE_LOGF（一种新的日志格式）。 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏控件相关功能从本实验性插件移出，放入新的正式插件 `ViewportWidgetOverlay`。 |
| 2026-02-05 | `25fe0362` | Deprecate FViewportFrame | 废弃了 `FViewportFrame` 相关代码。 |

### 维护评价

该插件创建于2019年初，已存在约7年。从近期（2026年）的提交记录看，它**仍在维护**，但维护重点在于**功能重构和清理**，而非大量新功能开发。

主要活动包括：
1.  **API清理**：将一部分成熟功能（如全屏控件、时间码自定义）从这个“实验性”插件迁移到更正式的、非实验性的插件或引擎模块中。
2.  **废弃旧API**：大量标记了 `DEPRECATED` 的函数，特别是与旧版VR编辑器相关的，正在被逐步移除，指引用户使用新的XR Creative Framework。
3.  **内部优化**：进行一些底层的代码改进和bug修复。

**结论**：这是一个**处于维护末期、正在逐步拆分和退休**的“实验性”工具集。它仍然可以使用，特别是其核心的书签系统和视口可Tick Actor基类。但是，部分功能（如全屏控件、时间码）已经被移出，且一些与旧VR编辑器深度绑定的功能已废弃。**推荐在新项目中谨慎评估**，优先考虑其非实验性的替代方案或仅使用其未被废弃的、经过验证的核心功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/VirtualProductionUtilities)
- [官方文档]() （无官方文档链接）
- [测试用例]() （未提供测试用例路径）