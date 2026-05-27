# Control Rig Modules

> Modules for Control Rig

| 属性 | 值 |
|---|---|
| 中文名 | 控制绑定模块包 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、控制绑定模块） |
| 模块 | `无（纯内容插件）` |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-29 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRigModules) | |

## 用途

此插件是一个**纯内容插件**，其核心作用是提供一组预先构建好的、可复用的**控制绑定模块**。它解决的问题是：当开发者需要同时使用 `ControlRig`、`ControlRigSpline`、`ControlRigPhysics` 和 `FullBodyIK` 等多个控制绑定相关插件的功能时，模块间的依赖关系会变得复杂。`ControlRigModules` 将这些插件的功能整合并封装成标准化的蓝图模块，使得开发者可以通过统一的接口来使用它们，简化了依赖管理和模块化角色的搭建流程。

## 使用场景

-   你需要为项目中的角色创建一个**模块化、标准化的动画控制系统**。
-   你正在使用 `ControlRig` 进行动画解算，并且需要用到样条线 (`ControlRigSpline`)、物理模拟 (`ControlRigPhysics`, `PhysicsControl`) 或全身IK (`FullBodyIK`) 功能。
-   你希望将角色的动画逻辑（如腿部IK、手臂IK、脊柱物理等）封装成可独立测试、复用和组合的**蓝图资产模块**，而不是全部写在一个庞大的控制绑定图中。

## 蓝图用法

此插件本身不包含可直接调用的 `UFUNCTION` 或可读写的 `UPROPERTY`。它的价值在于它提供的**蓝图资产**（控制绑定模块）。开发者通过**依赖此插件**，从而在其控制绑定图 (`ControlRig` Graph) 中**实例化**这些预设的模块。

### 核心节点（可间接使用的其他插件节点）

由于 `ControlRigModules` 是一个集成枢纽，使用它意味着你可以方便地访问其依赖插件提供的节点。以下是一些你将获得访问权限的节点类别示例：

| 节点/功能类别 | 说明 | 所在插件（通过本插件间接引入） |
|---|---|---|
| `Rig` 模块实例节点 | 在控制绑定图中添加和连接预制的模块。 | `ControlRig` |
| `Spline` 相关节点 | 创建和操作样条线，用于驱动链状结构（如尾巴、触手）。 | `ControlRigSpline` |
| `Physics` 相关节点 | 在控制绑定中集成刚体模拟、弹簧阻尼器等物理效果。 | `ControlRigPhysics`, `PhysicsControl` |
| `Full Body IK` 节点 | 执行基于骨骼拓扑和约束的全身逆向运动学解算。 | `FullBodyIK` |

### 使用示例（蓝图描述）

1.  **创建一个模块化角色蓝图**，并为其添加一个 `ControlRig Component`。
2.  在资产浏览器中，浏览 `ControlRigModules` 插件的内容，找到你需要的模块蓝图（例如，一个用于腿部IK的 `CR_Leg_IK` 模块）。
3.  打开你角色的主 `ControlRig` 资产。在图表中，右键搜索并添加来自 `ControlRigModules` 的 `Module` 节点。
4.  在模块节点的细节面板中，指定要使用的 `ControlRig` 模块资产（即步骤2找到的蓝图）。
5.  连接该模块的输入输出引脚（如骨骼变换、变量），将其集成到你的角色动画流程中。

## C++ 用法

此插件 **没有 C++ 源代码** (`“NoCode”: true`)。它不直接提供 C++ API。

如果你需要在 C++ 代码中以编程方式实例化或操作 `ControlRigModules` 中的模块，你需要通过 `ControlRig` 插件的 C++ API 来加载和使用这些蓝图资产。

### 头文件引入

由于没有自己的模块，你需要引入 `ControlRig` 的头文件来操作其资产。

```cpp
#include “ControlRig.h”
```

### 基本用法

加载一个来自 `ControlRigModules` 插件的控制绑定模块资产（蓝图）。

```cpp
// 引擎资产加载类
#include “UObject/ConstructorHelpers.h”

// 在某个构造函数或初始化函数中
ConstructorHelpers::FObjectFinder<UControlRig> ModuleAssetFinder(
    TEXT(“/ControlRigModules/Biped/Modules/CR_Leg_IK.CR_Leg_IK”)
);

if (ModuleAssetFinder.Succeeded())
{
    UControlRig* LegIKModule = ModuleAssetFinder.Object;
    // 你可以进一步使用这个模块资产，例如在 Control Rig 的图上下文中引用它。
}
```
*注意：上述路径仅为示例，实际路径需要根据插件内容目录调整。*

