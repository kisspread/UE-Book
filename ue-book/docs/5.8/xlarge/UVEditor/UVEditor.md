# UV Editor

> Asset editor for modifying the UV mapping of a mesh

| 属性 | 值 |
|---|---|
| 中文名 | UV编辑器 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器界面、工具集） |
| 模块 | `UVEditor` (Editor), `UVEditorTools` (Editor), `UVEditorToolsEditorOnly` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-15 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor) | |

## 用途

UV Editor 是一个专门用于编辑静态网格体 UV 映射的资产编辑器。它为用户提供了一个集成在 Unreal Editor 中的独立工作区，专门用于查看、选择、调整和优化模型的 UV 布局。其核心价值在于将 UV 编辑工作流从外部工具（如 Blender、Maya）直接集成到引擎中，避免了资产导出-编辑-导入的繁琐循环，提升了美术和TA的工作效率。

它解决的主要问题包括：
*   **UV 展开与重排**：使用交互式工具对 UV 岛进行移动、旋转、缩放、对齐和分布。
*   **缝合与拆分**：交互式地创建或移除 UV 接缝，以控制纹理拉伸和接缝位置。
*   **UDIM 支持**：配置和管理多象限 UV 布局（UDIM）。
*   **实时预览**：提供 2D 展开视图和 3D 实时预览视图，便于观察 UV 操作对最终纹理的影响。
*   **工具链集成**：无缝衔接引擎的 Interactive Tools Framework，提供了一整套专业级的 UV 编辑工具。

## 使用场景

*   你需要为角色、道具或环境模型优化 UV 布局，以最小化纹理拉伸并最大化纹理空间利用率。
*   你正在使用 UDIM 工作流，需要配置特定的 UV 瓦片布局。
*   你希望避免在 DCC 和引擎之间反复切换，直接在资产上下文中进行 UV 微调。
*   你需要快速修复导入模型中的 UV 问题（如错误接缝或重叠岛）。
*   在进行光照烘焙或纹理绘制前，需要确保 UV 通道的正确性。

## 蓝图用法

UV Editor 主要通过资产编辑器框架和子系统访问。大部分交互通过编辑器 UI 完成，但其核心子系统提供了一些蓝图可调用的接口用于检查目标资产和启动编辑器。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsObjectValidTarget` | 检查单个对象是否是 UV 编辑器的有效目标（如静态网格体） | `UUVEditorSubsystem` |
| `AreObjectsValidTargets` | 检查一组对象是否都是 UV 编辑器的有效目标 | `UUVEditorSubsystem` |
| `StartUVEditor` | 尝试启动或聚焦一个 UV 编辑器实例来编辑给定的对象数组 | `UUVEditorSubsystem` |

### 使用示例（蓝图描述）

要通过蓝图启动 UV 编辑器，你可以：
1.  获取 `UUVEditorSubsystem` 的实例。
2.  调用 `AreObjectsValidTargets` 来确认你想要编辑的 `UObject` 数组（通常是 `UStaticMesh`）是否有效。
3.  如果验证通过，调用 `StartUVEditor` 并传入该对象数组。
4.  编辑器窗口将会打开并加载这些网格体进行 UV 编辑。

**注意**：通常更常见的用法是在内容浏览器中右键点击静态网格体资产，选择“UV Editor”选项，这是通过编辑器扩展自动完成的。

## C++ 用法

### 头文件引入

```cpp
#include "UVEditorSubsystem.h"
#include "UVEditor.h"
```

### 基本用法

通过子系统检查并启动 UV 编辑器。这模拟了编辑器右键菜单的逻辑。

```cpp
// 假设你有一个 UObject 数组，例如从内容浏览器选择的资产
TArray<UObject*> MeshObjects;
// ... 填充 MeshObjects

if (UUVEditorSubsystem* UVEditorSubsystem = GEditor->GetEditorSubsystem<UUVEditorSubsystem>())
{
    // 检查这些对象是否可以被 UV 编辑器编辑
    if (UVEditorSubsystem->AreObjectsValidTargets(MeshObjects))
    {
        // 启动 UV 编辑器来编辑这些网格体
        TArray<TObjectPtr<UObject>> ObjectsToEdit;
        for (UObject* Obj : MeshObjects)
        {
            ObjectsToEdit.Add(Obj);
        }
        UVEditorSubsystem->StartUVEditor(ObjectsToEdit);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Selected objects are not valid targets for UV Editor."));
    }
}
```
*来源: 推断自 `UVEditorSubsystem.h` 中的公共接口。*

### 进阶用法

利用模块化特性（Modular Feature）来检测 UV 编辑器插件是否存在并可用。这对于可选依赖该插件的功能模块很有用。

```cpp
#include "UVEditorModularFeature.h"

// 检查 UV 编辑器模块是否已加载
IModularFeatures& ModularFeatures = IModularFeatures::Get();
if (ModularFeatures.IsModularFeatureAvailable(IUVEditorModularFeature::ModularFeatureName))
{
    IUVEditorModularFeature* UVEditorFeature = &ModularFeatures.GetModularFeature<IUVEditorModularFeature>(IUVEditorModularFeature::ModularFeatureName);
    
    // 检查是否可以针对给定对象启动编辑器
    TArray<TObjectPtr<UObject>> TargetObjects = { SomeMesh1, SomeMesh2 };
    if (UVEditorFeature->CanLaunchUVEditor(TargetObjects))
    {
        // 启动编辑器
        UVEditorFeature->LaunchUVEditor(TargetObjects);
    }
}
```
*来源: `UVEditorModularFeature.h`。*

## Demo 示例

一个简单的控制台命令或编辑器按钮，用于将选定的静态网格体在 UV 编辑器中打开。

```cpp
// MyUVEditorHelper.h
#pragma once

#include "CoreMinimal.h"

class FMyUVEditorHelper
{
public:
    static void OpenSelectedAssetsInUVEditor();
};

// MyUVEditorHelper.cpp
#include "MyUVEditorHelper.h"
#include "UVEditorSubsystem.h"
#include "Editor.h"
#include "AssetSelection.h"

void FMyUVEditorHelper::OpenSelectedAssetsInUVEditor()
{
    // 获取编辑器中当前选中的资产
    TArray<UObject*> SelectedObjects;
    GEditor->GetSelectedAssets()->GetSelectedObjects(SelectedObjects);

    if (SelectedObjects.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No assets selected."));
        return;
    }

    // 转换为 TObjectPtr 数组
    TArray<TObjectPtr<UObject>> ObjectsToEdit;
    for (UObject* Obj : SelectedObjects)
    {
        ObjectsToEdit.Add(Obj);
    }

    // 尝试启动编辑器
    if (UUVEditorSubsystem* UVEditorSubsystem = GEditor->GetEditorSubsystem<UUVEditorSubsystem>())
    {
        if (UVEditorSubsystem->AreObjectsValidTargets(SelectedObjects))
        {
            UVEditorSubsystem->StartUVEditor(ObjectsToEdit);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("One or more selected objects cannot be edited in UV Editor (e.g., not a Static Mesh)."));
        }
    }
}
```

## 模块依赖

要使用 `UVEditor` 插件提供的功能（特别是 C++ 接口），你的模块需要依赖以下插件模块。这些是该插件独特且必需的依赖：

| 模块 | 用途 |
|---|---|
| `UVEditor` | 核心编辑器模块，包含资产编辑器、子系统、模式和主要 UI 逻辑。 |
| `UVEditorTools` | 运行时工具模块，包含所有 UV 编辑交互工具的核心实现。 |
| `GeometryProcessing` | 提供几何处理算法，如网格参数化、UV 展开等核心数学运算。 |
| `MeshModelingToolset` | 提供基础网格编辑工具框架和常用工具，UV 编辑工具基于此构建。 |
| `MeshModelingToolsetExp` | 提供实验性网格工具，UV 编辑器可能使用其中一些先进或实验性功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-04-24 | `0213bc37` | [ITF] Call `UInputRouter::ForceTerminateSource()` from within `UInputRouter::DeregisterSource()` pri... | [交互工具框架] 在注销输入源时强制终止，提升了输入管理的健壮性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF，可能是日志宏的更新或修复。 |
| 2026-03-10 | `0b781d0c` | Add/RemoveOverlayWidget: | 更新了视口覆盖小部件（如工具按钮）的添加/移除逻辑。 |
| 2026-03-05 | `1adb9f68` | New material translator work: | 涉及新的材质转换器工作，可能用于改进 UV 编辑器中的材质预览。 |

### 维护评价

**活跃维护**。
*   **创建时间**：插件于 2023 年 6 月从实验性目录迁移并正式成为编辑器插件，历史约 3 年。
*   **更新频率**：从 git 历史看，在 2026 年初仍有密集的提交，表明开发团队在持续投入。
*   **更新内容**：近期更新主要集中在修复编译警告、提升输入系统稳健性、日志迁移以及 UI 和预览相关的改进，属于稳步的功能完善和代码质量提升阶段。
*   **状态**：`.uplugin` 标记为 `IsBetaVersion = true`，表明 Epic 官方认为此插件虽已成熟可用，但仍处于测试阶段，可能在未来版本中有 API 变动。
*   **推荐**：作为 UE5.4+ 版本中官方的 UV 编辑解决方案，**强烈推荐使用**。尽管是测试版，但其功能完整且集成度高，是当前引擎内 UV 编辑的最佳选择。使用者应关注后续版本的更新说明，以应对可能的 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/UVEditor/Tests)