```markdown
# Template Sequence

> Runtime for template sequences

| 属性 | 值 |
|---|---|
| 中文名 | 模板序列 |
| 分类 | Cinematics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TemplateSequence` (Runtime), `TemplateSequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-02 |
| 年龄标签 | 🆕（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence) | |

## 用途

Template Sequence 是 Sequencer 的扩展插件，提供**模板序列**功能，允许创建可绑定到不同类型 Actor 的序列资产。

核心概念：
- **模板序列**：一种特殊的 Level Sequence，包含一个根对象绑定（Root Object Binding），可以被绑定到不同类型的 Actor
- **相机动画序列**：模板序列的特化版本，专门用于相机动画，支持初始视口位置叠加
- **属性缩放**：允许对模板序列中的动画属性进行缩放

该插件解决的问题是：在 Sequencer 中创建可复用的动画模板，同一个动画可以应用到不同的 Actor 类型上，无需为每个 Actor 重新制作动画。

## 使用场景

- 你需要创建可复用的相机动画效果 → 使用 Camera Animation Sequence
- 你需要将相同的动画模板应用到不同类型的 Actor → 使用 Template Sequence
- 你需要在 Sequencer 中快速绑定不同的 Actor 类型 → 使用模板序列的绑定功能
- 你需要为过场动画创建可配置的相机轨迹 → 使用相机动画序列

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableNextFrame` | 启用相机预览系统，将当前视口变换写入相机对象 | `UTemplateSequenceCameraPreviewSystem` |
| `DisableNextFrame` | 禁用相机预览系统，重置相机变换到原点 | `UTemplateSequenceCameraPreviewSystem` |

## C++ 用法

### 头文件引入

```cpp
#include "TemplateSequence/Public/TemplateSequence.h"
```

### 基本用法

模板序列的核心是创建可绑定的序列资产。以下示例展示如何使用模板序列相关类：

```cpp
// 引用自 TemplateSequenceFactoryUtil.h
// 创建模板序列的工厂方法
UTemplateSequence* TemplateSequence = FTemplateSequenceFactoryUtil::CreateTemplateSequence(
    InParent,
    InName,
    RF_Public | RF_Standalone,
    UTemplateSequence::StaticClass(),
    ActorClass  // 要绑定的 Actor 类
);
```

### 进阶用法

相机预览系统允许在编辑器中预览相机效果：

```cpp
// 引用自 TemplateSequenceCameraPreviewSystem.h
// 启用相机预览，将当前视口位置作为初始变换
UTemplateSequenceCameraPreviewSystem::EnableNextFrame();

// 禁用相机预览，重置变换到原点
UTemplateSequenceCameraPreviewSystem::DisableNextFrame();
```

## Demo 示例

```cpp
// TemplateSequenceExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TemplateSequenceExample.generated.h"

UCLASS()
class ATemplateSequenceExample : public AActor
{
    GENERATED_BODY()

public:
    ATemplateSequenceExample();

protected:
    virtual void BeginPlay() override;

public:
    // 模板序列资产引用
    UPROPERTY(EditAnywhere, Category = "Template Sequence")
    class UTemplateSequence* TemplateSequenceAsset;
};
```

```cpp
// TemplateSequenceExample.cpp
#include "TemplateSequenceExample.h"
#include "TemplateSequence/Public/TemplateSequence.h"
#include "MovieScene/Public/MovieSceneSequencePlayer.h"

ATemplateSequenceExample::ATemplateSequenceExample()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ATemplateSequenceExample::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时播放模板序列
    if (TemplateSequenceAsset)
    {
        // 模板序列可以通过 Sequencer 播放系统播放
        // 需要先将序列绑定到具体的 Actor 实例
        UE_LOG(LogTemp, Log, TEXT("Template Sequence asset loaded: %s"), 
               *TemplateSequenceAsset->GetName());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LevelSequenceEditor` | 编辑器中的序列编辑功能 |
| `MovieScene` | Sequencer 核心模块 |
| `LevelSequence` | 关卡序列运行时 |
| `SequencerCore` | Sequencer 核心框架 |
| `MovieSceneTools` | Sequencer 编辑器工具 |
| `AssetDefinition` | 资产定义系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF |
| 2026-04-10 | `c03b3afd` | PR #14610: Rep layout mismatch in level sequence player due to with editoronly data property | 修复因 editoronly 数据属性导致的序列播放器 Rep 布局不匹配问题 |
| 2026-02-20 | `49054c9f` | Sequencer: Add Bake Transform to object binding menu | Sequencer: 在对象绑定菜单中添加烘焙变换功能 |
| 2026-02-11 | `5919e4fa` | Remove 7 virtual functions in UObject (either deprecated or toolonly) | 移除 UObject 中的 7 个虚函数（已废弃或仅工具使用） |

### 维护评价

**维护状态：活跃维护**

- 插件创建于 2019 年 10 月，至今约 7 年
- 最近更新显示持续活跃，有功能性改进（如添加烘焙变换功能）
- 有 bug 修复（浮点警告、Rep 布局问题）
- 进行现代化更新（UE_LOG 迁移）
- 仍标记为 Beta 版本且默认未启用，说明仍在开发完善中
- **推荐使用**：对于需要可复用动画模板的项目，该插件提供了解决方案，但需注意其 Beta 状态

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/TemplateSequence)
- [官方文档]()（暂无官方文档链接）
```