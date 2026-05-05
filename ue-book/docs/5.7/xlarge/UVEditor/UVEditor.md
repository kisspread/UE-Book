# UVEditor

> Asset editor for modifying the UV mapping of a mesh（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor) | |

## 用途

UVEditor 是一个功能完备的资产编辑器插件，其核心目的是在 Unreal Engine 内部提供一个专业级的 UV 映射编辑环境。它解决了传统工作流中需要将网格模型导出到外部软件（如 Maya、Blender）进行 UV 展开和编辑，然后再导回引擎的繁琐过程。

通过此插件，开发者和美术可以直接在编辑器中：
1.  **可视化编辑 UV**：在 2D 视口中直观地查看、选择、移动、旋转和缩放 UV 岛。
2.  **执行专业 UV 操作**：提供一系列工具，如自动展开（Unwrap）、对齐、分布、缝合（Sew）、分割（Split）、创建接缝（Seam）等。
3.  **实时 3D 预览**：在 3D 视口中实时查看 UV 编辑对模型纹理映射的影响。
4.  **分析与诊断**：通过扭曲可视化（Distortion Visualization）和背景棋盘格/纹理预览，帮助识别 UV 拉伸、压缩或密度不均等问题。
5.  **支持复杂工作流**：支持 UDIM 工作流、多 UV 通道编辑以及对多个资产的同时编辑。

其存在意义在于提升内容创作管线的效率，减少上下文切换，让 UV 调整成为引擎内迭代美术资源的一个自然环节。

## 使用场景

-   你正在为一个角色模型调整 UV，希望在引擎内快速测试不同布局对纹理细节的影响。
-   你导入了一个外部模型，发现其 UV 存在重叠或拉伸，需要在不离开编辑器的情况下进行修复。
-   你需要为一个大型场景中的多个静态网格体批量设置或优化 UV 布局。
-   你正在使用 UDIM 工作流，需要在引擎内管理不同纹理块的 UV 分布。
-   你需要检查模型的纹理像素密度（Texel Density）是否一致，以确保纹理资源的有效利用。

## 蓝图用法

UVEditor 的主要蓝图接口通过 `UUVEditorSubsystem` 暴露，用于控制编辑器的启动和验证。工具和可视化设置则通过对应的属性集（Property Set）进行配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartUVEditor` | 为指定的对象数组启动一个新的 UV 编辑器实例，或激活一个已存在的实例。 | `UUVEditorSubsystem` |
| `AreObjectsValidTargets` | 检查一组对象是否可以作为 UV 编辑器的有效目标（例如，是否为包含网格体的资产）。 | `UUVEditorSubsystem` |
| `AreAssetsValidTargets` | 检查一组资产数据是否可以作为 UV 编辑器的有效目标，无需加载资产。 | `UUVEditorSubsystem` |
| `NotifyThatUVEditorClosed` | 当 UV 编辑器实例关闭时调用，通知子系统以便管理。 | `UUVEditorSubsystem` |

### 使用示例（蓝图描述）

1.  **启动编辑器**：
    *   在蓝图中获取 `UVEditorSubsystem` 的引用。
    *   构建一个包含你想要编辑的 `UObject`（如 `UStaticMesh`）的数组。
    *   调用 `StartUVEditor` 节点，将对象数组作为输入。这将打开 UV 编辑器窗口。

2.  **配置背景预览**：
    *   在 UV 编辑器打开后，获取 `UUVEditorBackgroundPreviewProperties` 对象的引用。
    *   设置其 `bVisible` 属性为 `true` 以启用背景。
    *   设置 `SourceType` 为 `Checkerboard`、`Texture` 或 `Material`。
    *   如果选择 `Texture` 或 `Material`，则进一步设置 `SourceTexture` 或 `SourceMaterial` 属性。

3.  **配置扭曲可视化**：
    *   获取 `UUVEditorDistortionVisualizationProperties` 对象的引用。
    *   设置 `bVisible` 为 `true`。
    *   选择 `Metric`，例如 `ReedBeta`（椭圆离心率）或 `TexelDensity`（纹理像素密度）来查看不同的扭曲分析视图。

## C++ 用法

### 头文件引入

```cpp
#include "UVEditorSubsystem.h"
#include "UVEditorModularFeature.h"
```

### 基本用法

通过子系统启动 UV 编辑器是最直接的方式。

```cpp
// 假设在某个编辑器工具或菜单扩展中
#include "UVEditorSubsystem.h"

void OpenUVEditorForMesh(UStaticMesh* MeshToEdit)
{
    // 获取 UVEditor 子系统
    UUVEditorSubsystem* UVEditorSubsystem = GEditor->GetEditorSubsystem<UUVEditorSubsystem>();
    if (UVEditorSubsystem && MeshToEdit)
    {
        // 检查对象是否有效
        if (UVEditorSubsystem->IsObjectValidTarget(MeshToEdit))
        {
            // 启动编辑器
            TArray<TObjectPtr<UObject>> ObjectsToEdit;
            ObjectsToEdit.Add(MeshToEdit);
            UVEditorSubsystem->StartUVEditor(ObjectsToEdit);
        }
    }
}
```
*（来源：基于 `UUVEditorSubsystem` 公共接口推断）*

### 进阶用法

使用模块化特性（Modular Feature）接口来启动编辑器，这种方式更解耦，适用于其他插件需要调用 UV 编辑器功能的场景。

```cpp
#include "UVEditorModularFeature.h"
#include "IModularFeatures.h"

