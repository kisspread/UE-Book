# UAF Control Rig

> Control Rig integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF控制绑定集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFControlRig` (Runtime), `UAFControlRigEditor` (Runtime), `UAFControlRigTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig) | |

## 用途

该插件将 Control Rig（控制绑定）系统集成到 UAF（Unreal Animation Framework）的 Trait（特性）框架中。

UAF 是 Epic 正在开发的实验性动画框架，其核心概念是通过 Trait 来组合动画行为。此插件解决了**如何在 UAF Trait 体系中使用 Control Rig** 的问题——具体来说：

1. **Trait 共享数据定制**：为 `ControlRigTraitSharedData` 提供编辑器内的属性自定义面板，允许用户可视化地配置 Control Rig 与 UAF 之间的数据映射关系
2. **IO 映射**：管理 Control Rig 控件（Controls/ControlsInfo）与 UAF Trait 属性之间的输入/输出映射，支持将 Control Rig 的控件暴露为 Trait 的可选属性引脚
3. **编辑器集成**：提供 Control Rig 节点的双击交互等编辑器增强功能

简言之，这是连接 Control Rig 动画驱动系统与 UAF Trait 动画组合系统之间的桥梁。

## 使用场景

- 你正在使用 UAF 实验性动画框架构建角色动画系统 → 用此插件将 Control Rig 控件暴露为 UAF Trait 的属性
- 你需要在 UAF 的 Workspace 编辑器中可视化配置 Control Rig 的输入/输出映射 → 此插件提供属性自定义界面
- 你需要在 UAF Trait 系统中驱动 Control Rig 的控件（如 IK 目标、自定义骨骼变换等） → 通过变量映射实现
- 你正在编写依赖于 BP-independent Control Rig 资产的动画逻辑 → 此插件已修复对这类资产的查找支持

## 蓝图用法

该插件主要提供编辑器侧的属性自定义（Property Customization），没有直接暴露 BlueprintCallable 节点。其功能通过 UAF Trait 的编辑器界面隐式使用。

### 核心编辑器功能

| 功能 | 说明 | 所在类 |
|---|---|---|
| 属性自定义 | 为 ControlRigTraitSharedData 提供 IO 映射和属性暴露的自定义界面 | `FControlRigTraitSharedDataCustomization` |
| 变量映射 | 在 Control Rig 控件与 Trait 属性之间建立映射关系 | `FControlRigTraitSharedDataCustomization` |
| 控件信息查询 | 根据控件名称查找 Control Rig 中的控件元数据 | `FControlRigTraitSharedDataCustomization` |
| 节点交互 | 处理 Control Rig 节点的双击事件 | `FAnimNextControlRigEditorModule` |

### 使用方式

1. 在 UAF Workspace 编辑器中创建或选择一个使用 ControlRigTrait 的节点
2. 在细节面板（Details Panel）中，该插件会自动接管 `ControlRigTraitSharedData` 的属性显示
3. 通过自定义界面配置：
   - **变量映射**：将 Control Rig 变量映射到 Trait 的输入/输出
   - **属性暴露**：通过复选框控制哪些属性暴露为可选引脚
4. 映射配置通过 `FControlRigIOMapping` 结构体存储

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "AnimNextControlRigEditorModule.h"

// 控制绑定 Trait 属性自定义
#include "ControlRigTraitCustomization.h"
```

### 基本用法

基于头文件分析，该插件的核心 API 集中在 `FControlRigTraitSharedDataCustomization` 类中：

```cpp
// 获取 Control Rig Trait 的共享数据
// 来源: Internal/ControlRigTraitCustomization.h
TSharedPtr<FStructOnScope> SharedData = 
    FControlRigTraitSharedDataCustomization::GetControlRigSharedData(StructPropertyHandle);

// 获取目标 Control Rig 资产引用
FControlRigAssetStrongReference AssetRef = Customization->GetTargetAssetReference();

