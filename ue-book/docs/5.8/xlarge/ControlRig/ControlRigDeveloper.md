# Control Rig

> Framework for animation driven by user controls.

| 属性 | 值 |
|---|---|
| 中文名 | 控制绑定 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、形状库、材质模板） |
| 模块 | `ControlRig` (Runtime), `ControlRigDeveloper` (Runtime), `ControlRigEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-14 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig) | |

## 用途

ControlRig 是 UE5 的**程序化动画绑定框架**，允许用户通过可视化节点图（基于 RigVM）构建自定义动画操控系统。它解决了以下核心问题：

1. **自定义动画绑定**：在骨骼上创建控制器（Controls）、空物体（Nulls）、曲线（Curves）等元素，通过节点图定义它们之间的驱动关系，替代传统的蓝图动画逻辑。
2. **运行时动画控制**：不仅可以在编辑器中预览，还能在运行时驱动骨骼动画，支持程序化 IK、FK、物理混合等。
3. **模块化绑定系统**：支持将绑定拆分为可复用的模块（Modular Rig），在 Sequencer 中组合使用，实现复杂角色的分层动画。
4. **Sequencer 集成**：与 Sequencer 深度集成，支持在时间轴上动画化控制绑定的属性，实现关键帧动画与程序化动画的混合。
5. **资产化管理**：绑定蓝图（UControlRigBlueprint）可以作为独立资产管理，支持导入导出、版本控制、蓝图继承。

ControlRigDeveloper 模块是插件的**开发者工具层**，提供蓝图资产管理、动画图节点集成、编译支持、IO 映射等基础功能，是连接运行时 ControlRig 和编辑器 UI 的桥梁。

## 使用场景

- 你需要为角色创建自定义的 IK/FK 混合动画系统 → 用 ControlRig 构建绑定图
- 你需要在 Sequencer 中对程序化动画进行关键帧编辑 → 用 ControlRig + Sequencer
- 你正在做一个需要模块化动画的角色系统（如可更换装备的角色）→ 用 ControlRig 的 Modular Rig 功能
- 你需要在运行时通过代码或蓝图动态驱动骨骼姿态 → 用 ControlRig 的 Runtime API
- 你需要为动画蓝图中的某个节点自定义绑定逻辑 → 用 AnimGraphNode_ControlRig

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateControlRig` | 从蓝图资产创建一个 ControlRig 实例 | `UControlRigBlueprint` |
| `GetDebuggedControlRig` | 获取当前正在调试的 ControlRig 实例 | `UControlRigBlueprint` |
| `GetHierarchyController` | 获取层级控制器，用于操作骨骼/控制/空物体等元素 | `UControlRigBlueprint` |
| `GetModularRigController` | 获取模块化绑定控制器 | `UControlRigBlueprint` |
| `RecompileModularRig` | 重新编译模块化绑定 | `UControlRigBlueprint` |
| `SetPreviewMesh` | 设置蓝图编辑器中预览用的骨骼网格体 | `UControlRigBlueprint` |
| `GetPreviewMesh` | 获取当前预览用的骨骼网格体 | `UControlRigBlueprint` |
| `GetControlRigAssetReference` | 获取 ControlRig 的资产引用（强引用） | `UControlRigBlueprint` |
| `GetCurrentlyOpenRigBlueprints` | 获取所有当前打开的绑定蓝图（静态） | `UControlRigBlueprint` |
| `IsControlRigModule` | 检查当前蓝图是否是绑定模块 | `UControlRigBlueprint` |
| `FindReferencesToModule` | 查找所有引用了此模块的绑定资产 | `UControlRigBlueprint` |
| `UpdateExposedModuleConnectors` | 更新模块暴露的连接器 | `UControlRigBlueprint` |
| `ConvertHierarchyElementsToSpawnerNodes` | 将层级元素转换为生成器节点 | `UControlRigBlueprint` |
| `GetRigModuleIcon` | 获取绑定模块的图标纹理 | `UControlRigBlueprint` |

### 类型转换节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `TurnIntoControlRigModule` | 将独立绑定转换为绑定模块（仅编辑器） | `UControlRigBlueprint` |
| `CanTurnIntoStandaloneRig` | 检查是否可以转换为独立绑定（仅编辑器） | `UControlRigBlueprint` |
| `TurnIntoStandaloneRig` | 将绑定模块转换为独立绑定（仅编辑器） | `UControlRigBlueprint` |

### 使用示例（蓝图描述）

**创建并运行一个 ControlRig 实例：**

