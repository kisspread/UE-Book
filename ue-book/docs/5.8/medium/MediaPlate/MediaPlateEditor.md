# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体播放器 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（媒体材质模板） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate) | |

## 用途

Media Plate 插件提供了一套完整的解决方案，用于在 Unreal Engine 场景中播放视频或图像序列。它不仅仅是一个简单的播放器 Actor，更是一个包含媒体资源管理、播放控制、网格映射（平面、球面或自定义网格）、材质管理、以及深度集成编辑器工具（如 Sequencer 和拖放功能）的完整媒体播放工作流系统。其核心目标是解决在建筑可视化、虚拟制片或互动体验中高效、灵活地嵌入和控制动态媒体内容的问题。

## 使用场景

- **建筑/产品可视化**：在虚拟展厅或建筑漫游中，通过 Media Plate 播放产品介绍视频或环境光效动画。
- **展览与主题娱乐**：在虚拟展览馆或主题公园场景中，为“电子画布”、“环形屏幕”或“球幕”提供媒体内容。
- **影视预览与虚拟制片**：在场景中直接预览影片素材，或为虚拟场景中的屏幕（如新闻演播室背景）提供实时画面。
- **动态广告与信息牌**：在游戏中实现动态更新的广告牌或信息显示终端。

## 蓝图用法

Media Plate 的核心运行时功能由 `UMediaPlateComponent` 提供。以下列出其关键的蓝图可用节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open` | 根据当前资源设置打开媒体 | `UMediaPlateComponent` |
| `Close` | 关闭当前正在播放的媒体 | `UMediaPlateComponent` |
| `Play` | 播放或恢复播放媒体 | `UMediaPlateComponent` |
| `Pause` | 暂停媒体播放 | `UMediaPlateComponent` |
| `Reverse` | 反向播放媒体 | `UMediaPlateComponent` |
| `SetMeshType` | 设置媒体投射的网格类型（平面、球体等） | `UMediaPlateComponent` |
| `SetMediaSource` | 运行时更改媒体源（资产或外部路径） | `UMediaPlateComponent` |
| `GetMediaPlayer` | 获取关联的媒体播放器对象 | `UMediaPlateComponent` |

### 使用示例（蓝图描述）

1.  **基础播放**：在关卡中放置 `MediaPlate` Actor。在蓝图中，通过“Get Media Plate Component”获取其组件引用，然后调用“Open”节点即可开始播放默认媒体。
2.  **交互控制**：在角色蓝图中，通过射线检测获取到 MediaPlate Actor，然后调用其组件的“Play”、“Pause”、“Reverse”等节点，实现点击屏幕切换播放状态。
3.  **动态更换媒体**：创建一个媒体源资产（如 `FileMediaSource`），在蓝图中调用 `SetMediaSource` 节点将其传给 MediaPlate 组件，实现运行时切换视频内容。

## C++ 用法

编辑器模块 `FMediaPlateEditorModule` 提供了扩展编辑器功能和管理媒体播放状态的能力。

### 头文件引入

```cpp
#include "MediaPlateEditorModule.h"
```

### 基本用法

追踪正在编辑器中播放的 Media Plate。

```cpp
// 获取编辑器模块实例
FMediaPlateEditorModule& MediaPlateEditorModule = FModuleManager::LoadModuleChecked<FMediaPlateEditorModule>(TEXT("MediaPlateEditor"));

// 当一个 MediaPlate 组件开始播放时通知编辑器模块
MediaPlateEditorModule.MediaPlateStartedPlayback(MyMediaPlateComponent);
```

### 进阶用法

处理从编辑器拖拽到视口的媒体文件。编辑器模块会缓存这些临时创建的媒体源，以便正确管理其生命周期。

```cpp
// 在某个资产处理流程中，检查一个媒体源是否是由拖放操作创建的
if (MediaPlateEditorModule.RemoveMediaSourceFromDragDropCache(InMediaSource))
{
    // 是拖放创建的临时资产，可以安全地修改其 Outer 或进行其他操作
    InMediaSource->Rename(nullptr, NewOuter);
}
```

**来源文件**: `Source/MediaPlateEditor/Private/MediaPlateEditorModule.cpp` 中的 `OnAssetDropped` 和 `RemoveMediaSourceFromDragDropCache` 实现。

## Demo 示例

以下是一个在 Actor 中使用 `UMediaPlateComponent` 的最小 C++ 示例。

```cpp
// MyMediaActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMediaActor.generated.h"

class UMediaPlateComponent;

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

protected:
    virtual void BeginPlay() override;

public:
    // 核心媒体播放组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlateComponent* MediaPlateComp;
};

// MyMediaActor.cpp
#include "MyMediaActor.h"
#include "MediaPlateComponent.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建 MediaPlate 组件作为根组件
    MediaPlateComp = CreateDefaultSubobject<UMediaPlateComponent>(TEXT("MediaPlate"));
    RootComponent = MediaPlateComp;
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查组件有效性并打开媒体
    if (MediaPlateComp)
    {
        // 打开 MediaPlate 组件中设置的默认媒体源
        MediaPlateComp->Open();
        // 开始播放
        MediaPlateComp->Play();
    }
}
```

## 模块依赖

该插件包含一个编辑器专用模块，对使用者有特定依赖要求。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | `MediaPlateEditor` 模块需要依赖它来实现编辑器内的资产操作、细节面板定制、放置面板注册等所有编辑器扩展功能。 |

对于仅需在运行时使用 `MediaPlate` 组件的项目，无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏以适配引擎新规范。 |
| 2026-04-09 | `17c8eeed` | [MediaPlateEditor] Prevent adding multiple media tracks under the same media plate binding. | 修复了序列编辑器中同一 Media Plate 绑定下可重复添加媒体轨道的问题。 |
| 2026-04-08 | `786c0a7e` | [MediaPlate] Support multiple media textures in the “material instance constant” code path. | 增强了材质实例常量路径，支持多个媒体纹理，提升材质管理的灵活性。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修正了前次提交中错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚了之前的某个改动，恢复稳定性。 |

### 维护评价

Media Plate 插件创建于 2022 年初，目前仍在**积极维护**中。尽管其 `.uplugin` 标记为 `IsBetaVersion: true`，但从近期的提交历史可以看出，Epic 团队仍在持续修复 Bug（如序列编辑器问题）和增强功能（如多材质纹理支持）。最近的提交集中在 2026 年 4 月，表明该插件是媒体播放相关功能的核心部分，其稳定性和功能对虚拟制片和建筑可视化等项目至关重要。**推荐使用**，但需留意其 Beta 标签，意味着 API 或行为可能在引擎大版本更新时发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate/Tests)