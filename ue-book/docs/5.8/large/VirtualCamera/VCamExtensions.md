# VirtualCamera

> Content for VirtualCameraCore which adds actors, components, and utilities for controlling and viewing cameras via physical devices.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟摄像机 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、组件、工具类） |
| 模块 | `VCamExtensions` (Runtime), `VCamExtensionsEditor` (Runtime), `VirtualCamera` (Runtime), `VirtualCameraEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera) | |

## 用途

此插件是 Unreal Engine 虚拟制作工具集的核心组件，旨在通过物理设备（如平板电脑、手机或专用硬件）来远程控制和监视引擎内的摄像机。其主要功能是提供一套完整的框架，用于在设备端与 UE 内运行时摄像机之间建立实时连接、同步状态和传递输入命令。它解决了虚拟拍摄（Virtual Production）流程中，摄影指导或操作员能够灵活、实时地控制场景摄像机视图和参数的核心需求。

## 使用场景

*   你在进行一场虚拟制作拍摄，需要摄影指导通过平板设备上的专用 App 实时调整引擎中主摄像机的推、拉、摇、移、变焦和焦点。
*   你正在开发一个需要外部物理控制器（如游戏手柄、MIDI 控制器或自定义硬件）来精细操纵场景摄像机位置和旋转的交互式应用。
*   你需要在分布式团队中，让多个参与者同时查看或协同控制同一虚拟场景的不同摄像机视角。

## 蓝图用法

`VCamExtensions` 模块主要提供了用于配置虚拟摄像机 UI 样式和组织修饰符层次结构的框架。核心节点集中在配置 UI 显示样式和定义逻辑分组上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRootNode` | 获取修饰符层次结构树的根节点名称 | `UModifierHierarchyRules`, `UModifierHierarchyAsset` |
| `GetChildNodes` | 获取指定父节点下的所有子节点名称集合 | `UModifierHierarchyRules`, `UModifierHierarchyAsset` |
| `GetParentNode` | 获取指定子节点的父节点名称 | `UModifierHierarchyRules`, `UModifierHierarchyAsset` |
| `GetModifierInNode` | 在指定的 VCamComponent 中，获取属于指定层次节点的修饰符 | `UModifierHierarchyRules`, `UModifierHierarchyAsset` |
| `GetStylesForModifier` | 获取与指定修饰符关联的所有 UI 样式数据 | `UModifierBoundWidgetStyleDefinitions`, `UModifierBoundWidgetStylesAsset` |
| `GetStylesForConnectionPoint` | 获取指定修饰符上某个连接点关联的 UI 样式数据 | `UModifierBoundWidgetStyleDefinitions`, `UModifierBoundWidgetStylesAsset` |
| `GetStyleForModifierByClass` | 按特定类型获取与指定修饰符关联的 UI 样式数据 | `UModifierBoundWidgetStyleDefinitions`, `UModifierBoundWidgetStylesAsset` |

### 使用示例（蓝图描述）

1.  **创建层次规则资产**：在内容浏览器中右键，创建 `UModifierHierarchyAsset` 资产。在该资产的细节面板中，实例化一个 `UModifierHierarchyRules` 的子类（如 `UTargetModifierPerNodeHierarchyRules`）作为 `Rules` 属性，并根据需要配置其层次节点。
2.  **配置 UI 样式**：创建 `UModifierBoundWidgetStylesAsset` 资产，实例化 `UModifierBoundWidgetStyleDefinitions` 的子类（如 `UClassBasedWidgetStyleDefinitions`）。在配置中，将特定的修饰符类（如控制焦距的 `UVCamModifier` 子类）映射到 `UWidgetStyleData` 的子类实例（如 `UButtonWidgetStyleData`，可设置按钮外观）。
3.  **在运行时查询**：在蓝图中，引用上述资产，调用 `GetChildNodes(“Root”)` 获取根节点下的第一级分组（如 “Lens”, “Transform”）。对于 “Lens” 分组，调用 `GetModifierInNode(MyVCamComponent, “Lens”)` 获取对应的修饰符实例，然后调用 `GetStylesForModifier(RetrievedModifier)` 或 `GetStyleForModifierByClass(RetrievedModifier, UButtonWidgetStyleData::StaticClass())` 来获取用于在设备 UI 上渲染该修饰符控制项的样式信息（如图标、按钮风格）。

