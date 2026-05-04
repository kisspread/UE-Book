# UAF Layering

> Framework to define a layering setup in UAF

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `UAFLayering` (Runtime), `UAFLayeringEditor` (Runtime), `UAFLayeringUncookedOnly` (Runtime), `UAFLayeringTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering) | |

## 用途

UAF Layering 是 Unreal Animation Framework (UAF) 的一个实验性插件，它提供了一个用于定义和管理动画层叠（Layering）的框架。其核心目的是解决复杂动画混合场景下的组织和控制问题。

该插件允许用户创建一个“层栈”（Layer Stack），其中包含多个动画层。每个层可以独立配置其动画内容来源（如资产、蒙太奇）和混合行为（如权重、混合模式、遮罩）。在运行时，这些层会按照栈的顺序依次混合，最终生成一个复合的动画姿态。这使得开发者能够以模块化、可视化的方式构建复杂的动画逻辑，例如同时播放基础移动动画、上半身射击动画和表情动画，并精确控制它们之间的混合关系。

## 使用场景

- 你需要为角色构建一个复杂的动画状态机，其中多个动画片段需要同时播放并按权重混合（例如，跑步时上半身播放射击动画）。
- 你希望在编辑器中可视化地创建和调试动画层栈，而不是在蓝图或C++中硬编码混合逻辑。
- 你需要为不同的动画层应用不同的混合模式（如常规混合、叠加混合）和混合遮罩（如仅影响上半身骨骼）。
- 你正在使用 UAF 生态系统，并希望利用其提供的标准化工具来管理动画层。

## 蓝图用法

该插件的蓝图功能主要集中在编辑器数据管理和层栈操作上。核心节点位于 `UUAFLayerStack_EditorData` 类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddDefaultAssetBasedLayer` | 向层栈中添加一个新的、基于资产的动画层。 | `UUAFLayerStack_EditorData` |
| `MoveLayerUp` | 将指定层在栈中向上移动（索引减小）。 | `UUAFLayerStack_EditorData` |
| `MoveLayerDown` | 将指定层在栈中向下移动（索引增大）。 | `UUAFLayerStack_EditorData` |
| `RemoveLayer` | 从层栈中移除指定层。 | `UUAFLayerStack_EditorData` |
| `SetLayerState` | 设置层的状态（启用、预览禁用、禁用）。 | `UUAFLayerStack_EditorData` |
| `SelectLayer` | 在编辑器中选中指定层。 | `UUAFLayerStack_EditorData` |
| `GetAllLayers` | 获取层栈中的所有层（包括基础层）。 | `UUAFLayerStack_EditorData` |
| `GetNumLayers` | 获取层的数量。 | `UUAFLayerStack_EditorData` |

### 使用示例（蓝图描述）

1.  **创建层栈资产**：在内容浏览器中右键，选择 `Animation -> UAF Layer Stack` 创建一个新资产。
2.  **添加动画层**：打开该资产，在层栈编辑器中，通过右键菜单或工具栏按钮调用 `AddDefaultAssetBasedLayer` 节点，选择一个动画资产（如 `AnimSequence`）来创建新层。
3.  **配置层属性**：在层栈编辑器中选中一个层，在细节面板中配置其 `LayerWeight`（权重）、`BlendMode`（混合模式）、`BlendMask`（混合遮罩）等属性。
4.  **调整层顺序**：使用 `MoveLayerUp` 和 `MoveLayerDown` 节点（或在编辑器中拖拽）来调整层的混合顺序。
5.  **预览与调试**：在编辑器中播放，观察各层动画的混合效果。可以通过 `SetLayerState` 临时禁用某些层以隔离调试。

## C++ 用法

该插件的 C++ 用法主要涉及在编辑器工具或自定义工作流中程序化地操作层栈。

### 头文件引入

```cpp
#include "UAFLayerStack_EditorData.h"
#include "Layers/UAFLayer.h"
#include "LayeringUncookedOnlyTypes.h"
```

### 基本用法

以下示例展示了如何在 C++ 中获取并操作一个已存在的 `UUAFLayerStack_EditorData` 对象。

