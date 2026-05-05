# Live Link

> LiveLink allows streaming of animated data into Unreal Engine

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `LiveLink` (Runtime), `LiveLinkComponents` (Runtime), `LiveLinkEditor` (Runtime), `LiveLinkGraphNode` (Runtime), `LiveLinkMovieScene` (Runtime), `LiveLinkMultiUser` (Runtime), `LiveLinkSequencer` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-03-24 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink) | |

## 用途

Live Link 是一个实时数据流框架，其核心功能远不止于动画数据。它提供了一套标准化的接口和协议，用于将来自外部设备、软件或引擎内部其他系统的实时数据（如骨骼动画、变换、相机、光照、音频等）流式传输到虚幻引擎中。它解决的是“实时数据接入”问题，为虚拟制片、动作捕捉、实时渲染、多用户协作等场景提供了统一的数据管道。

## 使用场景

- **虚拟制片**：将外部摄像机跟踪系统（如 OptiTrack, Vicon）的实时数据流式传输到引擎内的虚拟摄像机，实现虚实同步。
- **动作捕捉**：将动捕设备（如 Xsens, Rokoko）的实时骨骼数据驱动引擎内的角色动画。
- **实时渲染与合成**：将外部渲染引擎或合成软件（如 Nuke）的实时数据（如相机、物体变换）同步到引擎场景中。
- **多用户协作**：通过 Live Link 在多个虚幻引擎实例之间同步数据，用于大型虚拟制片或分布式模拟。
- **自定义数据流**：开发者可以基于 Live Link 框架，创建自定义主题（Subject）来传输任何类型的数据。

## 蓝图用法

Live Link 提供了丰富的蓝图节点，用于创建、管理和消费实时数据流。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Virtual Subject` | 创建一个虚拟主题，用于聚合或转换来自其他主题的数据。 | `ULiveLinkBlueprintVirtualSubject` |
| `Get Live Link Subject Role` | 获取指定 Live Link 主题的角色（Role），如动画、变换等。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subject Frame Data` | 获取指定主题在特定时间点的帧数据。 | `ULiveLinkBlueprintLibrary` |
| `Get Live Link Subjects` | 获取当前所有可用的 Live Link 主题名称列表。 | `ULiveLinkBlueprintLibrary` |
| `Set Live Link Subject Enabled` | 启用或禁用一个 Live Link 主题。 | `ULiveLinkBlueprintLibrary` |
| `Evaluate Live Link Frame` | 在蓝图中评估一个 Live Link 帧，获取其数据。 | `ULiveLinkBlueprintVirtualSubject` |
| `Add Live Link Controller` | 为组件添加一个 Live Link 控制器（如变换控制器）。 | `ULiveLinkComponentController` |

### 使用示例（蓝图描述）

1.  **创建虚拟主题并连接数据源**：
    *   使用 `Create Virtual Subject` 节点创建一个新的虚拟主题。
    *   在虚拟主题的蓝图中，重写 `Evaluate Live Link Frame` 事件。
    *   在该事件内，使用 `Get Live Link Subject Frame Data` 从一个或多个源主题获取数据。
    *   对获取的数据进行处理（如混合、转换），然后将结果设置到输出帧数据中。

2.  **使用 Live Link 驱动 Actor 变换**：
    *   在 Actor 的组件（如 SceneComponent）上，添加 `Live Link Component Controller`。
    *   在控制器的细节面板中，选择要监听的 Live Link 主题和角色（例如 `LiveLinkTransformRole`）。
    *   控制器会自动将接收到的变换数据应用到该组件上。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkVirtualSubject.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"
```

### 基本用法

创建一个自定义的 Live Link 虚拟主题，用于处理和转发数据。
（来源：`Engine/Plugins/Animation/LiveLink/Source/LiveLink/Public/LiveLinkVirtualSubject.h`）

```cpp
// MyLiveLinkVirtualSubject.h
#pragma once
#include "LiveLinkVirtualSubject.h"
#include "MyLiveLinkVirtualSubject.generated.h"