// 获取目标骨骼
USkeleton* Skeleton = Customization->GetTargetSkeleton();
```

### 进阶用法

IO 映射与变量映射操作：

```cpp
// 来源: Internal/ControlRigTraitCustomization.h

// 监听变量映射变化
// 当用户在编辑器中修改变量映射时触发
void OnVariableMappingChanged(const FName& PathName, const FName& Curve, bool bInput);

// 监听属性暴露状态变化
// bInput: true 表示是输入映射，false 表示是输出映射
void OnPropertyExposeCheckboxChanged(ECheckBoxState NewState, FName PropertyName);

// 查询控件信息
const FControlRigIOMapping::FControlsInfo* ControlInfo = 
    FControlRigTraitSharedDataCustomization::GetControlInfo(Controls, ControlName);

// 判断是否为变量属性（模板函数）
bool bIsVariable = FControlRigTraitSharedDataCustomization::IsVariableProperty(
    ControlRigTraitSharedData, PropertyName);

// 处理对象重新实例化（蓝图重编译等场景）
void OnObjectsReinstanced(const TMap<UObject*, UObject*>& OldToNewInstanceMap);

// 在 RigVM 图中查找 ControlRigTrait 的引脚名称
FString PinName = FindControlRigTraitPinName(ModelNode);
```

## Demo 示例

基于头文件推断的最小编辑器集成示例：

```cpp
// MyAnimNode.h
#pragma once

#include "CoreMinimal.h"

// 自定义一个使用 ControlRigTrait 的编辑器扩展
class FMyControlRigTraitEditor
{
public:
    void Initialize()
    {
        // 创建属性自定义实例
        Customization = MakeShared<UE::UAF::Editor::FControlRigTraitSharedDataCustomization>();
    }

    void SetupMapping(TSharedRef<IPropertyHandle> PropertyHandle)
    {
        // 获取 Control Rig 共享数据
        auto SharedData = UE::UAF::Editor::FControlRigTraitSharedDataCustomization
            ::GetControlRigSharedData(PropertyHandle);
        
        if (SharedData.IsValid())
        {
            // 共享数据可用于进一步配置映射
        }
    }

private:
    TSharedPtr<UE::UAF::Editor::FControlRigTraitSharedDataCustomization> Customization;
};
```

## 模块依赖

从 `.uplugin` 的 Plugins 数组及代码分析：

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心 Control Rig 运行时，提供控件系统和资产引用 |
| `AnimNext` | UAF/AnimNext 动画框架核心（Trait 系统基础） |
| `RigVM` | RigVM 虚拟机，Control Rig 的底层计算图系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移为 UE_LOGF 格式 |
| 2026-03-03 | `fb006c07` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 修复无法查找较新的独立于蓝图的 Control Rig 资产 |
| 2026-03-03 | `3757a39a` | [Backout] - CL51376416 | 回退 CL51376416 的改动（撤销了一次有问题的提交） |
| 2026-03-03 | `fc9640e7` | Control Rig: Fix ControlRigTrait not finding newer BP-independent rigs | 修复无法查找独立 Control Rig 资产（后被回退后重新提交） |
| 2026-02-27 | `6f697f67` | Allow system and graph factory initializer callbacks to add custom variable references | 允许系统和图工厂初始化回调添加自定义变量引用 |

### 维护评价

- **活跃度**：插件仍处于**活跃开发**状态，最近一次更新在 2026 年 4 月，距今不到 1 个月
- **成熟度**：版本号 0.1，标记为实验性（IsExperimentalVersion=true），未默认启用
- **稳定性**：2026-03-03 的提交经历了提交→回退→重新提交的过程，说明功能仍在迭代调试中
- **依赖关系**：紧耦合于 UAF/AnimNext 框架，该框架本身也是实验性的

**⚠️ 注意**：此插件为 Epic 实验性项目，API 可能随时变更或废弃。仅建议在探索 UAF 动画框架时参考，不建议用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFControlRig)
- [Control Rig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRig)
- 官方文档：无
- 测试用例：`Tests/UAFControlRigTests.Build.cs`（测试模块随插件一同提供）