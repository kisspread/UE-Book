# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体板 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资源、样式） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate) | |

## 用途

Media Plate 提供一个可在关卡中直接放置的 Actor，能够在 3D 几何体（平面、球体、自定义网格）上播放媒体（视频、图片、音视频流）。它封装了 `UMediaPlayer`、`UMediaTexture` 以及相应的几何体组件，简化了媒体播放与 3D 场景的集成。该插件的主要目的是将媒体播放功能直接嵌入到关卡中的静态网格体上，无需手动搭建媒体管线。

MediaPlateEditor 模块则提供编辑器内对该组件的完整定制支持，包括：
- 属性面板自定义（切换网格体形状、材质、媒体源类型）
- 蓝图资产定义（可将 `UMediaPlateComponent` 视为资产直接打开）
- Sequencer 轨道编辑支持
- 播放控制工具栏（播放、暂停、快进、倒带等）
- 媒体详情与播放列表面板

## 使用场景

- 在 3D 世界中的屏幕上播放视频（如虚拟演播室的 LED 墙、游戏内电视、监控屏幕）
- 将球体映射为 360° 全景视频播放器
- 通过自定义网格体将媒体投射到任意形状表面（如弧形屏幕）
- 在编辑器中快速测试媒体资源的外观与播放效果

## 蓝图用法

> Media Plate 的主要蓝图 API 位于运行时模块 `MediaPlate` 的 `UMediaPlateComponent` 类中。由于本节仅提供编辑器模块头文件，以下为根据官方文档和常见用法推断的核心节点。**实际可用函数以运行时模块源码为准**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开指定的媒体源资源 | `UMediaPlateComponent` |
| `Play` | 开始播放当前媒体 | `UMediaPlateComponent` |
| `Pause` | 暂停播放当前媒体 | `UMediaPlateComponent` |
| `Close` | 关闭当前媒体 | `UMediaPlateComponent` |
| `Set Mesh Mode` | 设置网格体形状（平面/球体/自定义） | `UMediaPlateComponent` |
| `Set Visible Mips Tiles` | 设置可见 Mip/Tile 模式 | `UMediaPlateComponent` |

### 使用示例（蓝图描述）

1. **在关卡中播放视频**：将 `Media Plate Actor` 拖入场景，在细节面板中指定 `Media Source` 属性为任意媒体源，蓝图调用 `Play` 节点即可播放。
2. **动态切换媒体**：使用 `Open Source` 节点传入新的 `UMediaSource` 对象，然后调用 `Play`。
3. **动态切换网格体**：调用 `Set Mesh Mode` 节点，可选择 `Plane`、`Sphere` 或 `Custom`。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlateComponent.h"
#include "MediaPlateEditorModule.h"  // 编辑器模块
```

### 基本用法

运行时获取媒体板组件并控制播放：

```cpp
// 获取场景中的 MediaPlate Actor
AMediaPlate* MediaPlateActor = ...;
UMediaPlateComponent* MediaPlateComp = MediaPlateActor->GetComponentByClass<UMediaPlateComponent>();

