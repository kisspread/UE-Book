# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 实时数据链接 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-02-27 |
| 年龄标签 | 🆕（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是 Unreal Engine 的实时动画数据流传输框架，解决的核心问题是：**如何将外部设备或应用程序产生的动画数据（骨骼、变换、曲线、相机等）实时导入到引擎中**。

该插件提供了一套完整的数据管道架构：

- **源（Source）**：数据输入端，可以是 Motion Capture 设备、DCC 工具（Maya、MotionBuilder）、VR 追踪器、iPhone ARKit 面部捕捉等
- **主题（Subject）**：由 Source 发布的命名数据流，每条 Subject 包含特定类型的角色或对象数据
- **消费者（Consumer）**：引擎内接收数据的组件，如动画蓝图中的骨骼控制器、Sequencer 录制轨道等

该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动激活。它同时支持 `LiveLinkHub` 程序，表明设计用于独立的虚拟制片中心（Virtual Production Hub）场景，允许多台设备间共享数据流。

## 使用场景

- 你在做虚拟制片 / 虚拟摄影棚 → 用 Live Link 接收 OptiTrack、Vicon 等 Mocap 系统的骨骼数据
- 你使用 iPhone + ARKit 做面部捕捉 → 用 Live Link 接收面部动画数据驱动 Metahuman
- 你的 DCC 工具（Maya/Blender）需要实时预览 → 用 Live Link 实时推送变换和动画
- 你需要在多台机器间同步动画数据 → 用 Live Link Multi-User 模式
- 你需要在 Sequencer 中录制实时动画并回放 → 用 Live Link + LiveLinkSequencer
- 你使用 VR 追踪器做全身体追踪 → 用 Live Link 接收各追踪器的变换数据

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLiveLinkSubjects` | 获取当前所有可用的 Live Link 主题列表 | `ULiveLinkRole` / Blueprint Library |
| `GetLiveLinkSubjectRole` | 获取指定主题的角色类型（骨骼、变换等） | Blueprint Library |
| `IsLiveLinkSubjectEnabled` | 检查指定主题是否启用 | Blueprint Library |
| `GetLiveLinkSubjectData` | 获取指定主题的当前帧数据 | Blueprint Library |
| `Live Link Transform Controller` | 动画蓝图节点，用 Live Link 变换数据驱动骨骼 | `ULiveLinkTransformController` |
| `SetLiveLinkSubjectEnabled` | 启用/禁用指定主题 | Blueprint Library |

### 动画蓝图中的使用

1. 在动画蓝图的 **Animation Graph** 中，添加 `Live Link` 节点来获取骨骼姿态
2. 选择要连接的 Subject 名称和角色类型
3. 将输出连接到最终姿态或进行混合

### Live Link 面板

在编辑器菜单 **Window → Live Link** 中打开 Live Link 面板：
- 查看所有已连接的 Source
- 查看每个 Source 发布的 Subject 列表
- 启用/禁用特定 Subject
- 测试连接状态

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkComponent.h"
#include "Roles/LiveLinkBasicRole.h"
#include "Roles/LiveLinkTransformRole.h"
#include "ILiveLinkClient.h"
```

### 基本用法 — 获取 Live Link 客户端接口

```cpp
// 从模块获取 Live Link 客户端（用于直接查询/订阅）
#include "ILiveLinkClient.h"

// 获取 LiveLinkClient 模块
ILiveLinkClient* LiveLinkClient = nullptr;
if (IModularFeatures::Get().IsModularFeatureAvailable(ILiveLinkClient::ModularFeatureName))
{
    LiveLinkClient = &IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);
}
```

### 通过 Component 使用 Live Link 数据

```cpp
// 使用 ULiveLinkComponentController 组件在 Actor 上驱动变换
#include "LiveLinkComponent.h"

// 在 Actor 的构造函数或 BeginPlay 中
UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor()
    {
        // 创建 Live Link 组件控制器
        LiveLinkController = CreateDefaultSubobject<ULiveLinkComponentController>(TEXT("LiveLinkController"));
    }

    UPROPERTY(VisibleAnywhere)
    ULiveLinkComponentController* LiveLinkController;
};
```

