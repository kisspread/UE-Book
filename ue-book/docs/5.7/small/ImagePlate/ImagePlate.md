# Image Plate

> Actor and component types that provide a camera-aligned image plate

| 属性 | 值 |
|---|---|
| 中文名 | 图像板 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `ImagePlate` (Runtime), `ImagePlateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate) | |

---

## 用途

Image Plate 插件提供一个始终面向摄像机的 2D 图像板（Billboard）组件，用于在场景中渲染平面图像、材质或动态纹理序列。其核心特点是：

- 可自动适配摄像机视锥体，**填充屏幕**（`bFillScreen` 开启时基于活跃摄像机的镜头参数计算大小）。
- 支持**固定尺寸**，不受摄像机距离影响。
- 可通过 `UImagePlateFileSequence` 播放**图像序列**（类似翻页动画或视频帧），并带有异步预缓存机制。
- 基于 `UPrimitiveComponent` 实现，与渲染管线深度集成，适合高帧率、低延迟的 2D 覆盖场景。

**为什么存在？**  
在虚幻引擎中，若需要展示始终面向摄像头的 2D 内容（如 HUD 元素、广告牌、电影画幅、序列帧动画），原生没有专门的组件。Image Plate 填补了这一空白，提供开箱即用的相机对齐、填充屏幕、图像序列播放等能力，且支持蓝图与 C++ 灵活控制。

---

## 使用场景

- 制作**2D 覆盖层**：如游戏中角色头顶的 ID 标签、任务提示板。
- **电影级场景**：使用图像序列模拟老式胶片效果或过渡动画。
- **UI 原型**：快速在场景中放置带材质的平面替代 UMG 控件，尤其在 VR/AR 中需要世界空间的 UI。
- **虚拟制片**：将外部素材（如 LED 墙输出）映射到始终面向摄像机的板上。

---

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Image Plate` | 设置图像板的完整参数（材质、纹理参数名、填充方式、尺寸等） | `UImagePlateComponent` |
| `Get Plate` | 获取当前图像板参数 `FImagePlateParameters` | `UImagePlateComponent` |

#### `FImagePlateParameters` 关键属性（蓝图可读写）

| 属性 | 说明 |
|---|---|
| `Material` | 用于渲染的材质（可留空，内部会生成动态材质实例） |
| `Texture Parameter Name` | 材质中用于替换 `RenderTexture` 的参数名称 |
| `b Fill Screen` | 是否基于摄像机自动填充屏幕 |
| `Fill Screen Amount` | 填充倍数（1.0 = 完全填充，0.5 = 填一半） |
| `Fixed Size` | 固定尺寸（当 `bFillScreen` 关闭时生效） |
| `Render Texture` | 运行时渲染的纹理（由外部赋值或序列帧驱动） |

### 使用示例（蓝图描述）

1. 在关卡蓝图或 Actor 蓝图中获取 `Image Plate Component`。
2. 调用 `Set Image Plate` 节点，输入：
   - `Material`：选择任意带纹理参数的材质（如 `MI_ImagePlate` 提供的默认材质）。
   - `Texture Parameter Name`：输入材质中的参数名，例如 `"Texture2D"`。
   - 勾选 `b Fill Screen` 并设置 `Fill Screen Amount` 为 `(1.0, 1.0)`。
3. 运行游戏，图像板将自动适配当前摄像机的视锥，始终正对屏幕。

---

## C++ 用法

### 头文件引入

```cpp
#include "ImagePlateComponent.h"
#include "ImagePlate.h"
#include "ImagePlateFileSequence.h"
```

### 基本用法

从测试文件和源码提取，创建一个始终面向摄像机的图像板：

```cpp
// 在 Actor 的构造函数或 BeginPlay 中
#include "ImagePlateComponent.h"

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建 ImagePlate 组件（若 Actor 未自带）
    UImagePlateComponent* PlateComp = NewObject<UImagePlateComponent>(this);
    PlateComp->RegisterComponent();

    // 准备参数
    FImagePlateParameters Params;
    Params.Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/ImagePlate/MI_ImagePlate"));
    Params.TextureParameterName = FName("Texture2D");
    Params.bFillScreen = true;
    Params.FillScreenAmount = FVector2D(0.8f, 0.6f);

    PlateComp->SetImagePlate(Params);
}
```

### 进阶用法

播放图像序列（使用 `UImagePlateFileSequence`）：

```cpp
#include "ImagePlateFileSequence.h"
#include "Async/Async.h"

// 创建序列对象
UImagePlateFileSequence* Sequence = NewObject<UImagePlateFileSequence>();
Sequence->SequencePath.Path = TEXT("/Game/MySequence");
Sequence->FileWildcard = TEXT("*.exr");
Sequence->Framerate = 24.0f;

// 获取异步缓存
FImagePlateAsyncCache Cache = Sequence->GetAsyncCache();

// 在 Tick 中请求帧
float Time = 0.0f; // 当前播放时间（秒）
auto FrameFuture = Cache.RequestFrame(Time, 2, 2); // 预缓冲前2帧和后2帧

FrameFuture.OnThen([PlateComp](TFuture<FImagePlateSourceFrame> Future) {
    if (Future.IsValid())
    {
        FImagePlateSourceFrame Frame = Future.Get();
        // 将帧数据复制到组件的渲染纹理
        Frame.CopyTo(PlateComp->GetPlate().RenderTexture);
    }
});
```

> 源码参考：`Source/ImagePlate/Public/ImagePlateFileSequence.h` 及 `Private/*.cpp`

---

## Demo 示例

以下是一个完整的 Actor 派生类，在运行时创建一个填充屏幕的图像板并显示一个动态纹理（此处仅演示基本设置，实际纹理需外部提供）。

### MyImagePlateActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyImagePlateActor.generated.h"

class UImagePlateComponent;

UCLASS()
class AMYIMAGEPLATEACTOR : public AActor
{
    GENERATED_BODY()

public:
    AMYIMAGEPLATEACTOR();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    UImagePlateComponent* ImagePlateComp;
};
```

### MyImagePlateActor.cpp

```cpp
#include "MyImagePlateActor.h"
#include "ImagePlateComponent.h"

AMYIMAGEPLATEACTOR::AMYIMAGEPLATEACTOR()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建根组件
    RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));

    // 创建 ImagePlate 组件并附加到根
    ImagePlateComp = CreateDefaultSubobject<UImagePlateComponent>(TEXT("ImagePlate"));
    ImagePlateComp->SetupAttachment(RootComponent);
}

void AMYIMAGEPLATEACTOR::BeginPlay()
{
    Super::BeginPlay();

    // 设置参数：填充屏幕 80%
    FImagePlateParameters Params;
    Params.Material = LoadObject<UMaterialInterface>(nullptr, TEXT("/ImagePlate/MI_ImagePlate"));
    Params.TextureParameterName = FName("Texture2D");
    Params.bFillScreen = true;
    Params.FillScreenAmount = FVector2D(0.8f, 0.8f);

    ImagePlateComp->SetImagePlate(Params);
}
```

> 该示例依赖 `ImagePlate` 模块及默认材质 `/ImagePlate/MI_ImagePlate`（插件提供），运行即可看到始终面向摄像机的图像板。

---

## 模块依赖

本插件运行时模块 `ImagePlate` 的依赖如下（仅列出独特项）：

| 模块 | 用途 |
|---|---|
| `Slate` | 使用 `FSlateTextureData` 处理图像帧数据 |
| `SlateCore` | Slate 基础类型引用 |

> 其余依赖为引擎标准模块（Core, CoreUObject, Engine 等），不逐一列举。  
> 编辑器模块 `ImagePlateEditor` 额外依赖 `UnrealEd`, `PropertyEditor` 等。

---

## 维护状态

### 近期更新

- 2025-08-26 `ce867df3` — [HWRT] Refactored FRayTracingInstanceCollector to handle multiple views instead of a single reference（引擎级重构）
- 2025-06-18 `08316dbb` — Cache the ShaderPlatform inside MaterialResource, derive the FeatureLevel from that ShaderPlatform（渲染优化）
- 2025-04-23 `939cc6e5` — Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv（构建系统适配）
- 2025-04-14 `5eb43fcd` — [Log/2] Warn when runtime verbosity level is capped by compiled-time verbosity level of log category（日志改进）
- 2025-03-13 `b059f7b4` — Fix trivial unreachable code warnings.（首次创建前清理）

### 维护评价

- **创建时间**：2025 年 3 月，距今约 1 年。
- **最近更新频率和内容**：最近提交均非插件特有功能更新，而是引擎级重构和适配。插件本身自创建后无实质性功能迭代。
- **活跃度**：**维护不活跃**。插件仍处于实验性阶段（`IsBetaVersion=true`），可能随引擎迭代而更新，但无独立开发计划。
- **已知问题**：实验性，API 可能变化；当前版本功能有限（仅基础图像板 + 文件序列缓存）。
- **推荐使用**：在需要简单相机对齐图像板的场景下可用，但建议关注后续引擎版本更新，避免 API 变更风险。

---

## 相关链接

- [源码（根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate)
- [插件描述（.uplugin）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/ImagePlate/ImagePlate.uplugin)
- [Runtime 模块头文件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate/Source/ImagePlate/Public)
- [Editor 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ImagePlate/Source/ImagePlateEditor/)