// 打开并播放媒体源
MediaPlateComp->OpenSource(MyMediaSource);
MediaPlateComp->Play();
```

编辑器模块中注册拖放媒体的回调：

```cpp
// 在模块启动后，监听拖拽文件创建 MediaSource 的逻辑
FMediaPlateEditorModule& EditorModule = FModuleManager::LoadModuleChecked<FMediaPlateEditorModule>("MediaPlateEditor");
if (UMediaSource* Source = EditorModule.RemoveMediaSourceFromDragDropCache(SomeSource))
{
    // 将 Source 的 Outer 修改为持久对象
    Source->Rename(nullptr, GetTransientPackage());
}
```

### 进阶用法

结合 Sequencer 在编辑器中对媒体板进行轨道编辑（路径来自源码 `MediaPlateTrackEditor.h`）：

```cpp
// 注册 Sequencer 轨道编辑器
void FMyEditorModule::StartupModule()
{
    FMediaPlateEditorModule& EditorModule = FModuleManager::LoadModuleChecked<FMediaPlateEditorModule>("MediaPlateEditor");
    // 通过 TrackEditorBindingHandle 注册，但通常由模块自动完成
}
```

自定义网格体创建（使用编辑器提供的网格生成器 `FMediaPlateSphereGenerator`）：

```cpp
// 在自定义详情面板中，调用 FMediaPlateCustomizationMesh 方法
FMediaPlateCustomizationMesh MeshCustomization;
MeshCustomization.SetSphereMesh(MediaPlateComponent);
```

编辑器模块提供了获取媒体板材质资产路径的事件，可供其他插件扩展：

```cpp
// 在其他模块中订阅
MediaPlateEditorModule->OnGetMediaPlateMaterialAssetPaths().AddLambda([](TArray<FName>& Paths)
{
    Paths.Add(TEXT("/MyPlugin/Materials/MyMediaMaterial"));
});
```

## Demo 示例

以下演示如何在关卡中通过 C++ 动态创建 Media Plate Actor 并播放媒体。**注意**：本示例需要 `MediaPlate` 运行时模块可用。

### MediaPlatePlayer.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlatePlayer.generated.h"

class UMediaPlateComponent;
class UMediaSource;

UCLASS()
class AMediaPlatePlayer : public AActor
{
    GENERATED_BODY()

public:
    AMediaPlatePlayer();

    /** 媒体源资产 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaSource* MediaSource;

    /** 播放 */
    UFUNCTION(BlueprintCallable, Category = "Media")
    void Play();

    /** 停止 */
    UFUNCTION(BlueprintCallable, Category = "Media")
    void Stop();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlateComponent* MediaPlateComponent;
};
```

### MediaPlatePlayer.cpp

```cpp
#include "MediaPlatePlayer.h"
#include "MediaPlateComponent.h"
#include "MediaSource.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

AMediaPlatePlayer::AMediaPlatePlayer()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建主组件（此处应按 MediaPlate Actor 的结构创建，为简化直接添加组件）
    // 实际应使用 AMediaPlate 类，但这里展示手动构建
    MediaPlateComponent = CreateDefaultSubobject<UMediaPlateComponent>(TEXT("MediaPlate"));
    SetRootComponent(MediaPlateComponent->GetStaticMeshComponent());
}

void AMediaPlatePlayer::Play()
{
    if (MediaSource && MediaPlateComponent)
    {
        MediaPlateComponent->OpenSource(MediaSource);
        MediaPlateComponent->Play();
    }
}

void AMediaPlatePlayer::Stop()
{
    if (MediaPlateComponent)
    {
        MediaPlateComponent->Pause();
        // 可选关闭媒体
        MediaPlateComponent->Close();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器功能，如 ActorFactory、细节定制、Level Editor 集成（MediaPlateEditor 依赖） |

**说明**：
- `MediaPlate` 运行时模块依赖：`Core`, `CoreUObject`, `Engine`, `Media`, `MediaAssets`, `Slate`, `SlateCore`, `UMG`, `InputCore`（标准依赖，未单独列出）
- `MediaPlateEditor` 额外依赖：`UnrealEd`, `EditorStyle`, `PropertyEditor`, `LevelEditor`（仅列出独特项 `UnrealEd`）

## 维护状态

### 近期更新

- 2025-10-16 `39016be3` — MediaPlate: Light touch fix for Hidden In Game toggle causing the plate to lose its material in mult
- 2025-10-04 `d2f392ba` — [MediaPlateEditor] Fixing Next and Previous Buttons
- 2025-09-25 `31e29d58` — [MediaPlateEditor] Fix potential null dereference.
- 2025-09-25 `46c8aac9` — [MediaPlateEditor] Fix the media plate editor's playback buttons.
- 2025-09-23 `4a459146` — [Media Plate] Fix Aspect Ratio and Mesh Mode transactions to fix Multi-User operations.

### 维护评价

- **创建时间**：2025-09-23，至今约 1 年。
- **近期更新**：2025 年 10 月仍有修复，包括多用户、播放按钮、空指针等。
- **活跃度**：更新频繁且针对具体 Bug，属于 **活跃维护** 阶段。
- **实验性**：`.uplugin` 中 `IsBetaVersion=true`，但 `IsExperimentalVersion=false`，说明该插件仍处于 Beta 阶段，但并非实验性废弃状态。
- **是否推荐使用**：推荐用于需要快速将媒体集成到关卡中的场景。注意它是 Beta 版本，生产环境需自行测试稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate/Tests) (可能不存在，此为推测路径)