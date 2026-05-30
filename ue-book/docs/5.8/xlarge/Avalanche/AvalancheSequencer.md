# Motion Design

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态设计 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、自定义编辑器 UI） |
| 模块 | `Avalanche` (Runtime), `AvalancheAttribute` (Runtime), `AvalancheAttributeEditor` (Runtime), `AvalancheCamera` (Runtime), `AvalancheComponentVisualizers` (Runtime), `AvalancheCore` (Runtime), `AvalancheEditor` (Runtime), `AvalancheEditorCore` (Runtime), `AvalancheEffectors` (Runtime), `AvalancheEffectorsEditor` (Runtime), `AvalancheFunctionalTest` (Runtime), `AvalancheInteractiveTools` (Runtime), `AvalancheInteractiveToolsRuntime` (Runtime), `AvalancheLevelViewport` (Runtime), `AvalancheMRQ` (Runtime), `AvalancheMRQEditor` (Runtime), `AvalancheMask` (Runtime), `AvalancheMaskEditor` (Runtime), `AvalancheMaterial` (Runtime), `AvalancheMedia` (Runtime), `AvalancheMediaEditor` (Runtime), `AvalancheModifiers` (Runtime), `AvalancheModifiersEditor` (Runtime), `AvalancheOutliner` (Runtime), `AvalanchePropertyAnimator` (Runtime), `AvalanchePropertyAnimatorEditor` (Runtime), `AvalancheRemoteControl` (Runtime), `AvalancheRemoteControlEditor` (Runtime), `AvalancheSVGEditor` (Runtime), `AvalancheSceneRig` (Runtime), `AvalancheSceneRigEditor` (Runtime), `AvalancheSceneTree` (Runtime), `AvalancheSequence` (Runtime), `AvalancheSequencer` (Runtime), `AvalancheShapes` (Runtime), `AvalancheShapesEditor` (Runtime), `AvalancheTag` (Runtime), `AvalancheTagEditor` (Runtime), `AvalancheText` (Runtime), `AvalancheTextEditor` (Runtime), `AvalancheTransition` (Runtime), `AvalancheTransitionEditor` (Runtime), `AvalancheViewport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

## 用途

Motion Design（原名 Avalanche）是 Epic Games 为**虚拟制作（Virtual Production）**场景打造的综合性运动设计工具集。它解决的核心问题是：在 Unreal Engine 中实现**广播级动态图形（Motion Graphics）**的完整创作流程——从设计、合成到实时播出。

该插件并非单一功能模块，而是一个**大型工具生态系统**，涵盖：

- **场景合成**（Compositing）：通过 GeometryMask、ActorModifier 等模块实现图层式场景合成
- **设计工具**（Designer）：包括材质设计器（Material Designer）、SVG 导入、3D 文字、形状生成器、克隆/效果器（ClonerEffector）等
- **序列动画**（Sequencer Integration）：自定义的 AvaSequence 系统，预设管理、交错工具等
- **实时播出**（Broadcasting）：Media 集成、远程控制、MRQ 渲染队列集成
- **过渡逻辑**（Transition）：场景切换和过渡效果管理
- **属性动画**（Property Animator）：对象属性的关键帧动画
- **场景层级管理**（Scene Tree/Rig）：结构化的场景管理

该插件从 2025 年 5 月从 `Engine/Plugins/Experimental` 迁移到 `Engine/Plugins/VirtualProduction`，标志着从实验性功能升级为正式的虚拟制作工具。

## 使用场景

- 你在为电视广播或直播制作动态图形 → 用 Motion Design 的全套设计和播出工具
- 你需要在 Unreal 中创建类似 After Effects 的合成工作流 → 用 GeometryMask、ActorModifier、ClonerEffector
- 你需要快速创建带有预设模板的序列动画 → 用 AvaSequence 的预设系统
- 你需要对大量对象进行属性动画（如位置、旋转、缩放的时间线控制）→ 用 PropertyAnimator
- 你需要导入 SVG 矢量图形并转换为 3D 形状 → 用 SVG Importer 和 Shapes 模块
- 你需要远程控制场景中的对象和参数 → 用 Remote Control 集成
- 你需要使用 Movie Render Queue 高质量渲染运动设计场景 → 用 AvalancheMRQ

## 文档结构

该插件规模庞大（42 个模块，2060 个源文件），按模块拆分文档：

| 子模块文档 | 说明 |
|---|---|
| [AvalancheSequencer](AvalancheSequencer.md) | 序列动画管理、预设系统、交错工具、剪贴板操作 |

> 更多子模块文档将在后续补充。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加使用节目单页面设置时的 MRQ 分析追踪 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 在播出控制工具栏添加页面加载选项（全部、下一个、选中项） |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加项目设置以强制禁用 Text3D 和形状的碰撞 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口客户端关联/解除关联时的通知机制 |

### 维护评价

**活跃维护**。该插件在最近的提交中持续获得功能性更新（2026 年 5 月仍在活跃开发），包括 UI 改进、新功能添加（MRQ 分析、页面加载选项）和碰撞控制。作为 Epic Games 官方维护的虚拟制作核心工具，且已从 Experimental 晋升为正式 Virtual Production 分类，维护优先级很高。

⚠️ **注意**：该插件于 2025 年 5 月刚从 Experimental 迁移，API 可能仍在演进中，部分接口标注了 `UE_DEPRECATED`。建议关注版本升级时的 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [官方文档](https://docs.unrealengine.com/en-US/animation/motion-design/)（如有）

---

# Avalanche Sequencer

Avalanche Sequencer 模块为 Motion Design 提供了专属的序列动画管理系统。它在 Unreal Engine 标准 Sequencer 基础上，构建了一套面向运动设计的序列管理、预设应用、剪贴板操作和交错排布工具。

## 用途

该模块解决的核心问题是：**运动设计中的序列动画管理**。标准 Sequencer 面向游戏和电影，而 Avalanche Sequencer 为广播/动态图形场景提供了以下增强：

- **AvaSequence 系统**：独立于标准 Level Sequence 的自定义序列，支持嵌入式存储、树形组织和拖放排序
- **预设系统**（Presets）：预定义序列参数（标签、结束时间、标记等），支持分组快速创建
- **交错工具**（Stagger Tool）：批量排列选中的序列条或关键帧，支持增量、范围和随机分布
- **剪贴板集成**：复制粘贴 Actor 时自动携带其序列绑定数据
- **选择同步**：编辑器选择与 Sequencer 选择之间的双向同步
- **自定义干净视图**（Clean View）：播放时自定义视口显示状态
- **Sequencer 自定义**：扩展 Sequencer 工具栏、添加轨道菜单、侧边栏内容等

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sequencer` | Unreal Engine 标准 Sequencer 模块（核心依赖） |

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOrCreateSequencer` | 获取或创建当前世界的 Sequencer 实例 | `UAvaSequencerSubsystem` |
| `GetSequencer` | 获取已有的 Sequencer 实例（不创建新的） | `UAvaSequencerSubsystem` |
| `GetSequencesForObject` | 查找指定对象参与的所有序列 | `IAvaSequencer` |
| `CanAddSequence` | 检查是否可以添加新序列 | `IAvaSequencer` |
| `AddSequence` | 创建新序列，可指定父序列 | `IAvaSequencer` |
| `DeleteSequences` | 批量删除序列 | `IAvaSequencer` |
| `GetViewedSequence` | 获取当前 Sequencer 面板中查看的序列 | `IAvaSequencer` |
| `SetViewedSequence` | 设置 Sequencer 面板要查看的序列 | `IAvaSequencer` |
| `GetRootSequences` | 获取所有根级序列列表 | `IAvaSequencer` |
| `FindPreset` | 按名称查找序列预设 | `UAvaSequencerSettings` |
| `FindPresetGroup` | 按名称查找预设组 | `UAvaSequencerSettings` |
| `AddSequenceFromPresets` | 根据预设批量创建序列 | `IAvaSequencer` |

### 使用示例

**创建新序列并应用预设**：

1. 通过 `UAvaSequencerSubsystem` 获取 Sequencer 实例
2. 调用 `AddSequence()` 创建空序列
3. 通过 `UAvaSequencerSettings` 查找预设（`FindPreset`）
4. 将预设应用到序列上

**批量创建预设序列**：

1. 在项目设置（Motion Design > Sequencer）中配置自定义预设组和预设
2. 调用 `GatherPresetsFromGroup()` 获取预设列表
3. 调用 `AddSequenceFromPresets()` 一次性创建所有序列

## C++ 用法

### 头文件引入

```cpp
#include "IAvaSequencer.h"
#include "AvaSequencerSubsystem.h"
#include "IAvaSequencerProvider.h"
#include "Settings/AvaSequencerSettings.h"
#include "Settings/AvaSequencePreset.h"
#include "AvaSequencerUtils.h"
```

### 基本用法

**获取 Sequencer 实例**（来源：`Public/AvaSequencerSubsystem.h`）：

```cpp
// 通过 World Subsystem 获取 Sequencer 实例
UWorld* World = /* ... */;
UAvaSequencerSubsystem* SequencerSubsystem = World->GetSubsystem<UAvaSequencerSubsystem>();

