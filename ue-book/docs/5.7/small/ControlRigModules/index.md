# Control Rig Modules

> Modules for ControlRig

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 是 |
| 模块 | 无（纯内容插件，`NoCode: true`） |
| 创建时间 | 2024-02-29 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Animation/ControlRigModules) | |

## 用途

Control Rig Modules 是一个**纯内容插件**（无 C++ 代码），为 UE5 的 **Modular Control Rig** 系统提供一套预制的、可复用的 Control Rig 模块（Module）。

Modular Control Rig 是 UE5.4 引入的新范式——它允许你像搭积木一样，将多个独立的 Control Rig 模块（每个模块本身就是一个 ControlRig 蓝图）通过 **Connector（连接器）** 组装成一个完整的角色绑定（Rig）。与传统的单一 ControlRig 蓝图相比，Modular Rig 更加模块化、可复用，非常适合标准化的角色绑定流程。

本插件提供了涵盖人体、动物和载具的常用身体部位模块，让你无需从零开始构建基础模块。

## 使用场景

- 你需要快速搭建一个**双足角色（Biped）**的 Control Rig → 使用 Arm、Leg、Spine、Neck、Foot、Shoulder、Finger 等模块
- 你需要为**四足动物**（马、龙等）创建绑定 → 使用 HindLeg、AnimalSpine、AnimalNeck、Tail 等模块
- 你需要绑定**载具**（汽车等）→ 使用 Wheel、Suspension、PivotProxy、VehiclePivotProxy 等模块
- 你需要构建**链式结构**（触手、尾巴、绳索等）→ 使用 Chain 模块
- 你需要为**铰链/活塞**等机械结构创建 IK → 使用 Hinge、Piston 模块

## 模块清单

### 人形角色模块

| 模块 | 说明 |
|---|---|
| `Arm` | 手臂绑定（含 IK/FK 切换、PV 跟随） |
| `Leg` | 腿部绑定（含 IK/FK 切换、PV 跟随） |
| `Spine` | 脊柱绑定 |
| `Neck` | 脖子/头部绑定 |
| `Shoulder` | 肩部绑定 |
| `Foot` | 足部绑定（含脚趾滚动等） |
| `Finger` | 手指绑定 |

### 动物/生物模块

| 模块 | 说明 |
|---|---|
| `AnimalSpine` | 动物脊柱（四足动物适用） |
| `AnimalNeck` | 动物脖子/头部 |
| `HindLeg` | 后腿（反关节腿部） |
| `Tail` | 尾巴 |

### 通用/机械模块

| 模块 | 说明 |
|---|---|
| `Chain` | 链式结构（触手、绳索等） |
| `Hinge` | 铰链关节（单轴旋转） |
| `Piston` | 活塞/线性运动 |
| `Constraint` | 约束模块 |
| `PivotProxy` | 枢轴代理（用于传递旋转中心） |
| `AddControl` | 添加自定义控制器 |

### 载具模块

| 模块 | 说明 |
|---|---|
| `Wheel` | 车轮 |
| `Suspension` | 悬挂系统 |
| `VehiclePivotProxy` | 载具专用枢轴代理 |

### 配置与模板

| 资源 | 说明 |
|---|---|
| `ModuleSettings` | 模块通用设置 |
| `SKM_Biped_Template` | 双足人体模板骨骼网格体 |
| `SK_Biped_Template` | 双足人体模板骨架 |
| `SKM_Dragon_Template` | 龙形生物模板骨骼网格体 |
| `SK_Dragon_Template` | 龙形生物模板骨架 |
| `SKM_Car_Template` | 汽车模板骨骼网格体 |
| `SK_Car_Template` | 汽车模板骨架 |
| `SKM_Chain_Template` | 链式结构模板骨骼网格体 |
| `SK_Chain_Template` | 链式结构模板骨架 |

## 蓝图用法

本插件本身不包含 C++ 代码，所有模块都是 **Control Rig 蓝图资产**（`.uasset`），在 Control Rig 编辑器的 **Modular Rig** 模式下使用。