## C++ 用法

`VCamExtensions` 模块提供了用于构建自定义层次结构和样式规则的基础类。开发者通常需要继承并实现这些抽象类或资产。

### 头文件引入

```cpp
#include “Hierarchies/ModifierHierarchyRules.h”
#include “Styling/ModifierBoundWidgetStyleDefinitions.h”
#include “Hierarchies/ModifierHierarchyAsset.h”
```

### 基本用法

自定义一个基于类的 UI 样式定义。

```cpp
// 来源：基于 Public/Styling/ClassBasedWidgetStyleDefinitions.h 推断
UCLASS()
class UMyCustomClassBasedStyleDefinitions : public UClassBasedWidgetStyleDefinitions
{
    GENERATED_BODY()

public:
    UMyCustomClassBasedStyleDefinitions()
    {
        // 示例：为 UMyFocalLengthModifier 类关联一个按钮样式
        FWidgetStyleDataConfig StyleConfig;
        UButtonWidgetStyleData* ButtonStyle = NewObject<UButtonWidgetStyleData>(this);
        ButtonStyle->ButtonStyle = FCoreStyle::Get().GetWidgetStyle<FButtonStyle>(“Button”); // 使用引擎默认按钮样式
        StyleConfig.ModifierMetaData.Add(ButtonStyle);
        Config.Add(UMyFocalLengthModifier::StaticClass(), {StyleConfig, {}});
    }
};
```

### 进阶用法

结合层次结构资产和样式资产在运行时动态生成 UI 信息。

```cpp
// 来源：基于 Public/Hierarchies/ModifierHierarchyAsset.h 和 Public/Styling/ModifierBoundWidgetStylesAsset.h 推断
void GenerateUIForVCam(UVCamComponent* VCamComponent, UModifierHierarchyAsset* HierarchyAsset, UModifierBoundWidgetStylesAsset* StyleAsset)
{
    if (!VCamComponent || !HierarchyAsset || !StyleAsset) return;

    // 1. 从层次结构中获取所有顶级组（例如菜单的顶级分类）
    TArray<FName> TopGroups = HierarchyAsset->GetChildNodes(HierarchyAsset->GetRootNode());

    for (const FName& GroupName : TopGroups)
    {
        // 2. 获取属于该组的修饰符
        UVCamModifier* Modifier = HierarchyAsset->GetModifierInNode(VCamComponent, GroupName);
        if (Modifier)
        {
            // 3. 为该修饰符获取样式信息
            TArray<UWidgetStyleData*> Styles = StyleAsset->GetStylesForModifier(Modifier);
            for (UWidgetStyleData* StyleData : Styles)
            {
                // 4. 检查具体样式类型并应用（例如生成按钮）
                if (UButtonWidgetStyleData* ButtonStyle = Cast<UButtonWidgetStyleData>(StyleData))
                {
                    // 使用 ButtonStyle->ButtonStyle 创建或更新一个 Slate 按钮控件
                    UE_LOG(LogVCamExtensions, Log, TEXT(“Generating button for modifier %s in group %s”), *Modifier->GetName(), *GroupName.ToString());
                }
            }
        }
    }
}
```

## Demo 示例

一个最小的、可编译的自定义层次规则示例。

**MyCustomHierarchyRules.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “Hierarchies/ModifierHierarchyRules.h”
#include “MyCustomHierarchyRules.generated.h”

UCLASS()
class UMyCustomHierarchyRules : public UModifierHierarchyRules
{
    GENERATED_BODY()

public:
    UMyCustomHierarchyRules();

