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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 插件的核心功能是提供一种可复用的动画片段（Animation Clip）技术，称为“模板序列”。它解决了在 Sequencer（过场动画编辑器）中重复制作相似动画片段的效率问题。通过将一段精心调整好的动画（如角色特定的动作、摄像机运动、材质参数变化等）封装成模板，可以像预制件一样在其他 Sequencer 轨道中多次实例化，并允许在实例中进行覆盖和微调，从而大幅提升复杂角色动画和过场动画的制作效率与一致性。

## 使用场景

- 你正在开发一个拥有多名主角的角色扮演游戏，其中一些攻击、跳跃或待机动画在多个角色间相似但需微调 → 使用 Template Sequence 创建基础动画模板，然后在不同角色的动画蓝图或过场动画中实例化并覆盖关键差异。
- 你正在制作一部动画短片或游戏过场，其中有大量重复的镜头转场效果（如淡入淡出、特定类型的镜头抖动）→ 将转场效果封装为模板序列，在 Sequencer 中重复使用，只需调整时长和位置。
- 你作为技术美术，需要为团队提供标准化的动画资产，但允许设计师在特定场景中进行个性化调整 → 创建模板序列作为基础资产，供其他人在 Sequencer 中安全地修改和扩展。

## 蓝图用法

该插件的蓝图 API 主要集中在序列资产的操作上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Template Sequence` | 根据指定的命名和资源路径，创建一个新的空模板序列资产。 | `UTemplateSequenceSubsystem` |
| `Find Template Sequence` | 根据名称查找已存在的模板序列资产。 | `UTemplateSequenceSubsystem` |
| `Add Template Sequence Object Binding` | 向一个 Sequencer 轨道中添加模板序列实例。 | `UTemplateSequenceSubsystem` |

### 使用示例（蓝图描述）

1.  **创建模板序列**：使用 `Create Template Sequence` 节点，输入一个唯一的名称（如 `ATK_Combo1_Template`）和保存路径，即可在内容浏览器中生成一个新的模板序列资产。
2.  **在 Sequencer 中应用**：
    *   打开一个 Level Sequence。
    *   在轨道区域右键，选择 `Template Sequence` -> `Add Template Sequence Object Binding`。
    *   在弹出的面板中选择之前创建的模板序列资产（如 `ATK_Combo1_Template`）。
    *   此时，模板序列会作为一个新的轨道组出现在 Sequencer 中，包含了原始模板的所有动画数据。
3.  **覆盖与调整**：展开新添加的模板序列轨道组，可以像编辑普通轨道一样，在其中添加新的关键帧、修改曲线，这些修改仅影响当前实例，不会改变原始模板资产。

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence.h"
// 如果在编辑器模块中，还需要
#include "TemplateSequenceEditor.h"
```

### 基本用法

在 C++ 中，模板序列的核心是 `UTemplateSequence` 资产类和 `UTemplateSequenceSubsystem` 子系统。

```cpp
// 示例：在编辑器工具或运行时逻辑中，通过子系统创建一个模板序列
// 来源：引擎子系统标准用法，具体实现可参考 TemplateSequenceSubsystem.h
if (UTemplateSequenceSubsystem* Subsystem = GEditor->GetEditorSubsystem<UTemplateSequenceSubsystem>())
{
    // 创建一个新的模板序列资产
    UTemplateSequence* NewTemplate = Subsystem->CreateTemplateSequence(
        TEXT("MyNewTemplate"),
        TEXT("/Game/Sequences/Templates"),
        UTemplateSequence::StaticClass(),
        ULevelSequence::StaticClass()
    );

    if (NewTemplate)
    {
        // 现在可以对 NewTemplate 进行编辑，例如添加动画轨道
        UE_LOG(LogTemplateSequence, Log, TEXT("成功创建模板序列: %s"), *NewTemplate->GetPathName());
    }
}
```

### 进阶用法

结合 `ULevelSequence` API，可以将模板序列作为轨道添加到过场序列中。

