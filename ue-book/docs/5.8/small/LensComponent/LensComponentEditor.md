# Lens Component

> Implements the Lens Component for adding distortion to a cinematic camera

| 属性 | 值 |
|---|---|
| 中文名 | 镜头组件 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LensComponent` (Runtime), `LensComponentEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-12-21 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LensComponent) | |

## 用途

LensComponent 是 Camera Calibration（相机标定）系统的一个核心组件，专注于为电影摄像机（Cinematic Camera）添加精确的镜头畸变（Distortion）效果。它的主要目的是将镜头标定数据（如畸变参数、焦距、主点偏移等）实时应用到虚拟摄像机的渲染视图中，从而确保虚拟摄像机的成像特性与真实物理镜头完全匹配。

该插件解决了在虚拟制片（Virtual Production）工作流中，数字内容与实拍镜头在光学特性上保持一致的核心问题。它通过读取 `LensFile`（镜头文件）资产中的标定数据，并将其转化为可应用于摄像机组件的畸变效果。

**为什么存在？** 它将原本集成在 `CameraCalibrationCore` 中的镜头组件功能独立出来，形成了一个更专注、可独立管理的插件，便于维护和按需集成。

## 使用场景

- 你正在使用 nDisplay 或其他技术进行虚拟制片，需要让虚拟摄像机的畸变效果与现场实拍摄像机的畸变完全匹配，以实现无缝合成。
- 你需要为电影摄像机创建具有真实光学特性的数字孪生，用于前期预览（Previz）或后期合成。
- 你需要使用 `LiveLink` 从外部设备（如跟踪系统）接收实时的镜头参数，并应用于虚拟摄像机。
- 你需要在 `Sequencer` 中录制和回放真实的镜头畸变变化过程。

## 蓝图用法

LensComponent 主要通过其组件属性进行配置，直接在蓝图中暴露的节点相对较少。其核心交互通常发生在编辑器属性面板和 Sequencer 轨道中。

### 核心节点（LensComponent 组件属性）

根据 `LensComponent` 模块（未提供详细头文件，但可从Editor模块的引用推断）和 `UMovieSceneLensComponentSection` 的属性：

| 属性 | 说明 | 类型 |
|---|---|---|
| `bReapplyNodalOffset` | 是否每帧重新评估并应用节点偏移（Nodal Offset） | `bool` |
| `OverrideLensFile` | 在回放期间，用于替代缓存 `LensFile` 的资产引用 | `ULensFile` |

**注意**：LensComponent 的核心配置（如选择的镜头模型、使用的镜头文件）通常通过其组件属性面板设置，而非直接通过蓝图节点操作。

### Sequencer 集成

LensComponent 提供了与 Sequencer 深度集成的轨道编辑器，允许你在时间线上录制和控制镜头畸变参数的变化。

**录制**：通过 `UMovieSceneLensComponentTrackRecorder`，可以在 Sequencer 中为 LensComponent 轨道录制关键帧，将每一帧的畸变状态（畸变参数、FxFy、主点等）记录下来。

**编辑**：在 Sequencer 中，你可以手动为 `UMovieSceneLensComponentTrack` 添加关键帧，调整畸变参数等。

## C++ 用法

LensComponent 的主要使用方式是作为组件添加到摄像机 Actor 上，并通过其公共接口配置镜头数据。

### 头文件引入

```cpp
// 需要依赖 LensComponent 模块
#include "LensComponent.h"
// 如果涉及序列器操作
#include "MovieSceneLensComponentSection.h"
```

### 基本用法

以下是如何在 C++ 中访问和配置一个已存在的 `ULensComponent` 实例（通常从 Actor 或 Component 获取）。

```cpp
// 假设我们已经获取了一个 ULensComponent 指针
ULensComponent* MyLensComponent = ...;

// 设置或获取其使用的镜头文件（ULensFile）
ULensFile* NewLensFile = ...; // 从资产加载或引用
MyLensComponent->SetLensFile(NewLensFile); // 假设有这样的接口

// 检查是否需要每帧重新应用节点偏移
bool bShouldReapply = MyLensComponent->bReapplyNodalOffset;
```

*注意：`ULensComponent` 的具体公共API未在提供的代码片段中展示，上述代码为基于常见组件模式的推断。实际使用应参考 `LensComponent.h` 的完整头文件。*