// 获取现有实例（不创建新的）
TSharedPtr<IAvaSequencer> Sequencer = SequencerSubsystem->GetSequencer();

// 获取或创建实例（需要提供 Provider 和参数）
// TSharedRef<IAvaSequencer> SequencerRef = SequencerSubsystem->GetOrCreateSequencer(Provider, MoveTemp(Args));
```

**通过工具类获取关联对象**（来源：`Public/AvaSequencerUtils.h`）：

```cpp
// 从 ISequencer 获取 Motion Design 相关对象
TSharedRef<ISequencer> SequencerRef = /* ... */;

// 获取关联的 World
UWorld* World = FAvaSequencerUtils::GetSequencerWorld(SequencerRef);

// 获取 Sequencer Subsystem
UAvaSequencerSubsystem* Subsystem = FAvaSequencerUtils::GetSequencerSubsystem(SequencerRef);

// 获取 Scene Interface
IAvaSceneInterface* SceneInterface = FAvaSequencerUtils::GetSceneInterface(SequencerRef);

// 获取序列提供者
IAvaSequenceProvider* Provider = FAvaSequencerUtils::GetSequenceProvider(SequencerRef);

// 获取 Motion Design Sequencer
TSharedPtr<IAvaSequencer> AvaSequencer = FAvaSequencerUtils::GetAvaSequencer(SequencerRef);
```

**管理序列**（来源：`Public/IAvaSequencer.h`）：

```cpp
// 获取当前查看的序列
UAvaSequence* CurrentSeq = Sequencer->GetViewedSequence();

