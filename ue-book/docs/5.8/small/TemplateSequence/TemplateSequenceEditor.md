# Template Sequence

> Runtime for template sequences（照抄，不翻译）

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

Template Sequence 插件为 Unreal Engine 的 Sequencer 引入了“模板序列”资产。它解决的核心问题是**序列资产的复用与参数化**。

传统的 Level Sequence 资产（如过场动画）绑定了具体的场景对象和 Actor。当需要对同类对象（如多个相机）应用相似的动画时，你需要为每个实例创建并维护几乎相同的序列资产，这非常繁琐。

模板序列（`UTemplateSequence`）允许你创建一个独立于具体对象的“模板”，该模板定义了动画轨道和关键帧数据，但其绑定的对象是一个可配置的“模板对象”（如 `UCameraComponent`）。在 Sequencer 中，你可以将这个模板序列应用到不同的实际对象上，从而实现动画的复用。它本质上是 Sequencer 系统中的一种**可复用的、参数化的动画蓝图**。

此外，该插件还专门针对相机工作流提供了 `UCameraAnimationSequence`，这是一个专门用于相机动画的模板序列子类，极大地简化了相机抖动、推拉摇移等复杂镜头动画的制作与管理。

## 使用场景

- 你正在制作大量镜头动画，希望为不同场景的相机复用相同的运镜（如标准的推进、环绕镜头）。
- 你需要创建一个通用的“摇晃”动画模板，并将其应用到游戏内的手持相机、爆炸效果的摄像机等多个实例上。
- 你在开发一个包含多个过场动画的游戏，其中某些动画模式（如角色特写对话）需要应用于不同角色，但动画逻辑相同。
- 你希望利用 Sequencer 强大的关键帧编辑功能，但不想为每个动画资产重复设置轨道结构。

## 蓝图用法

此插件主要提供编辑器资产类型和 Sequencer 扩展，其运行时模块（`TemplateSequence`）主要用于序列的播放和解析，蓝图节点通常由 Sequencer 在播放时自动调用，不直接对外暴露复杂的调用接口。用户主要通过编辑器界面使用。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UTemplateSequence` | 基础模板序列资产，可绑定任意对象类型。 |
| `UCameraAnimationSequence` | 专用的相机动画序列资产，继承自 `UTemplateSequence`，专为相机设计。 |

### 编辑器中的使用

1.  **创建资产**：在内容浏览器中右键，选择“动画”下的“模板序列”或“相机动画序列”。
2.  **编辑模板**：双击打开资产，在 Sequencer 中像编辑普通序列一样添加轨道和关键帧。绑定的对象是模板对象。
3.  **应用模板**：在需要使用该动画的 Sequencer 中，为目标对象（如相机Actor）的轨道添加一个“模板序列”段。
4.  **指定资产**：在添加的段上，通过资产选择器指定之前创建的 `UTemplateSequence` 或 `UCameraAnimationSequence` 资产。
5.  **预览与调整**：序列会根据模板数据驱动目标对象。在模板序列编辑器中修改关键帧，所有使用该模板的地方都会更新。

## C++ 用法

C++ 用法主要集中在编辑器扩展、自定义工厂和工具类，用于集成或扩展模板序列的工作流。

### 头文件引入

```cpp
// 引入编辑器模块（用于创建新的编辑器工具）
#include "TemplateSequenceEditorToolkit.h"
// 引入工具类
#include "TemplateSequenceEditorUtil.h"
```

### 基本用法（利用工具类更改绑定）

以下代码片段展示了如何在 Sequencer 编辑器上下文中，将一个模板序列的根对象绑定更改为另一个 Actor。这通常用于编辑器扩展。
*来源：`Private/Misc/TemplateSequenceEditorUtil.h` 与对应 .cpp*

```cpp
// 假设你已经获取到 UTemplateSequence* TemplateSequence 和 ISequencer* Sequencer 实例
FTemplateSequenceEditorUtil EditorUtil(TemplateSequence, *Sequencer);

// 将模板序列的绑定更改为指向 NewActor，并设置默认属性
EditorUtil.ChangeActorBinding(NewActor, nullptr, true);
```

### 进阶用法（创建自定义资产定义）

要使模板序列资产出现在编辑器的右键菜单中，并定义其打开行为，你需要继承 `UAssetDefinition_TemplateSequence`。
*来源：`Private/AssetTools/AssetDefinition_TemplateSequence.h`*

```cpp
#include "AssetDefinition_TemplateSequence.h"

UCLASS()
class UAssetDefinition_MyCustomTemplateSequence : public UAssetDefinition_TemplateSequence
{
    GENERATED_BODY()

public:
    virtual FText GetAssetDisplayName() const override
    {
        return NSLOCTEXT("MyAsset", "DisplayName", "My Custom Template Sequence");
    }

    virtual TSoftClassPtr<UObject> GetAssetClass() const override
    {
        return UMyCustomTemplateSequence::StaticClass();
    }

