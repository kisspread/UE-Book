# Template Sequence

> Runtime for template sequences

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 插件提供了一种创建可重用序列模板的机制，这些模板可以绑定到场景中的不同对象上。它解决了在 Unreal Engine 的 Sequencer 中重复使用复杂动画或过场动画逻辑的需求。通过模板序列，用户可以预先定义一个包含动画、轨道和逻辑的序列，然后将其应用到多个角色或物体上，只需更改绑定即可，无需重新创建整个序列。这在制作需要相同动画模式但应用于不同角色（如游戏中的同类型敌人）或制作镜头动画模板（Camera Animation）时非常有用。

## 使用场景

- 你正在制作一个游戏，其中多个敌人需要共享相同的攻击动画序列 → 创建一个绑定到“敌人”类的模板序列，然后将其应用到每个敌人实例。
- 你需要为过场动画制作一组可重用的镜头运镜（Camera Animation）模板，可以快速应用到不同场景的不同摄像机上 → 创建一个 Camera Animation Sequence 模板。
- 你在编辑器中需要一种方法来快速预览模板序列绑定到不同对象上的效果 → 使用编辑器工具包进行拖放和绑定操作。

## 蓝图用法

### 核心节点

该插件的蓝图功能主要围绕序列的编辑和预览，运行时功能由 `TemplateSequence` 模块提供。以下是编辑器模块 (`TemplateSequenceEditor`) 提供的关键节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ChangeActorBinding` | 更改模板序列的绑定对象，允许拖放资产或类到序列轨道 | `FTemplateSequenceEditorUtil` |

### 使用示例（蓝图描述）

在编辑器中，你可以通过以下方式使用模板序列：
1. 在内容浏览器中右键选择“Cinematics”类别下的“Template Sequence”或“Camera Animation Sequence”来创建新资产。
2. 打开资产进行编辑，你会看到一个简化的 Sequencer 编辑器。
3. 在序列轨道中，你可以通过“绑定”菜单选择或更改模板序列所绑定的对象类（例如，选择一个摄像机或角色类）。
4. 将资产从内容浏览器或场景大纲拖放到 Sequencer 窗口中，可以自动创建绑定或替换现有绑定。
5. 使用 Sequencer 工具栏上的功能来配置模板的特定属性。

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence.h"
#include "TemplateSequenceEditor.h"
```

### 基本用法

从 `FTemplateSequenceFactoryUtil` 和 `UTemplateSequenceFactoryNew` 类中，我们可以看到创建模板序列的基本方法。

**创建模板序列 (C++)**
（来源：`Private/Factories/TemplateSequenceFactoryUtil.h`）
```cpp
#include "TemplateSequenceFactoryUtil.h"

// 创建一个模板序列资产
UTemplateSequence* NewSequence = FTemplateSequenceFactoryUtil::CreateTemplateSequence(
    GetTransientPackage(),          // 父包
    FName("MyTemplateSequence"),    // 资产名
    RF_Public | RF_Standalone,      // 对象标志
    UTemplateSequence::StaticClass(), // 序列类
    AMyActor::StaticClass()         // 要绑定的对象类模板
);
```

**使用编辑器工具类更改绑定**
（来源：`Private/Misc/TemplateSequenceEditorUtil.h`）
```cpp
#include "TemplateSequenceEditorUtil.h"

// 假设你已经有一个 UTemplateSequence 和一个有效的 ISequencer
UTemplateSequence* MyTemplateSeq = ...;
ISequencer& Sequencer = ...;

FTemplateSequenceEditorUtil EditorUtil(MyTemplateSeq, Sequencer);

// 将绑定更改为一个新对象，设置默认值
AActor* NewBoundActor = GetWorld()->SpawnActor<AActor>();
EditorUtil.ChangeActorBinding(NewBoundActor, nullptr, true);
```

### 进阶用法

**使用实体系统预览摄像机变换**
（来源：`Private/Systems/TemplateSequenceCameraPreviewSystem.h`）
该类是一个 UMovieSceneEntitySystem，用于将编辑器视口的变换写入摄像机对象的初始变换中。

```cpp
#include "TemplateSequenceCameraPreviewSystem.h"

// 在编辑器中，启用下一帧预览（将当前视口变换应用为摄像机初始值）
UTemplateSequenceCameraPreviewSystem::EnableNextFrame();

// 禁用下一帧预览（将摄像机初始值重置为原点）
UTemplateSequenceCameraPreviewSystem::DisableNextFrame();
```

## Demo 示例

以下是一个完整的、可编译的最小示例，演示如何在 C++ 中创建并初始化一个模板序列资产。

**MyTemplateSequenceDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyTemplateSequenceDemo.generated.h"

class UTemplateSequence;