1. 获取你的 `UControlRigBlueprint` 资产引用（通过"Set Object by Class"或直接引用）
2. 调用 `CreateControlRig` 节点，返回一个 `UControlRig*` 实例
3. 通过 `GetHierarchyController` 获取层级控制器
4. 使用层级控制器的 SetTransform / SetControlValue 等节点操作骨骼姿态

**动画蓝图中集成 ControlRig：**

1. 在动画蓝图的 AnimGraph 中添加 `ControlRig` 节点（AnimGraphNode_ControlRig）
2. 在节点属性中指定 ControlRig 蓝图资产
3. 通过 Pin 暴露需要动画化的输入输出变量
4. 将节点连接到动画状态机或混合节点

## C++ 用法

### 头文件引入

```cpp
#include "ControlRig.h"
#include "ControlRigBlueprint.h"
#include "RigVMBlueprint.h"
#include "Rigs/RigHierarchyController.h"
```

### 基本用法

从 UControlRigBlueprint 创建实例并操作层级（参考 ControlRigBlueprintLegacy.h 中的接口）：

```cpp
// 假设你有一个 UControlRigBlueprint 资产引用
UControlRigBlueprint* RigBlueprint = LoadObject<UControlRigBlueprint>(nullptr, TEXT("/Game/MyRig.MyRig"));
if (!RigBlueprint) return;

// 创建 ControlRig 运行时实例
UControlRig* ControlRig = RigBlueprint->CreateControlRig();
if (!ControlRig) return;

// 获取层级控制器
URigHierarchyController* Controller = RigBlueprint->GetHierarchyController();
if (Controller)
{
    // 通过控制器可以添加/删除骨骼、控制、空物体等
    // Controller->AddBone(TEXT("MyBone"), FRigElementKey(), FTransform::Identity);
}

// 获取层级数据
URigHierarchy* Hierarchy = RigBlueprint->GetHierarchy();
if (Hierarchy)
{
    // 遍历所有层级元素
    for (auto Element : *Hierarchy)
    {
        UE_LOG(LogTemp, Log, TEXT("Element: %s (Type: %d)"), *Element->GetName().ToString(), Element->GetType());
    }
}
```

来源：`Public/ControlRigBlueprintLegacy.h` — `CreateControlRig()`, `GetHierarchyController()`, `GetHierarchy()`

### 进阶用法

查询资产信息和模块化绑定操作（结合 ControlRigBlueprintLegacy.h 和 ControlRigEditorAsset.h）：

```cpp
#include "ControlRigEditorAsset.h"

// 静态工具：检查一个对象是否是 ControlRig 资产
bool bIsCR = IControlRigEditorAssetInterface::IsAControlRigAsset(SomeObject);

// 从 AssetData 获取绑定类型
FAssetData AssetData = /* ... */;
EControlRigType RigType = IControlRigEditorAssetInterface::GetRigType(AssetData);

// 查询模块引用
TArray<FSoftObjectPath> References = IControlRigEditorAssetInterface::GetReferencesToRigModule(ModuleAssetData);

// 获取所有当前打开的绑定蓝图
TArray<UControlRigBlueprint*> OpenBPs = UControlRigBlueprint::GetCurrentlyOpenRigBlueprints();

// 模块化绑定控制器
if (RigBlueprint->IsControlRigModule())
{
    UModularRigController* ModularController = RigBlueprint->GetModularRigController();
    // 使用 ModularController 进行模块化绑定操作
}

// 影响图（Influence Map）- 定义元素间的依赖关系
FRigInfluenceMapPerEvent& Influences = RigBlueprint->GetInfluences();

// 模块化绑定模型
FModularRigModel& Model = RigBlueprint->GetModularRigModel();
```

来源：`Public/ControlRigEditorAsset.h` — `IsAControlRigAsset()`, `GetRigType()`, `GetReferencesToRigModule()`

### 编译器集成

```cpp
#include "ControlRigBlueprintCompiler.h"

// FControlRigBlueprintCompiler 可以判断蓝图是否可编译并执行编译
FControlRigBlueprintCompiler Compiler;
if (Compiler.CanCompile(MyBlueprint))
{
    FCompilerResultsLog Results;
    FKismetCompilerOptions Options;
    Compiler.Compile(MyBlueprint, Options, Results);
    
    if (Results.NumErrors > 0)
    {
        UE_LOG(LogTemp, Error, TEXT("ControlRig compile failed with %d errors"), Results.NumErrors);
    }
}
```

