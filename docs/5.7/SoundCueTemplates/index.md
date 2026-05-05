# Sound Cue Templates

> Collection of SoundCue Templates, which provide rapid design of common audio design workflows.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | 是 |
| 包含内容 | 是 |
| 模块 | SoundCueTemplates (Runtime), SoundCueTemplatesEditor (Editor) |
| 创建时间 | 2019-07-18 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundCueTemplates) | |

## 用途

SoundCueTemplates 提供了一套**预制的 SoundCue 模板类**，让你无需手动搭建 SoundCue 节点图，就能快速创建常见的音频设计模式。模板在编辑器中暴露简化的属性面板，隐藏底层 SoundCue 节点图的复杂性——当你修改属性时，模板会**自动重建**整个节点图。

核心思想：SoundCue 节点图虽然灵活，但对于"随机播放变体"、"距离衰减交叉淡入淡出"这类常见模式，每次都手动搭建节点图既繁琐又容易出错。模板将这些模式封装为高层属性，自动生成正确的节点图。

> ⚠️ 此插件标记为 `IsBetaVersion: true`，仍处于 Beta 阶段。

## 使用场景

- 你有多个音效变体（如脚步声），需要随机播放 → 用 **SoundCueContainer**（Randomize 模式）
- 你需要多个音效按顺序播放 → 用 **SoundCueContainer**（Concatenate 模式）
- 你需要多个音效同时混合播放 → 用 **SoundCueContainer**（Mix 模式）
- 你需要根据距离自动切换近处/远处音效 → 用 **SoundCueDistanceCrossfade**

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSoundWavesToTemplate` | 向模板添加 SoundWave 资源 | `USoundCueTemplate` |

### 编辑器中的使用方式

SoundCueTemplates 主要通过**编辑器面板**操作，而非蓝图节点：

1. **创建模板资产**：在 Content Browser 中右键 → Audio → 选择对应的模板类型（SoundCueContainer 或 SoundCueDistanceCrossfade）
2. **配置属性**：选中创建的资产，在 Details 面板中设置参数
3. **查看节点图**：双击资产可打开 SoundCue 编辑器，查看自动生成的节点图

## C++ 用法

### 头文件引入

```cpp
#include "SoundCueTemplate.h"
#include "SoundCueContainer.h"
#include "SoundCueDistanceCrossfade.h"
#include "SoundCueTemplateSettings.h"
```

### 自定义模板子类

继承 `USoundCueTemplate` 可创建自定义模板。核心是实现 `OnRebuildGraph()`：

```cpp
// 来源: Engine/Plugins/Runtime/SoundCueTemplates/Source/SoundCueTemplates/Public/SoundCueTemplate.h
UCLASS()
class UMyCustomTemplate : public USoundCueTemplate
{
    GENERATED_UCLASS_BODY()

    UPROPERTY(EditAnywhere, Category = "Settings")
    bool bLooping;

    UPROPERTY(EditAnywhere, Category = "Settings")
    TSet<TObjectPtr<USoundWave>> Sounds;

protected:
    // 自动在属性变更时重建节点图
    virtual void OnRebuildGraph(USoundCue& SoundCue) const override;
};
```

在 `OnRebuildGraph` 中使用模板提供的工具函数构建节点图：

```cpp
void UMyCustomTemplate::OnRebuildGraph(USoundCue& SoundCue) const
{
    // 创建根节点
    USoundNodeModulator& Root = ConstructSoundNodeRoot<USoundNodeModulator>(SoundCue);

    // 在指定列/行创建子节点并连接
    auto& WavePlayer = ConstructSoundNodeChild<USoundNodeWavePlayer>(
        SoundCue, &Root, /*Column=*/1, /*Row=*/0, /*InputPinIndex=*/0);

    WavePlayer.SetSoundWave(Sounds.Array()[0]);
    WavePlayer.bLooping = bLooping;
}
```

### 内置模板类

| 类 | 说明 |
|---|---|
| `USoundCueContainer` | 多变体容器（随机/拼接/混合），支持音高和音量调制 |
| `USoundCueDistanceCrossfade` | 基于距离的近/远音效交叉淡入淡出 |

### 质量等级配置

```cpp
// 来源: Engine/Plugins/Runtime/SoundCueTemplates/Source/SoundCueTemplates/Public/SoundCueTemplateSettings.h
// 通过项目设置 → Sound Cue Templates 配置每个质量等级的最大变体数
// FSoundCueTemplateQualitySettings:
//   MaxConcatenatedVariations - Concatenate 模式的最大变体数
//   MaxRandomizedVariations   - Randomize 模式的最大变体数
//   MaxMixVariations          - Mix 模式的最大变体数
```

### 注册 Detail Customization

自定义模板需要在模块启动时注册 Detail 自定义面板以隐藏不必要的属性：

```cpp
// 来源: SoundCueContainer.h 注释
FPropertyEditorModule& PropertyModule =
    FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