UCLASS()
class UMyLiveLinkVirtualSubject : public ULiveLinkVirtualSubject
{
    GENERATED_BODY()

public:
    // 重写此函数以定义如何评估（处理）来自源主题的数据
    virtual void EvaluateLiveLinkFrame(const FLiveLinkSubjectKey& SubjectKey,
                                       const TSubclassOf<ULiveLinkRole>& Role,
                                       const FLiveLinkSubjectFrameData& InFrameData,
                                       FLiveLinkBlueprintDataStruct& OutBlueprintData) const override;
};
```

```cpp
// MyLiveLinkVirtualSubject.cpp
#include "MyLiveLinkVirtualSubject.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

void UMyLiveLinkVirtualSubject::EvaluateLiveLinkFrame(const FLiveLinkSubjectKey& SubjectKey,
                                                      const TSubclassOf<ULiveLinkRole>& Role,
                                                      const FLiveLinkSubjectFrameData& InFrameData,
                                                      FLiveLinkBlueprintDataStruct& OutBlueprintData) const
{
    // 检查角色是否为变换角色
    if (Role == ULiveLinkTransformRole::StaticClass())
    {
        // 从输入帧数据中提取变换数据
        const FLiveLinkTransformFrameData* TransformData = InFrameData.FrameData.Cast<FLiveLinkTransformFrameData>();
        if (TransformData)
        {
            // 在这里进行数据处理，例如应用一个偏移
            FLiveLinkTransformFrameData ModifiedData = *TransformData;
            ModifiedData.Transform.AddToTranslation(FVector(100.f, 0.f, 0.f)); // X轴偏移100单位

            // 将处理后的数据设置到输出中
            OutBlueprintData.FrameData.InitializeWith(FLiveLinkTransformFrameData::StaticStruct(), &ModifiedData);
        }
    }
}
```

### 进阶用法

在 C++ 中注册一个自定义的 Live Link 控制器，用于驱动组件属性。
（来源：`Engine/Plugins/Animation/LiveLink/Source/LiveLinkComponents/Public/LiveLinkTransformController.h`）

```cpp
// MyCustomLiveLinkController.h
#pragma once
#include "LiveLinkControllerBase.h"
#include "MyCustomLiveLinkController.generated.h"

UCLASS()
class UMyCustomLiveLinkController : public ULiveLinkControllerBase
{
    GENERATED_BODY()

public:
    // 指定此控制器支持的角色
    virtual TSubclassOf<ULiveLinkRole> GetRole() const override;

    // 当接收到新的 Live Link 帧数据时调用
    virtual void Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData) override;

    // 控制器的目标组件
    UPROPERTY(Transient)
    TObjectPtr<USceneComponent> ControlledComponent;
};

// MyCustomLiveLinkController.cpp
#include "MyCustomLiveLinkController.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

TSubclassOf<ULiveLinkRole> UMyCustomLiveLinkController::GetRole() const
{
    return ULiveLinkTransformRole::StaticClass();
}

void UMyCustomLiveLinkController::Tick(float DeltaTime, const FLiveLinkSubjectFrameData& SubjectData)
{
    if (ControlledComponent)
    {
        const FLiveLinkTransformFrameData* TransformData = SubjectData.FrameData.Cast<FLiveLinkTransformFrameData>();
        if (TransformData)
        {
            // 将 Live Link 数据应用到组件变换上
            ControlledComponent->SetWorldTransform(TransformData->Transform);
        }
    }
}
```

## Demo 示例

一个最小的自定义 Live Link 虚拟主题示例，它接收一个变换主题的数据，并在 Z 轴上添加一个正弦波动画。

```cpp
// WavingLiveLinkSubject.h
#pragma once
#include "LiveLinkVirtualSubject.h"
#include "WavingLiveLinkSubject.generated.h"