### 进阶用法：操作 Sequencer 中的镜头关键帧

当需要在运行时或编辑器工具中程序化地为镜头组件录制动画时，会用到 `UMovieSceneLensComponentSection`。

```cpp
// 1. 获取或创建一个 Sequencer 序列和对应的 Lens Component 轨道
// 2. 获取或创建该轨道上的 Section
UMovieSceneLensComponentSection* LensSection = ...;

// 3. 初始化 Section，将其绑定到特定的 LensComponent
if (LensSection && MyLensComponent)
{
    LensSection->Initialize(MyLensComponent);
}

// 4. 在特定时间点（帧）录制当前 LensComponent 的状态
FFrameNumber FrameToRecord(100); // 第100帧
LensSection->RecordFrame(FrameToRecord);

// 5. 完成录制后，减少关键帧数据（优化）
LensSection->Finalize();
```

*代码逻辑参考自 `UMovieSceneLensComponentSection` 的类声明。*

## Demo 示例

以下示例展示了一个在 BeginPlay 时获取自身 LensComponent 并执行基本操作的 Actor。

**LensDemoActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "LensDemoActor.generated.h"

class ULensComponent;

UCLASS()
class ALensDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ALensDemoActor();

protected:
    virtual void BeginPlay() override;

private:
    /** 组件引用，通常在蓝图或编辑器中设置 */
    UPROPERTY(VisibleAnywhere)
    ULensComponent* LensComponent;
};
```

**LensDemoActor.cpp**
```cpp
#include "LensDemoActor.h"
#include "LensComponent.h" // 关键头文件

ALensDemoActor::ALensDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    // 假设 LensComponent 是在蓝图中添加到此Actor上的，这里仅为变量初始化
    LensComponent = nullptr;
}

void ALensDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (LensComponent)
    {
        UE_LOG(LogTemp, Log, TEXT("LensComponent found. Is applying nodal offset every frame: %s"),
            LensComponent->bReapplyNodalOffset ? TEXT("Yes") : TEXT("No"));

        // 这里可以执行更多操作，例如动态切换镜头文件
        // LensComponent->SetLensFile(...);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("LensComponent not found on actor %s."), *GetName());
    }
}
```

## 模块依赖

使用 LensComponent 插件，你的模块需要依赖其提供的运行时模块。

| 模块 | 用途 |
|---|---|
| `CameraCalibrationCore` | 核心镜头标定数据和功能，LensComponent 的基础 |
| `LiveLink` | 用于接收来自外部设备（如跟踪系统）的实时镜头数据 |
| `Takes` | 用于与虚拟制片的 Take 系统集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-15 | `d7870116` | LensDistortion: Add new lens distortion option to apply distortion as a scene view extension pass af | 为镜头畸变新增了通过场景视图扩展通道应用的选项 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件从 Base.ini 重命名为 Default.ini |
| 2025-09-02 | `006bdf67` | CameraCalibration: Add default distortion rendering mode option. | 为相机标定添加了默认的畸变渲染模式选项 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为生成的 .cpp 文件添加了内联宏，优化编译 |
| 2025-06-13 | `6bb19da9` | LensComponent: Make the Lens Distortion Scene View Extension the default distortion rendering mode. | 将镜头畸变场景视图扩展设为默认的畸变渲染模式 |

### 维护评价

LensComponent 是一个于 2023 年底创建的相对较新的插件，目前标记为实验性（Beta）。从 Git 历史看，它在创建后持续有功能更新和优化（最近一次更新在 2026 年初），**维护活跃**。更新内容集中在改进畸变渲染管线和配置系统上，表明它正在积极开发以满足虚拟制片的需求。

**推荐使用**：如果你的项目涉及高精度的虚拟制片，并且需要将数字摄像机与物理镜头精确匹配，这个插件是必需的。但由于其**实验性**状态和**默认未启用**（`Hidden: true`， `Installed: false`）的特性，在生产环境中使用前应进行充分测试。请注意，它目前仅支持 `LiveLinkHub` 程序。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LensComponent)
- 官方文档：暂无 (DocsURL 为空)
- 测试用例：未在提供的信息中发现标准测试用例文件路径。