```cpp
// 假设你已经通过某种方式（如资产加载）获得了 UUAFLayerStack_EditorData 指针
UUAFLayerStack_EditorData* LayerStackEditorData = GetLayerStackEditorData();

if (LayerStackEditorData)
{
    // 1. 获取所有层
    TArray<TObjectPtr<UUAFLayer>> AllLayers = LayerStackEditorData->GetAllLayers();
    
    // 2. 获取层的数量（不包括基础层）
    int32 NumLayers = LayerStackEditorData->GetNumLayers(UE::UAF::Layering::EBaseLayerInclusion::Exclude);
    
    // 3. 添加一个新层（基于资产）
    FAssetData AnimAssetData = ...; // 获取一个动画资产的 FAssetData
    TObjectPtr<UUAFLayer> NewLayer = LayerStackEditorData->AddDefaultAssetBasedLayer(AnimAssetData);
    
    // 4. 设置新层的权重
    if (NewLayer)
    {
        // 权重通过其 BlendProvider 设置，这里需要访问具体的 Provider 类型
        // 例如，对于默认的混合提供者：
        TInstancedStruct<FUAFLayerBlendProviderBase>& BlendProvider = NewLayer->GetLayerBlendProvider();
        if (BlendProvider.GetScriptStruct() == FUAFDefaultBlendProvider::StaticStruct())
        {
            FUAFDefaultBlendProvider* DefaultBlend = BlendProvider.GetMutablePtr<FUAFDefaultBlendProvider>();
            if (DefaultBlend)
            {
                DefaultBlend->LayerWeight = 0.75f;
            }
        }
    }
    
    // 5. 将新层移动到栈顶（索引为0，基础层之上）
    LayerStackEditorData->MoveLayerToIndex(NewLayer, 0);
    
    // 6. 选中该层以便在编辑器中查看
    LayerStackEditorData->SelectLayer(NewLayer);
}
```

### 进阶用法

结合层的内容和混合提供者，可以创建更复杂的层配置。

```cpp
// 创建一个自定义的蒙太奇层
TObjectPtr<UUAFLayer> MontageLayer = LayerStackEditorData->AddDefaultAssetBasedLayer(FAssetData()); // 先添加一个空层

if (MontageLayer)
{
    // 设置内容提供者为蒙太奇提供者
    TInstancedStruct<FUAFLayerContentProviderBase> MontageContentProvider;
    MontageContentProvider.InitializeAs<FUAFMontageProvider>();
    FUAFMontageProvider* MontageProvider = MontageContentProvider.GetMutablePtr<FUAFMontageProvider>();
    MontageProvider->SlotName = FName("UpperBody");
    MontageProvider->bAutoEnableLayerWithMontage = true;
    MontageLayer->SetLayerContentProvider(MontageContentProvider);
    
    // 配置其混合行为
    TInstancedStruct<FUAFLayerBlendProviderBase>& BlendProvider = MontageLayer->GetLayerBlendProvider();
    if (BlendProvider.GetScriptStruct() == FUAFDefaultBlendProvider::StaticStruct())
    {
        FUAFDefaultBlendProvider* DefaultBlend = BlendProvider.GetMutablePtr<FUAFDefaultBlendProvider>();
        DefaultBlend->BlendMode = EUAFLayerBlendMode::Blend;
        DefaultBlend->LayerWeight = 1.0f;
        DefaultBlend->LayerBlendInTime = 0.2f;
        DefaultBlend->LayerBlendOutTime = 0.3f;
        // 可以进一步设置 BlendMask, BlendProfile 等
    }
    
    // 重命名层以便识别
    MontageLayer->RenameLayer(FName("UpperBodyMontageLayer"));
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在编辑器工具中创建一个简单的层栈并添加两个层。

**MyLayerStackTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UUAFLayerStack_EditorData;
class UUAFLayer;

class FMyLayerStackTool
{
public:
    void CreateAndPopulateLayerStack();
    
private:
    UUAFLayerStack_EditorData* LayerStackData = nullptr;
};
```