// 获取默认序列（回退用）
UAvaSequence* DefaultSeq = Sequencer->GetDefaultSequence();

// 切换查看的序列
Sequencer->SetViewedSequence(NewSequence);

// 创建新序列
if (Sequencer->CanAddSequence())
{
    UAvaSequence* NewSeq = Sequencer->AddSequence();
    // 创建子序列
    UAvaSequence* ChildSeq = Sequencer->AddSequence(NewSeq);
}

// 删除序列
TSet<UAvaSequence*> SequencesToDelete;
SequencesToDelete.Add(SomeSequence);
Sequencer->DeleteSequences(SequencesToDelete);

// 查找对象参与的所有序列
TArray<UAvaSequence*> FoundSequences = Sequencer->GetSequencesForObject(SomeObject);
```

### 进阶用法

**使用预设系统批量创建序列**（来源：`Public/Settings/AvaSequencerSettings.h`、`Public/Settings/AvaSequencePreset.h`）：

```cpp
// 获取 Sequencer 设置
UAvaSequencerSettings* Settings = GetMutableDefault<UAvaSequencerSettings>();

// 查找特定预设
const FAvaSequencePreset* Preset = Settings->FindPreset(FName("MyPreset"));
if (Preset)
{
    // 应用预设到现有序列
    Preset->ApplyPreset(MySequence);
}

// 通过预设组批量创建
TArray<const FAvaSequencePreset*> Presets = Settings->GatherPresetsFromGroup(FName("TransitionIn"));
uint32 CreatedCount = Sequencer->AddSequenceFromPresets(Presets);

// 自定义预设（在代码中动态创建）
FAvaSequencePreset CustomPreset(FName("CustomIntro"));
CustomPreset.bEnableLabel = true;
CustomPreset.SequenceLabel = FName("Intro");
CustomPreset.bEnableEndTime = true;
CustomPreset.EndTime = 3.0;  // 3 秒
```

**监听序列变化事件**（来源：`Public/IAvaSequencer.h`、`Public/AvaSequencerSubsystem.h`）：

```cpp
// 监听序列添加
Sequencer->OnSequenceAdded().AddLambda([](UAvaSequence* InNewSequence)
{
    UE_LOG(LogTemp, Log, TEXT("New sequence added: %s"), *InNewSequence->GetName());
});

// 监听序列删除
Sequencer->OnSequenceRemoved().AddLambda([](UAvaSequence* InRemovedSequence)
{
    UE_LOG(LogTemp, Log, TEXT("Sequence removed: %s"), *InRemovedSequence->GetName());
});

// 监听 Sequencer 实例创建
UAvaSequencerSubsystem* Subsystem = World->GetSubsystem<UAvaSequencerSubsystem>();
Subsystem->OnSequencerCreated().AddLambda([](TSharedRef<IAvaSequencer> InSequencer)
{
    // Sequencer 刚被创建，可在此进行初始化
});
```

**实现自定义 Sequencer Provider**（来源：`Public/IAvaSequencerProvider.h`）：

```cpp
class FMySequencerProvider : public IAvaSequencerProvider
{
public:
    virtual TSharedPtr<IAvaSequencer> GetAvaSequencer() const override
    {
        return AvaSequencer;
    }
    