    // 可以重写 InitializeToolkitParams 来定制打开编辑器时的参数
protected:
    virtual void InitializeToolkitParams(FTemplateSequenceToolkitParams& ToolkitParams) const override
    {
        // 例如，禁止在此类序列中更改绑定
        ToolkitParams.bCanChangeBinding = false;
    }
};
```

## Demo 示例

以下是一个最小化的示例，展示了如何通过 C++ 创建一个运行时可播放的 `UTemplateSequence` 资产，并为其设置一个简单的浮点属性动画。这在自定义资产创建管线或单元测试中很有用。

**MyTemplateSequenceFactory.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Factories/Factory.h"
#include "MyTemplateSequenceFactory.generated.h"

class UTemplateSequence;

UCLASS()
class UMyTemplateSequenceFactory : public UFactory
{
    GENERATED_BODY()

public:
    UMyTemplateSequenceFactory();

    virtual UObject* FactoryCreateNew(UClass* Class, UObject* InParent, FName Name, EObjectFlags Flags, UObject* Context, FFeedbackContext* Warn) override;
};
```

**MyTemplateSequenceFactory.cpp**
```cpp
#include "MyTemplateSequenceFactory.h"
#include "TemplateSequence.h"
#include "MovieScene.h"
#include "MovieSceneFloatTrack.h"
#include "MovieSceneFloatSection.h"
#include "Sections/MovieScenePropertySection.h"

UMyTemplateSequenceFactory::UMyTemplateSequenceFactory()
{
    SupportedClass = UTemplateSequence::StaticClass();
    bCreateNew = true;
    bEditAfterNew = true;
}

UObject* UMyTemplateSequenceFactory::FactoryCreateNew(UClass* Class, UObject* InParent, FName Name, EObjectFlags Flags, UObject* Context, FFeedbackContext* Warn)
{
    UTemplateSequence* NewSequence = NewObject<UTemplateSequence>(InParent, Class, Name, Flags);

    // 1. 初始化序列
    NewSequence->Initialize(NewSequence->GetMovieScene(), NewSequence->GetRootObjectTemplate());

    UMovieScene* MovieScene = NewSequence->GetMovieScene();
    if (MovieScene)
    {
        // 设置序列的播放范围 (0-5 秒，30fps)
        MovieScene->SetPlaybackRange(FFrameRange(0, 150)); // 5秒 * 30帧/秒

        // 2. 为根对象模板添加一个浮点属性轨道（例如，控制某个材质参数的强度）
        // 注意：实际应用中，需要确保对象模板（GetRootObjectTemplate()）拥有该属性。
        FMovieScenePropertyBinding PropertyBinding(FName("SomeFloatProperty"), FName("SomeFloatProperty"));

        UMovieSceneFloatTrack* FloatTrack = MovieScene->AddTrack<UMovieSceneFloatTrack>(FGuid()); // 对应根对象的BindingID
        if (FloatTrack)
        {
            UMovieSceneFloatSection* FloatSection = Cast<UMovieSceneFloatSection>(FloatTrack->CreateNewSection());
            FloatSection->SetRange(FFrameRange(0, 150));

            // 在开始和结束处设置关键帧（例如，从0到1）
            FloatSection->GetChannel().AddLinearKey(FFrameNumber(0), 0.0f);
            FloatSection->GetChannel().AddLinearKey(FFrameNumber(150), 1.0f);

            FloatTrack->AddSection(*FloatSection);
        }
    }

    return NewSequence;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | **必需**。该插件依赖此模块来实现 Sequencer 编辑器内的扩展功能（如轨道编辑器、资产操作）。 |
| `MovieSceneTools` | 提供 Sequencer 框架的核心编辑器工具和类型支持。 |
| `PropertyEditor` | 用于创建和定制资产细节面板（Details Panel）中的属性自定义。 |
| `AssetDefinition` | 用于注册新的资产定义（Asset Definition），控制资产在内容浏览器中的显示和行为。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量隐式转换为浮点数导致的编译器警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式的 `UE_LOG` 宏调用迁移到新的、功能更强大的 `UE_LOGF` 宏。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复了 Level Sequence Player 中由于仅编辑器数据属性导致的网络复制布局不匹配问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在 Sequencer 对象绑定菜单中添加了“烘焙变换”功能。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除了 UObject 中7个已废弃或仅供工具使用的虚函数。 |

### 维护评价

**维护中**。该插件自 2019 年创建，已有约 7 年历史。根据最近的提交记录（截至 2026 年），它仍然在持续接收更新，包括错误修复、代码现代化（如宏迁移）以及功能增强（如烘焙变换）。

- **活跃度**：更新频率不低，平均每年都有多次提交，表明 Epic Games 在持续维护这个插件。
- **状态**：**实验性** (`IsBetaVersion=true`)，且默认禁用 (`EnabledByDefault=false`)。这意味着虽然功能可用，但 API 和行为可能在未来的版本中发生不兼容的变化，不建议在需要长期稳定的核心项目中重度依赖。
- **推荐**：适用于需要高级序列化工作流的项目，特别是涉及复杂相机动画管理的项目。对于生产环境，建议密切关注其更新日志，并做好应对潜在 Breaking Changes 的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [官方文档]() (暂无公开官方文档链接)