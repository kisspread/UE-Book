# Gameplay Cameras Uncooked Only

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机（仅未打包） |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

`GameplayCamerasUncookedOnly` 模块是 GameplayCameras 插件的编辑器扩展部分，专为蓝图图表服务。它主要包含了在蓝图编辑器中操作摄像机Rig（Camera Rig）及其参数所需的自定义蓝图节点（K2Node）。该模块解决了在蓝图层面直观、安全地绑定和修改复杂摄像机Rig参数的需求，使得设计师无需编写C++代码即可通过可视化方式配置摄像机系统的数据驱动部分。

## 使用场景

- 你的项目使用了 GameplayCameras 插件的数据驱动摄像机Rig资产，需要在蓝图中动态设置或获取这些Rig的参数。
- 作为关卡设计师，你需要在蓝图中为过场动画或游戏逻辑调整摄像机行为，而这些行为由一个预先定义好的、复杂的摄像机Rig控制。
- 你希望避免在蓝图中手动构造复杂的结构体来设置摄像机参数，而是希望通过更友好、类型安全的自定义节点来完成。

## 蓝图用法

该模块提供的主要是自定义的蓝图节点（K2Node），用于操作摄像机Rig的参数。这些节点会根据关联的`UCameraRigAsset`资产，自动生成正确的输入/输出引脚。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Rig Parameters` | 给定一个摄像机Rig资产，设置其所有已暴露参数的值。 | `UK2Node_SetCameraRigParameters` |
| `Get Camera Rig Parameters` | 给定一个摄像机Rig资产，获取其所有已暴露参数的当前值。 | `UK2Node_GetCameraRigParameters` |
| `Set Camera Rig Parameter` | 给定一个摄像机Rig资产，设置其单个已暴露参数的值。 | `UK2Node_SetCameraRigParameter` |
| `Get Camera Rig Parameter` | 给定一个摄像机Rig资产，获取其单个已暴露参数的当前值。 | `UK2Node_GetCameraRigParameter` |

### 使用示例（蓝图描述）

1.  **设置参数**：在蓝图中，右键点击并搜索 “Set Camera Rig Parameters”。从下拉列表中选择你想要操作的摄像机Rig资产。节点会自动生成与该Rig中所有已暴露的“混合可调参数”和“数据参数”相对应的输入引脚。将你的数据（如旋转值、布尔开关等）连接到这些引脚上，当节点执行时，它会将这些值注入到正在使用该Rig的摄像机评估数据中。
2.  **获取参数**：类似地，使用 “Get Camera Rig Parameters” 或 “Get Camera Rig Parameter” 节点。选择一个Rig资产后，节点会生成输出引脚，用于读取该Rig在当前帧或特定评估上下文中的参数值。这些节点是纯函数（无执行引脚），可以在任何需要读取参数的地方使用。
3.  **参数关联**：如果蓝图类持有一个对 `UCameraRigAsset` 的引用（例如，通过变量暴露），你可以在节点的资产选择器中选择 “Use member variable”，然后选择该蓝图变量。这将把节点动态绑定到该变量指向的Rig上，使蓝图更加灵活。

## C++ 用法

此模块主要是编辑器和蓝图扩展，其运行时逻辑位于`GameplayCamerasRuntime`模块中。在C++层面，该模块主要提供了一些用于处理引脚类型的静态辅助类。

### 头文件引入

```cpp
#include “Helpers/CameraVariablePinTypeHelper.h“
#include “Helpers/CameraContextDataPinTypeHelper.h“
```

### 基本用法

这些辅助类的主要用途是，在编写自定义的K2Node或蓝图扩展时，将GameplayCameras系统内部的变量类型（如 `ECameraVariableType`）或数据类型（如 `ECameraContextDataType`）转换为蓝图编辑器可以识别的 `FEdGraphPinType`。

```cpp
// 示例：将一个摄像机变量类型（如浮点数）转换为蓝图引脚类型
// 来源：Public/Helpers/CameraVariablePinTypeHelper.h
ECameraVariableType MyVariableType = ECameraVariableType::Float;
const UScriptStruct* BlendableStructType = nullptr; // 对于基础类型，此参数为nullptr

FEdGraphPinType PinType = UE::Cameras::FCameraVariablePinTypeHelper::GetPinType(MyVariableType, BlendableStructType);

