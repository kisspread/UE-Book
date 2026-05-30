# Lens Component

> Implements the Lens Component for adding distortion to a cinematic camera

| 属性 | 值 |
|---|---|
| 中文名 | 镜头畸变组件 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LensComponent` (Runtime), `LensComponentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LensComponent) | |

## 用途

LensComponent 是一个从 CameraCalibrationCore 插件中分离出来的独立组件，其核心功能是**将相机标定数据（镜头畸变、焦距等）以组件形式应用到电影摄像机上**。

该插件解决了在虚拟制片流程中，需要将真实相机或虚拟相机的光学畸变效果实时应用到场景渲染视图中的问题。它允许用户通过组件化的方式，灵活地将镜头标定文件（`.lens`）中存储的畸变数据应用到摄像机Actor上，从而在实时渲染或最终渲染中模拟真实镜头的光学特性。它通过 LiveLink 等数据流接收数据，并能在编辑器中提供预览。

## 使用场景

- **虚拟制片 (Virtual Production)**：在 LED Volume 拍摄中，需要将主摄像机的真实镜头畸变匹配到虚拟场景中，以保证前景和背景的透视与畸变一致。
- **电影级渲染**：在过场动画或最终渲染中，需要为虚拟摄像机添加特定的、已标定的镜头畸变效果，以匹配实拍素材的镜头特征。
- **实时预览与调整**：在编辑器中，通过组件属性快速预览和调整镜头畸变效果，无需进入播放模式。
- **数据驱动的镜头切换**：通过切换组件引用的镜头资产（`.lens`文件），可以快速在不同镜头型号间切换畸变效果。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `LensComponent` | Runtime | 核心运行时模块，定义 `ULensComponent` 及相关的数据处理、畸变应用逻辑，是插件功能的主体。 |
| `LensComponentEditor` | Editor | 编辑器模块，提供组件的自定义属性面板、资产选择器等编辑器内交互功能。 |

## 蓝图用法

`ULensComponent` 是主要的蓝图接口类，用于挂载到电影摄像机上并配置畸变效果。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Lens File` | 设置要应用的镜头资产文件（`.lens`），该文件包含畸变、焦距等标定数据。 | `ULensComponent` |
| `Get Lens File` | 获取当前组件引用的镜头资产文件。 | `ULensComponent` |
| `Set Distortion Source` | 设置畸变数据的来源模式，例如使用镜头文件数据或通过LiveLink接收。 | `ULensComponent` |
| `Get Distortion State` | 获取当前的畸变状态（包含畸变参数等）。 | `ULensComponent` |
| `Apply Distortion` | (内部逻辑) 根据当前配置，将畸变应用到场景视图中。 | `ULensComponent` |

### 使用示例（蓝图描述）

1.  **添加组件**：在电影摄像机 (`CineCameraActor`) 的蓝图或实例上，添加 `LensComponent`。
2.  **指定镜头资产**：在 `LensComponent` 的细节面板中，通过 `Lens File` 属性选择一个预先标定好的 `.lens` 文件。
3.  **选择畸变来源**：设置 `Distortion Source`。若使用静态文件数据，选择 `LensFile`；若需从外部设备（如跟踪系统）实时获取数据，选择 `LiveLink`。
4.  **配置渲染模式**：设置 `Distortion Rendering Mode`，通常使用默认的 `SceneViewExtension` 模式以获得最佳效果。
5.  **查看效果**：在场景中，摄像机视图将自动应用所选镜头的畸变效果。

## C++ 用法

### 头文件引入

```cpp
#include "LensComponent.h"
```

### 基本用法

在 C++ 中动态创建和配置 `ULensComponent`。
*来源参考: 模块文档 `LensComponent.md`*

```cpp
// 假设在某个 Actor 或 Component 的 BeginPlay 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 动态创建一个镜头组件
    ULensComponent* LensComp = NewObject<ULensComponent>(this, TEXT("MyLensComp"));
    LensComp->RegisterComponent();

    // 加载镜头资产
    ULensFile* LensFile = LoadObject<ULensFile>(nullptr, TEXT("/Game/Path/To/MyLens.LensFile"));
    if (LensFile)
    {
        // 设置镜头组件使用的镜头文件
        LensComp->SetLensFile(LensFile);
    }

    // 设置畸变来源为使用镜头文件数据
    LensComp->SetDistortionSource(ELensDistortionSource::LensFile);
}
```

### 进阶用法

结合 `LensDistortion` 组件进行更底层的畸变效果控制。
*来源参考: 测试用例逻辑推断*

```cpp
// 在某些需要直接控制畸变参数的场景下
void ApplyCustomDistortion(ULensComponent* LensComponent)
{
    // 从镜头组件获取当前的畸变状态/参数
    FLensDistortionState CurrentDistortionState = LensComponent->GetDistortionState();

    // 可以对 CurrentDistortionState 中的参数进行修改或混合
    // 例如，插值到另一个目标状态
    FLensDistortionState TargetDistortionState = GetSomeTargetState();
    CurrentDistortionState = FLensDistortionState::Lerp(CurrentDistortionState, TargetDistortionState, 0.5f);

    // 将修改后的状态设置回去，触发视图更新
    LensComponent->SetDistortionState(CurrentDistortionState);
}
```

## Demo 示例

一个可运行的最小示例，展示如何用 C++ 创建一个带有镜头组件的电影摄像机 Actor。
*注意：需要确保项目已启用 `LensComponent` 和 `CameraCalibrationCore` 插件。*

```cpp
// MyLensCameraActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyLensCameraActor.generated.h"

