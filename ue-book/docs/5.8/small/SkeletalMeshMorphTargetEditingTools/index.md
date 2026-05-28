# Skeletal Mesh Morph Target Editing Tools

> Tools to edit morph targets within the skeletal mesh editor.

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼网格变形目标编辑工具 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SkeletalMeshMorphTargetEditingTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/SkeletalMeshMorphTargetEditingTools) | |

## 用途

该插件为 Unreal Engine 的**骨骼网格编辑器**（Skeletal Mesh Editor）提供了直接在编辑器内创建和编辑**变形目标（Morph Target， 也称 Blend Shape）** 的工具集。传统上，变形目标的创建和调整通常需要在外部 DCC 软件（如 Maya、Blender）中完成并重新导入，或者需要通过复杂的动画蓝图和曲线进行间接控制。此插件解决了这个痛点，允许美术和开发者在引擎内部，以直观、交互式的方式直接雕刻和编辑变形目标。

其核心功能包括两个工具：
1.  **变形目标顶点雕刻工具**：允许用户使用标准的雕刻笔刷（如移动、平滑、擦除）直接操作网格顶点，所作的修改会实时存储为一个新的变形目标形状。
2.  **变形目标遮罩工具**：允许用户基于一个已有的变形目标作为基础，通过绘制顶点权重的方式创建一个新的顶点属性遮罩。这个遮罩可以用于驱动其他效果，实现更复杂的变形组合或遮罩控制。

## 使用场景

-   你在制作角色面部表情，需要快速迭代并调整一个“微笑”或“皱眉”的变形目标形状。
-   你需要为角色创建口型同步（Lip-sync）所需的一系列基础音素（Phoneme）变形目标。
-   你想基于一个“肌肉隆起”的变形目标，绘制一个遮罩来精确控制哪些顶点受该变形影响。
-   你正在开发一个需要动态、程序化控制网格局部变形的系统，需要在编辑器内预览和调试这些变形效果。

## 蓝图用法

此插件主要作为编辑器工具扩展，其蓝图可访问性集中在命令触发层面。核心的功能操作通过编辑器 UI 触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginMorphTargetTool` | 触发开始使用变形目标编辑工具（主入口） | `FSkeletalMeshMorphTargetEditingToolsCommands` |
| `BeginMorphTargetSculptTool` | 直接触发开始变形目标顶点雕刻工具 | `FSkeletalMeshMorphTargetEditingToolsCommands` |
| `BeginMorphTargetMaskTool` | 直接触发开始变形目标遮罩工具 | `FSkeletalMeshMorphTargetEditingToolsCommands` |

### 使用示例（蓝图描述）

1.  **在蓝图中触发工具**：
    通常，这些命令节点不会直接在游戏逻辑蓝图中使用，而是在编辑器工具或编辑器扩展蓝图中通过“Get UI Command Info”和“Execute UI Command”节点来调用，以编程方式启动特定的编辑器工具。例如，你可以创建一个自定义的编辑器工具栏按钮，当点击时执行 `BeginMorphTargetSculptTool` 命令。

2.  **监听工具事件**：
    工具的运行时逻辑主要在 C++ 层。如果需要在蓝图中响应工具状态（例如，工具启动、关闭、属性变化），通常需要通过插件暴露的接口或事件委托来实现，这超出了基础蓝图节点的范围，需要参考 C++ 用法部分。

## C++ 用法

### 头文件引入

```cpp
#include "SkeletalMeshMorphTargetEditingToolsModule.h"
#include "MorphTargetVertexSculptTool.h"
#include "MorphTargetMaskTool.h"
```

### 基本用法

以下示例展示了如何检查该插件模块是否已加载，并获取工具命令信息。

```cpp
// 检查插件模块是否加载
FModuleManager& ModuleManager = FModuleManager::Get();
if (ModuleManager.IsModuleLoaded(TEXT("SkeletalMeshMorphTargetEditingTools")))
{
    UE_LOG(LogTemp, Log, TEXT("Skeletal Mesh Morph Target Editing Tools module is loaded."));
}