来源：`Public/ControlRigBlueprintCompiler.h`

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在运行时创建 ControlRig 并设置预览网格体：

```cpp
// MyRigHelper.h
#pragma once

#include "CoreMinimal.h"
#include "ControlRigBlueprint.h"

class FMyRigHelper
{
public:
    /** 从蓝图资产创建 ControlRig 并设置预览网格体 */
    static UControlRig* CreateRigFromBlueprint(
        UControlRigBlueprint* InBlueprint,
        USkeletalMesh* InPreviewMesh)
    {
        if (!InBlueprint)
        {
            return nullptr;
        }

        // 设置预览网格体
        InBlueprint->SetPreviewMesh(InPreviewMesh, false);

        // 创建运行时实例
        UControlRig* RigInstance = InBlueprint->CreateControlRig();
        return RigInstance;
    }

    /** 检查蓝图是否是模块化绑定 */
    static bool IsModuleRig(UControlRigBlueprint* InBlueprint)
    {
        if (!InBlueprint) return false;
        return InBlueprint->IsControlRigModule();
    }

    /** 获取绑定层级中的所有骨骼名称 */
    static TArray<FName> GetBoneNames(UControlRigBlueprint* InBlueprint)
    {
        TArray<FName> BoneNames;
        if (!InBlueprint) return BoneNames;

        URigHierarchy* Hierarchy = InBlueprint->GetHierarchy();
        if (!Hierarchy) return BoneNames;

        for (auto Element : *Hierarchy)
        {
            if (Element->GetType() == ERigElementType::Bone)
            {
                BoneNames.Add(Element->GetName());
            }
        }

        return BoneNames;
    }
};
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `RigVM` | 虚拟机核心，ControlRig 的节点图执行引擎 |
| `LevelSequence` | Sequencer 集成，支持在时间轴上动画化控制绑定 |

### 模块依赖

基于 ControlRigDeveloper 模块的头文件和接口分析，使用该模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心运行时模块，提供 UControlRig、URigHierarchy 等基础类型 |
| `RigVM` | 虚拟机引擎，提供 URigVMBlueprint、URigVMEdGraph 等基类 |
| `AnimationBlueprintLibrary` | 动画蓝图工具库 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等 + RigVM）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7fc008ea` | AutoBake: Fix crash with using Shim track editor, need to get real one in order to cast to shared po | 修复 AutoBake 使用 Shim 轨道编辑器时的崩溃问题 |
| 2026-05-26 | `0f35dc86` | Animating in Engine: Marquee selection in Animation Mode picks controls by pivot in addition to mesh | 动画模式下框选控制器时增加按枢轴点选择的支持 |
| 2026-05-22 | `c09576c8` | Control Rig: Fix older rigs not creating gizmos when controls are selected | 修复旧版绑定选择控制器时 Gizmo 不显示的问题 |
| 2026-05-22 | `4eed6d63` | Control Rig: Guard against invalid instance proxy. | 增加对无效实例代理的防护检查 |
| 2026-05-20 | `818e65b0` | Control Rig Nullptr check for static analyzer | 增加空指针检查以通过静态分析器 |

### 维护评价

**活跃维护** ⭐⭐⭐⭐⭐

- **年龄**：约 5 年，2021 年从 Experimental 迁移到 Animation 分类，标志着其正式成为引擎核心功能
- **更新频率**：极高，最近一周内有 5 次提交，包含功能增强、Bug 修复和代码质量改进
- **维护状态**：由 Epic Games 官方团队持续维护，是 UE5 动画系统的核心组件之一
- **代码规模**：861 个源文件，是引擎中最大的插件之一，体现了其功能的全面性
- **推荐度**：**强烈推荐**。ControlRig 是 UE5 官方推荐的动画绑定解决方案，正在逐步替代传统的 AnimGraph 手动节点方式。对于任何需要程序化动画、自定义 IK/FK 或与 Sequencer 深度集成的项目，ControlRig 都是首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig)
- [ControlRigDeveloper 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig/Source/ControlRigDeveloper)
- [UControlRigBlueprint 蓝图类](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/ControlRig/Source/ControlRigDeveloper/Public/ControlRigBlueprintLegacy.h)
- [IControlRigEditorAssetInterface 接口](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/ControlRig/Source/ControlRigDeveloper/Public/ControlRigEditorAsset.h)
- [AnimGraphNode_ControlRig 动画节点](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Animation/ControlRig/Source/ControlRigDeveloper/Public/AnimGraphNode_ControlRig.h)