    virtual IAvaSequenceProvider* GetSequenceProvider() const override
    {
        return SequenceProvider;
    }
    
    virtual FEditorModeTools* GetSequencerModeTools() const override
    {
        return ModeTools;
    }
    
    virtual IAvaSequencePlaybackObject* GetPlaybackObject() const override
    {
        return PlaybackObject;
    }
    
    virtual TSharedPtr<IToolkitHost> GetSequencerToolkitHost() const override
    {
        return ToolkitHost;
    }
    
    virtual UObject* GetPlaybackContext() const override
    {
        return PlaybackContext;
    }
    
    virtual bool CanEditOrPlaySequences() const override
    {
        return bCanPlay;
    }
    
    // 可选：使用外部 Sequencer
    virtual TSharedPtr<ISequencer> GetExternalSequencer() const override
    {
        return ExternalSequencer; // 返回 nullptr 使用内部创建的
    }

private:
    TSharedPtr<IAvaSequencer> AvaSequencer;
    IAvaSequenceProvider* SequenceProvider = nullptr;
    FEditorModeTools* ModeTools = nullptr;
    IAvaSequencePlaybackObject* PlaybackObject = nullptr;
    TSharedPtr<IToolkitHost> ToolkitHost;
    UObject* PlaybackContext = nullptr;
    TSharedPtr<ISequencer> ExternalSequencer;
    bool bCanPlay = true;
};
```

## Demo 示例

**自定义序列管理器**：

```cpp
// MySequenceManager.h
#pragma once

#include "IAvaSequencer.h"
#include "AvaSequencerSubsystem.h"
#include "AvaSequencerArgs.h"

class FMySequenceManager
{
public:
    void Initialize(UWorld* InWorld, IAvaSequencerProvider& InProvider)
    {
        UAvaSequencerSubsystem* Subsystem = InWorld->GetSubsystem<UAvaSequencerSubsystem>();
        if (!Subsystem) return;

        // 创建 Sequencer 实例
        FAvaSequencerArgs Args;
        Args.bUseCustomCleanPlaybackMode = true;
        Args.bCanProcessSequencerSelections = true;
        
        Sequencer = Subsystem->GetOrCreateSequencer(InProvider, MoveTemp(Args));
        
        // 绑定事件
        Sequencer->OnSequenceAdded().AddSP(this, &FMySequenceManager::HandleSequenceAdded);
        Sequencer->OnSequenceRemoved().AddSP(this, &FMySequenceManager::HandleSequenceRemoved);
    }

    void CreateSequenceFromPreset(FName InPresetName)
    {
        if (!Sequencer.IsValid()) return;
        
        const UAvaSequencerSettings* Settings = GetDefault<UAvaSequencerSettings>();
        const FAvaSequencePreset* Preset = Settings->FindPreset(InPresetName);
        
        if (Preset)
        {
            TArray<const FAvaSequencePreset*> Presets;
            Presets.Add(Preset);
            Sequencer->AddSequenceFromPresets(Presets);
        }
    }
    
    TArray<UAvaSequence*> GetSequencesForActor(AActor* InActor)
    {
        if (!Sequencer.IsValid()) return {};
        return Sequencer->GetSequencesForObject(InActor);
    }

    void Shutdown()
    {
        Sequencer.Reset();
    }

private:
    void HandleSequenceAdded(UAvaSequence* InSequence)
    {
        UE_LOG(LogTemp, Log, TEXT("Sequence added: %s"), 
            InSequence ? *InSequence->GetName() : TEXT("null"));
    }

    void HandleSequenceRemoved(UAvaSequence* InSequence)
    {
        UE_LOG(LogTemp, Log, TEXT("Sequence removed: %s"),
            InSequence ? *InSequence->GetName() : TEXT("null"));
    }

    TSharedPtr<IAvaSequencer> Sequencer;
};
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将 Motion Design 的场景设置和大纲视图标签页移至独立分组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加使用节目单页面设置时的 MRQ 分析追踪 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and adde | 添加页面加载选项到播出控制工具栏 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加禁用 Text3D 和形状碰撞的项目设置 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 优化视口客户端关联通知机制 |

### 维护评价

**活跃维护**。AvalancheSequencer 模块作为 Motion Design 插件的核心组件之一，随主插件持续获得更新。2026 年 5 月仍有功能性提交。该模块从 2025 年 5 月从 Experimental 迁移至 Virtual Production，API 已相对稳定，但部分接口已标记 `UE_DEPRECATED`（如 `GetSequencer()` → `GetSequencerPtr()`、侧边栏状态迁移至 `USequencerSettings`），表明正在经历 API 演进。建议关注 5.7 版本的弃用警告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheSequencer)
- [主插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [功能测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheFunctionalTest)