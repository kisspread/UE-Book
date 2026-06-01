# Motion Design

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Avalanche` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheMedia` (Runtime), `AvalancheRemoteControl` (Runtime), 等共 43 个模块 |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（原名 Avalanche）是 UE5 虚拟制片生态中的**广播级动态图形设计与合成工具链**。它为实时广播、虚拟制片场景提供了一整套从设计到播出的工作流：

- **合成与排版**：在 3D 视口中直接创建和编辑动态图形元素（文字、形状、特效），类似 After Effects 与 Unreal 的深度融合
- **场景管理**：通过 SceneTree、Outliner、SceneRig 等模块提供专业级场景组织能力
- **远程控制**：通过 Remote Control 集成实现外部系统（如广播控制台）对场景参数的实时驱动
- **属性动画**：PropertyAnimator 与 Sequencer 集成提供关键帧动画能力
- **克隆与效果器**：ClonerEffector 系统用于阵列化复制和程序化动画
- **材质设计**：Material Designer 提供节点化材质编辑
- **媒体合成**：与 Media IO 集成，支持视频输入输出和实时合成
- **渲染队列**：MRQ（Movie Render Queue）集成用于高质量离线渲染

本插件最初位于 `Engine/Plugins/Experimental/`，于 2025 年 5 月正式迁移至 `Engine/Plugins/VirtualProduction/`，标志着从实验性阶段转为正式支持的生产工具。

> **本文档聚焦 `AvalancheRemoteControl` 模块**，该模块负责 Motion Design 与 Unreal Remote Control 框架的桥接。

## 使用场景

- 你在做电视直播/虚拟制片，需要从广播控制台实时操控 UE 场景中的元素属性 → 用 Motion Design + Remote Control
- 你需要设计复杂的 3D 动态图形（片头、Lower Third、Logo 动画）并实时渲染 → 用 Motion Design 的文本、形状和克隆效果器系统
- 你需要通过外部 Web API 或 OSC 协议远程控制场景中的参数 → 用 `AvalancheRemoteControl` 模块的注册/绑定机制
- 你需要将场景中的 Actor 属性暴露给 Remote Control Preset 并支持自动重绑定 → 用 `FAvaRemoteControlRebind`

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Controlled Actors` | 根据 Remote Control 虚拟属性控制器获取其控制的所有 Actor | `UAvaRCLibrary` |
| `On Values Applied` | 当远程控制值被应用时的回调事件（需实现接口） | `IAvaRemoteControlInterface` |

### 接口实现

通过实现 `IAvaRemoteControlInterface`（蓝图显示名 "Motion Design Remote Control Interface"），你的 Actor 可以在远程控制值被应用时收到通知：

- 在蓝图中添加 **Motion Design Remote Control Interface** 接口
- 重写 **On Values Applied** 事件
- 在该事件中执行你需要的逻辑（如更新 UI、触发特效等）

### 使用 Get Controlled Actors

- 在蓝图中调用 **Get Controlled Actors** 节点
- 传入 **World Context Object**（通常是 Self）和一个 **RC Virtual Property Base** 控制器引用
- 返回一个 Actor 数组，表示该控制器当前控制的所有 Actor

### FAvaRCControllerId 使用

- 在蓝图中创建 **Motion Design RC Controller Id** 结构体
- 设置 **Name** 字段为目标控制器名称
- 使用 **Find Controller** 方法在指定 Preset 中查找对应的虚拟属性控制器

## C++ 用法

### 头文件引入

```cpp
#include "IAvaRemoteControlInterface.h"
#include "AvaRCLibrary.h"
#include "AvaRemoteControlUtils.h"
#include "AvaRemoteControlRebind.h"
#include "AvaRCControllerId.h"
```

### 基本用法

#### 实现 Remote Control 接口

让 Actor 响应远程控制值更新事件：

```cpp
// MyRemoteActor.h
#include "IAvaRemoteControlInterface.h"
#include "GameFramework/Actor.h"

UCLASS()
class AMyRemoteControlledActor : public AActor, public IAvaRemoteControlInterface
{
    GENERATED_BODY()

public:
    // 重写远程控制值应用回调
    virtual void OnValuesApplied_Implementation() override;
};

// MyRemoteActor.cpp
void AMyRemoteControlledActor::OnValuesApplied_Implementation()
{
    // 当 Remote Control 系统应用新值时执行自定义逻辑
    UE_LOG(LogTemp, Log, TEXT("Remote control values applied to %s"), *GetName());
}
```

#### 获取受控 Actor 列表

```cpp
// 通过虚拟属性控制器获取所有被控制的 Actor
URCVirtualPropertyBase* Controller = /* 获取控制器引用 */;
TArray<AActor*> ControlledActors = UAvaRCLibrary::GetControlledActors(GetWorld(), Controller);

for (AActor* Actor : ControlledActors)
{
    UE_LOG(LogTemp, Log, TEXT("Controlled: %s"), *Actor->GetName());
}
```

*来源：`Public/AvaRCLibrary.h`*

#### 注册/注销 Remote Control Preset

```cpp
URemoteControlPreset* MyPreset = /* 获取或创建 Preset */;

// 注册到 Remote Control 模块，使其可通过 Web 接口访问
bool bSuccess = FAvaRemoteControlUtils::RegisterRemoteControlPreset(MyPreset, true /* bInEnsureUniqueId */);

// 查找当前 Level 中嵌入的 Preset
URemoteControlPreset* EmbeddedPreset = FAvaRemoteControlUtils::FindEmbeddedPresetInLevel(GetLevel());

