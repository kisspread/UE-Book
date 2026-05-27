# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画层叠 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、样式资源） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (UncookedOnly), `UAFLayeringTests` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAFLayering 是 Unreal Animation Framework (UAF) 的层叠混合系统插件。它解决的核心问题是：**如何在新的 UAF 动画框架下，以可视化、可编辑的方式组织和混合多个动画层**。

该插件提供了一套完整的"层叠栈（Layer Stack）"系统，允许用户：

1. **创建和管理动画层栈** — 每个层栈包含一个基础层（BaseLayer）和多个叠加层，层的顺序决定了动画混合的优先级
2. **灵活的混合模式** — 支持标准混合（Blend）、叠加混合（Additive）和仅缓存（CacheOnly）三种模式
3. **分层内容提供器** — 通过可插拔的 ContentProvider 和 BlendProvider 结构体，支持不同的动画内容来源（如资产动画、Montage 动画等）
4. **运行时与编辑器统一** — 同一套层栈定义既用于编辑器预览，也用于运行时执行

本质上，它是 UAF 框架中对传统 Animation Layer 系统的现代化重写，底层基于 RigVM 图节点系统自动生成混合逻辑。

## 使用场景

- 你在使用 UAF 动画框架制作角色动画，需要分层混合上半身/下半身/面部动画 → 用 UAF Layering
- 你需要在编辑器中可视化地管理和预览多个动画层的叠加效果 → 用 UAF Layering 的层栈编辑器
- 你需要基于 Montage 播放状态自动启停动画层 → 用 `FUAFMontageProvider` 内容提供器
- 你需要对不同骨骼应用不同的混合权重（如只混合手臂） → 配合 BlendMask 和 BlendProfile

## 蓝图用法

> ⚠️ 注意：本插件主要面向编辑器和运行时动画系统，大部分 API 为 C++ 结构体和编辑器 Widget，蓝图暴露有限。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLayerName` | 获取当前层的名称 | `UUAFLayer` |
| `RenameLayer` | 重命名动画层 | `UUAFLayer` |
| `TogglePreviewVisibility` | 切换层的预览可见性 | `UUAFLayer` |
| `GetLayerState` | 获取层状态（启用/预览禁用/完全禁用） | `UUAFLayer` |
| `SetLayerState` | 设置层状态 | `UUAFLayer` |
| `GetNumLayers` | 获取层栈中的层数量 | `UUAFLayerStack_EditorData` |
| `GetAllLayers` | 获取所有层（含基础层） | `UUAFLayerStack_EditorData` |
| `IsBaseLayer` | 判断是否为基础层 | `UUAFLayerStack_EditorData` |
| `MoveLayerUp` | 将层上移（降低混合优先级） | `UUAFLayerStack_EditorData` |
| `MoveLayerDown` | 将层下移（提高混合优先级） | `UUAFLayerStack_EditorData` |
| `RemoveLayer` | 从层栈移除层 | `UUAFLayerStack_EditorData` |
| `SelectLayer` | 在编辑器中选中指定层 | `UUAFLayerStack_EditorData` |

### 使用示例（蓝图描述）

由于 UAF Layering 的核心操作主要在编辑器 UI 中完成，典型的使用流程为：

1. 在 Workspace 编辑器中创建一个 Layer Stack 资产
2. 通过层栈编辑器 UI（SLayerStack）添加、删除、重排层
3. 每个层通过属性面板配置 ContentProvider（内容来源）和 BlendProvider（混合参数）
4. 层栈编译时自动在底层 RigVM 图中生成对应的混合节点

## C++ 用法

### 头文件引入

```cpp
// 层叠核心类型
#include "LayeringUncookedOnlyTypes.h"

// 层和层栈
#include "Layers/UAFLayer.h"
#include "Internal/Layers/UAFBaseLayer.h"

