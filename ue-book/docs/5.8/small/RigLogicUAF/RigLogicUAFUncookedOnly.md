# RigLogic for UAF

> RigLogic for UAF

| 属性 | 值 |
|---|---|
| 中文名 | RigLogic UAF集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RigLogicUAF` (Runtime), `RigLogicUAFUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RigLogicUAF) | |

## 用途

此插件的核心目的是将 `RigLogic` 面部动画驱动系统集成到 Unreal Engine 的 **UAF (Unreal Animation Framework)** 动画框架中。它提供了一个预定义的动画图节点模板 (`UUAFGraphNodeTemplate_RigLogic`)，允许开发者在UAF动画图中方便地使用RigLogic功能，以驱动高品质的面部表情动画和相关身体校正。本质上，它是连接专业动画技术（RigLogic）与UE5现代化动画系统（UAF）的桥梁。

## 使用场景

-   你正在开发一个需要**高品质、逼真面部动画**的数字人项目，尤其是与 MetaHuman 配合使用时。
-   你的项目采用了 **UAF** 作为主要的动画系统架构，并希望将先进的 RigLogic 面部动画驱动能力集成到 UAF 动画图中。
-   你需要一个标准化的、易于配置的节点来处理面部骨骼变换和混合形状（Blend Shape）曲线的输出。

## 蓝图用法

该插件主要通过 UAF 动画图编辑器提供蓝图节点，而非直接暴露 `BlueprintCallable` 函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RigLogic` | UAF 动画图节点。执行面部动画驱动，并在适用时驱动身体校正。 | `UUAFGraphNodeTemplate_RigLogic` |

### 使用示例（蓝图描述）

1.  在 **UAF 动画图编辑器**中，从节点菜单的 **UAF** 分类下找到并拖入 **RigLogic** 节点。
2.  该节点具有两个输入引脚：
    -   **Input**：连接一个输入姿态（例如，来自之前的动画节点）。
    -   **Enabled**：一个布尔型开关，用于动态控制该节点是否生效。
3.  节点的输出将自动包含被 RigLogic 覆盖的**关节变换（Joint Transforms）** 和用于驱动**混合形状（Blend Shapes）及动画贴图（Animated Maps）** 的**曲线（Curves）**。

## C++ 用法

### 头文件引入

```cpp
// 主要用于引擎内部或工具开发
#include "UAFGraphNodeTemplate_RigLogic.h"
#include "RigLogicUAFUncookedOnly.h"
```

### 基本用法

该插件的核心是提供一个动画图节点模板类。以下是该模板的初始化配置（从源码中提取），展示了其属性的设定方式：

```cpp
// 源自 Engine/Plugins/Experimental/RigLogicUAF/Source/RigLogicUAFUncookedOnly/Public/UAFGraphNodeTemplate_RigLogic.h
UCLASS()
class UUAFGraphNodeTemplate_RigLogic : public UUAFGraphNodeTemplate
{
    GENERATED_BODY()

    UUAFGraphNodeTemplate_RigLogic()
    {
        Title = LOCTEXT("RigLogicUAFTitle", "RigLogic");
        TooltipText = LOCTEXT("RigLogicUAFTooltip", "RigLogic\n"
            "Performs facial animation and drives body correctives where applicable.\n"
            "Input: Input Pose\n"
            "Output: Overwritten joint transforms, and curves to drive blend shapes and animated maps.");
        Category = LOCTEXT("RigLogicUAFCategory", "UAF");
        MenuDescription = LOCTEXT("RigLogicUAFMenuDesc", "RigLogic");
        Color = FLinearColor(FColor(38, 187, 255));
        // 从 UncookedOnly 模块获取图标
        Icon = UE::UAF::FRigLogicModuleUncookedOnly::GetIcon();

        // 配置用于控制启用的混合特性（Passthrough Blend Trait）
        FPassthroughBlendTraitSharedData PassthroughData;
        PassthroughData.AlphaInputType = EAnimAlphaInputType::Bool;

        // 组合该节点包含的所有特性（Traits）
        Traits =
        {
            TInstancedStruct<FUAFRigLogicTraitSharedData>::Make(),
            TInstancedStruct<FPassthroughBlendTraitSharedData>::Make(PassthroughData)
        };
        // ... 省略布局配置代码 ...
    }
};
```

### 进阶用法

了解 `FRigLogicModuleUncookedOnly` 模块类，它负责提供插件所需的编辑器资源（如图标）和进行模块的初始化与清理。

```cpp
// 源自 Engine/Plugins/Experimental/RigLogicUAF/Source/RigLogicUAFUncookedOnly/Public/RigLogicUAFUncookedOnly.h
DECLARE_LOG_CATEGORY_EXTERN(LogRigLogicUAFUncookedOnly, Log, All);

