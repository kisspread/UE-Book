# Material Designer Texture Set Editor

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 中文名 | 纹理集编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产与蓝图） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

DynamicMaterialTextureSetEditor 插件是“Material Designer”（材质设计器）套件中的一个**编辑器扩展**模块，专注于**纹理集 (Texture Set)** 的高效创建与管理。它解决的核心问题是：在虚拟制片或复杂的材质工作流程中，艺术家通常需要将一组相关的纹理（如基础颜色、法线、粗糙度等 PBR 贴图）打包成一个逻辑单元——“纹理集”，以便于管理、分配和使用。此插件提供了一个图形化界面，允许用户通过**拖放**和**自动筛选**的方式，快速地将多个零散的纹理资产组织成一个统一的纹理集资产 (`UDMTextureSet`)，并智能地将它们映射到不同的材质属性通道上。

## 使用场景

- 你是一名虚拟制片或关卡美术，在 Content Browser 中积攒了一堆 PBR 贴图文件（如 `T_Rock_BaseColor.png`, `T_Rock_Normal.png`, `T_Rock_Roughness.png`），需要快速将它们整合成一个名为 `TS_Rock` 的纹理集，以便在材质实例中一次性引用。
- 你希望自定义一套命名规则（例如，所有以 `_ORM` 结尾的纹理都应映射到材质的 Ambient Occlusion、Roughness 和 Metallic 通道），并让工具自动完成分配，节省手动配置的时间。
- 你需要在编辑器中通过一个直观的交互面板，对纹理到材质属性的映射关系进行检查和手动调整，确保最终的纹理集符合预期。

## 蓝图用法

插件暴露了一个蓝图函数库 `UDMTextureSetBlueprintFunctionLibrary`，提供了用于创建纹理集的静态节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Texture Set From Assets` | 根据提供的资产数组，使用预设的过滤器规则自动创建纹理集。如果无纹理匹配，则返回 `nullptr`。 | `UDMTextureSetBlueprintFunctionLibrary` |
| `Create Texture Set From Assets (Interactive)` | 根据提供的资产数组和过滤器规则创建纹理集，但会弹出一个交互式 UI 面板，允许用户确认和调整插槽分配，操作完成后通过委托回调通知。 | `UDMTextureSetBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

**基本创建流程：**
1.  获取一组 `FAssetData` 类型的纹理资产（例如，通过 `Get Assets by Filter` 节点或直接拖入 Content Browser 中的资产引用）。
2.  将这些资产连接到 `Create Texture Set From Assets` 节点的 `In Assets` 输入引脚。
3.  该节点的输出引脚即为新创建的 `UDMTextureSet` 对象，你可以将其保存到磁盘或用于后续操作。

**交互式创建流程：**
1.  同样获取一组纹理资产。
2.  使用 `Create Texture Set From Assets (Interactive)` 节点，并连接一个自定义事件到 `In On Complete` 委托引脚。
3.  调用节点后，编辑器会弹出一个对话框。在该对话框中，你可以：
    *   查看每个材质属性（如基础颜色、法线）被自动分配了哪个纹理。
    *   通过拖放操作，在“已分配”和“未分配”区域之间或不同属性之间交换纹理。
    *   调整每个纹理的通道遮罩。
    *   点击“接受”或“取消”完成操作。
4.  操作结果将通过之前连接的委托事件回调。

## C++ 用法

### 头文件引入

```cpp
#include "DMTextureSetBlueprintFunctionLibrary.h"
#include "DMTextureSetFactory.h"
#include "DMTextureSetSettings.h" // 如需自定义过滤器
```

### 基本用法

通过工厂或蓝图函数库创建纹理集。

```cpp
// 1. 准备纹理资产数据
TArray<FAssetData> TextureAssets;
// ... 填充 TextureAssets 数组，例如从 Asset Registry 查询获得 ...

// 2. 使用工厂创建（更底层的方式，适用于需要更多控制的情况）
UDMTextureSetFactory* TextureSetFactory = NewObject<UDMTextureSetFactory>();
UDMTextureSet* NewTextureSet = Cast<UDMTextureSet>(TextureSetFactory->FactoryCreateNew(
    UDMTextureSet::StaticClass(),
    GetTransientPackage(), // 或者你希望的父包
    NAME_None,
    RF_Transient,
    nullptr,
    GWarn
));

// 3. 使用蓝图函数库（更便捷）
UDMTextureSet* NewTextureSetViaBPFunc = UDMTextureSetBlueprintFunctionLibrary::CreateTextureSetFromAssets(TextureAssets);
```
*(代码灵感来源于 `DMTextureSetFactory.h` 和 `DMTextureSetBlueprintFunctionLibrary.h` 中的函数声明)*