### 进阶用法

`ControlRigModules` 中的模块本质上是 `UControlRig` 的子类蓝图。在更高级的用法中，你可以：
1.  使用 `UControlRigComponent` 的 API 来运行一个包含多个预制模块的主控制绑定图。
2.  通过 `FRigVMController` 等接口，以程序化方式向控制绑定图中添加模块实例。
3.  理解模块之间的数据流（通过RigVM的Pin），并在C++层面设置或读取这些数据。

## Demo 示例

由于是纯内容插件，没有独立的编译示例。一个最小的“使用示例”体现在模块依赖设置上。

### 模块依赖设置 (.Build.cs)

```cpp
// MyAnimationModule.Build.cs
using UnrealBuildTool;

public class MyAnimationModule : ModuleRules
{
    public MyAnimationModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        // 你的模块需要依赖 ControlRig，以便能够操作控制绑定资产和组件
        PublicDependencyModuleNames.AddRange(new string[] {
            “Core”,
            “CoreUObject”,
            “Engine”,
            “ControlRig” // 关键依赖
        });

        // 如果你需要直接使用 ControlRigModules 中的资产，建议在 Content 中引用，无需额外 C++ 模块依赖。
    }
}
```

## 模块依赖

此插件作为**内容插件**，自身无C++模块。但它通过 `.uplugin` 的 `Plugins` 字段声明了对以下插件的**强依赖**。这意味着启用 `ControlRigModules` 会自动启用这些插件，并且你的项目或使用其中内容的模块间接触了这些依赖。

| 依赖插件 | 用途 |
|---|---|
| `ControlRig` | 核心控制绑定运行时和编辑器框架。 |
| `ControlRigSpline` | 提供样条线功能，用于创建和驱动链状骨骼。 |
| `RigVM` | 控制绑定使用的虚拟机，负责执行节点逻辑。 |
| `ControlRigPhysics` | 在控制绑定中集成物理模拟（刚体、约束等）。 |
| `PhysicsControl` | 提供更高级的物理角色控制功能。 |
| `FullBodyIK` | 提供全身逆向运动学解算器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `dfee5052` | Control Rig: Fix missing dependency in ControlRigModules | 修复了 ControlRigModules 中缺失的插件依赖问题。 |
| 2026-04-21 | `375fe847` | [ControlRigPhysics] Moved BipedPhysics to Control Rig Modules plugin. Reworked and fixed issues. | 将双足物理模块迁移到此插件，并进行了重构和问题修复。 |
| 2024-08-02 | `44826d01` | [Modular Control Rig]- Added arm and leg pv follow rigs to modules, wrist align options. | 为模块增加了手臂和腿的极矢量跟随控制，以及手腕对齐选项。 |
| 2024-08-01 | `9277a401` | [Backout] - CL35228213 - Assert during Cook Content Worker !NodeName.IsEmpty() && !RemainingPinPath. | 回滚了一次导致内容打包时崩溃的提交。 |
| 2024-07-31 | `ae169a7b` | Control Rig Modules - Marking plugin as Beta for 5.5. Lots of animation fixes for the modules - adde | 标记为5.5的Beta版，并对模块进行了大量动画修复和功能添加。 |

### 维护评价

**活跃维护**。尽管创建于2024年初，但直到2026年仍有功能性更新和缺陷修复，表明该插件处于持续开发和完善中。

*   **年龄**：约2年，相对于其他核心动画系统较新。
*   **更新频率**：近期（2026年）仍有两次提交，且内容涉及功能迁移和依赖修复，属于实质性维护。
*   **状态**：官方标记为 `Beta`，表明功能可能还未最终稳定，API和资产结构在未来版本中可能有变动。
*   **推荐度**：**推荐尝试使用**。对于需要快速搭建模块化、功能丰富的控制绑定系统的项目，这是一个非常有价值的资源包。但鉴于其Beta状态，在生产环境中使用时应密切关注版本更新日志，以应对可能的breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRigModules)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRigModules/Tests) (如果存在)