    //~ Begin UModifierHierarchyRules Interface
    virtual FName GetRootNode_Implementation() const override;
    virtual bool GetParentNode_Implementation(FName ChildNode, FName& ParentNode) const override;
    virtual TSet<FName> GetChildNodes_Implementation(FName Node) const override;
    virtual UVCamModifier* GetModifierInNode_Implementation(UVCamComponent* Component, FName NodeName) const override;
    virtual TSet<FName> GetNodesContainingModifier_Implementation(UVCamModifier* Modifier) const override;
    //~ End UModifierHierarchyRules Interface

private:
    // 定义一些固定的组名
    static const FName RootGroupName;
    static const FName LensGroupName;
    static const FName FocusGroupName;
};
```

**MyCustomHierarchyRules.cpp**
```cpp
#include “MyCustomHierarchyRules.h”

const FName UMyCustomHierarchyRules::RootGroupName = TEXT(“All”);
const FName UMyCustomHierarchyRules::LensGroupName = TEXT(“Lens”);
const FName UMyCustomHierarchyRules::FocusGroupName = TEXT(“Focus”);

UMyCustomHierarchyRules::UMyCustomHierarchyRules()
{
}

FName UMyCustomHierarchyRules::GetRootNode_Implementation() const
{
    return RootGroupName;
}

bool UMyCustomHierarchyRules::GetParentNode_Implementation(FName ChildNode, FName& ParentNode) const
{
    if (ChildNode == LensGroupName || ChildNode == FocusGroupName)
    {
        ParentNode = RootGroupName;
        return true;
    }
    return false; // Root 没有父节点
}

TSet<FName> UMyCustomHierarchyRules::GetChildNodes_Implementation(FName Node) const
{
    if (Node == RootGroupName)
    {
        return { LensGroupName, FocusGroupName };
    }
    return {}; // 叶子节点没有子节点
}

UVCamModifier* UMyCustomHierarchyRules::GetModifierInNode_Implementation(UVCamComponent* Component, FName NodeName) const
{
    // 此处仅为示例，实际应根据组件内修饰符名称或类型进行匹配
    if (NodeName == FocusGroupName && Component)
    {
        // 假设组件中有一个名为 “FocusModifier” 的修饰符
        return FindObject<UVCamModifier>(Component, TEXT(“FocusModifier”));
    }
    return nullptr;
}

TSet<FName> UMyCustomHierarchyRules::GetNodesContainingModifier_Implementation(UVCamModifier* Modifier) const
{
    // 反向查询，对于示例中的 FocusModifier，它属于 FocusGroup
    if (Modifier && Modifier->GetName() == TEXT(“FocusModifier”))
    {
        return { FocusGroupName };
    }
    return {};
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该模块（VCamExtensions）提供基础框架，被其他更具体的模块（如 `VirtualCamera`）使用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 调整虚拟制作资产的目录分类并进行了迁移。 |
| 2026-04-20 | `9de9532f` | VCam: update transform track mask based on constraint filter | 根据约束过滤器更新摄像机变换轨道的遮罩。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的全局查找替换后，进行的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了变更列表 CL51314860 的修改。 |

### 维护评价

**积极维护中**。该插件创建于 2024 年初，最近的代码提交记录持续至 2026 年 5 月，表明 Epic Games 团队仍在对其进行功能更新和 bug 修复。从提交信息看，工作包括资产迁移、功能增强（如约束过滤器）和代码质量改进（日志宏迁移）。作为虚幻引擎虚拟制作工具集的重要组成部分，它目前处于活跃开发状态，且标记为测试版 (`IsBetaVersion=true`)，这意味着其 API 可能在未来版本中发生变化。推荐在虚拟制作项目中尝试使用，但需注意其测试版状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCamera)
- 官方文档：未提供
- 测试用例：未提供，可在 Engine/Tests 目录下搜索相关自动化测试。