class UCineCameraComponent;
class ULensComponent;
class ULensFile;

UCLASS()
class AMyLensCameraActor : public AActor
{
    GENERATED_BODY()

public:
    AMyLensCameraActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera", meta = (AllowPrivateAccess = "true"))
    UCineCameraComponent* CameraComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera", meta = (AllowPrivateAccess = "true"))
    ULensComponent* LensComponent;

    UPROPERTY(EditDefaultsOnly, Category = "Camera")
    TSoftObjectPtr<ULensFile> DefaultLensFile;
};
```

```cpp
// MyLensCameraActor.cpp
#include "MyLensCameraActor.h"
#include "CineCameraComponent.h"
#include "LensComponent.h"
#include "LensFile.h"

AMyLensCameraActor::AMyLensCameraActor()
{
    // 创建根组件和电影摄像机组件
    CameraComponent = CreateDefaultSubobject<UCineCameraComponent>(TEXT("CineCamera"));
    RootComponent = CameraComponent;

    // 创建镜头组件，并附加到摄像机上
    LensComponent = CreateDefaultSubobject<ULensComponent>(TEXT("LensDistortion"));
    LensComponent->SetupAttachment(CameraComponent);
}

void AMyLensCameraActor::BeginPlay()
{
    Super::BeginPlay();

    // 异步或同步加载镜头资产
    if (!DefaultLensFile.IsNull())
    {
        ULensFile* LoadedLensFile = DefaultLensFile.LoadSynchronous();
        if (LoadedLensFile)
        {
            LensComponent->SetLensFile(LoadedLensFile);
            // 设置畸变来源为镜头文件
            LensComponent->SetDistortionSource(ELensDistortionSource::LensFile);
        }
    }
}
```

## 模块依赖

此插件依赖以下插件/模块，因此你的项目或模块在使用 `LensComponent` 时，也需要声明对它们的依赖。

| 模块/插件 | 用途 |
|---|---|
| `CameraCalibrationCore` | 核心依赖。提供镜头资产(`ULensFile`)、标定数据结构(`FLensDistortionState`)等基础类和功能。 |
| `LiveLink` | 用于通过 LiveLink 协议从外部设备（如跟踪系统）实时接收镜头畸变数据。 |
| `Takes` | 与虚拟制片的工作流程集成，用于在 Take（镜头录制）过程中管理和应用镜头数据。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-15 | `d7870116` | LensDistortion: Add new lens distortion option to apply distortion as a scene view extension pass af | 新增镜头畸变渲染选项，支持作为场景视图扩展通道后处理应用畸变。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范更新。 |
| 2025-09-02 | `006bdf67` | CameraCalibration: Add default distortion rendering mode option. | 新增默认的畸变渲染模式配置选项。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 代码生成优化，提升编译性能。 |
| 2025-06-13 | `6bb19da9` | LensComponent: Make the Lens Distortion Scene View Extension the default distortion rendering mode. | 将镜头畸变场景视图扩展设为默认的畸变渲染模式。 |

### 维护评价

**活跃维护中**。该插件创建于2023年底，从最近的提交记录看，开发活动持续至今。过去一年内有多次实质性更新，主要集中在**优化畸变渲染管线**（引入新的后处理通道模式并将其设为默认）和**完善配置选项**上。这表明该插件正在积极演进，以适应虚拟制片中更复杂的渲染需求。

由于插件本身标记为 `IsBetaVersion: true` 且 `Hidden: true`，属于**实验性**功能，可能在未来版本中会有API变更或进一步整合。目前阶段，推荐在虚拟制片相关项目中**谨慎使用和测试**，但不适合用于追求稳定性的最终发布产品。

## 相关链接

- [源码目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LensComponent)
- (官方文档链接暂缺，.uplugin中未提供 `DocsURL`)
- [相关测试用例参考路径] (可查阅 `Engine/Plugins/VirtualProduction/CameraCalibrationCore` 下的测试，或通过 `IMPLEMENT_SIMPLE_AUTOMATION_TEST` 搜索 `LensComponent` 关键词)