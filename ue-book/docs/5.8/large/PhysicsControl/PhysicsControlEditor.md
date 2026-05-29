# PhysicsControl Editor

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制编辑器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、预览场景、工具栏命令） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlEditor` (Editor), `PhysicsControlUncookedOnly` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl) | |

## 用途

基于源码分析，`PhysicsControl` 插件是一个**编辑器工具集**，其核心功能是提供一个专用的资产编辑器（`FPhysicsControlAssetEditor`），用于创建、编辑和预览 `UPhysicsControlAsset`。这个资产定义了如何通过物理约束（Controls）和物理修改器（Body Modifiers）来驱动骨骼网格体的物理模拟。

它解决了以下具体问题：
1.  **物理驱动动画的配置与调试**：为动画师和开发者提供了一个可视化、可交互的编辑环境，用于配置和调试“基于物理的动画”（Physics-Based Animation, PBA）或“布娃娃”（Ragdoll）效果，而无需反复运行游戏。
2.  **复杂的物理动画混合**：允许用户定义多个“控制配置文件”（Profiles），快速切换不同的物理驱动行为（例如，不同的布娃娃姿态、被击中时的反应、平衡保持方式），并在编辑器中实时预览效果。
3.  **交互式物理调试**：在模拟运行时，用户可以在编辑器视口直接用鼠标抓取、拖拽角色身体部位，观察物理系统的实时响应和约束行为，极大简化了调试流程。

该插件的存在是为了**标准化并简化基于物理的动画资产的创作工作流**，将复杂的物理配置数据封装为可复用的资产。

## 使用场景

-   你在制作一个动作或格斗游戏，需要为角色配置多种受击、死亡、失衡的物理反应动画 → 使用 `PhysicsControl Editor` 创建和编辑 `UPhysicsControlAsset`。
-   你需要为一个过场动画中的角色创建一段物理驱动的“被大风吹动”或“在颠簸车辆上保持平衡”的动画 → 在该编辑器中调整物理约束和目标值，并在预览中实时迭代。
-   你在开发一个需要复杂布娃娃系统的角色，需要精细调整每个骨骼关节的物理属性、驱动强度和限制 → 利用编辑器的骨骼树视图和细节面板进行精确控制。
-   你希望快速测试不同物理设置（如重力、碰撞）对角色动画的影响 → 使用编辑器的工具栏开关（如无重力模拟、地面碰撞）进行快速切换对比。

## 蓝图用法

`PhysicsControlEditor` 模块主要提供编辑器扩展和资产编辑器功能，不直接暴露运行时蓝图节点。其核心交互发生在 **Persona 编辑器** 和 **专用资产编辑器** 的 UI 中。

### 核心节点（编辑器内）

由于这是编辑器模块，功能通过编辑器 UI 实现，而非蓝图节点。核心交互在 `FPhysicsControlAssetEditor` 类中：

| 功能 | 说明 | 实现位置 |
|---|---|---|
| `InitAssetEditor` | 初始化资产编辑器，注册所有模式、视口和面板。 | `FPhysicsControlAssetEditor` |
| `InvokeControlProfile(FName)` | 在模拟运行时，按名称激活一个预设的控制配置文件。 | `FPhysicsControlAssetEditor` |
| `RecreateControlsAndModifiers` | 根据资产当前数据，销毁并重新创建所有物理控制和修改器。 | `FPhysicsControlAssetEditor` |
| `ToggleSimulation` | 开始或停止编辑器内的物理模拟。 | `FPhysicsControlAssetEditorData` |
| `HitBone` | 处理用户在视口中点击骨骼/身体的操作，用于选择。 | `FPhysicsControlAssetEditorData` |

### 使用示例（在编辑器中）

1.  **创建资产**：在内容浏览器右键，选择“Physics”类别下的“Physics Control Asset”。
2.  **打开编辑器**：双击创建的资产，会打开 `FPhysicsControlAssetEditor` 窗口。
3.  **配置与预览**：
    *   在左侧“骨架树”面板中，展开并选择身体部位（Body）。
    *   在右侧“细节”面板中，配置选中部位的“控制”（Controls）和“修改器”（Body Modifiers）属性（如目标位置、旋转、强度、阻尼）。
    *   点击编辑器工具栏的“模拟”按钮启动物理模拟。
    *   在视口中，用鼠标左键点击并拖拽角色身体，观察物理反应。
    *   使用工具栏的下拉菜单切换不同的“控制配置文件”（Profiles）来查看预设效果。
4.  **调整与迭代**：实时修改属性，观察模拟结果，直至达到预期效果。

## C++ 用法

`PhysicsControlEditor` 模块主要用于编辑器扩展，直接的 C++ API 使用较少。主要交互是通过创建和编辑资产。

### 头文件引入

```cpp
// 用于创建资产
#include "PhysicsControlAsset.h"
// 用于操作资产编辑器（通常由引擎内部调用，但可编程启动）
#include "PhysicsControlAssetEditor/PhysicsControlAssetEditor.h"
```

### 基本用法：以编程方式创建资产

```cpp
// 来源：基于 UPhysicsControlAssetFactory 逻辑推断
#include "AssetToolsModule.h"
#include "IAssetTools.h"
#include "PhysicsControlAsset.h"

void CreateNewPhysicsControlAsset()
{
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    
    // 定义资产的基本信息
    FString PackagePath = TEXT("/Game/MyCharacters");
    FString AssetName = TEXT("PC_Hero_Death");
    
    // 使用工厂类创建资产
    UPhysicsControlAsset* NewAsset = Cast<UPhysicsControlAsset>(
        AssetTools.CreateAsset(AssetName, PackagePath, UPhysicsControlAsset::StaticClass(), nullptr)
    );
    
    if (NewAsset)
    {
        // 在此对 NewAsset 进行初始配置...
        // 例如，NewAsset->ControlSets.Add(...);
        
        // 标记为已修改，以便保存
        NewAsset->MarkPackageDirty();
    }
}
```

### 进阶用法：打开资产编辑器

通常由引擎资产定义类 `UAssetDefinition_PhysicsControlAsset::OpenAssets` 触发，但你也可以尝试编程打开：

```cpp
#include "PhysicsControlAsset.h"
#include "PhysicsControlAssetEditor/PhysicsControlAssetEditor.h"

void OpenAssetEditorForPhysicsControl(UPhysicsControlAsset* AssetToEdit)
{
    if (AssetToEdit)
    {
        // 获取资产编辑器模块（如果已加载）
        // 注意：直接实例化编辑器类（FPhysicsControlAssetEditor）是内部用法，不推荐。
        // 正确做法是通过资产系统触发，例如在代码中模拟双击打开资产。
        FAssetEditorManager::Get().OpenEditorForAsset(AssetToEdit);
    }
}
```

## Demo 示例

这是一个创建 `UPhysicsControlAsset` 并为其简单初始化数据的最小示例。

**MyPhysicsControlAssetHelper.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "PhysicsControlAsset.h"

class FMyPhysicsControlAssetHelper
{
public:
    // 创建一个基础的物理控制资产，并添加一个示例控制
    static UPhysicsControlAsset* CreateBasicAsset(const FString& InAssetPath, const FString& InAssetName);
};
```