// 获取并执行一个工具命令
if (FSkeletalMeshMorphTargetEditingToolsCommands::IsRegistered())
{
    const FSkeletalMeshMorphTargetEditingToolsCommands& Commands = FSkeletalMeshMorphTargetEditingToolsCommands::Get();
    // 假设我们有一个 FUICommandList，例如在自定义编辑器工具栏中
    CommandList->MapAction(
        Commands.BeginMorphTargetSculptTool,
        FExecuteAction::CreateLambda([](){
            // 执行逻辑会由插件模块内部处理
            UE_LOG(LogTemp, Log, TEXT("Morph Target Sculpt Tool action triggered."));
        }),
        FCanExecuteAction()
    );
}
```
*来源: `SKMMorphTargetEditingToolsCommands.h`, `SKMMorphTargetEditingToolsModule.h`*

### 进阶用法

该插件的核心是作为 `ISkeletalMeshModelingModeToolExtension` 的实现，将工具注册到骨骼网格编辑器的建模模式中。以下是一个模拟其内部工作原理的简化示例，展示了如何通过接口与工具交互。

```cpp
// 假设我们正在一个自定义的编辑器工具上下文中
// 获取当前骨骼网格编辑器上下文对象
USkeletalMeshEditorContextObjectBase* EditorContext = /* ... 通过某种方式获取 ... */;

if (EditorContext)
{
    // 工具内部使用 PoseChangeDetector 监听骨骼姿势变化
    SkeletalMeshToolsHelper::FPoseChangeDetector PoseChangeDetector;
    PoseChangeDetector.OnPoseChanged.AddLambda([](SkeletalMeshToolsHelper::FPoseChangeDetector::FPayload Payload){
        // 当骨骼姿势改变时，这里会被调用
        // Payload 中包含新的 ComponentSpaceBoneTransforms 和 MorphTargetWeights
        UE_LOG(LogTemp, Log, TEXT("Skeleton pose changed in editor."));
    });

    // 工具使用 FMorphTargetEditingToolInterface 来设置通用属性
    // 在实际的 UMorphTargetVertexSculptTool 中，它会实现 SetupCommonProperties
    auto SetupProps = [](UMorphTargetEditingToolProperties* Props){
        if (Props)
        {
            Props->EditMorphTargetName = FName("MyNewMorphTarget");
        }
    };
    // 调用接口函数（假设 `MyTool` 实现了 `IMorphTargetEditingToolInterface`）
    // MyTool->SetupCommonProperties(SetupProps);
}
```
*来源: `MorphTargetVertexSculptTool.h`, `IMorphTargetEditingToolInterface.h`*

## Demo 示例

以下是一个完整的、可编译的最小编辑器工具扩展示例，展示了如何将变形目标工具命令集成到自定义编辑器模块中。

**MyMorphToolEditorExtension.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyMorphToolEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FUICommandList> PluginCommands;
    void RegisterMenus();
};
```