// 内容提供器和混合提供器
#include "Layers/UAFLayerAssetProvider.h"
#include "Layers/UAFMontageProvider.h"
#include "Layers/UAFLayerDefaultBlendProvider.h"
```

### 基本用法 — 创建自定义内容提供器

内容提供器（ContentProvider）决定了一个动画层"播放什么内容"。以下是继承 `FUAFLayerContentProviderBase` 创建自定义内容提供器的示例。

来源：`Internal/Layers/UAFLayerAssetProvider.h`

```cpp
// 自定义内容提供器，用于从特定资产生成动画内容
USTRUCT()
struct FMyCustomContentProvider : public FUAFLayerContentProviderBase
{
    GENERATED_BODY()

public:
    // 在层栈编译时，创建对应的 RigVM 图节点来播放此层的内容
    virtual URigVMPin* CreateLayerContentTrait(
        UE::UAF::Layering::FLayerCreationContext& LayerCreationContext) override
    {
        // 通过 LayerCreationContext.GraphController 操控底层 RigVM 图
        // 返回此内容 trait 的输出引脚，供混合提供器使用
        return nullptr;
    }

    // 创建编辑器中该内容类型的可视化 Widget
    virtual TSharedRef<SWidget> CreateLayerContentWidget(UUAFLayer* InLayer) override
    {
        return SNullWidget::NullWidget;
    }

#if WITH_EDITOR
    // 声明引用的 UObject，确保它们被正确追踪
    virtual void GetObjectReferences(TArray<const UObject*>& OutReferencedObjects) const override
    {
    }
#endif
};
```

### 基本用法 — 创建自定义混合提供器

混合提供器（BlendProvider）决定了一个动画层"如何与前一层混合"。

来源：`Internal/Layers/UAFLayerBlendProviderBase.h` 和 `Internal/Layers/UAFLayerDefaultBlendProvider.h`

```cpp
USTRUCT()
struct FMyCustomBlendProvider : public FUAFLayerBlendProviderBase
{
    GENERATED_BODY()

public:
    // 创建混合逻辑的 RigVM trait 节点
    // 返回最终输出引脚，可被后续层引用或链接到结果
    virtual URigVMPin* CreateBlendGraphTrait(
        UE::UAF::Layering::FLayerCreationContext& LayerCreationContext) override
    {
        return nullptr;
    }

    // 创建混合设置的编辑器 Widget
    virtual TSharedRef<SWidget> CreateLayerBlendWidget(UUAFLayer* InLayer) override
    {
        return SNullWidget::NullWidget;
    }

    // 可选：覆盖该层在编辑器中的背景样式
    virtual const FSlateBrush* GetOverrideLayerBackground() const override
    {
        return nullptr;
    }

    // 可选：覆盖该层在编辑器中的指示器颜色
    virtual bool GetOverrideIndicatorColor(FSlateColor& OutSlateColor) const override
    {
        return false;
    }

    // 设置是否始终更新子层（即使此层权重为 0）
    void SetAlwaysUpdateChildren(bool bInAlwaysUpdate)
    {
        bAlwaysUpdateChildren = bInAlwaysUpdate;
    }

    // 自定义混合参数
    UPROPERTY(EditAnywhere, Category = "Layer")
    EUAFLayerBlendMode BlendMode = EUAFLayerBlendMode::Blend;

    UPROPERTY(EditAnywhere, Category = "Layer",
        meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float LayerWeight = 1.0f;
};
```

### 进阶用法 — 理解层栈编译上下文

层栈在编译时通过 `FLayerCreationContext` 将所有层转换为 RigVM 图节点。

来源：`Public/LayeringUncookedOnlyTypes.h`

```cpp
// FLayerCreationContext 在层栈编译时被传递给每一层的 CreateLayerContentTrait 和 CreateBlendGraphTrait
namespace UE::UAF::Layering
{
    struct FLayerCreationContext
    {
        // 编译设置，可用于报告错误
        const FRigVMCompileSettings& CompileSettings;

        // 当前层栈
        TObjectPtr<UUAFLayerStack> LayerStack;

        // 当前正在生成的层
        TObjectPtr<UUAFLayer> Layer;

        // 控制底层 RigVM 图的 UAF Controller
        TObjectPtr<UAnimNextController> GraphController;

        // 输入引脚：[0] = 上一层输出, [1] = 当前层内容输出
        TArray<URigVMPin*> LayerInputs;

