# UAF Control Rig

> Control Rig integration for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 控制绑定集成 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFControlRig` (Runtime), `UAFControlRigEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig) | |

## 用途

UAF Control Rig 插件为 UAF（Animation Unification Framework）提供了 Control Rig 集成能力。它允许在 UAF 的“特征”（Trait）系统中使用 Control Rig 进行骨骼控制映射，从而将 Control Rig 的灵活性与 UAF 的模块化动画框架结合。主要解决以下问题：

- 在 UAF 特征中绑定 Control Rig 的输入/输出参数（变量、曲线）
- 通过编辑器自定义 UI 方便地配置 Control Rig 与 UAF 特征之间的映射关系
- 统一控制绑定逻辑，简化动画艺术家的工作流

## 使用场景

- **开发 UAF 特征时集成 Control Rig**：如果你在 UAF 框架下创建自定义特征，并希望利用 Control Rig 进行骨骼控制（如位置、旋转、缩放），此插件提供可视化界面对齐输入/输出映射。
- **编辑器配置**：在动画编辑器中，通过细节面板直接选择目标 Control Rig 并暴露/隐藏属性，无需手动编写代码。

## 蓝图用法

此插件主要为编辑器 UI 扩展，不提供公开的蓝图可调用函数。所有功能通过细节面板自定义（`FControlRigTraitSharedDataCustomization`）实现，在蓝图编辑器中无直接使用的节点。

## C++ 用法

### 头文件引入

```cpp
#include "ControlRigTraitCustomization.h"
#include "AnimNextControlRigEditorModule.h"
```

### 基本用法

注册属性自定义化是此插件的主要用法。在模块启动时，通过 `PropertyEditorModule` 注册 `FControlRigTraitSharedData` 的自定义化。

**示例（在模块中注册）**：

```cpp
// 来源：Private/AnimNextControlRigEditorModule.cpp（推断）
void FAnimNextControlRigEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    PropertyModule.RegisterCustomPropertyTypeLayout(
        "ControlRigTraitSharedData",
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&UE::UAF::Editor::FControlRigTraitSharedDataCustomization::MakeInstance)
    );
}
```

### 进阶用法

当自定义化创建后，它会根据选择的 UAF 特征节点动态获取可用的 Control Rig 控制项，并在细节面板中生成相应的输入/输出映射 UI。开发者可以通过重写 `FControlRigTraitSharedDataCustomization` 中的回调（如 `OnVariableMappingChanged`）来响应映射变更。

**来源路径**：`Engine/Plugins/Experimental/UAF/UAFControlRig/Source/UAFControlRigEditor/Private/ControlRigTraitCustomization.cpp`

## Demo 示例

一个完整的最小示例，演示如何为自定义 UAF 特征设置 Control Rig 映射。

### MyUAFCharacterTrait.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/ObjectMacros.h"
#include "UAF/UAFTrait.h"
#include "UAFControlRig/Public/ControlRigTraitSharedData.h" // 实际路径可能不同
#include "MyUAFCharacterTrait.generated.h"

UCLASS(meta = (DisplayName = "My Character Trait"))
class UMyUAFCharacterTrait : public UActorComponent
{
    GENERATED_BODY()

public:
    // 此结构体由插件提供，用于存储 Control Rig 映射配置
    UPROPERTY(EditAnywhere, Category = "Control Rig")
    FControlRigTraitSharedData ControlRigData;
};
```

### MyUAFCharacterTrait.cpp

```cpp
#include "MyUAFCharacterTrait.h"
```

### 说明

- 在 UE 编辑器中，选择该特征组件后，细节面板将显示 `ControlRigData` 属性，并自动启用 UAF Control Rig 自定义 UI。
- 用户可在此 UI 中选择目标 Control Rig 蓝图，并映射其控制参数（如输入变量、曲线）到该特征的外部引脚。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 提供 Control Rig 运行时核心和蓝图支持 |
| `ControlRigEditor` | 提供编辑器自定义化和节点编辑功能 |
| `PropertyEditor` | 支持细节面板的自定义布局 |
| `UnrealEd` | 编辑器基础设施（如对象重新实例化回调） |

> **注意**：此列表包含非标准依赖。常见依赖（`Core`, `Engine`, `Slate` 等）已省略。

## 维护状态

### 近期更新

- 2025-09-23 `0ea1c505` 强制在 Update_AnyThread 中立即执行构造，如果必要
- 2025-08-26 `81f8ccfb` 创建 `IControlRigAssetInterface`，Control Rig 资产将继承自该接口
- 2025-08-22 `f187d7bb` 修复位置和缩放潜在引脚大小错误（使用了错误的类型）
- 2025-08-22 `66585cf3` 修复映射的控制被随机内存初始化（因控件不再...）
- 2025-07-22 `1fb8b34a` 正确处理乱序的潜在引脚

### 维护评价

- 创建于 2025-07-22，至今约 3 个月，属于**全新插件**。
- 最近几次提交均为功能修复和重要重构（如接口抽象、引脚处理），表明团队正在积极完善功能。
- 标记为实验性（`IsExperimentalVersion=true`），API 可能不稳定，但功能已经可用。
- 目前推荐用于尝试 UAF 与 Control Rig 集成的项目，但需注意未来可能的破坏性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFControlRig/Tests)（如果存在）