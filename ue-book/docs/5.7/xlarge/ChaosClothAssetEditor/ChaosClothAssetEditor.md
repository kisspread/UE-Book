# Chaos Cloth Asset Editor

> Editor for modifying cloth assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `ChaosClothAssetDataflowNodes` (Runtime), `ChaosClothAssetEditor` (Runtime), `ChaosClothAssetEditorTools` (Runtime), `ChaosClothAssetTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

ChaosClothAssetEditor 是一个用于创建、编辑和预览基于 Chaos 物理引擎的布料资产的完整编辑器系统。它解决的核心问题是：为美术师和开发者提供一个可视化的、基于节点图的工具，用于定义布料的物理属性、约束和模拟行为，而无需直接编写复杂的物理参数代码。该插件是 UE5 Chaos 布料系统在编辑器层面的核心工具链。

## 使用场景

- 你正在为角色或物体创建复杂的布料模拟（如披风、旗帜、衣物），需要精细控制布料的拉伸、弯曲、碰撞等物理属性。
- 你需要一个可视化的节点图编辑器（Dataflow）来构建和调试布料资产的生成逻辑。
- 你需要在编辑器中实时预览布料资产在不同姿态下的模拟效果，并生成缩略图。
- 你正在开发需要集成自定义布料数据处理流程的工具或管线。

## 蓝图用法

本插件的核心功能主要通过编辑器界面（如资产编辑器、细节面板）和数据流图（Dataflow Graph）暴露，而非传统的蓝图节点。其提供的 `UChaosClothAssetThumbnailRenderer` 等类主要由编辑器内部系统调用，用于资产预览。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetClothAsset` | 为缩略图预览场景设置要渲染的布料资产 | `UE::Chaos::ClothAsset::FThumbnailScene` |
| `GetClothComponent` | 获取用于预览的布料组件实例 | `AChaosClothPreviewActor` |

### 使用示例（蓝图描述）

在蓝图中直接操作这些类的场景较少。典型的工作流是：
1.  在内容浏览器中右键创建 `ChaosClothAsset`。
2.  双击打开资产，进入专用的布料资产编辑器界面。
3.  在编辑器中，通过“布料面板”或“数据流编辑器”选项卡，使用节点图定义布料的几何体、约束和模拟参数。
4.  编辑器会自动使用 `UChaosClothAssetThumbnailRenderer` 为资产生成预览缩略图。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ChaosClothAssetThumbnailRenderer.h"
```

### 基本用法

该模块主要提供编辑器扩展功能。一个典型的用法是注册自定义的缩略图渲染器，或扩展现有的布料预览场景。

```cpp
// 来源：Engine/Plugins/ChaosClothAssetEditor/Source/ChaosClothAssetEditor/Public/ChaosClothAsset/ChaosClothAssetThumbnailRenderer.h
// 展示如何为自定义布料资产类型创建缩略图渲染器
class UMyCustomClothAssetThumbnailRenderer : public UChaosClothAssetThumbnailRenderer
{
    GENERATED_BODY()
public:
    // 可以重写 Draw, CanVisualizeAsset 等函数来自定义渲染行为
    virtual bool CanVisualizeAsset(UObject* Object) override
    {
        // 检查对象是否是你的自定义布料资产类型
        return Cast<UMyCustomClothAsset>(Object) != nullptr;
    }
};
```

### 进阶用法

结合 `ChaosClothAssetTools` 模块，可以在 C++ 中程序化地创建或修改布料资产。

```cpp
// 假设的用法，结合 ChaosClothAssetTools 模块
#include "ChaosClothAssetToolsModule.h"

// 获取布料资产工具模块
IChaosClothAssetToolsModule& ClothAssetToolsModule = FModuleManager::Get().LoadModuleChecked<IChaosClothAssetToolsModule>(TEXT("ChaosClothAssetTools"));

// 使用工具模块提供的接口来创建或处理布料资产
// 具体函数需参考 ChaosClothAssetTools 模块的公开 API
```

## Demo 示例

以下示例展示了如何创建一个自定义的布料资产缩略图渲染器，并注册到引擎中。

```cpp
// MyClothThumbnailRenderer.h
#pragma once

#include "ChaosClothAsset/ChaosClothAssetThumbnailRenderer.h"
#include "MyClothThumbnailRenderer.generated.h"

class UMyClothAsset;

UCLASS()
class UMyClothThumbnailRenderer : public UChaosClothAssetThumbnailRenderer
{
    GENERATED_BODY()

public:
    virtual bool CanVisualizeAsset(UObject* Object) override;
    virtual void Draw(UObject* Object, int32 X, int32 Y, uint32 Width, uint32 Height, FRenderTarget* Viewport, FCanvas* Canvas, bool bAdditionalViewFamily) override;
};
```

```cpp
// MyClothThumbnailRenderer.cpp
#include "MyClothThumbnailRenderer.h"
#include "MyClothAsset.h"

bool UMyClothThumbnailRenderer::CanVisualizeAsset(UObject* Object)
{
    // 只能渲染我们自定义的布料资产
    return Cast<UMyClothAsset>(Object) != nullptr;
}

void UMyClothThumbnailRenderer::Draw(UObject* Object, int32 X, int32 Y, uint32 Width, uint32 Height, FRenderTarget* Viewport, FCanvas* Canvas, bool bAdditionalViewFamily)
{
    UMyClothAsset* MyAsset = Cast<UMyClothAsset>(Object);
    if (MyAsset)
    {
        // 在这里实现自定义的渲染逻辑
        // 通常可以调用父类的 Draw 方法，或完全重写
        Super::Draw(Object, X, Y, Width, Height, Viewport, Canvas, bAdditionalViewFamily);
    }
}
```

## 模块依赖

从模块名称和常见布料系统依赖推断，使用本插件需要以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 核心布料资产数据结构和运行时逻辑 |
| `ChaosCloth` | Chaos 布料物理模拟引擎 |
| `SkeletalMesh` | 骨骼网格体，布料通常附着其上 |
| `Dataflow` | 节点图编辑器框架，用于构建布料资产生成逻辑 |
| `GeometryFramework` | 几何体框架，可能用于布料网格体的编辑和显示 |
| `PropertyEditor` | 细节面板和属性自定义编辑器 |

## 维护状态

### 近期更新

```
- 1255b1ae5b50 Dataflow : cloth make sure we instantly update the viewport when updating cloth visualization menu
- 7eb102a3b02d Make the code to toggle between Cloth panel Editor and dataflow editor for cloth asset symmetrical - set the cloth panel editor to be default for 5.7
- 8e7ffc251b74 Datafolw : allow evaluation of the dataflow graph while in PIE for cloth asset - added evaluation settings to the dataflow editors
```

### 维护评价

- **活跃维护**：最近 3 次提交均在 2024 年内，且都是功能性更新（视图刷新、编辑器切换逻辑、PIE 中的数据流评估），表明该插件处于**积极开发**状态。
- **实验性**：`.uplugin` 中 `IsBetaVersion: true`，且 `EnabledByDefault: false`，表明它仍被视为实验性功能，API 和功能可能发生变化。
- **推荐使用**：对于需要在 UE5 中创建高质量布料模拟的项目，**推荐使用**。它是 Epic 官方提供的、与 Chaos 物理引擎深度集成的工具。但需注意其“实验性”状态，在生产环境中应做好应对未来变更的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor)
- [官方文档]() （暂无）
- [测试用例]() （暂未在插件目录内发现标准测试文件）