FSoundCueContainerDetailCustomization::Register(PropertyModule);
```

## Demo 示例

### 最小自定义模板

```cpp
// MySimpleTemplate.h
#pragma once
#include "SoundCueTemplate.h"
#include "MySimpleTemplate.generated.h"

UCLASS(BlueprintType, hidecategories = object)
class UMySimpleTemplate : public USoundCueTemplate
{
    GENERATED_UCLASS_BODY()

#if WITH_EDITORONLY_DATA
    UPROPERTY(EditAnywhere, Category = "Settings")
    bool bLooping = false;

    UPROPERTY(EditAnywhere, Category = "Settings")
    TObjectPtr<USoundWave> SoundWave = nullptr;
#endif

protected:
#if WITH_EDITOR
    virtual void OnRebuildGraph(USoundCue& SoundCue) const override;
#endif
};

// MySimpleTemplate.cpp
#include "MySimpleTemplate.h"
#include "Sound/SoundNodeWavePlayer.h"

UMySimpleTemplate::UMySimpleTemplate(const FObjectInitializer& OI) : Super(OI) {}

#if WITH_EDITOR
void UMySimpleTemplate::OnRebuildGraph(USoundCue& SoundCue) const
{
    if (!SoundWave) return;

    auto& Player = ConstructSoundNodeRoot<USoundNodeWavePlayer>(SoundCue);
    Player.SetSoundWave(SoundWave);
    Player.bLooping = bLooping;
}
#endif
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "SoundCueTemplates" });
```

## 模块依赖

### SoundCueTemplates（Runtime）

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心功能 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（SoundCue、SoundNode 等） |
| `DeveloperSettings` | 项目设置支持 |

### SoundCueTemplatesEditor（Editor）

| 模块 | 用途 |
|---|---|
| `SoundCueTemplates` | Runtime 模块依赖 |
| `AudioEditor` | 音频编辑器集成 |
| `AssetDefinition` | 资产定义系统 |
| `ToolMenus` | 右键菜单扩展 |
| `UnrealEd` | 编辑器核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-10 | `9803c443cfab` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 代码质量改进，添加内联 gen.cpp 宏 |
| 2025-06-19 | `800d7a513809` | 右键音频操作反馈、USoundSimple 废弃清理、ParentPreset 重命名 | 功能性更新：清理废弃功能，改进编辑器 UX |
| 2025-05-19 | `a60b2b5c1723` | Fixup API macros for merged modules | API 宏修复，构建系统适配 |

### 维护评价

- **创建时间**：2019 年 7 月，约 7 年历史
- **Beta 状态**：`IsBetaVersion=true`，自创建以来一直是 Beta
- **维护频率**：近期（2025 年）有多次更新，主要是编辑器体验改进和废弃代码清理
- **评估**：**维护中** — 虽然是 Beta 且更新不算频繁，但仍在持续使用中，2025 年仍有实质性更新
- **风险提示**：Beta 标记意味着 API 可能变化；依赖 `USoundSimple` 的相关功能已被废弃

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundCueTemplates)
- 官方文档：无（.uplugin 的 DocsURL 为空）