void LaunchUVEditorViaModularFeature(const TArray<UObject*>& Objects)
{
    // 从模块化特性系统中查找 UV 编辑器功能
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (ModularFeatures.IsModularFeatureImplemented(UE::Geometry::IUVEditorModularFeature::GetModularFeatureName()))
    {
        // 获取功能实例
        UE::Geometry::IUVEditorModularFeature& UVEditorFeature = 
            ModularFeatures.GetModularFeature<UE::Geometry::IUVEditorModularFeature>(
                UE::Geometry::IUVEditorModularFeature::GetModularFeatureName());

        // 检查是否可以启动，并启动
        TArray<TObjectPtr<UObject>> ObjectPtrs;
        for (UObject* Obj : Objects) { ObjectPtrs.Add(Obj); }
        
        if (UVEditorFeature.CanLaunchUVEditor(ObjectPtrs))
        {
            UVEditorFeature.LaunchUVEditor(ObjectPtrs);
        }
    }
}
```
*（来源：基于 `FUVEditorModularFeature` 和 `IUVEditorModularFeature` 接口推断）*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在编辑器工具中集成启动 UV 编辑器的功能。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Toolkits/BaseToolkit.h"

class FMyEditorTool : public FBaseToolkit
{
public:
    // ... 其他工具代码 ...

    /** 菜单命令：为选中的资产打开 UV 编辑器 */
    void OpenUVEditorForSelectedAssets();

    // ... 其他工具代码 ...
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "UVEditorSubsystem.h"
#include "ContentBrowserModule.h"
#include "IContentBrowserSingleton.h"

void FMyEditorTool::OpenUVEditorForSelectedAssets()
{
    // 从内容浏览器获取当前选中的资产
    FContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<FContentBrowserModule>("ContentBrowser");
    TArray<FAssetData> SelectedAssets;
    ContentBrowserModule.Get().GetSelectedAssets(SelectedAssets);

    if (SelectedAssets.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No assets selected."));
        return;
    }

    // 获取 UV 编辑器子系统
    UUVEditorSubsystem* UVEditorSubsystem = GEditor->GetEditorSubsystem<UUVEditorSubsystem>();
    if (!UVEditorSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("UV Editor Subsystem not available."));
        return;
    }

    // 检查所有选中的资产是否都是有效的 UV 编辑目标
    if (!UVEditorSubsystem->AreAssetsValidTargets(SelectedAssets))
    {
        UE_LOG(LogTemp, Warning, TEXT("Selected assets are not valid for UV editing."));
        return;
    }

    // 将资产数据转换为 UObject 指针（这会强制加载资产）
    TArray<TObjectPtr<UObject>> ObjectsToEdit;
    for (const FAssetData& Asset : SelectedAssets)
    {
        if (UObject* Object = Asset.GetAsset())
        {
            ObjectsToEdit.Add(Object);
        }
    }

    // 启动 UV 编辑器
    if (ObjectsToEdit.Num() > 0)
    {
        UVEditorSubsystem->StartUVEditor(ObjectsToEdit);
    }
}
```

## 模块依赖

从 `.uplugin` 文件的 `Plugins` 部分可知，UVEditor 依赖于以下插件，因此你的模块也需要依赖这些模块才能使用其完整功能。

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供底层的几何处理算法，如网格参数化、UV 展开等核心数学功能。 |
| `MeshModelingToolset` | 提供网格建模工具集，UVEditor 中的许多交互式工具（如变换、对齐）基于此构建。 |
| `MeshModelingToolsetExp` | MeshModelingToolset 的实验性扩展，可能包含一些前沿或正在开发中的工具功能。 |

## 维护状态

### 近期更新

```
- 670a57acc54b UVEditor: Fix bug where if a collection of objects in the viewport are selected, where at least two objects are backed by the same asset, the UV Editor would fail to position them relative to their viewport locations.
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- a2e75189887d Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup using LyraEditor win64 development as target)
```

*   第一条提交修复了一个具体的使用场景下的定位 Bug，属于功能性修复。
*   后两条提交是代码维护性质的，添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏以优化编译，不涉及功能变更。

### 维护评价

**活跃维护**。

-   **创建时间**：插件于 2021 年创建，至今约 3 年，属于较新的工具。
-   **更新频率**：从提供的 git 历史看，近期仍有提交，表明插件处于活跃开发或维护周期中。
-   **内容性质**：最近的提交包含具体的 Bug 修复，说明 Epic 团队仍在关注并改进该插件的稳定性和用户体验。
-   **实验性状态**：`.uplugin` 中 `IsBetaVersion: true`，表明该插件虽已默认启用，但仍被视为测试版，可能在未来版本中有 API 变动或功能调整。
-   **推荐使用**：**推荐使用**。对于需要在引擎内进行 UV 编辑的工作流，这是一个官方提供的、功能强大的解决方案。尽管是 Beta 版，但其默认启用且持续维护，是当前 UE 内 UV 编辑的首选工具。使用者应留意其 Beta 状态，关注后续版本的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/UVEditor)
- [官方文档]() （暂无）
- [测试用例]() （插件目录内未发现独立测试文件，测试可能集成在引擎测试套件中）