**MyLayerStackTool.cpp**
```cpp
#include "MyLayerStackTool.h"
#include "UAFLayerStack_EditorData.h"
#include "Layers/UAFLayer.h"
#include "Layers/UAFLayerAssetProvider.h"
#include "Layers/UAFLayerDefaultBlendProvider.h"
#include "AssetRegistry/AssetRegistryModule.h"

void FMyLayerStackTool::CreateAndPopulateLayerStack()
{
    // 注意：在实际编辑器工具中，LayerStackData 通常来自已打开的资产。
    // 这里仅为演示，假设我们通过某种方式获得了它。
    if (!LayerStackData)
    {
        UE_LOG(LogTemp, Warning, TEXT("LayerStackData is null. This is a demo and requires a valid editor data object."));
        return;
    }

    // 1. 添加第一个基于资产的层
    // 假设我们有一个名为 “Idle” 的动画资产
    FAssetData IdleAnimAsset = FAssetData(FName("/Game/Animations/Idle_Anim.Idle_Anim"));
    TObjectPtr<UUAFLayer> IdleLayer = LayerStackData->AddDefaultAssetBasedLayer(IdleAnimAsset);
    if (IdleLayer)
    {
        IdleLayer->RenameLayer(FName("IdleBase"));
        // 设置其权重为1.0（默认）
    }

    // 2. 添加第二个层，配置为叠加混合
    FAssetData WalkAnimAsset = FAssetData(FName("/Game/Animations/Walk_Anim.Walk_Anim"));
    TObjectPtr<UUAFLayer> WalkLayer = LayerStackData->AddDefaultAssetBasedLayer(WalkAnimAsset);
    if (WalkLayer)
    {
        WalkLayer->RenameLayer(FName("WalkAdditive"));
        
        // 修改其混合模式为叠加
        TInstancedStruct<FUAFLayerBlendProviderBase>& BlendProvider = WalkLayer->GetLayerBlendProvider();
        if (BlendProvider.GetScriptStruct() == FUAFDefaultBlendProvider::StaticStruct())
        {
            FUAFDefaultBlendProvider* DefaultBlend = BlendProvider.GetMutablePtr<FUAFDefaultBlendProvider>();
            if (DefaultBlend)
            {
                DefaultBlend->BlendMode = EUAFLayerBlendMode::Additive;
                DefaultBlend->LayerWeight = 0.5f; // 50% 的叠加强度
            }
        }
    }

    // 3. 将 WalkLayer 移动到 IdleLayer 之上
    LayerStackEditorData->MoveLayerUp(WalkLayer);

    UE_LOG(LogTemp, Log, TEXT("Layer stack populated with %d layers."), LayerStackEditorData->GetNumLayers());
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下 UAF 生态系统模块：

| 模块 | 用途 |
|---|---|
| `Workspace` | 提供工作区编辑器框架，层栈编辑器基于此构建。 |
| `AnimNext` | UAF 的核心动画图模块，层栈的底层图结构依赖于此。 |
| `RigVM` | 提供 RigVM 图和编译系统，用于在运行时执行层栈生成的动画逻辑。 |
| `UAF` | UAF 的核心运行时模块，提供基础类型和资产数据结构。 |

## 维护状态

### 近期更新

由于无法访问具体的 git log，基于插件元数据进行分析：
- 创建时间：2026-03-04
- 版本：0.1
- 状态：实验性 (`IsExperimentalVersion: true`)，默认禁用 (`EnabledByDefault: false`)

### 维护评价

- **年龄**：插件非常新（约2年），处于早期开发阶段。
- **状态**：明确标记为**实验性**，且默认禁用。这表明 Epic Games 将其视为前沿功能，API 和功能可能在未来版本中发生重大变化。
- **活跃度**：作为 UAF 框架的一部分，很可能随着 UAF 的整体开发而持续更新。但作为实验性模块，其独立更新频率和稳定性可能低于正式版插件。
- **已知限制**：实验性意味着可能存在未发现的 Bug、不完整的功能或性能问题。文档和社区支持可能有限。
- **推荐使用**：**仅推荐用于研究、原型开发或对 UAF 前沿功能有强烈需求的项目**。不建议在需要长期稳定维护的生产项目中直接依赖此插件。使用前请做好应对 Breaking Changes 的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFLayering)
- 官方文档：暂无
- 测试用例：路径未知，可能位于 `Engine/Plugins/Experimental/UAF/UAFLayering/Tests/` 或 `Engine/Tests/` 目录下。