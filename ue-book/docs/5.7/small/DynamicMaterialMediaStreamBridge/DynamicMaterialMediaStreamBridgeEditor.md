# Material Designer Media Stream Bridge

> Integrates the Media Stream plugin with the Material Designer.

| 属性 | 值 |
|---|---|
| 中文名 | 材质设计师媒体流桥接 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DynamicMaterialMediaStreamBridge` (Runtime), `DynamicMaterialMediaStreamBridgeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge) | |

## 用途

本插件将 **Media Stream** 插件与 **Material Designer**（材质设计器）相集成。  
它允许材质设计器用户在材质图表中使用媒体流（如视频、摄像头）作为纹理输入，并提供编辑器工具用于配置媒体流属性、在场景中设置媒体层等。  
核心解决：**在材质设计器内便捷地使用动态媒体资源**，无需手动编写复杂的 C++ 或蓝图逻辑。

## 使用场景

- 你需要制作一个使用实时视频流或网络摄像头画面的材质 → 使用此插件将媒体流绑定到材质设计器节点。
- 你希望在材质设计器中对媒体源进行播放控制（播放、暂停、跳转等）并调节其属性 → 插件在属性面板中自动生成媒体流相关的属性分类。
- 你负责制作互动媒体装置或虚拟演播室，需要将多个媒体层混合 → 插件提供了“更改源”和“添加层”的菜单扩展。

## 蓝图用法

本插件主要提供编辑器集成，**无公开的蓝图调用节点**。  
媒体流的控制（播放/暂停/选择源等）需通过 Media Stream 插件的蓝图 API 完成。  
材质设计器中的属性编辑通过自动生成的属性行实现，无需手动调用函数。

## C++ 用法

### 头文件引入

```cpp
#include "UI/PropertyGenerators/DMComponentPropertyRowGenerator.h"
#include "DMMaterialValueMediaStreamPropertyRowGenerator.h"
#include "DMMediaStreamStageSourceMenuExtender.h"
```

### 基本用法：在材质设计器属性面板中集成媒体流属性

```cpp
// 获取单例生成器并添加属性行
const TSharedRef<FDMMaterialValueMediaStreamPropertyRowGenerator>& Generator = FDMMaterialValueMediaStreamPropertyRowGenerator::Get();

// 在合适的时机（如材质设计器打开时）调用 AddComponentProperties
FDMComponentPropertyRowGeneratorParams Params;
// ... 填充 Params（例如关联的 UMediaStream 组件）
Generator->AddComponentProperties(Params);
```
**来源文件**：`Private/DMMaterialValueMediaStreamPropertyRowGenerator.h`

### 进阶用法：扩展材质设计器右键菜单

```cpp
// 在模块启动时集成菜单扩展
FDMMediaStreamStageSourceMenuExtender::Get().Integrate();

// 内部实现 – 将媒体源选择注入到“更改源”菜单
void FDMMediaStreamStageSourceMenuExtender::ExtendMenu_ChangeSource(FToolMenuSection& InSection)
{
    // 添加“媒体流”菜单项
    InSection.AddMenuEntry(
        "ChangeSourceToMediaStream",
        FText::FromString("Media Stream"),
        FText::FromString("Change the material's source to a Media Stream"),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateStatic(&FDMMediaStreamStageSourceMenuExtender::ChangeSourceToMediaStreamFromContext))
    );
}
```
**来源文件**：`Private/DMMediaStreamStageSourceMenuExtender.h`

## Demo 示例

以下示例演示如何在材质设计器内将一个 UMediaStream 组件与材质参数绑定，并注册属性行生成器。

### .h

```cpp
// MyCustomMaterialDesignerIntegration.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "UI/PropertyGenerators/DMComponentPropertyRowGenerator.h"

class UMediaStream;
class UMaterialDesignerInstance;

class FMyMediaStreamIntegration
{
public:
    static void SetupMediaStreamPropertyRow(UMaterialDesignerInstance* InDesignerInstance, UMediaStream* InMediaStream);
};
```

### .cpp

```cpp
// MyCustomMaterialDesignerIntegration.cpp
#include "MyCustomMaterialDesignerIntegration.h"
#include "DMMaterialValueMediaStreamPropertyRowGenerator.h"
#include "UI/PropertyGenerators/DMComponentPropertyRowGeneratorParams.h"

void FMyMediaStreamIntegration::SetupMediaStreamPropertyRow(UMaterialDesignerInstance* InDesignerInstance, UMediaStream* InMediaStream)
{
    FDMComponentPropertyRowGeneratorParams Params;
    Params.Component = InMediaStream;   // 绑定媒体流组件
    Params.OwnerObject = InDesignerInstance;

    // 调用插件提供的生成器，填充属性面板
    FDMMaterialValueMediaStreamPropertyRowGenerator::Get().AddComponentProperties(Params);
}
```

将此函数在材质设计器打开媒体流时调用，即可自动在属性面板显示媒体流的控制项、源选择、纹理缓存等分类。

## 模块依赖

使用此插件前，你的模块需在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 材质设计器核心模块，提供材质图表编辑器 |
| `MediaStream` | 媒体流播放与控制模块，提供 `UMediaStream` 核心类 |
| `DynamicMaterialMediaStreamBridge` | 本插件的运行时模块，定义桥接逻辑 |

> 常见依赖（Core、CoreUObject、Engine、Slate、SlateCore、UMG、InputCore、UnrealEd、Projects 等）已省略，它们会被自动引入。

## 维护状态

### 近期更新

| 日期 | Hash | Commit 信息 |
|---|---|---|
| 2025-06-13 | `b366e598` | Material Designer: You can now save levels with Material Designer instances … |
| 2025-05-09 | `9070f107` | Media Stream: When choosing a media layer, now sets the mask stage to a 'use base' … |
| 2025-05-09 | `19d6a91f` | Media Stream: Player changes (as well as source changes) are now propagated. |
| 2025-05-09 | `c513bc93` | Material Designer: Changed order of change stage source and layer add menus. |
| 2025-05-06 | `967c5dd6` | Material Designer / Media Stream: Fixed remote control integration for source selector. |

### 维护评价

- **创建时间**：2025-05-06，距今约 0 年。
- **最近更新频率**：前两个月内（截至 2025-06-13）有多次功能性更新和 Bug 修复，说明团队在积极开发。
- **活跃度**：由于插件仍处于 Experimental 阶段，且版本号仅为 1.0，属于早期迭代期，预计后续会有更多特性加入。
- **已知限制**：实验性插件，API 可能变更；未发现官方已知问题。
- **推荐使用**：适合需要将媒体流与材质设计器深度集成的项目，但建议随时关注插件更新，避免 API 变动导致兼容性问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicMaterialMediaStreamBridge/Tests)（未提供，可能不存在）