// 现在 PinType 可以用于创建蓝图节点的引脚，它对应一个Float类型的引脚。
```

```cpp
// 示例：将一个摄像机上下文数据类型转换为蓝图引脚类型
// 来源：Public/Helpers/CameraContextDataPinTypeHelper.h
ECameraContextDataType MyDataType = ECameraContextDataType::Rotator;
ECameraContextDataContainerType ContainerType = ECameraContextDataContainerType::Single;
const UObject* DataTypeObject = nullptr; // 对于基础类型，此参数为nullptr

FEdGraphPinType PinType = UE::Cameras::FCameraContextDataPinTypeHelper::GetPinType(MyDataType, ContainerType, DataTypeObject);

// PinType 对应一个 FRotator 类型的引脚。
```

## Demo 示例

以下是一个极简的示例，展示如何在自定义的蓝图节点（非K2Node）中利用这些辅助类来创建一个与摄像机参数类型匹配的引脚。

**MyCustomCameraNode.h**
```cpp
#pragma once

#include “CoreMinimal.h“
#include “K2Node.h“
#include “MyCustomCameraNode.generated.h“
// 引入前向声明
enum class ECameraVariableType : uint8;

UCLASS()
class UMyCustomCameraNode : public UK2Node
{
    GENERATED_BODY()

public:
    virtual void AllocateDefaultPins() override;
};
```

**MyCustomCameraNode.cpp**
```cpp
#include “MyCustomCameraNode.h“
#include “Helpers/CameraVariablePinTypeHelper.h“ // 关键的辅助类头文件

void UMyCustomCameraNode::AllocateDefaultPins()
{
    // 假设我们要为一个“混合可调浮点数”参数创建一个引脚
    const ECameraVariableType FloatType = ECameraVariableType::Float;

    // 使用辅助函数获取对应的FEdGraphPinType
    const FEdGraphPinType FloatPinType = UE::Cameras::FCameraVariablePinTypeHelper::GetPinType(FloatType, nullptr);

    // 创建一个输入引脚，其类型与摄像机变量类型自动匹配
    CreatePin(EGPD_Input, FloatPinType.GetTerminalType(), FloatPinType.PinCategory, FloatPinType.PinSubCategory, FloatPinType.PinSubCategoryObject.Get(), FName(“ParameterValue“));

    // 继续创建其他引脚（如输出、执行引脚等）...
    Super::AllocateDefaultPins();
}
```

## 模块依赖

根据常见的UE插件结构和此类编辑器/蓝图扩展模块的模式，推断其依赖如下（具体需参考其`Build.cs`文件）：

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 提供核心的摄像机Rig资产、变量类型等运行时数据结构。 |
| `GameplayCamerasEditor` | 可能提供基础的编辑器工具或资产类型定义。 |
| `BlueprintGraph` | 提供自定义蓝图节点（K2Node）所需的基础框架。 |
| `KismetCompiler` | 用于编译和扩展蓝图图表。 |

（注：`Core`, `CoreUObject`, `Engine`, `Slate`, `UMG` 等为常见依赖已省略。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复了在PIE（编辑器内运行）模式下摄像机变量覆盖不生效的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，将double常量截断为float时产生编译器警告的代码。 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为一些追踪通道添加或更新了描述信息。 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 提交标题仅为插件名称，可能是一次合并、清理或小幅调整。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移为UE_LOGF格式。 |

### 维护评价

-   **创建时间与年龄**：该插件创建于2020年，已有约6年历史，属于“老古董”级别。
-   **近期更新频率与内容**：从2026年4月至5月的提交记录来看，插件仍在持续维护中，更新包括功能性bug修复（PIE模式下的变量覆盖）、代码质量改进（编译器警告修复、日志宏迁移）以及信息补充。
-   **活跃度与状态**：更新频率中等，关注点从新功能转向稳定性和代码质量。标记为 `IsExperimentalVersion=true`，表明它仍处于实验性阶段，接口或功能可能在未来发生变化。
-   **推荐使用**：**有条件推荐**。如果你的项目需要其核心功能（数据驱动、模块化摄像机），并且愿意接受实验性API可能带来的变更风险，那么该插件是一个强大的工具。但对于追求长期稳定性的项目，需谨慎评估其实验性状态。建议关注其后续版本说明，以确认是否已转为稳定版。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- 测试用例路径（根据常见UE项目结构推断，可能位于 `Engine/Tests/GameplayCameras/` 或插件内部，需自行查找）