// 使用完毕后注销
FAvaRemoteControlUtils::UnregisterRemoteControlPreset(MyPreset);
```

*来源：`Public/AvaRemoteControlUtils.h`*

### 进阶用法

#### 重绑定未解析的实体

在关卡加载或对象重建后，Remote Control Preset 中的绑定可能失效。使用重绑定工具恢复：

```cpp
URemoteControlPreset* Preset = /* 获取 Preset */;

// 步骤 1：重绑定未解析的实体（允许瞬态对象）
FAvaRemoteControlRebind::RebindUnboundEntities(Preset, GetLevel());

// 步骤 2：确保所有字段的 FieldPathInfo 正确解析（必须在 Rebind 之后调用）
FAvaRemoteControlRebind::ResolveAllFieldPathInfos(Preset);
```

*来源：`Public/AvaRemoteControlRebind.h`*

#### 通过 ControllerId 查找控制器

```cpp
// 从已知控制器创建 ID
URCVirtualPropertyBase* OriginalController = /* ... */;
FAvaRCControllerId ControllerId(OriginalController);

// 序列化后，在另一个 Preset 中查找同名控制器
URemoteControlPreset* OtherPreset = /* ... */;
URCVirtualPropertyBase* FoundController = ControllerId.FindController(OtherPreset);

if (FoundController)
{
    FText DisplayName = ControllerId.ToText();
    UE_LOG(LogTemp, Log, TEXT("Found controller: %s"), *DisplayName.ToString());
}
```

*来源：`Public/AvaRCControllerId.h`*

## Demo 示例

### 完整的远程控制 Actor 实现

```cpp
// MyBroadcastGraphic.h
#pragma once

#include "IAvaRemoteControlInterface.h"
#include "GameFramework/Actor.h"
#include "MyBroadcastGraphic.generated.h"

UCLASS()
class AMyBroadcastGraphic : public AActor, public IAvaRemoteControlInterface
{
    GENERATED_BODY()

public:
    AMyBroadcastGraphic();

    // IAvaRemoteControlInterface
    virtual void OnValuesApplied_Implementation() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Broadcast")
    FText DisplayText;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Broadcast")
    FLinearColor TintColor;

protected:
    UPROPERTY(VisibleAnywhere)
    UTextRenderComponent* TextComponent;

    UPROPERTY()
    URemoteControlPreset* RegisteredPreset;

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    void UpdateVisuals();
};
```

```cpp
// MyBroadcastGraphic.cpp
#include "MyBroadcastGraphic.h"
#include "AvaRemoteControlUtils.h"
#include "AvaRemoteControlRebind.h"
#include "Components/TextRenderComponent.h"
#include "RemoteControlPreset.h"

AMyBroadcastGraphic::AMyBroadcastGraphic()
{
    TextComponent = CreateDefaultSubobject<UTextRenderComponent>(TEXT("Text"));
    RootComponent = TextComponent;
    TextComponent->SetText(DisplayText);
}

void AMyBroadcastGraphic::BeginPlay()
{
    Super::BeginPlay();

    // 查找当前 Level 中嵌入的 Remote Control Preset
    RegisteredPreset = FAvaRemoteControlUtils::FindEmbeddedPresetInLevel(GetLevel());

    if (RegisteredPreset)
    {
        // 重绑定可能在加载过程中失效的实体
        FAvaRemoteControlRebind::RebindUnboundEntities(RegisteredPreset, GetLevel());
        FAvaRemoteControlRebind::ResolveAllFieldPathInfos(RegisteredPreset);

        // 注册 Preset 使其可通过 Web 接口访问
        FAvaRemoteControlUtils::RegisterRemoteControlPreset(RegisteredPreset, true);
    }

    UpdateVisuals();
}

void AMyBroadcastGraphic::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (RegisteredPreset)
    {
        FAvaRemoteControlUtils::UnregisterRemoteControlPreset(RegisteredPreset);
    }
    Super::EndPlay(EndPlayReason);
}

void AMyBroadcastGraphic::OnValuesApplied_Implementation()
{
    // 远程控制值更新后刷新视觉表现
    UpdateVisuals();
}

void AMyBroadcastGraphic::UpdateVisuals()
{
    if (TextComponent)
    {
        TextComponent->SetText(DisplayText);
        TextComponent->SetTextRenderColor(TintColor.ToFColor(true));
    }
}
```

## 模块依赖

`AvalancheRemoteControl` 模块的关键依赖：

| 模块 | 用途 |
|---|---|
| `RemoteControl` | Unreal Remote Control 框架核心，提供 Preset、虚拟属性、Web API 等基础能力 |
| `RemoteControlLogic` | Remote Control 的逻辑层，处理绑定解析和字段路径 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将 Motion Design 面板移至独立标签组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 为 MRQ 渲染添加了节目单页面分析数据 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 为播出控制工具栏添加页面加载选项 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it or disassociated wit | 视口客户端关联/解除关联通知重构 |

### 维护评价

- **活跃维护**：最近更新频率极高（2026 年 5 月有多次提交），持续有功能迭代
- **正式支持**：从 Experimental 迁移到 VirtualProduction 分类，表明已进入正式生产支持阶段
- **大型插件**：43 个模块、2060 个源文件，属于 Epic 重点维护的旗舰级插件
- **推荐使用**：如果你的项目涉及虚拟制片、广播或实时动态图形设计，强烈推荐使用
- **注意**：依赖链较长（Advanced Renamer, Custom Details View, Dynamic Material 等 12 个插件），启用时需确保所有依赖可用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [Remote Control 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/RemoteControl)