namespace UE::UAF
{
    class FRigLogicModuleUncookedOnly : public IModuleInterface
    {
    public:
        virtual void StartupModule() override;
        virtual void ShutdownModule() override;

        // 静态方法，用于获取插件在编辑器中显示的图标（Slate Brush）
        static const FSlateBrush& GetIcon();
    };
} // namespace UE::UAF
```

## Demo 示例

虽然此插件主要通过蓝图（动画图节点）使用，但以下代码演示了如何在 C++ 中访问插件提供的模块接口：

```cpp
// MyAnimGraphEditorTool.h
#pragma once
#include "CoreMinimal.h"

class FMyAnimGraphEditorTool
{
public:
    void Initialize()
    {
        // 获取 RigLogicUAFUncookedOnly 模块
        FRigLogicModuleUncookedOnly* RigLogicModule = FModuleManager::GetModulePtr<FRigLogicModuleUncookedOnly>(TEXT("RigLogicUAFUncookedOnly"));
        if (RigLogicModule)
        {
            // 获取插件定义的图标，可用于自定义编辑器UI
            const FSlateBrush& RigLogicIcon = RigLogicModule->GetIcon();
            // 使用 RigLogicIcon ... (例如设置到一个 Slate Image 控件上)
        }
    }
};
```

**注意**：实际开发中，开发者主要通过 UAF 动画图编辑器使用 `RigLogic` 节点，而无需直接编写上述 C++ 代码。

## 模块依赖

你的项目模块如果需要与 `RigLogicUAF` 插件深度集成，可能需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `RigLogic` | 核心的 RigLogic 动画驱动库和类型定义 |
| `UAF` | Unreal Animation Framework 核心运行时模块 |
| `UAFAnimGraph` | UAF 动画图的编辑器和运行时支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `de315afa` | Fix compile error for RigLogicUAF test module | 修复了RigLogicUAF测试模块的编译错误。 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为所有三个RigLogic运行时集成实现了统一的集成测试。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位和64位格式说明符不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移至UE_LOGF日志系统。 |
| 2026-03-18 | `d5252a70` | RigLogicUAF: Support new UDNAAssetUserData in addition to legacy UDNAAsset | 现在支持新的UDNAAssetUserData，同时兼容旧版UDNAAsset。 |

### 维护评价

- **创建时间**：2025年8月创建，相对年轻。
- **近期活动**：最后一次更新在2026年5月，包含测试修复和功能增强（支持新资产类型），表明仍在积极维护。
- **维护状态**：**活跃维护中**。Epic官方团队正在对其开发和测试。
- **已知限制**：作为实验性插件（`IsExperimentalVersion=true`），API和功能可能在未来版本中发生变化，不建议在追求稳定性的正式项目中作为核心依赖。
- **推荐使用**：如果你正在实验性地构建基于UAF的数字人或高级面部动画管线，并且希望快速集成RigLogic，可以尝试使用。但对于生产环境，需密切关注其更新和稳定性公告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RigLogicUAF)
- [官方文档]( ) （暂无）