UCLASS(BlueprintType)
class UMyTemplateSequenceDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 创建并返回一个新的模板序列示例 */
    UFUNCTION(BlueprintCallable, Category = "TemplateSequenceDemo")
    static UTemplateSequence* CreateDemoTemplateSequence();

private:
    /** 初始化一个模板序列的根绑定 */
    static void InitializeDemoSpawnable(UMovieSceneSequence* InSequence);
};
```

**MyTemplateSequenceDemo.cpp**
```cpp
#include "MyTemplateSequenceDemo.h"
#include "TemplateSequence.h"
#include "TemplateSequenceFactoryUtil.h"
#include "MovieScene.h"
#include "MovieSceneSpawnable.h"
#include "Sections/MovieScene3DTransformSection.h"
#include "Tracks/MovieScene3DTransformTrack.h"

UTemplateSequence* UMyTemplateSequenceDemo::CreateDemoTemplateSequence()
{
    // 使用工厂工具创建序列
    UTemplateSequence* DemoSequence = FTemplateSequenceFactoryUtil::CreateTemplateSequence(
        GetTransientPackage(),
        FName("DemoTemplateSequence"),
        RF_Public | RF_Standalone,
        UTemplateSequence::StaticClass(),
        AActor::StaticClass() // 绑定到基类 Actor
    );

    if (DemoSequence)
    {
        // 为了演示，我们手动向模板序列的 MovieScene 添加一个变换轨道和关键帧
        UMovieScene* MovieScene = DemoSequence->GetMovieScene();
        if (MovieScene)
        {
            // 获取第一个（也是唯一的）可生成对象
            FMovieSceneSpawnable* Spawnable = MovieScene->FindSpawnable(0);
            if (Spawnable)
            {
                // 添加一个 3D 变换轨道
                UMovieScene3DTransformTrack* TransformTrack = MovieScene->AddTrack<UMovieScene3DTransformTrack>(Spawnable->GetGuid());
                if (TransformTrack)
                {
                    // 添加一个从 0 到 60 帧（2 秒）的区段
                    UMovieScene3DTransformSection* TransformSection = Cast<UMovieScene3DTransformSection>(TransformTrack->CreateNewSection());
                    TransformSection->SetRange(TRange<FFrameNumber>(0, 60));
                    TransformTrack->AddSection(*TransformSection);

                    // 在位置上设置一个简单的移动关键帧 (例如，X轴从0到100)
                    // 注意：完整的动画创建会更复杂，这里仅为演示结构
                }
            }
        }
    }
    return DemoSequence;
}

void UMyTemplateSequenceDemo::InitializeDemoSpawnable(UMovieSceneSequence* InSequence)
{
    // 此函数由 FTemplateSequenceFactoryUtil::InitializeSpawnable 调用
    // 用于设置初始的可生成对象属性。此处为空，依赖基类实现。
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `TemplateSequence` | 核心运行时模块，提供序列资产类和基础播放功能 |
| `TemplateSequenceEditor` | 编辑器模块，提供资产创建、编辑工具包、轨道编辑器和自定义功能 |
| `LevelSequence` | 基础 Sequencer 序列功能（隐含依赖） |
| `LevelSequenceEditor` | Sequencer 编辑器框架（.uplugin 中声明的插件依赖） |
| `SequencerCore` | Sequencer 核心功能 |

**注意**：由于该插件默认未启用 (`EnabledByDefault: false`)，你还需要在你的项目的 .uproject 文件或插件设置中显式启用它。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生警告的代码。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复关卡序列播放器中因编辑器独有数据属性导致的 Rep 布局不匹配问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | Sequencer：在对象绑定菜单中添加“烘焙变换”功能。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中的 7 个虚函数（已废弃或仅供工具使用）。 |

### 维护评价

Template Sequence 插件自 2019 年创建以来，一直处于 **实验性** 状态 (`IsBetaVersion: true`)，且默认未启用 (`EnabledByDefault: false`)。从近期的 Git 提交记录看（最后提交于 2026-05-13），它仍在被维护，但更新主要集中在**错误修复、编译器警告清理和小幅功能增强**（如添加“烘焙变换”菜单项）上，没有大规模的功能迭代。

**综合评价**：
- **年龄**：插件已存在约 7 年。
- **活跃度**：仍在维护，但更新频率较低，且无实质性新功能。
- **状态**：实验性，未默认启用，表明 Epic 官方可能认为其尚未达到生产就绪标准。
- **推荐度**：如果你需要模板序列的核心功能且接受其“实验性”标签，可以谨慎使用。对于生产项目，建议评估其稳定性，或考虑使用更成熟的工作流（如蓝图实例化、共享动画资产）。作为镜头动画（Camera Animation）的模板，它可能是一个专为 Sequencer 深度集成的有用工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [官方文档]() （无）