```cpp
// 假设我们已经有了一个主关卡序列 (MasterSequence) 和一个模板序列资产 (TemplateAsset)
ULevelSequence* MasterSequence = ...;
ULevelSequence* TemplateAsset = ...;

// 获取 MasterSequence 的可修改电影场景
UMovieScene* MasterMovieScene = MasterSequence->GetMovieScene();

// 创建模板序列的轨道
UMovieSceneSequenceTrack* TemplateTrack = MasterMovieScene->AddTrack<UMovieSceneSequenceTrack>();

// 添加一个片段，将模板序列实例化
if (UMovieSceneSequenceSection* Section = Cast<UMovieSceneSequenceSection>(TemplateTrack->CreateNewSection()))
{
    Section->SetSequence(TemplateAsset);
    Section->SetRange(TRange<FFrameNumber>(0, 1000)); // 设置播放范围
    TemplateTrack->AddSection(*Section);
}

// 最后需要编译序列以使改动生效
MasterSequence->Compile();
```

## Demo 示例

一个简单的编辑器工具类，用于创建和列出模板序列。

```cpp
// TemplateSequenceDemoTool.h
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "TemplateSequenceDemoTool.generated.h"

UCLASS()
class UTemplateSequenceDemoTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "TemplateSequence Demo")
    void CreateNewTemplate(const FString& TemplateName);

    UFUNCTION(BlueprintCallable, Category = "TemplateSequence Demo")
    TArray<UTemplateSequence*> GetAllTemplates() const;
};
```

```cpp
// TemplateSequenceDemoTool.cpp
#include "TemplateSequenceDemoTool.h"
#include "TemplateSequence.h"
#include "TemplateSequenceSubsystem.h"

void UTemplateSequenceDemoTool::CreateNewTemplate(const FString& TemplateName)
{
    if (UTemplateSequenceSubsystem* Subsystem = GEditor->GetEditorSubsystem<UTemplateSequenceSubsystem>())
    {
        UTemplateSequence* NewTemplate = Subsystem->CreateTemplateSequence(
            TemplateName,
            TEXT("/Game/Templates"),
            UTemplateSequence::StaticClass(),
            ULevelSequence::StaticClass()
        );
        if (NewTemplate)
        {
            UE_LOG(LogTemp, Log, TEXT("模板序列 '%s' 创建成功。"), *TemplateName);
        }
    }
}

TArray<UTemplateSequence*> UTemplateSequenceDemoTool::GetAllTemplates() const
{
    TArray<UTemplateSequence*> OutTemplates;
    if (UTemplateSequenceSubsystem* Subsystem = GEditor->GetEditorSubsystem<UTemplateSequenceSubsystem>())
    {
        Subsystem->GetAllTemplateSequences(OutTemplates);
    }
    return OutTemplates;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心模块，提供序列、轨道、片段等基础框架。 |
| `LevelSequence` | 关卡序列模块，模板序列的核心父类 `ULevelSequence` 的来源。 |
| `MovieSceneTools` | 提供编辑器中的序列相关工具和 UI。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下，双精度常量转换为浮点数时产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复了由于包含编辑器专用数据属性而导致关卡序列播放器中复制布局不匹配的问题。 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | 在 Sequencer 的对象绑定菜单中增加了“烘焙变换”选项。 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除了 UObject 中 7 个虚函数（已废弃或仅工具使用）。 |

### 维护评价

**综合评价：**
*   **状态**：**维护中，但标记为实验性**。
*   **年龄与活跃度**：插件已存在约6年，近期（2026年）仍有持续的更新，主要集中在代码质量改进、bug 修复和与引擎其他部分的同步上（如虚函数清理、日志宏迁移）。这表明 Epic 仍在内部使用和维护它。
*   **功能性质**：其核心动画复用功能对于大型项目具有显著价值。然而，`.uplugin` 中 `IsBetaVersion=true` 和 `EnabledByDefault=false` 表明 Epic 仍将其视为实验性功能，可能意味着 API 仍有变动风险，或某些高级功能尚不完善。
*   **推荐**：**推荐用于项目开发，尤其是在编辑器环境下**。对于需要高效处理重复动画片段的团队，值得投入学习。但由于其“实验性”标签，在项目初期应谨慎评估其稳定性，并做好应对未来 API 变更的准备。不建议在追求最高稳定性的生产环境运行时关键路径中重度依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence/Tests) (如果存在)