### 在 Modular Rig 编辑器中使用模块

1. **创建 Modular Rig 蓝图**：在内容浏览器中右键 → Animation → Control Rig → 勾选 "Modular Rig" 选项
2. **添加模块**：在 Modular Rig 编辑器中，右键空白区域或使用工具栏，从模块列表中选择本插件提供的模块（如 `Arm`、`Leg` 等）
3. **连接模块**：通过拖拽 Connector 将模块连接到父模块或骨骼层级
4. **配置参数**：在 Details 面板中调整每个模块的配置值（Config Values），如 IK/FK 切换、极向量位置等

### 模块连接概念

Modular Rig 的核心是 **Connector（连接器）** 机制：

- 每个模块暴露若干 Connector，用于与其他模块的元素建立连接
- 例如：`Arm` 模块有一个 "Parent" Connector，需要连接到 `Shoulder` 模块的输出或骨骼层级中的某个骨骼
- 连接关系决定了模块间的父子层级和数据流向

### 模板使用

插件提供了多个模板骨架和网格体，用于快速预览和测试：

- `SKM_Biped_Template` / `SK_Biped_Template`：标准双足人体，适用于 Arm、Leg、Spine 等人形模块
- `SKM_Dragon_Template` / `SK_Dragon_Template`：龙形生物，适用于 AnimalSpine、Tail、AnimalNeck 等动物模块
- `SKM_Car_Template` / `SK_Car_Template`：汽车，适用于 Wheel、Suspension 等载具模块

## C++ 用法

本插件无 C++ 代码（`NoCode: true`），不提供 API。

如需通过 C++ 编程式操作 Modular Rig，请使用 ControlRig 插件中提供的 `UModularRigController` 类（属于 `ControlRig` 模块，非本插件）：

```cpp
#include "ModularRigController.h"

// 获取 Modular Rig 的控制器
UModularRigController* Controller = ControlRigAsset->GetModularRigController();

// 添加模块
FName ModuleName = Controller->AddModule(TEXT("MyArm"), ArmRigClass, ParentModuleName);

// 连接模块的 Connector
Controller->ConnectConnectorToElement(ConnectorKey, TargetBoneKey);

// 设置模块的配置值
Controller->SetConfigValueInModule(ModuleName, TEXT("bUseIK"), TEXT("true"));
```

## 模块依赖

本插件依赖以下插件（在 `.uplugin` 中声明）：

| 插件 | 用途 |
|---|---|
| `ControlRig` | 核心 Control Rig 框架，提供 Modular Rig 基础设施 |
| `ControlRigSpline` | Spline 相关的 Control Rig 功能（Chain 等模块使用） |
| `RigVM` | RigVM 虚拟机，Control Rig 的底层执行引擎 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2024-08-02 | `44826d01c29b` | 添加手臂/腿部 PV 跟随绑定、腕部对齐选项 |
| 2024-07-31 | `9277a40134bf` | 标记为 Beta 版本（5.5），大量动画修复：保持对齐、自动 PV 跟随、模板骨骼兼容性改进、肩部控制器形状修复 |
| 2024-02-29 | `3fe3f021e84d` | 从 5.4 的 29.01 重新提交，移除与 ControlRig 和 ControlRigSpline 插件的依赖问题 |

### 维护评价

- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，表明该插件仍处于 Beta 阶段
- **创建时间**：2024-02-29，约 2 年历史
- **活跃程度**：2024 年 7-8 月有密集的功能更新和修复，此后暂无新 commit（基于当前分支）
- **推荐使用**：作为 Epic 官方提供的预制模块库，适合快速原型和标准化绑定流程。但需注意其 Beta 状态，模块行为可能在后续版本中变化
- **注意事项**：存在 `Modules56` 目录（UE 5.6 版本的模块），表明模块资产在不同引擎版本间有兼容性适配

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Animation/ControlRigModules)
- [ControlRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/Animation/ControlRig)（本插件的依赖项，包含 Modular Rig 核心实现）