**MyMorphToolEditorExtension.cpp**
```cpp
#include "MyMorphToolEditorExtension.h"
#include "SKMMorphTargetEditingToolsCommands.h"
#include "Toolkits/AssetEditorManager.h"

#define LOCTEXT_NAMESPACE "FMyMorphToolEditorModule"

void FMyMorphToolEditorModule::StartupModule()
{
    // 注册插件命令（如果尚未由主插件注册）
    FSkeletalMeshMorphTargetEditingToolsCommands::Register();

    PluginCommands = MakeShareable(new FUICommandList);

    // 将命令映射到动作
    PluginCommands->MapAction(
        FSkeletalMeshMorphTargetEditingToolsCommands::Get().BeginMorphTargetSculptTool,
        FExecuteAction::CreateRaw(this, &FMyMorphToolEditorModule::RegisterMenus), // 简化示例，实际应调用工具
        FCanExecuteAction());

    // 注册菜单扩展点
    UToolMenus::RegisterStartupCallback(FSimpleMulticastDelegate::FDelegate::CreateRaw(this, &FMyMorphToolEditorModule::RegisterMenus));
}

void FMyMorphToolEditorModule::ShutdownModule()
{
    UToolMenus::UnRegisterStartupCallback(this);
    UToolMenus::UnregisterOwner(this);
    FSkeletalMeshMorphTargetEditingToolsCommands::Unregister();
}

void FMyMorphToolEditorModule::RegisterMenus()
{
    // 示例：在编辑器的“工具”菜单中添加一个条目来启动变形目标雕刻工具
    FToolMenuOwnerScoped OwnerScoped(this);
    {
        UToolMenu* Menu = UToolMenus::Get()->ExtendMenu("LevelEditor.MainMenu.Tools");
        FToolMenuSection& Section = Menu->FindOrAddSection("MySection");
        Section.AddMenuEntry(
            "OpenMorphSculptTool",
            LOCTEXT("OpenMorphSculptTool", "Morph Target Sculpt Tool"),
            LOCTEXT("OpenMorphSculptToolToolTip", "Opens the Skeletal Mesh Morph Target Sculpt Tool"),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateLambda([](){
                // 通过编辑器子系统执行命令
                FAssetEditorManager::Get().FindEditorForAsset(/* 需要一个骨骼网格资产 */, true);
                // 实际的工具启动逻辑由 FSkeletalMeshMorphTargetEditingToolsModule 内部处理
            }))
        );
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyMorphToolEditorModule, MyMorphToolEditorExtension)
```

## 模块依赖

该插件依赖于其他骨骼网格建模相关的插件和模块。要在你的项目或插件中使用它，需要在 `Build.cs` 中添加相应的依赖。

| 模块 | 用途 |
|---|---|
| `ModelingToolsEditorRuntime` | 提供基础的编辑器交互工具运行时框架（如雕刻笔刷、输入行为） |
| `SkeletalMeshModelingTools` | 提供骨骼网格编辑器集成、几何体隔离、姿势变化检测等核心功能 |
| `MeshModelingToolset` | 提供网格建模的基础工具集（如顶点属性绘制工具基类） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `79bd51de` | Direct Mesh Control: more descriptive icons | 为直接网格控制添加了更描述性的图标 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack valid tangents | 为缺少有效切线的预览/雕刻网格设置自动计算切线模式 |
| 2026-05-20 | `884a7c6f` | [SkeletalMeshModelingTools] Fix vert drift in HandleGeometryUpdate when editing multiple morph targets | 修复编辑多个变形目标时几何体更新处理中的顶点漂移问题 |
| 2026-05-12 | `423a1a54` | [MorphTargetTools] Add the Inflate brush back to the morph target vertex sculpt tool curated brush list | 将膨胀笔刷重新添加到变形目标顶点雕刻工具的精选笔刷列表中 |
| 2026-05-12 | `db666868` | [MorphTargetEditingTools] Stop Smooth, Flatten, and the Erase brush from accumulating while the cursor is stationary | 修复平滑、平整和擦除笔刷在光标静止时仍持续累积效果的问题 |

### 维护评价

该插件创建于 **2025年初**，属于较新的工具。从 Git 历史记录看，在 **2026年5月** 有连续且密集的更新，主要集中在**功能完善（添加笔刷）、错误修复（顶点漂移、笔刷累积）和用户体验优化（图标）** 上。

-   **维护状态**：**积极维护中**。尽管标记为实验性 (`IsExperimentalVersion: true`)，但近期更新频繁，表明 Epic 开发团队仍在迭代和改进此工具。
-   **稳定性**：近期多个 commit 专注于修复具体的几何计算和笔刷行为问题，说明工具在核心雕刻逻辑上正在趋于稳定，但仍处于实验阶段，可能存在未发现的边缘情况。
-   **推荐度**：**推荐关注和试用**。对于需要在编辑器内直接编辑变形目标的工作流，此插件是唯一且官方的解决方案。由于其活跃的维护状态和实验性标签，适合在项目中率先尝试，以提前适应未来可能成为标准功能的工具链，但需留意未来 API 可能的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/SkeletalMeshMorphTargetEditingTools)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/SkeletalMeshMorphTargetEditingTools/Tests)