### 进阶用法

自定义纹理集过滤规则，影响自动创建的结果。

```cpp
// 获取或自定义纹理集设置（通常通过编辑器 UI 配置，此处演示代码访问）
UDMTextureSetSettings* Settings = UDMTextureSetSettings::Get();
if (Settings)
{
    // 创建一个新的过滤器规则
    FDMTextureSetFilter NewFilter;
    NewFilter.FilterStrings.Add(TEXT("_Normal")); // 匹配名称中包含 “_Normal” 的纹理
    // 将匹配的纹理映射到材质的法线贴图通道，并使用 RGB 通道
    NewFilter.MaterialProperties.Add(EDMTextureSetMaterialProperty::Normal, EDMTextureChannelMask::RGB);
    
    // 添加到全局设置中
    Settings->Filters.Add(NewFilter);
    Settings->SaveConfig(); // 保存设置
}

// 之后，再次调用 CreateTextureSetFromAssets 时，便会使用更新后的过滤规则进行匹配和分配。
```
*(代码灵感来源于 `DMTextureSetSettings.h` 和 `DMTextureSetFilter.h` 中的结构体定义)*

## Demo 示例

一个最小示例，展示如何在C++中创建一个纹理集并查询其信息。

**头文件 (TextureSetDemo.h):**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DMTextureSet.h"
#include "TextureSetDemo.generated.h"

UCLASS()
class UTextureSetDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "TextureSetDemo")
    static UDMTextureSet* CreateDemoTextureSet(const TArray<FAssetData>& InTextures);

    UFUNCTION(BlueprintCallable, Category = "TextureSetDemo")
    static FString GetTextureSetInfo(const UDMTextureSet* InTextureSet);
};
```

**源文件 (TextureSetDemo.cpp):**
```cpp
#include "TextureSetDemo.h"
#include "DMTextureSetBlueprintFunctionLibrary.h"
#include "DMTextureSet.h"
#include "Engine/Texture.h"

UDMTextureSet* UTextureSetDemo::CreateDemoTextureSet(const TArray<FAssetData>& InTextures)
{
    // 直接复用插件提供的便捷函数
    return UDMTextureSetBlueprintFunctionLibrary::CreateTextureSetFromAssets(InTextures);
}

FString UTextureSetDemo::GetTextureSetInfo(const UDMTextureSet* InTextureSet)
{
    if (!InTextureSet)
    {
        return TEXT("Invalid Texture Set");
    }

    FString Info = FString::Printf(TEXT("Texture Set: %s\n"), *InTextureSet->GetName());
    // 假设 UDMTextureSet 有方法获取其内部纹理映射，此处为示意
    // Info += TEXT("Contains textures for: BaseColor, Normal, ...");
    return Info;
}
```

## 模块依赖

该插件（DynamicMaterialTextureSetEditor 模块）自身依赖于 DynamicMaterialTextureSet 运行时模块，并大量使用了 Slate 和 Content Browser 集成功能。对于想要使用此插件API的项目模块，通常需要如下依赖：

| 模块 | 用途 |
|---|---|
| `DynamicMaterialTextureSet` | 核心运行时数据类型，如 `UDMTextureSet`、`EDMTextureSetMaterialProperty` 等。 |
| `ContentBrowser` | 集成到内容浏览器右键菜单。 |
| `AssetDefinition` | 定义资产的显示和交互行为。 |
| `PropertyEditor` | 用于自定义细节面板和属性编辑器（如纹理集过滤器设置）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | Motion Design 标签页移动，表明插件作为 Motion Design 项目的一部分仍在被整体管理。 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口代码重构，为客户端关联/断开添加通知。属于底层框架改进。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚一个提交。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口代码重构的另一个相关提交。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的编译警告。 |

### 维护评价

**创建时间较短，处于活跃期**。插件在 2025 年 5 月作为 “Material Designer” 项目的一部分从 Experimental 目录迁移至 Virtual Production，表明其已脱离实验状态。从最近的 git 记录看，虽然近期提交主要集中在与该插件并行开发的其他 “Motion Design” 模块（如视口重构、标签页调整），但底层框架（如代码警告修复）的更新表明整个项目仍在活跃维护中。

该插件的代码结构完整，包含运行时、编辑器模块、蓝图API、自定义资产定义和Content Browser集成，是一个功能闭环的编辑器工具。目前没有发现重大已知问题或废弃标记。

**推荐使用**，尤其适合需要在虚拟制片工作流中高效管理纹理资产的团队。作为 Epic Games 官方推出的插件，其质量和与引擎的集成度有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DynamicMaterial)
- [官方文档]() (暂无)
- [测试用例]() (插件目录内未发现公开测试文件)