        // 上一个创建的节点位置，用于构建可读的图布局
        FVector2D LastNodeLocation;
    };
}
```

## Demo 示例

### 自定义内容提供器 + 混合提供器组合

```cpp
// MyAnimLayerProvider.h
#pragma once

#include "CoreMinimal.h"
#include "Layers/UAFLayerContentProviderBase.h"
#include "Layers/UAFLayerBlendProviderBase.h"
#include "LayeringUncookedOnlyTypes.h"
#include "MyAnimLayerProvider.generated.h"

// 内容提供器：播放指定的动画序列
USTRUCT(DisplayName = "Animation Sequence Layer")
struct FMySequenceContentProvider : public FUAFLayerContentProviderBase
{
    GENERATED_BODY()

public:
    virtual URigVMPin* CreateLayerContentTrait(
        UE::UAF::Layering::FLayerCreationContext& Context) override
    {
        // 在此处通过 Context.GraphController 创建动画播放节点
        // 通常会创建一个 AnimNext 的采样节点来播放 SequenceAsset
        // 返回内容 trait 的输出引脚
        return nullptr;
    }

    virtual TSharedRef<SWidget> CreateLayerContentWidget(UUAFLayer* InLayer) override
    {
        // 返回一个显示资产选择器的 Widget
        return SNullWidget::NullWidget;
    }

#if WITH_EDITOR
    virtual void GetObjectReferences(TArray<const UObject*>& OutRefs) const override
    {
        // 声明对 SequenceAsset 的引用
    }
#endif

    UPROPERTY(EditAnywhere, Category = "Content")
    TObjectPtr<UAnimSequence> SequenceAsset = nullptr;
};

// 混合提供器：自定义 Additive 混合
USTRUCT(DisplayName = "Custom Additive Blend")
struct FMyAdditiveBlendProvider : public FUAFLayerBlendProviderBase
{
    GENERATED_BODY()

public:
    virtual URigVMPin* CreateBlendGraphTrait(
        UE::UAF::Layering::FLayerCreationContext& Context) override
    {
        // 创建 Additive 混合节点
        // Context.LayerInputs[0] 是前一层输出
        // Context.LayerInputs[1] 是当前层内容输出
        // 将两者通过 Additive 方式混合并返回输出引脚
        return nullptr;
    }

    virtual TSharedRef<SWidget> CreateLayerBlendWidget(UUAFLayer* InLayer) override
    {
        return SNullWidget::NullWidget;
    }

    UPROPERTY(EditAnywhere, Category = "Blend",
        meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float AdditiveWeight = 1.0f;
};
```

## 模块依赖

从 Build.cs 分析，该插件依赖 UAF 核心框架和 Workspace 系统：

| 模块 | 用途 |
|---|---|
| `AnimNext` | UAF 动画框架核心，提供 AnimGraph、Controller、RigVM 编译等基础设施 |
| `Workspace` | 工作空间系统，提供资产编辑器集成和 Outliner 支持 |
| `ControlRig` | RigVM 图系统，层叠栈底层通过 RigVM 节点实现动画混合逻辑 |
| `AnimationCore` | 动画核心类型，混合配置文件（BlendProfile）等 |
| `RigVM` | RigVM 虚拟机，层栈编译后生成的节点图运行环境 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF |
| 2026-04-10 | `797a6da6` | Rename GetComponent to GetOrAddComponent to match functionality | 重命名函数以匹配实际行为，API 修正 |
| 2026-03-05 | `dd5531fb` | UAF Layering: | UAF Layering 相关改动（信息不完整） |
| 2026-03-04 | `d9a06590` | Update UAF blend profiles | 更新混合配置文件功能 |
| 2026-03-04 | `95766f52` | UAF Layering: Expand outliner items per default | 层栈编辑器中默认展开 Outliner 列表项 |

### 维护评价

- **创建时间**：2026-01-13，非常新的插件（约 3 个月）
- **更新频率**：保持月度更新节奏，最近一次改动在 2026 年 4 月
- **活跃程度**：**活跃开发中** — 作为 UAF 框架的重要子系统，持续有功能迭代和 API 修正
- **已知限制**：
  - 标记为 `IsExperimentalVersion: true`，API 可能随时变化
  - 默认未启用（`EnabledByDefault: false`），需要手动在插件管理器中开启
  - 部分属性标记为 `TODO: This should be a binding`，说明绑定系统尚未完全实现
  - 5.8 版本中有 deprecated 字段（`LayerAsset_DEPRECATED`、`Parameters_DEPRECATED`），API 正在演进
- **推荐程度**：⚠️ **仅供研究和实验使用**。如果你正在为 UAF 框架开发动画系统，这是一个重要的参考插件；但目前不适合作为生产依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- [UAF 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF)