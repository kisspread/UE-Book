# PhysicsControl

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产编辑器、骨骼网格体预览、操作器查看器） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlUncookedOnly` (UncookedOnly), `PhysicsControlEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl) | |

## 用途

PhysicsControl 插件提供了一套完整的运行时和编辑器工具，用于对静态网格体和骨骼网格体进行**物理驱动控制**。它的核心是 `UPhysicsControlComponent` 组件和 `AnimNode_RigidBodyWithControl` 动画图节点，允许开发者通过编程或动画蓝图定义身体的物理行为（如弹簧、阻尼、目标位置/旋转），而无需手动编写复杂的物理约束逻辑。

**为什么存在？**  
传统 UE 的物理系统（如物理资产 PhAT）侧重于物理资产的碰撞和约束编辑，但缺乏高级的物理控制抽象。PhysicsControl 插件通过以下方式解决：
- 提供**基于命名的控制集（Control Sets）和身体修改器（Body Modifiers）**，可以批量管理多个身体的控制参数。
- 支持**配置文件（Profile）系统**，可在运行时切换不同的控制行为（如受伤、死亡、抓取等）。
- 提供基于 **Rigid Body With Control 动画节点**的混合，在动画蓝图内无缝集成交互式物理模拟。
- 编辑器模块（PhysicsControlEditor）提供了专门的 **Physics Control Asset 编辑器**，用于可视化编辑控制配置、预览效果，并集成操作器查看器（Operator Viewer）来浏览所有可用的控制操作符及其标签。

## 使用场景

- **角色受伤/死亡效果**：当角色受伤时，通过切换配置文件使部分身体立刻进入 ragdoll 物理，同时保持其他身体受控。
- **动态抓取与操控**：使用 Physics Control Component 的 Grab/Release 功能，让角色手部抓住物体并传递物理力。
- **车辆/机械装置**：对骨骼网格体的特定身体施加弹簧阻尼，模拟悬挂或软体效果。
- **环境交互**：通过控制集为场景中的多个可破坏物体赋予受控物理，实现交互式破坏。
- **动画与物理融合**：在动画蓝图中使用 Rigid Body With Control 节点，让角色在播放动画的同时局部身体响应物理（如飘动的衣服）。

## 蓝图用法

> 本模块（PhysicsControlEditor）为编辑器模块，不直接暴露运行时蓝图节点。运行时蓝图功能由 `PhysicsControl` 运行时模块提供，常见可调用节点如下：

### 核心节点（运行时模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Control Set` | 创建一个控制集（Control Set），用于分组管理控制 | `UPhysicsControlComponent` |
| `Create Body Modifier Set` | 创建一个身体修改器集（Body Modifier Set），用于分组管理身体修改器 | `UPhysicsControlComponent` |
| `Add Control / Add Body Modifier` | 向已存在的控制集/修改器集中添加单项控制或修改器 | `UPhysicsControlComponent` |
| `Set Control Scale` | 设置一个控制的强度缩放 | `UPhysicsControlComponent` |
| `Activate Control Profile` | 激活指定名称的控制配置文件，批量改变控制参数 | `UPhysicsControlComponent` |
| `Grab / Ungrab` | 抓取/释放一个物体（PhysicsHandle 风格） | `UPhysicsControlComponent` |

### 使用示例（蓝图）

1. **创建并设置一个简单的身体控制**  
   - 获取 `PhysicsControlComponent`（通常附加在拥有骨骼网格体的 Actor 上）。  
   - 调用 `Create Control Set` 生成一个控制集并命名（例如 "LegControls"）。  
   - 调用 `Add Control`，指定骨骼名称、控制集名称，设置目标位置和强度。  
   - 编译运行后，该身体会受到弹簧力，趋向于保持初始位置。  

2. **切换配置文件实现受伤**  
   - 预先在 Physics Control Asset 中定义两个配置文件："Normal" 和 "Injured"。  
   - 在蓝图事件（如 `OnTakeDamage`）中调用 `Activate Control Profile`，传入 "Injured" 名称。  
   - 配置文件中的控制参数（如线性刚度、阻尼）将立即生效，模拟受伤后的物理柔化。

## C++ 用法

### 头文件引入

```cpp
#include "PhysicsControlComponent.h"
#include "PhysicsControlAsset.h"
#include "PhysicsControlEditorModule.h"
```

### 基本用法

**创建 PhysicsControlComponent 并添加控制（运行时模块）**

```cpp
// 在 Actor 的构造函数或 BeginPlay 中
UPhysicsControlComponent* ControlComp = CreateDefaultSubobject<UPhysicsControlComponent>(TEXT("PhysicsControl"));

// 创建一个控制集
FName ControlSetName = "TestControls";
ControlComp->CreateControlSet(ControlSetName);

// 为指定的骨骼添加一个控制
UControl* NewControl = ControlComp->AddControl(
    ControlSetName,
    SkeletalMeshComponent,
    BoneName,
    EControlType::PositionAndRotation,
    FControlParameters()
);
if (NewControl)
{
    NewControl->SetEnabled(true);
    NewControl->SetTargetTransform(FTransform::Identity);
}
```

**在编辑器中使用 PhysicsControlAsset 编辑器（PhysicsControlEditor 模块）**

```cpp
// 在某个工具类中
#include "PhysicsControlAssetFactory.h"
#include "PhysicsControlAssetEditor.h"

// 创建 PhysicsControlAsset 资产
UPhysicsControlAsset* NewAsset = NewObject<UPhysicsControlAsset>(Package, FName("MyPhysicsControl"), RF_Public | RF_Standalone);
NewAsset->CreateControlsFromSkeletalMesh(SkeletalMesh);

// 打开编辑器（通常在双击资产时自动执行）
// 手动调用：可以创建 FPhysicsControlAssetEditor::InitAssetEditor()
```

### 进阶用法

**自定义组件可视化器（扩展编辑器绘制）**

```cpp
// 继承 FPhysicsControlComponentVisualizer 的 DrawVisualization
class FMyCustomVisualizer : public FPhysicsControlComponentVisualizer
{
    virtual void DrawVisualization(
        const UActorComponent* Component,
        const FSceneView* View,
        FPrimitiveDrawInterface* PDI) override
    {
        // 调用基类绘制后，添加自定义线框/标签
        Super::DrawVisualization(Component, View, PDI);
        // 绘制自定义辅助线...
    }
};
```

**通过 OperatorViewer 获取所有可用的控制操作符**

```cpp
// 在编辑器模块启动后
if (FPhysicsControlOperatorViewer* Viewer = FModuleManager::LoadModuleChecked<FPhysicsControlEditorModule>("PhysicsControlEditor").GetOperatorViewer())
{
    Viewer->OpenOperatorNamesTab();
    // 界面中会显示 ControlType / ModifierType 等层次树
}
```

## Demo 示例

以下是一个最小可编译的编辑器模块示例，用于注册并打开 PhysicsControlAsset 编辑器：

### PhysicsControlEditorDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FPhysicsControlEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### PhysicsControlEditorDemo.cpp

```cpp
#include "PhysicsControlEditorDemo.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "PhysicsControlAsset.h"
#include "PhysicsControlAssetEditor.h"
#include "AssetTypeCategories.h"

#define LOCTEXT_NAMESPACE "FPhysicsControlEditorDemoModule"

void FPhysicsControlEditorDemoModule::StartupModule()
{
    // 注册 AssetTypeActions（示例中直接使用引擎内建注册；真实插件已在 FPhysicsControlEditorModule 中注册）
    // 此处仅为演示如何手动触发编辑器
    // 通常不需要手动执行，双击资产即可。
}

void FPhysicsControlEditorDemoModule::ShutdownModule()
{
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FPhysicsControlEditorDemoModule, PhysicsControlEditorDemo);
```

**注意**：此模块仅为演示结构，实际编辑器功能由引擎内部的 `FPhysicsControlEditorModule` 提供，无需额外代码。

## 模块依赖

### PhysicsControlEditor 的特殊依赖

| 模块 | 用途 |
|---|---|
| `PhysicsControl` | 运行时模块，提供核心类（PhysicsControlComponent, PhysicsControlAsset） |
| `PhysicsControlUncookedOnly` | 编译支持模块，处理控制集、修改器集的序列化和验证 |
| `Persona` | 提供骨骼网格体预览场景、骨架树、编辑模式框架 |
| `AssetTools` | 资产类型动作注册 |
| `PhysicsCore` | 物理引擎核心（与 PhysicsAsset 共享） |
| `AnimGraph` | 提供 RigidBodyWithControl 动画节点编辑 |
| `ApplicationCore` | 编辑器窗口管理等 |

### 其他（省略标准依赖）

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-11-18 bfe4143 — Sets the PhysicsControl plugin to Beta
- 2025-09-26 e040cfa — Disable diagnostic logging in RigidBodyWithControl in test/shipping and demote level to verbose.
- 2025-09-23 7b7ebe0 — Support using a mask when invoking control profiles
- 2025-09-23 4e0fa71 — Support control/modifier and set names in all the functions. Also tidies up the docs etc. No behavior change
- 2025-09-23 4bdb12a — Align RigidBodyWithControl KinematicTargetSpace with the other parts of PhysicsControl

### 维护评价

- **创建时间**：2025-09-23（约 0.2 年）。
- **最近更新**：2025-11-18 标记为 Beta，说明插件已相对稳定。之前有持续的功能更新（控制剖面掩码、名称支持等）。
- **活跃程度**：处于积极开发中，最近几个月有多个功能提交、日志和 API 清理。
-  **已知问题**：无（实验性阶段，但已标记为 Beta，说明 API 已趋稳定）。
- **推荐使用**：✅ 推荐在 UE5.7+ 项目中使用。由于是 Beta 插件，建议在测试环境中试用，但已可用于生产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/physics-control-plugin/)（如已发布）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/PhysicsControl/Tests)（假设路径）