UCLASS()
class UWavingLiveLinkSubject : public ULiveLinkVirtualSubject
{
    GENERATED_BODY()

public:
    virtual void EvaluateLiveLinkFrame(const FLiveLinkSubjectKey& SubjectKey,
                                       const TSubclassOf<ULiveLinkRole>& Role,
                                       const FLiveLinkSubjectFrameData& InFrameData,
                                       FLiveLinkBlueprintDataStruct& OutBlueprintData) const override;

    UPROPERTY(EditAnywhere, Category = "Wave")
    float WaveAmplitude = 50.f;

    UPROPERTY(EditAnywhere, Category = "Wave")
    float WaveFrequency = 2.f;
};
```

```cpp
// WavingLiveLinkSubject.cpp
#include "WavingLiveLinkSubject.h"
#include "Roles/LiveLinkTransformRole.h"
#include "Roles/LiveLinkTransformTypes.h"

void UWavingLiveLinkSubject::EvaluateLiveLinkFrame(const FLiveLinkSubjectKey& SubjectKey,
                                                   const TSubclassOf<ULiveLinkRole>& Role,
                                                   const FLiveLinkSubjectFrameData& InFrameData,
                                                   FLiveLinkBlueprintDataStruct& OutBlueprintData) const
{
    if (Role == ULiveLinkTransformRole::StaticClass())
    {
        const FLiveLinkTransformFrameData* TransformData = InFrameData.FrameData.Cast<FLiveLinkTransformFrameData>();
        if (TransformData)
        {
            FLiveLinkTransformFrameData WavingData = *TransformData;
            // 使用世界时间计算正弦波偏移
            float TimeOffset = FMath::Sin(FPlatformTime::Seconds() * WaveFrequency) * WaveAmplitude;
            WavingData.Transform.AddToTranslation(FVector(0.f, 0.f, TimeOffset));

            OutBlueprintData.FrameData.InitializeWith(FLiveLinkTransformFrameData::StaticStruct(), &WavingData);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLinkInterface` | Live Link 的核心接口定义，包括角色、主题、帧数据等基础类型。 |
| `LiveLinkMessageBusFramework` | 实现基于消息总线（Message Bus）的 Live Link 数据传输协议。 |
| `LiveLink` | Live Link 的核心运行时逻辑，包括主题管理、数据路由等。 |
| `LiveLinkComponents` | 提供用于在场景中消费 Live Link 数据的组件（如控制器）。 |
| `LiveLinkEditor` | 提供编辑器内的 UI，如 Live Link 面板、主题浏览器等。 |
| `LiveLinkMovieScene` | 将 Live Link 数据集成到 Sequencer 中，用于录制和回放。 |
| `LiveLinkGraphNode` | 提供用于蓝图虚拟主题的图表节点。 |
| `LiveLinkMultiUser` | 支持多用户编辑环境下的 Live Link 数据同步。 |
| `LiveLinkSequencer` | 提供 Sequencer 中录制 Live Link 数据的轨道录制器。 |

## 维护状态

### 近期更新

- `de838a477a04` Move ProcessRecordedTimes to TakesCore. This allows the function to be used in TakeRecorder in a follow-up change.
  *（将录制时间处理功能移至 TakesCore 模块，为后续在 TakeRecorder 中使用做准备。）*
- `2057280165b3` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
  *（使用工具更新头文件，确保 DLL 导出符号正确。）*
- `b827fbc03aa6` Take Recorder
  *（与 Take Recorder 功能相关的提交。）*

### 维护评价

Live Link 是一个**成熟且活跃维护**的核心动画/虚拟制片插件。它自 2017 年创建以来，一直是虚幻引擎实时数据流的标准解决方案。尽管标记为实验性（`IsBetaVersion=true`），但其功能非常稳定，并被广泛应用于大型项目中。近期的提交显示 Epic 仍在持续对其进行优化和功能整合（如与 Take Recorder 的深度集成）。**强烈推荐**在任何需要实时数据接入的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/LiveLink/Tests)