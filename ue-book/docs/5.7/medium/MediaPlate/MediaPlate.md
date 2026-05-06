# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体面板 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资源、演员、组件） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate) | |

## 用途

Media Plate 是一个可以在关卡中放置的演员（`AMediaPlate`），用于在世界中播放和显示媒体内容（视频、图像流等）。它把媒体播放、纹理显示、声音输出等功能封装到 `UMediaPlateComponent` 中，提供了一套完整的“屏幕上播放视频”的解决方案。

相比直接使用 `UMediaPlayer` + `UMediaTexture` + `UMeshComponent` 手动搭建，Media Plate 自动化了以下工作：
- 自动创建并管理 `UMediaPlayer`、`UMediaTexture`、`UMediaSoundComponent`。
- 自动生成平面几何体（或使用自定义静态网格体）并应用材质，将媒体纹理渲染到表面。
- 支持多种媒体源类型：资源资产、外部文件、播放列表。
- 支持实时 Mip 生成、Holdout Composite（后期合成）、多用户协作编辑。
- 提供蓝图和 C++ 接口，方便在动画、蓝图逻辑中控制播放。

本质上，它是“在 3D 世界中放置一块能播放视频的屏幕”的最快路径。

## 使用场景

- **游戏内电视/监控屏幕**：在场景中放置一个 Media Plate，播放本地视频文件或来自媒体源的流。
- **广告牌/信息展示**：循环播放多个视频或图片序列。
- **多用户协作**：在 Multi-User 编辑环境中，多个用户可以同步控制媒体播放状态（播放、暂停、跳转等）。
- **材质预览/动态纹理**：将媒体内容作为动态纹理应用到自定义网格体上（如曲面屏、透明屏幕）。
- **Holdout Composite**：使用 `bEnableHoldoutComposite` 将媒体画面从场景中单独提取，与后处理效果组合（例如后期合成中的虚拟屏幕）。

## 蓝图用法

核心操作通过 `UMediaPlateComponent` 暴露。常用节点按功能分组如下：

### 🔗 媒体源操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenSource` | 打开指定的媒体源（资产、文件或播放列表） | `UMediaPlateComponent` |
| `Close` | 关闭当前媒体 | `UMediaPlateComponent` |
| `SelectMediaSourceAsset` | 切换为资产型媒体源 | `UMediaPlateComponent` |
| `SelectExternalMedia` | 切换为外部文件媒体源 | `UMediaPlateComponent` |
| `GetMediaPlaylist` | 获取当前播放列表（可用于添加/移除项目） | `UMediaPlateComponent` |

### ▶️ 播放控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 开始播放 | `UMediaPlateComponent` |
| `Pause` | 暂停播放 | `UMediaPlateComponent` |
| `Next` | 播放列表下一项 | `UMediaPlateComponent` |
| `Previous` | 播放列表上一项 | `UMediaPlateComponent` |
| `Reverse` | 反向播放 | `UMediaPlateComponent` |
| `Forward` | 快进（默认 1x 速度） | `UMediaPlateComponent` |
| `Rewind` | 倒带（默认 -1x 速度） | `UMediaPlateComponent` |
| `SetLooping` | 设置是否循环 | `UMediaPlateComponent` |
| `SetRate` | 设置播放速率（支持负数） | `UMediaPlateComponent` |

### 📐 外观与属性

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetHoldoutCompositeEnabled` | 开启/关闭 Holdout Composite | `AMediaPlate` |
| `IsHoldoutCompositeEnabled` | 查询 Holdout Composite 状态 | `AMediaPlate` |
| `GetCurrentMaterial` | 获取当前应用的材质（用于进一步修改） | `AMediaPlate` |
| `GetCurrentOverlayMaterial` | 获取当前叠加材质 | `AMediaPlate` |
| `SetMediaTextureResourceSettings` | 设置媒体纹理的 Mip 生成等参数 | `UMediaPlateComponent` |

### ⏳ 延迟（Latent）操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenSourceLatent` | 延迟打开媒体源，可等待纹理就绪（用于同步动画加载） | `UMediaPlateComponent` |

### 使用示例（蓝图描述）

**播放一个外部视频文件：**
1. 在关卡中放置一个 `BP_MediaPlate` 蓝图（或直接放置 `AMediaPlate` 演员）。
2. 调用 `MediaPlateComponent` → `SelectExternalMedia`，传入视频文件的磁盘路径。
3. 调用 `Play` 开始播放。可以连接 `Play` 节点的输出执行线到下一步。

**循环播放播放列表中的多个视频：**
1. 预先创建一个 `UMediaPlaylist` 资产，添加多个媒体源。
2. 在蓝图中获取该播放列表，调用 `MediaPlateComponent` → `OpenSource`（选择 Playlist 模式）并传入播放列表。
3. 调用 `Play`。使用 `Next` / `Previous` 切换。

**在 Level Sequence 中控制播放：**
- 可以使用 `MediaPlateComponent` 的 `Play`、`Pause`、`Close` 等节点作为 Sequence 中的事件轨道。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlate.h"
#include "MediaPlateComponent.h"
```

### 基本用法

```cpp
// 在关卡中创建 Media Plate 演员
AMediaPlate* MediaPlate = GetWorld()->SpawnActor<AMediaPlate>(AMediaPlate::StaticClass(), SpawnTransform);

// 获取组件
UMediaPlateComponent* MediaPlateComp = MediaPlate->MediaPlateComponent;

// 选择外部文件作为媒体源
MediaPlateComp->SelectExternalMedia(TEXT("E:/Movies/myVideo.mp4"));

// 播放
MediaPlateComp->Play();

// 暂停
MediaPlateComp->Pause();

// 关闭
MediaPlateComp->Close();
```

### 进阶用法：使用播放列表并延迟打开

```cpp
// 创建播放列表
UMediaPlaylist* Playlist = NewObject<UMediaPlaylist>();
Playlist->Add(MyMediaSource1);
Playlist->Add(MyMediaSource2);

// 设置到组件
UMediaPlateComponent* MediaPlateComp = ...;
MediaPlateComp->GetMediaPlaylist()->ReplacePlaylist(Playlist);

// 延迟打开（等待纹理就绪）
FLatentActionInfo LatentInfo;
LatentInfo.CallbackTarget = this;
LatentInfo.ExecutionFunction = TEXT("OnMediaOpened");
LatentInfo.Linkage = 0;
LatentInfo.UUID = 12345;
bool bSuccess = false;
MediaPlateComp->OpenSourceLatent(LatentInfo, 10.0f, true, bSuccess);
// 在 OnMediaOpened 中处理 bSuccess
```

### 编辑器使用：自定义材质与 Holdout Composite

```cpp
// 获取当前材质并修改
UMaterialInterface* CurrentMat = MediaPlate->GetCurrentMaterial();
if (UMaterialInstanceDynamic* MID = Cast<UMaterialInstanceDynamic>(CurrentMat))
{
    MID->SetScalarParameterValue(TEXT("Brightness"), 1.5f);
}

// 开启 Holdout Composite
MediaPlate->SetHoldoutCompositeEnabled(true);
```

## Demo 示例

以下是一个最小 C++ Actor 示例，它在 BeginPlay 时创建一个 MediaPlate 并播放本地视频。

**MyMediaPlayerActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMediaPlayerActor.generated.h"

class AMediaPlate;

UCLASS()
class MYGAME_API AMyMediaPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    AMediaPlate* MediaPlate = nullptr;
};
```

**MyMediaPlayerActor.cpp**
```cpp
#include "MyMediaPlayerActor.h"
#include "MediaPlate.h"
#include "MediaPlateComponent.h"
#include "Engine/World.h"

void AMyMediaPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    // 在玩家位置前方 200 单位生成 MediaPlate
    FVector Location = GetActorLocation() + GetActorForwardVector() * 200.0f;
    FRotator Rotation = FRotator::ZeroRotator;
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    MediaPlate = GetWorld()->SpawnActor<AMediaPlate>(AMediaPlate::StaticClass(), Location, Rotation, SpawnParams);

    if (MediaPlate)
    {
        UMediaPlateComponent* Comp = MediaPlate->MediaPlateComponent;
        // 使用外部文件（请替换为实际路径）
        Comp->SelectExternalMedia(TEXT("D:/Videos/Intro.mp4"));
        Comp->Play();
    }
}
```

*提示：实际使用时建议将文件路径配置为 `FString` 属性，或通过媒体源资产引用。*

## 模块依赖

### MediaPlate (Runtime)

无特殊依赖（仅标准 Core/Engine/Slate 等）。

### MediaPlateEditor (Runtime)

| 模块 | 用途 |
|---|---|
| `MediaPlate` | 依赖运行时核心逻辑，用于编辑器扩展 |
| `UnrealEd` | 编辑器基础设施，提供细节面板自定义等 |

## 维护状态

### 近期更新

- **2025-10-16** `39016be3` — MediaPlate: Light touch fix for Hidden In Game toggle causing the plate to lose its material in mult
- **2025-10-04** `d2f392ba` — [MediaPlateEditor] Fixing Next and Previous Buttons
- **2025-09-25** `31e29d58` — [MediaPlateEditor] Fix potential null dereference.
- **2025-09-25** `46c8aac9` — [MediaPlateEditor] Fix the media plate editor's playback buttons.
- **2025-09-23** `4a459146` — [Media Plate] Fix Aspect Ratio and Mesh Mode transactions to fix Multi-User operations.

### 维护评价

这是一个全新的插件（2025年9月引入），目前处于 Beta 阶段（`.uplugin` 中 `IsBetaVersion = true`）。从近期提交来看，修复主要集中在 Multi-User 协作和编辑器按钮功能上，表明开发者正在积极打磨其稳定性和可用性。由于是 beta，可能会存在一些边缘情况或 API 变更。推荐在新项目中尝试使用，但对于生产项目建议进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)（通用的 Media Framework 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate/Tests)（若有）