### 在动画蓝图中查询 Live Link 数据

```cpp
// 通过 FLiveLinkSubjectKey 和 FLiveLinkSubjectFrameData 获取骨骼数据
#include "LiveLinkTypes.h"
#include "Roles/LiveLinkAnimationRole.h"

// 获取特定 Subject 的当前帧骨骼数据
FLiveLinkSubjectKey SubjectKey;
SubjectKey.Guid = FGuid(); // Subject 的唯一标识
SubjectKey.SubjectName = FName("MyMocapSubject");

// 通过客户端查询
if (LiveLinkClient && LiveLinkClient->IsSubjectValid(SubjectKey))
{
    TSubclassOf<ULiveLinkRole> Role = LiveLinkClient->GetSubjectRole(SubjectKey);
    if (Role && Role->IsChildOf(ULiveLinkAnimationRole::StaticClass()))
    {
        // 处理动画数据
    }
}
```

## Demo 示例

### Live Link 驱动 Actor 变换的最小示例

```cpp
// MyLiveLinkActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkComponent.h"
#include "MyLiveLinkActor.generated.h"

UCLASS()
class AMyLiveLinkActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLiveLinkActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Live Link")
    ULiveLinkComponentController* LiveLinkController;

    // Live Link Subject 名称（在编辑器中选择）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Live Link")
    FLiveLinkSubjectName LiveLinkSubjectName;
};
```

```cpp
// MyLiveLinkActor.cpp
#include "MyLiveLinkActor.h"

AMyLiveLinkActor::AMyLiveLinkActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建 Live Link 控制组件
    LiveLinkController = CreateDefaultSubobject<ULiveLinkComponentController>(TEXT("LiveLinkController"));

    // 默认控制 Actor Root 组件的变换
    LiveLinkController->ComponentToControl = FLiveLinkComponentController::ComponentToControlType::ThisComponent;
}

void AMyLiveLinkActor::BeginPlay()
{
    Super::BeginPlay();

    // 在编辑器中配置 Subject 名称后，组件会自动接收并应用数据
    // 可在此处添加额外的初始化逻辑
}
```

> 注：此示例展示最基本的 Live Link Actor 集成。完整的骨骼驱动通常在动画蓝图中完成。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 核心接口定义（角色、主题、数据类型） |
| `LiveLinkMessageBusFramework` | 基于 MessageBus 的网络传输层 |
| `AnimationCore` | 动画核心数学和骨骼工具 |
| `AnimationBlueprintLibrary` | 动画蓝图辅助功能 |

> 注：以上依赖从 Build.cs 的模块依赖列表中提取（去除了 Core、CoreUObject、Engine 等常见依赖）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cd46766d` | Fix crash in ULiveLinkBroadcastComponent::PostEditChangeProperty when the broadcast subsystem is una | 修复广播子系统未初始化时编辑属性导致的崩溃 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的警告 |
| 2026-05-13 | `057dbc69` | Fix crashes in PostEditChangeProperty overrides when MemberProperty is null, which occurs when Pytho | 修复 Python 脚本触发 PostEditChangeProperty 时 MemberProperty 为空的崩溃 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片资产分类重组，迁移至新资产类别 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **创建时间**：2018年2月（约 7 年前），随 UE4.19 从实验性文件夹正式迁移至 Animation 分类
- **近期更新**：2026年5月仍有频繁的 bug 修复和稳定性改进，属于持续活跃维护
- **更新质量**：近期提交集中在崩溃修复、浮点精度、编辑器稳定性等方面，表明在进行生产级打磨
- **模块规模**：7 个子模块、215 个源文件，是引擎中最复杂的插件之一
- **官方地位**：由 Epic Games 官方维护，是虚拟制片管线的核心组件

**推荐使用**：✅ 强烈推荐。Live Link 是 UE 虚拟制片的标准数据管道，拥有成熟的生态支持（Maya、MotionBuilder、MotionLive 等官方客户端），且持续维护。需要注意默认不启用，需在项目设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLink)
- 官方文档：https://docs.unrealengine.com/en-US/animation-live-link-in-unreal-engine/（Epic 官方 Live Link 文档页）