**MyPhysicsControlAssetHelper.cpp**
```cpp
#include "MyPhysicsControlAssetHelper.h"
#include "AssetToolsModule.h"
#include "PhysicsControlAsset.h"

UPhysicsControlAsset* FMyPhysicsControlAssetHelper::CreateBasicAsset(const FString& InAssetPath, const FString& InAssetName)
{
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
    
    // 创建资产对象
    UPhysicsControlAsset* Asset = Cast<UPhysicsControlAsset>(
        AssetTools.CreateAsset(InAssetName, InAssetPath, UPhysicsControlAsset::StaticClass(), nullptr)
    );
    
    if (!Asset)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Physics Control Asset: %s/%s"), *InAssetPath, *InAssetName);
        return nullptr;
    }
    
    // 添加一个简单的控制集示例（具体结构需根据 UPhysicsControlAsset 实际定义）
    // 注意：以下为示意代码，真实的 ControlSet 结构可能不同。
    /*
    FPhysicsControlSet NewControlSet;
    NewControlSet.Name = FName("DefaultControl");
    
    // 配置一个控制...
    FPhysicsControl NewControl;
    NewControl.BoneName = FName("spine_01");
    NewControl.ControlType = EPhysicsControlType::Orientation; // 假设的枚举
    NewControl.Strength = 100.0f;
    NewControl.Damping = 1.0f;
    
    NewControlSet.Controls.Add(NewControl);
    Asset->ControlSets.Add(NewControlSet);
    */
    
    Asset->MarkPackageDirty();
    UE_LOG(LogTemp, Log, TEXT("Successfully created Physics Control Asset: %s/%s"), *InAssetPath, *InAssetName);
    
    return Asset;
}
```

## 模块依赖

从 `PhysicsControlEditor.Build.cs` 分析，该模块依赖核心的 `PhysicsControl` 运行时模块以及 Persona 编辑器框架。

| 模块 | 用途 |
|---|---|
| `PhysicsControl` | 核心运行时模块，提供 `UPhysicsControlAsset`、`UPhysicsControlComponent` 等基础类型。 |
| `Persona` | 提供 Persona 编辑器框架、预览场景、骨架树等基础设施。 |
| `SkeletalMeshEditor` | 提供骨骼网格体编辑相关的工具和UI支持。 |
| `PhysicsControlUncookedOnly` | 提供仅在未打包时使用的功能，可能包含蓝图图表节点等。 |
| `PropertyEditor` | 提供细节面板自定义（IDetailCustomization）的支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `6df5417c` | PhysicsControl: Clamp skeletal animation drive targets to joint limits to prevent spurious forces an | 修复骨骼动画驱动目标值越限问题，防止产生意外的物理力。 |
| 2026-05-14 | `99441775` | Physics Control - Fix for Enable/DiableDisableCollisionBetweenBody when called on the same frame as | 修复同一帧内调用“启用/禁用身体间碰撞”函数可能出现的时序问题。 |
| 2026-05-13 | `78406e38` | Control rig physics and Physics Control - clamp strength so that value < 0 don't cause unwanted beha | 对强度值进行钳制，防止负值导致意外行为。 |
| 2026-05-12 | `d5ffc351` | Add simple array versions of the Blueprint Enable/DisableCollisionBetweenBodies in PhysicsControl | 为蓝图的“启用/禁用身体间碰撞”功能添加了数组版本。 |
| 2026-05-12 | `647e07c7` | Add support for acceleration/force mode (a simple toggle) in physics control - control rig physics, | 为物理控制新增加速度/力模式切换支持。 |

### 维护评价

-   **创建时间**：2026年5月12日，非常新的插件。
-   **近期更新频率**：在创建后的一周内有密集的功能更新和Bug修复（至少5次提交），表明处于**活跃开发初期**。
-   **活跃状态**：**活跃维护中**。第一个提交信息显示“Move PhysicsControl plugin out of Experimental”，表明这是从实验性模块正式移出的版本，代码经过审查和整理。
-   **已知问题**：由于是新移出实验阶段，可能存在未经大规模用户验证的边界情况问题。从提交历史看，团队正在积极修复发现的问题。
-   **推荐使用**：**推荐尝试使用**。该插件功能明确，编辑器工具链完整，并且有Epic官方维护。对于需要实现复杂物理驱动动画的项目，它是官方提供的一套强大工具。但由于较新，建议在项目早期进行集成测试。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl)
-   [官方文档]() （暂无）
-   [测试用例]() （该编辑器模块的测试用例路径未在提供的资料中明确，通常位于 `Engine/Tests/` 或插件内部的 `Tests` 目录下）